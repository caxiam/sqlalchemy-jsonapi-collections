

class JSONAPIQueryError(Exception):
    """All errors raised from this module will subclass this class."""


class PathError(JSONAPIQueryError):
    """Raised when a Python path can not be derived."""


class DataError(JSONAPIQueryError):
    """Raised when a value can not be deserialized to a Python type."""
