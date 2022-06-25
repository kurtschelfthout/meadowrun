from ._bytesjson import dumps as dumps, loads as loads
from _typeshed import Incomplete
from json import JSONEncoder

class _DatetimeJSONEncoder(JSONEncoder):
    def default(self, o): ...

class EliotFilter:
    code: Incomplete
    incoming: Incomplete
    output: Incomplete
    def __init__(self, expr, incoming, output) -> None: ...
    def run(self) -> None: ...

USAGE: bytes

def main(sys=...): ...
