from ._action import (
    ACTION_STATUS_FIELD as ACTION_STATUS_FIELD,
    ACTION_TYPE_FIELD as ACTION_TYPE_FIELD,
    FAILED_STATUS as FAILED_STATUS,
)
from ._bytesjson import dumps as dumps
from ._message import (
    MESSAGE_TYPE_FIELD as MESSAGE_TYPE_FIELD,
    TASK_UUID_FIELD as TASK_UUID_FIELD,
)

def sd_journal_send(**kwargs) -> None: ...

class JournaldDestination:
    def __init__(self) -> None: ...
    def __call__(self, message) -> None: ...
