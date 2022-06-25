from ._action import (
    ACTION_STATUS_FIELD as ACTION_STATUS_FIELD,
    ACTION_TYPE_FIELD as ACTION_TYPE_FIELD,
    FAILED_STATUS as FAILED_STATUS,
    STARTED_STATUS as STARTED_STATUS,
    SUCCEEDED_STATUS as SUCCEEDED_STATUS,
    log_message as log_message,
    startTask as startTask,
    start_action as start_action,
)
from ._message import (
    MESSAGE_TYPE_FIELD as MESSAGE_TYPE_FIELD,
    Message as Message,
    REASON_FIELD as REASON_FIELD,
    TASK_LEVEL_FIELD as TASK_LEVEL_FIELD,
    TASK_UUID_FIELD as TASK_UUID_FIELD,
    TIMESTAMP_FIELD as TIMESTAMP_FIELD,
)
from _typeshed import Incomplete
from pyrsistent import PClass

unicode: Incomplete

class ValidationError(Exception): ...

RESERVED_FIELDS: Incomplete

class Field:
    key: Incomplete
    description: Incomplete
    def __init__(
        self,
        key,
        serializer,
        description: str = ...,
        extraValidator: Incomplete | None = ...,
    ) -> None: ...
    def validate(self, input) -> None: ...
    def serialize(self, input): ...
    @classmethod
    def forValue(klass, key, value, description): ...
    for_value: Incomplete
    @classmethod
    def forTypes(
        klass, key, classes, description, extraValidator: Incomplete | None = ...
    ): ...
    for_types: Incomplete

def fields(*fields, **keys): ...

REASON: Incomplete
TRACEBACK: Incomplete
EXCEPTION: Incomplete

class _MessageSerializer:
    fields: Incomplete
    allow_additional_fields: Incomplete
    def __init__(self, fields, allow_additional_fields: bool = ...) -> None: ...
    def serialize(self, message) -> None: ...
    def validate(self, message) -> None: ...

class MessageType:
    message_type: Incomplete
    description: Incomplete
    def __init__(self, message_type, fields, description: str = ...) -> None: ...
    def __call__(self, **fields): ...
    def log(self, **fields) -> None: ...

class _ActionSerializers(PClass):
    start: Incomplete
    success: Incomplete
    failure: Incomplete

class ActionType:
    action_type: Incomplete
    description: Incomplete
    def __init__(
        self, action_type, startFields, successFields, description: str = ...
    ): ...
    def __call__(self, logger: Incomplete | None = ..., **fields): ...
    def as_task(self, logger: Incomplete | None = ..., **fields): ...
    asTask: Incomplete
