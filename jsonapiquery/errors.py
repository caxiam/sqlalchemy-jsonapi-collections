import functools
import json


class CollectErrors:

    def __init__(self, exc_type):
        self.errors = []
        self.exc_type = exc_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == self.exc_type:
            self.errors.append(exc_value)
            return True


class JSONAPIQueryError(Exception):
    namespace = 120000

    def __init__(self, detail, item, code, meta=None):
        self.detail = detail
        self.item = item
        self.code = code
        self.meta = meta or {}

    def __iter__(self):
        yield from self.message.items()

    def __repr__(self):
        return json.dumps(self.message)

    @property
    def message(self):
        return {
            'code': self.namespace + self.code,
            'detail': self.detail,
            'source': {'parameter': self.source},
        }

    @property
    def source(self):
        source = self.item.source
        while True:
            if isinstance(source, str):
                break
            source = source.source
        return source


InvalidPath = functools.partial(JSONAPIQueryError, code=1)
InvalidFieldType = functools.partial(JSONAPIQueryError, code=2)
InvalidValue = functools.partial(JSONAPIQueryError, code=3)
InvalidQuery = functools.partial(
    JSONAPIQueryError, detail='Invalid query specified.', code=4)
InvalidPaginationValue = InvalidQuery = functools.partial(
    JSONAPIQueryError, detail='Pagination values must be integers.', code=5)


def make_error_response(errors: list) -> dict:
    """Return a JSONAPI compliant error response."""
    return {'errors': [dict(error) for error in errors]}
