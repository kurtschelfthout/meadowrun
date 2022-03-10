"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class StringPair(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    KEY_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    key: typing.Text
    value: typing.Text
    def __init__(
        self,
        *,
        key: typing.Text = ...,
        value: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]
    ) -> None: ...

global___StringPair = StringPair

class ServerAvailableFolder(google.protobuf.message.Message):
    """Represents a folder (or folders) that contain code that the meadowgrid server can
    access directly
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    CODE_PATHS_FIELD_NUMBER: builtins.int
    @property
    def code_paths(
        self,
    ) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[typing.Text]:
        """code_paths[0] will be set as the working directory, and all code_paths will be
        added to the PYTHONPATH. These code_paths must "make sense" on the machine where
        the meadowgrid agent is running. One typical use case for this is that the
        meadowgrid agents have access to a shared filesystem where code has been
        deployed. Order matters as usual for PYTHONPATH. Another typical use case is to
        provide no code_paths because all of the code needed is already specified in the
        interpreter_deployment
        """
        pass
    def __init__(
        self,
        *,
        code_paths: typing.Optional[typing.Iterable[typing.Text]] = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["code_paths", b"code_paths"]
    ) -> None: ...

global___ServerAvailableFolder = ServerAvailableFolder

class GitRepoCommit(google.protobuf.message.Message):
    """Represents a git repo at a specific commit"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    REPO_URL_FIELD_NUMBER: builtins.int
    COMMIT_FIELD_NUMBER: builtins.int
    PATH_IN_REPO_FIELD_NUMBER: builtins.int
    repo_url: typing.Text
    """specifies the url, will be provided to git clone, see
    https://git-scm.com/docs/git-clone
    """

    commit: typing.Text
    """specifies the commit to use, will be provided to git checkout [commit] see
    https://git-scm.com/book/en/v2/Git-Tools-Revision-Selection
    """

    path_in_repo: typing.Text
    """specifies a relative path within the repo to treat as the "root" directory for
    the purposes of this deployment
    """

    def __init__(
        self,
        *,
        repo_url: typing.Text = ...,
        commit: typing.Text = ...,
        path_in_repo: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "commit",
            b"commit",
            "path_in_repo",
            b"path_in_repo",
            "repo_url",
            b"repo_url",
        ],
    ) -> None: ...

global___GitRepoCommit = GitRepoCommit

class GitRepoBranch(google.protobuf.message.Message):
    """Represents a git repo on a specific branch. Note that this is NOT deterministic as
    the coordinator will resolve the branch to a specific commit. In order to reproduce
    any results, the code must be run with the specific commit that this resolves to, NOT
    the branch that was originally specified. This should only be used when GitRepoBranch
    cannot be resolved to a GitRepoCommit on the client.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    REPO_URL_FIELD_NUMBER: builtins.int
    BRANCH_FIELD_NUMBER: builtins.int
    PATH_IN_REPO_FIELD_NUMBER: builtins.int
    repo_url: typing.Text
    """specifies the url, will be provided to git clone, see
    https://git-scm.com/docs/git-clone
    """

    branch: typing.Text
    """specifies the branch to use"""

    path_in_repo: typing.Text
    """specifies a relative path within the repo to treat as the "root" directory for
    the purposes of this deployment
    """

    def __init__(
        self,
        *,
        repo_url: typing.Text = ...,
        branch: typing.Text = ...,
        path_in_repo: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "branch",
            b"branch",
            "path_in_repo",
            b"path_in_repo",
            "repo_url",
            b"repo_url",
        ],
    ) -> None: ...

global___GitRepoBranch = GitRepoBranch

class ServerAvailableInterpreter(google.protobuf.message.Message):
    """Represents an interpreter that the meadowgrid server can access directly.
    interpreter_path can be set to meadowgrid.config.MEADOWGRID_INTERPRETER to indicate
    that this job should run using the same interpreter that's being used to run
    meadowgrid, which is only recommended for testing.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    INTERPRETER_PATH_FIELD_NUMBER: builtins.int
    interpreter_path: typing.Text
    def __init__(
        self,
        *,
        interpreter_path: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal["interpreter_path", b"interpreter_path"],
    ) -> None: ...

global___ServerAvailableInterpreter = ServerAvailableInterpreter

class ContainerAtDigest(google.protobuf.message.Message):
    """Represents a specific version (aka digest) of a container"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    REPOSITORY_FIELD_NUMBER: builtins.int
    DIGEST_FIELD_NUMBER: builtins.int
    repository: typing.Text
    """Together, repository and digest should be such that `docker pull
    [repository]@[digest]` works
    """

    digest: typing.Text
    def __init__(
        self,
        *,
        repository: typing.Text = ...,
        digest: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "digest", b"digest", "repository", b"repository"
        ],
    ) -> None: ...

global___ContainerAtDigest = ContainerAtDigest

class ContainerAtTag(google.protobuf.message.Message):
    """Represents a tag of a container. Note that this is NOT deterministic as the
    coordinator will resolve the tag to a specific digest. In order to reproduce any
    results, the code must be run with the specific digest that this resolves to, NOT the
    tag that was originally specified. This should only be used when ContainerAtTag
    cannot be resolved to a ContainerAtDigest on the client.
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    REPOSITORY_FIELD_NUMBER: builtins.int
    TAG_FIELD_NUMBER: builtins.int
    repository: typing.Text
    """Together, repository and tag should be such that `docker pull [repository]:[tag]`
    works
    """

    tag: typing.Text
    def __init__(
        self,
        *,
        repository: typing.Text = ...,
        tag: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "repository", b"repository", "tag", b"tag"
        ],
    ) -> None: ...

global___ContainerAtTag = ContainerAtTag

class ServerAvailableContainer(google.protobuf.message.Message):
    """Only recommended for testing. Represents a container image that already exists on the
    meadowgrid server. Helpful for testing with locally built images that haven't been
    uploaded to a repository and don't have a digest
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    IMAGE_NAME_FIELD_NUMBER: builtins.int
    image_name: typing.Text
    def __init__(
        self,
        *,
        image_name: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["image_name", b"image_name"]
    ) -> None: ...

global___ServerAvailableContainer = ServerAvailableContainer

class PyCommandJob(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    COMMAND_LINE_FIELD_NUMBER: builtins.int
    PICKLED_CONTEXT_VARIABLES_FIELD_NUMBER: builtins.int
    @property
    def command_line(
        self,
    ) -> google.protobuf.internal.containers.RepeatedScalarFieldContainer[
        typing.Text
    ]: ...
    pickled_context_variables: builtins.bytes
    def __init__(
        self,
        *,
        command_line: typing.Optional[typing.Iterable[typing.Text]] = ...,
        pickled_context_variables: builtins.bytes = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "command_line",
            b"command_line",
            "pickled_context_variables",
            b"pickled_context_variables",
        ],
    ) -> None: ...

global___PyCommandJob = PyCommandJob

class QualifiedFunctionName(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    MODULE_NAME_FIELD_NUMBER: builtins.int
    FUNCTION_NAME_FIELD_NUMBER: builtins.int
    module_name: typing.Text
    function_name: typing.Text
    def __init__(
        self,
        *,
        module_name: typing.Text = ...,
        function_name: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "function_name", b"function_name", "module_name", b"module_name"
        ],
    ) -> None: ...

global___QualifiedFunctionName = QualifiedFunctionName

class PyFunctionJob(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    QUALIFIED_FUNCTION_NAME_FIELD_NUMBER: builtins.int
    PICKLED_FUNCTION_FIELD_NUMBER: builtins.int
    PICKLED_FUNCTION_ARGUMENTS_FIELD_NUMBER: builtins.int
    @property
    def qualified_function_name(self) -> global___QualifiedFunctionName: ...
    pickled_function: builtins.bytes
    pickled_function_arguments: builtins.bytes
    def __init__(
        self,
        *,
        qualified_function_name: typing.Optional[global___QualifiedFunctionName] = ...,
        pickled_function: builtins.bytes = ...,
        pickled_function_arguments: builtins.bytes = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "function_spec",
            b"function_spec",
            "pickled_function",
            b"pickled_function",
            "qualified_function_name",
            b"qualified_function_name",
        ],
    ) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "function_spec",
            b"function_spec",
            "pickled_function",
            b"pickled_function",
            "pickled_function_arguments",
            b"pickled_function_arguments",
            "qualified_function_name",
            b"qualified_function_name",
        ],
    ) -> None: ...
    def WhichOneof(
        self, oneof_group: typing_extensions.Literal["function_spec", b"function_spec"]
    ) -> typing.Optional[
        typing_extensions.Literal["qualified_function_name", "pickled_function"]
    ]: ...

global___PyFunctionJob = PyFunctionJob

class GridTask(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    PICKLED_FUNCTION_ARGUMENTS_FIELD_NUMBER: builtins.int
    task_id: builtins.int
    pickled_function_arguments: builtins.bytes
    def __init__(
        self,
        *,
        task_id: builtins.int = ...,
        pickled_function_arguments: builtins.bytes = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "pickled_function_arguments",
            b"pickled_function_arguments",
            "task_id",
            b"task_id",
        ],
    ) -> None: ...

global___GridTask = GridTask

class Resource(google.protobuf.message.Message):
    """Agents have resources, and jobs can use resources. Examples of resources are CPU and
    memory
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    NAME_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    name: typing.Text
    value: builtins.float
    def __init__(
        self,
        *,
        name: typing.Text = ...,
        value: builtins.float = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["name", b"name", "value", b"value"]
    ) -> None: ...

global___Resource = Resource

class Job(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    JOB_ID_FIELD_NUMBER: builtins.int
    JOB_FRIENDLY_NAME_FIELD_NUMBER: builtins.int
    SERVER_AVAILABLE_FOLDER_FIELD_NUMBER: builtins.int
    GIT_REPO_COMMIT_FIELD_NUMBER: builtins.int
    GIT_REPO_BRANCH_FIELD_NUMBER: builtins.int
    SERVER_AVAILABLE_INTERPRETER_FIELD_NUMBER: builtins.int
    CONTAINER_AT_DIGEST_FIELD_NUMBER: builtins.int
    CONTAINER_AT_TAG_FIELD_NUMBER: builtins.int
    SERVER_AVAILABLE_CONTAINER_FIELD_NUMBER: builtins.int
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: builtins.int
    RESULT_HIGHEST_PICKLE_PROTOCOL_FIELD_NUMBER: builtins.int
    PY_COMMAND_FIELD_NUMBER: builtins.int
    PY_FUNCTION_FIELD_NUMBER: builtins.int
    job_id: typing.Text
    """job_id uniquely identifies this request to avoid duplicates and for getting the
    results later. Make sure job_id is unique! Multiple requests with the same job_id
    will be treated as duplicates even if all of the other parameters are different.
    Also, job_id may only use string.ascii_letters, numbers, ., -, and _.
    """

    job_friendly_name: typing.Text
    @property
    def server_available_folder(self) -> global___ServerAvailableFolder: ...
    @property
    def git_repo_commit(self) -> global___GitRepoCommit: ...
    @property
    def git_repo_branch(self) -> global___GitRepoBranch: ...
    @property
    def server_available_interpreter(self) -> global___ServerAvailableInterpreter: ...
    @property
    def container_at_digest(self) -> global___ContainerAtDigest:
        """The container specified should be such that running `docker run
        [repository]@[digest] python --version` works. Currently only works with
        Linux containers. If code_deployment specifies any code folders, they will be
        mounted in the container as /meadowgrid/code0, /meadowgrid/code1, etc.
        """
        pass
    @property
    def container_at_tag(self) -> global___ContainerAtTag: ...
    @property
    def server_available_container(self) -> global___ServerAvailableContainer: ...
    @property
    def environment_variables(
        self,
    ) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[
        global___StringPair
    ]: ...
    result_highest_pickle_protocol: builtins.int
    """result_highest_pickle_protocol tells the remote code what the highest pickle
    protocol we can read on this end is which will help it determine what pickle
    protocol to use to send back results. This should almost always be set to
    pickle.HIGHEST_PROTOCOL in the calling python process
    """

    @property
    def py_command(self) -> global___PyCommandJob: ...
    @property
    def py_function(self) -> global___PyFunctionJob: ...
    def __init__(
        self,
        *,
        job_id: typing.Text = ...,
        job_friendly_name: typing.Text = ...,
        server_available_folder: typing.Optional[global___ServerAvailableFolder] = ...,
        git_repo_commit: typing.Optional[global___GitRepoCommit] = ...,
        git_repo_branch: typing.Optional[global___GitRepoBranch] = ...,
        server_available_interpreter: typing.Optional[
            global___ServerAvailableInterpreter
        ] = ...,
        container_at_digest: typing.Optional[global___ContainerAtDigest] = ...,
        container_at_tag: typing.Optional[global___ContainerAtTag] = ...,
        server_available_container: typing.Optional[
            global___ServerAvailableContainer
        ] = ...,
        environment_variables: typing.Optional[
            typing.Iterable[global___StringPair]
        ] = ...,
        result_highest_pickle_protocol: builtins.int = ...,
        py_command: typing.Optional[global___PyCommandJob] = ...,
        py_function: typing.Optional[global___PyFunctionJob] = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "code_deployment",
            b"code_deployment",
            "container_at_digest",
            b"container_at_digest",
            "container_at_tag",
            b"container_at_tag",
            "git_repo_branch",
            b"git_repo_branch",
            "git_repo_commit",
            b"git_repo_commit",
            "interpreter_deployment",
            b"interpreter_deployment",
            "job_spec",
            b"job_spec",
            "py_command",
            b"py_command",
            "py_function",
            b"py_function",
            "server_available_container",
            b"server_available_container",
            "server_available_folder",
            b"server_available_folder",
            "server_available_interpreter",
            b"server_available_interpreter",
        ],
    ) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "code_deployment",
            b"code_deployment",
            "container_at_digest",
            b"container_at_digest",
            "container_at_tag",
            b"container_at_tag",
            "environment_variables",
            b"environment_variables",
            "git_repo_branch",
            b"git_repo_branch",
            "git_repo_commit",
            b"git_repo_commit",
            "interpreter_deployment",
            b"interpreter_deployment",
            "job_friendly_name",
            b"job_friendly_name",
            "job_id",
            b"job_id",
            "job_spec",
            b"job_spec",
            "py_command",
            b"py_command",
            "py_function",
            b"py_function",
            "result_highest_pickle_protocol",
            b"result_highest_pickle_protocol",
            "server_available_container",
            b"server_available_container",
            "server_available_folder",
            b"server_available_folder",
            "server_available_interpreter",
            b"server_available_interpreter",
        ],
    ) -> None: ...
    @typing.overload
    def WhichOneof(
        self,
        oneof_group: typing_extensions.Literal["code_deployment", b"code_deployment"],
    ) -> typing.Optional[
        typing_extensions.Literal[
            "server_available_folder", "git_repo_commit", "git_repo_branch"
        ]
    ]: ...
    @typing.overload
    def WhichOneof(
        self,
        oneof_group: typing_extensions.Literal[
            "interpreter_deployment", b"interpreter_deployment"
        ],
    ) -> typing.Optional[
        typing_extensions.Literal[
            "server_available_interpreter",
            "container_at_digest",
            "container_at_tag",
            "server_available_container",
        ]
    ]: ...
    @typing.overload
    def WhichOneof(
        self, oneof_group: typing_extensions.Literal["job_spec", b"job_spec"]
    ) -> typing.Optional[typing_extensions.Literal["py_command", "py_function"]]: ...

global___Job = Job

class JobToRun2(google.protobuf.message.Message):
    """TODO delete JobToRun and coordinator-based meadowgrid and rename this to JobToRun"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    JOB_FIELD_NUMBER: builtins.int
    CREDENTIALS_SOURCES_FIELD_NUMBER: builtins.int
    @property
    def job(self) -> global___Job: ...
    @property
    def credentials_sources(
        self,
    ) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[
        global___AddCredentialsRequest
    ]: ...
    def __init__(
        self,
        *,
        job: typing.Optional[global___Job] = ...,
        credentials_sources: typing.Optional[
            typing.Iterable[global___AddCredentialsRequest]
        ] = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["job", b"job"]
    ) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "credentials_sources", b"credentials_sources", "job", b"job"
        ],
    ) -> None: ...

global___JobToRun2 = JobToRun2

class ProcessState(google.protobuf.message.Message):
    """Represents the state of a process, can apply to a job or a grid task"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _ProcessStateEnum:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _ProcessStateEnumEnumTypeWrapper(
        google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[
            ProcessState._ProcessStateEnum.ValueType
        ],
        builtins.type,
    ):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        DEFAULT: ProcessState._ProcessStateEnum.ValueType  # 0
        """Reserved, not used"""

        RUN_REQUESTED: ProcessState._ProcessStateEnum.ValueType  # 1
        """These states represent a job that is "in progress"

        The meadowgrid coordinator has received the Job
        """

        RUNNING: ProcessState._ProcessStateEnum.ValueType  # 2
        """The assigned agent has launched the job. pid and log_file_name will be
        populated.
        """

        SUCCEEDED: ProcessState._ProcessStateEnum.ValueType  # 3
        """These states represent a job that is "done". log_file_name, return_code, and
        one of pid/container_id will be populated unless otherwise noted.

        The job has completed normally. pickled_result may be populated.
        """

        RUN_REQUEST_FAILED: ProcessState._ProcessStateEnum.ValueType  # 4
        """There was an exception before launching the job process. pid/container_id,
        log_file_name, and return_code will not be populated. pickled_result will be
        populated with a tuple representing the python exception from the agent
        process (see PYTHON_EXCEPTION for the format).
        """

        PYTHON_EXCEPTION: ProcessState._ProcessStateEnum.ValueType  # 5
        """A python exception was thrown from the job process. pickled_result will be a
        pickled tuple (exception_type, exception_message, exception_traceback). We
        don't pickle the exception itself because it may not be unpicklable on this
        end (e.g. it involves types that don't exist in the current process' code
        base). Exceptions are by their nature unexpected, so we shouldn't expect that
        they can be unpickled on the client.
        """

        NON_ZERO_RETURN_CODE: ProcessState._ProcessStateEnum.ValueType  # 6
        """The process exited with a non-zero return code. This could mean that a
        non-python exception was thrown (e.g. in the interpreter itself, or in a C
        extension), or os.exit was called with a non-zero argument, or there was a
        python exception thrown in the meadowgrid worker code.
        """

        RESOURCES_NOT_AVAILABLE: ProcessState._ProcessStateEnum.ValueType  # 7
        """We do not have any agents that are capable of running the job given its
        resource requirements. Either reduce the resource requirements of the job or
        launch agents that have enough resources.
        """

        ERROR_GETTING_STATE: ProcessState._ProcessStateEnum.ValueType  # 8
        """There was an error while reading the outputs of the process. This could mean
        that the child process somehow silently failed to write its outputs correctly
        or there was a python exception thrown in the meadowgrid worker code.
        """

        UNKNOWN: ProcessState._ProcessStateEnum.ValueType  # 9
        """This state represents a job that is neither "done" nor "in progress"

        We do not know the job id
        """

    class ProcessStateEnum(
        _ProcessStateEnum, metaclass=_ProcessStateEnumEnumTypeWrapper
    ):
        pass
    DEFAULT: ProcessState.ProcessStateEnum.ValueType  # 0
    """Reserved, not used"""

    RUN_REQUESTED: ProcessState.ProcessStateEnum.ValueType  # 1
    """These states represent a job that is "in progress"

    The meadowgrid coordinator has received the Job
    """

    RUNNING: ProcessState.ProcessStateEnum.ValueType  # 2
    """The assigned agent has launched the job. pid and log_file_name will be
    populated.
    """

    SUCCEEDED: ProcessState.ProcessStateEnum.ValueType  # 3
    """These states represent a job that is "done". log_file_name, return_code, and
    one of pid/container_id will be populated unless otherwise noted.

    The job has completed normally. pickled_result may be populated.
    """

    RUN_REQUEST_FAILED: ProcessState.ProcessStateEnum.ValueType  # 4
    """There was an exception before launching the job process. pid/container_id,
    log_file_name, and return_code will not be populated. pickled_result will be
    populated with a tuple representing the python exception from the agent
    process (see PYTHON_EXCEPTION for the format).
    """

    PYTHON_EXCEPTION: ProcessState.ProcessStateEnum.ValueType  # 5
    """A python exception was thrown from the job process. pickled_result will be a
    pickled tuple (exception_type, exception_message, exception_traceback). We
    don't pickle the exception itself because it may not be unpicklable on this
    end (e.g. it involves types that don't exist in the current process' code
    base). Exceptions are by their nature unexpected, so we shouldn't expect that
    they can be unpickled on the client.
    """

    NON_ZERO_RETURN_CODE: ProcessState.ProcessStateEnum.ValueType  # 6
    """The process exited with a non-zero return code. This could mean that a
    non-python exception was thrown (e.g. in the interpreter itself, or in a C
    extension), or os.exit was called with a non-zero argument, or there was a
    python exception thrown in the meadowgrid worker code.
    """

    RESOURCES_NOT_AVAILABLE: ProcessState.ProcessStateEnum.ValueType  # 7
    """We do not have any agents that are capable of running the job given its
    resource requirements. Either reduce the resource requirements of the job or
    launch agents that have enough resources.
    """

    ERROR_GETTING_STATE: ProcessState.ProcessStateEnum.ValueType  # 8
    """There was an error while reading the outputs of the process. This could mean
    that the child process somehow silently failed to write its outputs correctly
    or there was a python exception thrown in the meadowgrid worker code.
    """

    UNKNOWN: ProcessState.ProcessStateEnum.ValueType  # 9
    """This state represents a job that is neither "done" nor "in progress"

    We do not know the job id
    """

    STATE_FIELD_NUMBER: builtins.int
    PID_FIELD_NUMBER: builtins.int
    CONTAINER_ID_FIELD_NUMBER: builtins.int
    LOG_FILE_NAME_FIELD_NUMBER: builtins.int
    PICKLED_RESULT_FIELD_NUMBER: builtins.int
    RETURN_CODE_FIELD_NUMBER: builtins.int
    state: global___ProcessState.ProcessStateEnum.ValueType
    pid: builtins.int
    container_id: typing.Text
    log_file_name: typing.Text
    pickled_result: builtins.bytes
    return_code: builtins.int
    def __init__(
        self,
        *,
        state: global___ProcessState.ProcessStateEnum.ValueType = ...,
        pid: builtins.int = ...,
        container_id: typing.Text = ...,
        log_file_name: typing.Text = ...,
        pickled_result: builtins.bytes = ...,
        return_code: builtins.int = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "container_id",
            b"container_id",
            "log_file_name",
            b"log_file_name",
            "pickled_result",
            b"pickled_result",
            "pid",
            b"pid",
            "return_code",
            b"return_code",
            "state",
            b"state",
        ],
    ) -> None: ...

global___ProcessState = ProcessState

class JobStateUpdate(google.protobuf.message.Message):
    """For updating the state of a job"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    JOB_ID_FIELD_NUMBER: builtins.int
    GRID_WORKER_ID_FIELD_NUMBER: builtins.int
    PROCESS_STATE_FIELD_NUMBER: builtins.int
    job_id: typing.Text
    grid_worker_id: typing.Text
    """will only be populated if job_id refers to a GridJob"""

    @property
    def process_state(self) -> global___ProcessState: ...
    def __init__(
        self,
        *,
        job_id: typing.Text = ...,
        grid_worker_id: typing.Text = ...,
        process_state: typing.Optional[global___ProcessState] = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["process_state", b"process_state"]
    ) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "grid_worker_id",
            b"grid_worker_id",
            "job_id",
            b"job_id",
            "process_state",
            b"process_state",
        ],
    ) -> None: ...

global___JobStateUpdate = JobStateUpdate

class GridTaskStateResponse(google.protobuf.message.Message):
    """For getting the state of a grid task"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_ID_FIELD_NUMBER: builtins.int
    PROCESS_STATE_FIELD_NUMBER: builtins.int
    task_id: builtins.int
    @property
    def process_state(self) -> global___ProcessState: ...
    def __init__(
        self,
        *,
        task_id: builtins.int = ...,
        process_state: typing.Optional[global___ProcessState] = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing_extensions.Literal["process_state", b"process_state"]
    ) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "process_state", b"process_state", "task_id", b"task_id"
        ],
    ) -> None: ...

global___GridTaskStateResponse = GridTaskStateResponse

class GridTaskStatesResponse(google.protobuf.message.Message):
    """For getting the states of grid tasks"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    TASK_STATES_FIELD_NUMBER: builtins.int
    @property
    def task_states(
        self,
    ) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[
        global___GridTaskStateResponse
    ]: ...
    def __init__(
        self,
        *,
        task_states: typing.Optional[
            typing.Iterable[global___GridTaskStateResponse]
        ] = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["task_states", b"task_states"]
    ) -> None: ...

global___GridTaskStatesResponse = GridTaskStatesResponse

class AddCredentialsRequest(google.protobuf.message.Message):
    """This represents a credentials source (see credentials.py)"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    SERVICE_FIELD_NUMBER: builtins.int
    SERVICE_URL_FIELD_NUMBER: builtins.int
    AWS_SECRET_FIELD_NUMBER: builtins.int
    SERVER_AVAILABLE_FILE_FIELD_NUMBER: builtins.int
    service: global___Credentials.Service.ValueType
    service_url: typing.Text
    @property
    def aws_secret(self) -> global___AwsSecret: ...
    @property
    def server_available_file(self) -> global___ServerAvailableFile:
        """TODO add e.g. Azure secrets, Hashicorp Vault"""
        pass
    def __init__(
        self,
        *,
        service: global___Credentials.Service.ValueType = ...,
        service_url: typing.Text = ...,
        aws_secret: typing.Optional[global___AwsSecret] = ...,
        server_available_file: typing.Optional[global___ServerAvailableFile] = ...,
    ) -> None: ...
    def HasField(
        self,
        field_name: typing_extensions.Literal[
            "aws_secret",
            b"aws_secret",
            "server_available_file",
            b"server_available_file",
            "source",
            b"source",
        ],
    ) -> builtins.bool: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "aws_secret",
            b"aws_secret",
            "server_available_file",
            b"server_available_file",
            "service",
            b"service",
            "service_url",
            b"service_url",
            "source",
            b"source",
        ],
    ) -> None: ...
    def WhichOneof(
        self, oneof_group: typing_extensions.Literal["source", b"source"]
    ) -> typing.Optional[
        typing_extensions.Literal["aws_secret", "server_available_file"]
    ]: ...

global___AddCredentialsRequest = AddCredentialsRequest

class Credentials(google.protobuf.message.Message):
    """Represents actual credentials"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    class _Service:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _ServiceEnumTypeWrapper(
        google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[
            Credentials._Service.ValueType
        ],
        builtins.type,
    ):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        DEFAULT_SERVICE: Credentials._Service.ValueType  # 0
        DOCKER: Credentials._Service.ValueType  # 1
        GIT: Credentials._Service.ValueType  # 2

    class Service(_Service, metaclass=_ServiceEnumTypeWrapper):
        pass
    DEFAULT_SERVICE: Credentials.Service.ValueType  # 0
    DOCKER: Credentials.Service.ValueType  # 1
    GIT: Credentials.Service.ValueType  # 2

    class _Type:
        ValueType = typing.NewType("ValueType", builtins.int)
        V: typing_extensions.TypeAlias = ValueType

    class _TypeEnumTypeWrapper(
        google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[
            Credentials._Type.ValueType
        ],
        builtins.type,
    ):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
        DEFAULT_TYPE: Credentials._Type.ValueType  # 0
        USERNAME_PASSWORD: Credentials._Type.ValueType  # 1
        SSH_KEY: Credentials._Type.ValueType  # 2

    class Type(_Type, metaclass=_TypeEnumTypeWrapper):
        pass
    DEFAULT_TYPE: Credentials.Type.ValueType  # 0
    USERNAME_PASSWORD: Credentials.Type.ValueType  # 1
    SSH_KEY: Credentials.Type.ValueType  # 2

    CREDENTIALS_FIELD_NUMBER: builtins.int
    credentials: builtins.bytes
    def __init__(
        self,
        *,
        credentials: builtins.bytes = ...,
    ) -> None: ...
    def ClearField(
        self, field_name: typing_extensions.Literal["credentials", b"credentials"]
    ) -> None: ...

global___Credentials = Credentials

class AwsSecret(google.protobuf.message.Message):
    """Represents credentials stored in AWS. Must be accessible by the coordinator.
    - For credentials_type = USERNAME_PASSWORD: Expected keys are "username" and
      "password", e.g. SecretString should be like
      '{"username":"my_username","password":"my_password"}'
    - For credentials_type = SSH_KEY: Expected key is "private_key", which should contain
      the contents of the SSH private key file
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    CREDENTIALS_TYPE_FIELD_NUMBER: builtins.int
    SECRET_NAME_FIELD_NUMBER: builtins.int
    credentials_type: global___Credentials.Type.ValueType
    secret_name: typing.Text
    def __init__(
        self,
        *,
        credentials_type: global___Credentials.Type.ValueType = ...,
        secret_name: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "credentials_type", b"credentials_type", "secret_name", b"secret_name"
        ],
    ) -> None: ...

global___AwsSecret = AwsSecret

class ServerAvailableFile(google.protobuf.message.Message):
    """Represents credentials in a file. Must be a file accessible by the coordinator.
    - For credentials_type = USERNAME_PASSWORD: The file must have username on the first
      line and password on the second line. Final newline character is optional
    - For credentials_type = SSH_KEY: The file should be an SSH private key file
    """

    DESCRIPTOR: google.protobuf.descriptor.Descriptor
    CREDENTIALS_TYPE_FIELD_NUMBER: builtins.int
    PATH_FIELD_NUMBER: builtins.int
    credentials_type: global___Credentials.Type.ValueType
    path: typing.Text
    def __init__(
        self,
        *,
        credentials_type: global___Credentials.Type.ValueType = ...,
        path: typing.Text = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing_extensions.Literal[
            "credentials_type", b"credentials_type", "path", b"path"
        ],
    ) -> None: ...

global___ServerAvailableFile = ServerAvailableFile
