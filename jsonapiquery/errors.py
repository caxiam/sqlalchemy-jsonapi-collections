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
    http_status = 400
    namespace = 120000

    def __init__(self, detail, item, code):
        self.detail = detail
        self.item = item
        self.code = code

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
            'status': self.http_status,
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


def make_error_response(errors: list) -> dict:
    """Return a JSONAPI compliant error response."""
    return {'errors': [dict(error) for error in errors]}
