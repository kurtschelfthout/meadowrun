from _typeshed import Incomplete

class ErrorExtraction:
    registry: Incomplete
    def __init__(self) -> None: ...
    def register_exception_extractor(self, exception_class, extractor) -> None: ...
    def get_fields_for_exception(self, logger, exception): ...

register_exception_extractor: Incomplete
get_fields_for_exception: Incomplete
