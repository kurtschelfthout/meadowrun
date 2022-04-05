from __future__ import annotations

import abc
import asyncio
import dataclasses
import functools
import io
import os.path
import pickle
import shlex
import threading
import uuid
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import cloudpickle
import fabric
import paramiko.ssh_exception

from meadowrun.aws_integration.ssh_keys import ensure_meadowrun_key_pair
from meadowrun.run_job_local import run_local
from meadowrun.aws_integration.aws_core import _get_default_region_name
from meadowrun.config import MEADOWRUN_INTERPRETER, JOB_ID_VALID_CHARACTERS
from meadowrun.credentials import CredentialsSourceForService
from meadowrun.deployment import (
    CodeDeployment,
    InterpreterDeployment,
    VersionedCodeDeployment,
    VersionedInterpreterDeployment,
)
from meadowrun.aws_integration.ec2_alloc import allocate_ec2_instances
from meadowrun.aws_integration.grid_tasks_sqs import (
    get_results,
    worker_loop,
    create_queues_and_add_tasks,
)
from meadowrun.meadowrun_pb2 import (
    AwsSecret,
    ContainerAtDigest,
    ContainerAtTag,
    Credentials,
    CredentialsSourceMessage,
    EnvironmentSpecInCode,
    GitRepoBranch,
    GitRepoCommit,
    Job,
    ProcessState,
    PyCommandJob,
    PyFunctionJob,
    QualifiedFunctionName,
    ServerAvailableContainer,
    ServerAvailableFile,
    ServerAvailableFolder,
    ServerAvailableInterpreter,
    StringPair,
)
from meadowrun.instance_selection import Resources

_T = TypeVar("_T")
_U = TypeVar("_U")


# if num_concurrent_tasks isn't specified, by default, launch total_num_tasks *
# _DEFAULT_CONCURRENT_TASKS_FACTOR workers
_DEFAULT_CONCURRENT_TASKS_FACTOR = 0.5


async def _retry(
    function: Callable[[], _T],
    exception_types: Union[Exception, Tuple[Exception, ...]],
    max_num_attempts: int = 5,
    delay_seconds: float = 1,
) -> _T:
    i = 0
    while True:
        try:
            return function()
        except exception_types as e:  # type: ignore
            i += 1
            if i >= max_num_attempts:
                raise
            else:
                print(f"Retrying on error: {e}")
                await asyncio.sleep(delay_seconds)


@dataclasses.dataclass(frozen=True)
class Deployment:
    interpreter: Union[
        InterpreterDeployment, VersionedInterpreterDeployment, None
    ] = None
    code: Union[CodeDeployment, VersionedCodeDeployment, None] = None
    environment_variables: Optional[Dict[str, str]] = None
    credentials_sources: Optional[List[CredentialsSourceForService]] = None

    @classmethod
    def git_repo(
        cls,
        repo_url: str,
        branch: Optional[str] = None,
        commit: Optional[str] = None,
        path_to_source: Optional[str] = None,
        conda_yml_file: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        ssh_key_aws_secret: Optional[str] = None,
    ) -> Deployment:
        """
        A deployment based on a git repo:
        - repo_url: e.g. https://github.com/meadowdata/test_repo
        - branch: defaults to "main" if neither branch nor commit are specified.
        - commit: can be provided instead of branch to use a specific commit hash
        - path_to_source: e.g. "src/python" to use a subdirectory of the repo
        - conda_yml_file: a directory (relative to the repo, note that this IGNORES
          path_to_source) that points to a file generated by `conda env export`. This
          file will be used to generate the environment to run in.
        - environment_variables: see class variable
        - ssh_key_aws_secret: The name of an AWS secret that has the
        """
        if branch and commit:
            raise ValueError("Only one of branch and commit can be specified")

        if not branch and not commit:
            branch = "main"

        if branch:
            code: Union[CodeDeployment, VersionedCodeDeployment, None] = GitRepoBranch(
                repo_url=repo_url,
                branch=branch,
                # the generated protobuf types say that path_to_source must not be None,
                # but this is not actually the case, it handles None fine, which we want
                # to take advantage of
                path_to_source=cast(str, path_to_source),
            )
        else:  # commit
            # guaranteed by prior ifs, this is just for mypy
            assert commit is not None
            code = GitRepoCommit(
                repo_url=repo_url,
                commit=commit,
                # see comment above
                path_to_source=cast(str, path_to_source),
            )

        if conda_yml_file:
            interpreter: Optional[InterpreterDeployment] = EnvironmentSpecInCode(
                environment_type=EnvironmentSpecInCode.EnvironmentType.CONDA,
                path_to_spec=conda_yml_file,
            )
        else:
            interpreter = None

        if ssh_key_aws_secret:
            credentials_sources = [
                CredentialsSourceForService(
                    service="GIT",
                    service_url=repo_url,
                    source=AwsSecret(
                        credentials_type=Credentials.Type.SSH_KEY,
                        secret_name=ssh_key_aws_secret,
                    ),
                )
            ]
        else:
            credentials_sources = []

        return cls(interpreter, code, environment_variables, credentials_sources)


def _credentials_source_message(
    credentials_source: CredentialsSourceForService,
) -> CredentialsSourceMessage:
    result = CredentialsSourceMessage(
        service=Credentials.Service.Value(credentials_source.service),
        service_url=credentials_source.service_url,
    )
    if isinstance(credentials_source.source, AwsSecret):
        result.aws_secret.CopyFrom(credentials_source.source)
    elif isinstance(credentials_source.source, ServerAvailableFile):
        result.server_available_file.CopyFrom(credentials_source.source)
    else:
        raise ValueError(
            f"Unknown type of credentials source {type(credentials_source.source)}"
        )
    return result


def _add_defaults_to_deployment(
    deployment: Optional[Deployment],
) -> Tuple[
    Union[InterpreterDeployment, VersionedInterpreterDeployment],
    Union[CodeDeployment, VersionedCodeDeployment],
    Iterable[StringPair],
    List[CredentialsSourceMessage],
]:
    if deployment is None:
        return (
            ServerAvailableInterpreter(interpreter_path=MEADOWRUN_INTERPRETER),
            ServerAvailableFolder(),
            {},
            [],
        )

    if deployment.credentials_sources:
        credentials_sources = [
            _credentials_source_message(c) for c in deployment.credentials_sources
        ]
    else:
        credentials_sources = []

    if deployment.environment_variables:
        environment_variables = [
            StringPair(key=key, value=value)
            for key, value in deployment.environment_variables.items()
        ]
    else:
        environment_variables = []

    return (
        deployment.interpreter
        or ServerAvailableInterpreter(interpreter_path=MEADOWRUN_INTERPRETER),
        deployment.code or ServerAvailableFolder(),
        environment_variables,
        credentials_sources,
    )


@dataclasses.dataclass
class JobCompletion(Generic[_T]):
    """Information about how a job completed"""

    # TODO both JobCompletion and MeadowrunException should be revisited

    result: _T
    process_state: ProcessState._ProcessStateEnum.ValueType
    log_file_name: str
    return_code: int


class MeadowrunException(Exception):
    def __init__(self, process_state: ProcessState) -> None:
        super().__init__("Failure while running a meadowrun job: " + str(process_state))
        self.process_state = process_state


class Host(abc.ABC):
    @abc.abstractmethod
    async def run_job(self, job: Job) -> JobCompletion[Any]:
        pass


@dataclasses.dataclass(frozen=True)
class LocalHost(Host):
    async def run_job(self, job: Job) -> JobCompletion[Any]:
        initial_update, continuation = await run_local(job)
        if (
            initial_update.state != ProcessState.ProcessStateEnum.RUNNING
            or continuation is None
        ):
            result = initial_update
        else:
            result = await continuation

        if result.state == ProcessState.ProcessStateEnum.SUCCEEDED:
            job_spec_type = job.WhichOneof("job_spec")
            # we must have a result from functions, in other cases we can optionally
            # have a result
            if job_spec_type == "py_function" or result.pickled_result:
                unpickled_result = pickle.loads(result.pickled_result)
            else:
                unpickled_result = None

            return JobCompletion(
                unpickled_result, result.state, result.log_file_name, result.return_code
            )
        else:
            raise MeadowrunException(result)


@dataclasses.dataclass(frozen=True)
class SshHost(Host):
    """
    Tells run_function and related functions to connects to the remote machine over SSH
    via the fabric library https://www.fabfile.org/ fabric_kwargs are passed directly to
    fabric.Connection().
    """

    address: str
    # these options are forwarded directly to Fabric
    fabric_kwargs: Optional[Dict[str, Any]] = None

    async def run_job(self, job: Job) -> JobCompletion[Any]:
        with fabric.Connection(
            self.address, **(self.fabric_kwargs or {})
        ) as connection:
            job_io_prefix = ""

            try:
                # assumes that meadowrun is installed in /var/meadowrun/env as per
                # build_meadowrun_amis.md. Also uses the default working_folder, which
                # should (but doesn't strictly need to) correspond to
                # agent._set_up_working_folder

                # try the first command 3 times, as this is when we actually try to
                # connect to the remote machine.
                connection.config["run"]["hide"] = True
                home_result = await _retry(
                    lambda: connection.run("echo $HOME"),
                    (
                        cast(Exception, paramiko.ssh_exception.NoValidConnectionsError),
                        cast(Exception, TimeoutError),
                    ),
                )
                if not home_result.ok:
                    raise ValueError(
                        "Error getting home directory on remote machine "
                        + home_result.stdout
                    )
                connection.config["run"]["hide"] = False

                remote_working_folder = f"{home_result.stdout.strip()}/meadowrun"
                mkdir_result = connection.run(f"mkdir -p {remote_working_folder}/io")
                if not mkdir_result.ok:
                    raise ValueError(
                        "Error creating meadowrun directory " + mkdir_result.stdout
                    )

                job_io_prefix = f"{remote_working_folder}/io/{job.job_id}"

                # serialize job_to_run and send it to the remote machine
                with io.BytesIO(job.SerializeToString()) as job_to_run_serialized:
                    connection.put(
                        job_to_run_serialized, remote=f"{job_io_prefix}.job_to_run"
                    )

                # fabric doesn't have any async APIs, which means that in order to run
                # more than one fabric command at the same time, we need to have a
                # thread per fabric command. We use an asyncio.Future here to make the
                # API async, so from the user perspective, it feels like this function
                # is async

                # fabric is supposedly not threadsafe, but it seems to work as long as
                # more than one connection is not being opened at the same time:
                # https://github.com/fabric/fabric/pull/2010/files
                result_future: asyncio.Future = asyncio.Future()
                event_loop = asyncio.get_running_loop()

                command = (
                    f"/var/meadowrun/env/bin/meadowrun-local --job-id {job.job_id} "
                    # TODO --needs-deallocation should only be passed in if we were
                    # originally using an EC2AllocHost
                    f"--working-folder {remote_working_folder} --needs-deallocation"
                )

                print(f"Running {command}")

                def run_and_wait() -> None:
                    try:
                        # use meadowrun to run the job
                        returned_result = connection.run(command)
                        event_loop.call_soon_threadsafe(
                            lambda r=returned_result: result_future.set_result(r)
                        )
                    except Exception as e2:
                        event_loop.call_soon_threadsafe(
                            lambda e2=e2: result_future.set_exception(e2)
                        )

                threading.Thread(target=run_and_wait).start()

                result = await result_future

                # TODO consider using result.tail, result.stdout

                # see if we got a normal return code
                if result.return_code != 0:
                    raise ValueError(f"Process exited {result.return_code}")

                with io.BytesIO() as result_buffer:
                    connection.get(f"{job_io_prefix}.process_state", result_buffer)
                    result_buffer.seek(0)
                    process_state = ProcessState()
                    process_state.ParseFromString(result_buffer.read())

                if process_state.state == ProcessState.ProcessStateEnum.SUCCEEDED:
                    job_spec_type = job.WhichOneof("job_spec")
                    # we must have a result from functions, in other cases we can
                    # optionally have a result
                    if job_spec_type == "py_function" or process_state.pickled_result:
                        result = pickle.loads(process_state.pickled_result)
                    else:
                        result = None
                    return JobCompletion(
                        result,
                        process_state.state,
                        process_state.log_file_name,
                        process_state.return_code,
                    )
                else:
                    raise MeadowrunException(process_state)
            finally:
                if job_io_prefix:
                    remote_paths = " ".join(
                        [
                            f"{job_io_prefix}.job_to_run",
                            f"{job_io_prefix}.state",
                            f"{job_io_prefix}.result",
                            f"{job_io_prefix}.process_state",
                            f"{job_io_prefix}.initial_process_state",
                        ]
                    )
                    try:
                        # -f so that we don't throw an error on files that don't
                        # exist
                        connection.run(f"rm -f {remote_paths}")
                    except Exception as e:
                        print(
                            f"Error cleaning up files on remote machine: "
                            f"{remote_paths} {e}"
                        )

                    # TODO also clean up log files?


@dataclasses.dataclass(frozen=True)
class EC2AllocHost(Host):
    """A placeholder for a host that will be allocated/created by ec2_alloc.py"""

    logical_cpu_required: int
    memory_gb_required: float
    interruption_probability_threshold: float
    region_name: Optional[str] = None

    async def run_job(self, job: Job) -> JobCompletion[Any]:
        region_name = self.region_name or await _get_default_region_name()
        pkey = ensure_meadowrun_key_pair(region_name)

        hosts = await allocate_ec2_instances(
            Resources(self.memory_gb_required, self.logical_cpu_required, {}),
            1,
            self.interruption_probability_threshold,
            region_name,
        )

        fabric_kwargs: Dict[str, Any] = {
            "user": "ubuntu",
            "connect_kwargs": {"pkey": pkey},
        }

        if len(hosts) != 1:
            raise ValueError(f"Asked for one host, but got back {len(hosts)}")
        host, job_ids = list(hosts.items())[0]
        if len(job_ids) != 1:
            raise ValueError(f"Asked for one job allocation but got {len(job_ids)}")

        # Kind of weird that we're changing the job_id here, but okay as long as job_id
        # remains mostly an internal concept
        job.job_id = job_ids[0]

        return await SshHost(host, fabric_kwargs).run_job(job)


@dataclasses.dataclass(frozen=True)
class EC2AllocHosts:
    """
    A placeholder for a set of hosts that will be allocated/created by ec2_alloc.py
    """

    logical_cpu_required_per_task: int
    memory_gb_required_per_task: float
    interruption_probability_threshold: float
    # defaults to half the number of total tasks
    num_concurrent_tasks: Optional[int] = None
    region_name: Optional[str] = None


def _pickle_protocol_for_deployed_interpreter() -> int:
    """
    This is a placeholder, the intention is to get the deployed interpreter's version
    somehow from the Deployment object or something like it and use that to determine
    what the highest pickle protocol version we can use safely is.
    """

    # TODO just hard-coding the interpreter version for now, need to actually grab it
    #  from the deployment somehow
    interpreter_version = (3, 8, 0)

    # based on documentation in
    # https://docs.python.org/3/library/pickle.html#data-stream-format
    if interpreter_version >= (3, 8, 0):
        protocol = 5
    elif interpreter_version >= (3, 4, 0):
        protocol = 4
    elif interpreter_version >= (3, 0, 0):
        protocol = 3
    else:
        # TODO support for python 2 would require dealing with the string/bytes issue
        raise NotImplementedError("We currently only support python 3")

    return min(protocol, pickle.HIGHEST_PROTOCOL)


def _make_valid_friendly_name(job_id: str) -> str:
    return "".join(c for c in job_id if c in JOB_ID_VALID_CHARACTERS)


def _get_friendly_name(function: Callable[[_T], _U]) -> str:
    friendly_name = getattr(function, "__name__", "")
    if not friendly_name:
        friendly_name = "lambda"

    return _make_valid_friendly_name(friendly_name)


async def run_function(
    function: Union[Callable[..., _T], str],
    host: Host,
    deployment: Optional[Deployment] = None,
    args: Optional[Sequence[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
) -> _T:
    """
    Runs function on a remote machine, specified by "host".

    Function can either be a reference to a function, a lambda, or a string like
    "package.module.function_name" (the last option is useful if the function cannot be
    referenced in the current environment but can be referenced in the deployed
    environment)

    The remote machine must have meadowrun installed as per build_meadowrun_amis.md
    """

    pickle_protocol = _pickle_protocol_for_deployed_interpreter()

    # first pickle the function arguments from job_run_spec

    # TODO add support for compressions, pickletools.optimize, possibly cloudpickle?
    # TODO also add the ability to write this to a shared location so that we don't need
    #  to pass it through the server.
    if args or kwargs:
        pickled_function_arguments = pickle.dumps(
            (args, kwargs), protocol=pickle_protocol
        )
    else:
        # according to docs, None is translated to empty anyway
        pickled_function_arguments = b""

    # now, construct the PyFunctionJob

    job_id = str(uuid.uuid4())
    if isinstance(function, str):
        friendly_name = function
        module_name, separator, function_name = function.rpartition(".")
        if not separator:
            raise ValueError(
                f"Function must be in the form module_name.function_name: {function}"
            )
        py_function = PyFunctionJob(
            pickled_function_arguments=pickled_function_arguments,
            qualified_function_name=QualifiedFunctionName(
                module_name=module_name,
                function_name=function_name,
            ),
        )
    else:
        friendly_name = _get_friendly_name(function)
        pickled_function = cloudpickle.dumps(function)
        # TODO larger functions should get copied to S3/filesystem instead of sent
        # directly
        print(f"Size of pickled function is {len(pickled_function)}")
        py_function = PyFunctionJob(
            pickled_function_arguments=pickled_function_arguments,
            pickled_function=pickled_function,
        )

    # now create the Job

    (
        interpreter,
        code,
        environment_variables,
        credentials_sources,
    ) = _add_defaults_to_deployment(deployment)

    job = Job(
        job_id=job_id,
        job_friendly_name=friendly_name,
        environment_variables=environment_variables,
        result_highest_pickle_protocol=pickle.HIGHEST_PROTOCOL,
        py_function=py_function,
        credentials_sources=credentials_sources,
    )
    _add_deployments_to_job(job, code, interpreter)

    return (await host.run_job(job)).result


async def run_command(
    args: Union[str, Sequence[str]],
    host: Host,
    deployment: Optional[Deployment] = None,
    context_variables: Optional[Dict[str, Any]] = None,
) -> JobCompletion[None]:
    """
    Runs the specified command on a remote machine. See run_function_remote for more
    details on requirements for the remote host.
    """

    job_id = str(uuid.uuid4())
    if isinstance(args, str):
        args = shlex.split(args)
    # this is kind of a silly way to get a friendly name--treat the first three
    # elements of args as if they're paths and take the last part of each path
    friendly_name = "-".join(os.path.basename(arg) for arg in args[:3])

    (
        interpreter,
        code,
        environment_variables,
        credentials_sources,
    ) = _add_defaults_to_deployment(deployment)

    if context_variables:
        pickled_context_variables = pickle.dumps(
            context_variables, protocol=_pickle_protocol_for_deployed_interpreter()
        )
    else:
        pickled_context_variables = b""

    job = Job(
        job_id=job_id,
        job_friendly_name=_make_valid_friendly_name(friendly_name),
        environment_variables=environment_variables,
        result_highest_pickle_protocol=pickle.HIGHEST_PROTOCOL,
        py_command=PyCommandJob(
            command_line=args, pickled_context_variables=pickled_context_variables
        ),
        credentials_sources=credentials_sources,
    )
    _add_deployments_to_job(job, code, interpreter)

    return await host.run_job(job)


async def run_map(
    function: Callable[[_T], _U],
    args: Sequence[_T],
    hosts: EC2AllocHosts,
    deployment: Optional[Deployment] = None,
) -> Sequence[_U]:
    """Equivalent to map(function, args), but runs distributed."""

    if not hosts.num_concurrent_tasks:
        num_concurrent_tasks = len(args) // 2 + 1
    else:
        num_concurrent_tasks = min(hosts.num_concurrent_tasks, len(args))

    region_name = hosts.region_name or await _get_default_region_name()
    pkey = ensure_meadowrun_key_pair(region_name)

    # the first stage of preparation, which happens concurrently:

    # 1. get hosts
    allocated_hosts_future = asyncio.create_task(
        allocate_ec2_instances(
            Resources(
                hosts.memory_gb_required_per_task,
                hosts.logical_cpu_required_per_task,
                {},
            ),
            num_concurrent_tasks,
            hosts.interruption_probability_threshold,
            region_name,
        )
    )

    # 2. create SQS queues and add tasks to the request queue
    queues_future = asyncio.create_task(create_queues_and_add_tasks(region_name, args))

    # 3. prepare some variables for constructing the worker jobs
    friendly_name = _get_friendly_name(function)
    (
        interpreter,
        code,
        environment_variables,
        credentials_sources,
    ) = _add_defaults_to_deployment(deployment)
    pickle_protocol = _pickle_protocol_for_deployed_interpreter()
    fabric_kwargs: Dict[str, Any] = {"user": "ubuntu", "connect_kwargs": {"pkey": pkey}}

    # now wait for 1 and 2 to complete:
    request_queue_url, result_queue_url = await queues_future
    allocated_hosts = await allocated_hosts_future

    # Now we will run worker_loop jobs on the hosts we got:

    pickled_worker_function = cloudpickle.dumps(
        functools.partial(
            worker_loop, function, request_queue_url, result_queue_url, region_name
        ),
        protocol=pickle_protocol,
    )

    worker_tasks = []
    worker_id = 0
    for public_address, worker_job_ids in allocated_hosts.items():
        for worker_job_id in worker_job_ids:
            job = Job(
                job_id=worker_job_id,
                job_friendly_name=friendly_name,
                environment_variables=environment_variables,
                result_highest_pickle_protocol=pickle.HIGHEST_PROTOCOL,
                py_function=PyFunctionJob(
                    pickled_function=pickled_worker_function,
                    pickled_function_arguments=pickle.dumps(
                        ([public_address, worker_id], {}), protocol=pickle_protocol
                    ),
                ),
                credentials_sources=credentials_sources,
            )
            _add_deployments_to_job(job, code, interpreter)

            worker_tasks.append(
                asyncio.create_task(SshHost(public_address, fabric_kwargs).run_job(job))
            )

            worker_id += 1

    # finally, wait for results:

    results = await get_results(result_queue_url, region_name, len(args))

    # not really necessary except interpreter will complain...
    await asyncio.gather(*worker_tasks)

    return results


def _add_deployments_to_job(
    job: Job,
    code_deployment: Union[CodeDeployment, VersionedCodeDeployment],
    interpreter_deployment: Union[
        InterpreterDeployment, VersionedInterpreterDeployment
    ],
) -> None:
    """
    Think of this as job.code_deployment = code_deployment; job.interpreter_deployment =
    interpreter_deployment, but it's complicated because these are protobuf oneofs
    """
    if isinstance(code_deployment, ServerAvailableFolder):
        job.server_available_folder.CopyFrom(code_deployment)
    elif isinstance(code_deployment, GitRepoCommit):
        job.git_repo_commit.CopyFrom(code_deployment)
    elif isinstance(code_deployment, GitRepoBranch):
        job.git_repo_branch.CopyFrom(code_deployment)
    else:
        raise ValueError(f"Unknown code deployment type {type(code_deployment)}")

    if isinstance(interpreter_deployment, ServerAvailableInterpreter):
        job.server_available_interpreter.CopyFrom(interpreter_deployment)
    elif isinstance(interpreter_deployment, ContainerAtDigest):
        job.container_at_digest.CopyFrom(interpreter_deployment)
    elif isinstance(interpreter_deployment, ServerAvailableContainer):
        job.server_available_container.CopyFrom(interpreter_deployment)
    elif isinstance(interpreter_deployment, ContainerAtTag):
        job.container_at_tag.CopyFrom(interpreter_deployment)
    elif isinstance(interpreter_deployment, EnvironmentSpecInCode):
        job.environment_spec_in_code.CopyFrom(interpreter_deployment)
    else:
        raise ValueError(
            f"Unknown interpreter deployment type {type(interpreter_deployment)}"
        )
