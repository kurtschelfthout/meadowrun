from __future__ import annotations

import contextlib
import functools
import inspect
import pickle
import traceback
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    OrderedDict,
    TypeVar,
    Union,
    cast,
    overload,
)

import meadowrun.optional_eliot as eliot
from meadowrun.meadowrun_pb2 import ProcessState


def pickle_exception(e: Exception, pickle_protocol: int) -> bytes:
    """
    We generally don't want to pickle exceptions directly--there's no guarantee that a
    random exception that was thrown can be unpickled in a different process.
    """
    tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    return pickle.dumps(
        (str(type(e)), str(e), tb),
        protocol=pickle_protocol,
    )


COMPLETED_PROCESS_STATES = {
    ProcessState.ProcessStateEnum.SUCCEEDED,
    ProcessState.ProcessStateEnum.RUN_REQUEST_FAILED,
    ProcessState.ProcessStateEnum.PYTHON_EXCEPTION,
    ProcessState.ProcessStateEnum.NON_ZERO_RETURN_CODE,
    ProcessState.ProcessStateEnum.RESOURCES_NOT_AVAILABLE,
    ProcessState.ProcessStateEnum.ERROR_GETTING_STATE,
}


_T = TypeVar("_T")


def assert_is_not_none(resources: Optional[_T]) -> _T:
    """A helper for mypy"""
    assert resources is not None
    return resources


F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


@overload
def log_call_async(
    *,
    action_type: Optional[str] = ...,
    include_args: Optional[Iterable[str]] = ...,
    include_result: bool = ...,
) -> Callable[[F], F]:
    ...


@overload
def log_call_async(wrapped_function: F) -> F:
    ...


def log_call_async(
    wrapped_function: Optional[F] = None,
    *,
    action_type: Optional[str] = None,
    include_args: Optional[Iterable[str]] = tuple(),
    include_result: bool = False,
) -> Union[F, Callable[[F], F]]:
    """Decorator/decorator factory that logs inputs and the return result.
    If used with inputs (i.e. as a decorator factory), it accepts the following
    parameters:
    @param action_type: The action type to use.  If not given the function name
        will be used.
    @param include_args: If given, should be a list of strings, the arguments to log.
    @param include_result: True by default. If False, the return result isn't logged.
    """
    if wrapped_function is None:
        r = functools.partial(
            log_call_async,
            action_type=action_type,
            include_args=include_args,
            include_result=include_result,
        )
        return cast(Callable[[F], F], r)

    if action_type is None:
        action_type = "{}.{}".format(
            wrapped_function.__module__, wrapped_function.__qualname__
        )

    if include_args is not None:
        from inspect import signature

        sig = signature(wrapped_function)
        if set(include_args) - set(sig.parameters):
            raise ValueError(
                (
                    "include_args ({}) lists arguments not in the " "wrapped function"
                ).format(include_args)
            )

    @functools.wraps(wrapped_function)
    async def logging_wrapper(*args: Any, **kwargs: Any) -> Any:
        assert wrapped_function is not None
        bound_args = inspect.signature(wrapped_function).bind(*args, **kwargs)

        # Remove self if it's included:
        if "self" in bound_args.arguments:
            bound_args.arguments.pop("self")

        # Filter arguments to log, if necessary:
        if include_args is not None:
            bound_args.arguments = OrderedDict(
                {
                    k: bound_args.arguments[k]
                    for k in include_args
                    if k in bound_args.arguments
                }
            )

        with contextlib.ExitStack() as stack:
            ctx = stack.enter_context(
                eliot.start_action(
                    action_type=action_type or "", **bound_args.arguments
                )
            )
            result = await wrapped_function(*args, **kwargs)
            if not include_result:
                return result

            ctx.add_success_fields(result=result)
            return result

    return cast(F, logging_wrapper)
