import json


ERRORS = {
    'KEY_PARSE_ERROR': {'code': 1, 'message': 'Could not parse key.'}
}


class ErrorHandler:
    """Error collection management object."""

    def __init__(self, strict=False):
        """Initialize ErrorHandler object.

        :param strict (bool): If strict raise errors without collection.
        """
        self.errors = []
        self.strict = strict

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not self.strict and isinstance(value, JSONAPIQueryError):
            self.errors.append(value)
            return True

    def __iter__(self):
        return iter(self.errors)

    def __len__(self):
        return len(self.errors)

    def __str__(self):
        return json.dumps(dict(self))

    @property
    def __dict__(self):
        return make_error_response(self.errors)


class JSONAPIQueryError(Exception):
    http_status_code = 400
    error_map = ERRORS
    namespace = 120000

    def __init__(self, key, source, meta={}):
        self.key = key
        self.source = source
        self.meta = meta

    def __repr__(self):
        msg = '{}(code={}, message={})'
        return msg.format(self.__class__.__name__, self.code, self.message)

    @property
    def __dict__(self):
        result = {
            'code': self.code + self.namespace,
            'detail': self.message,
            'source': {'parameter': self.source},
            'status': self.http_status_code,
        }
        if self.meta:
            result['meta'] = self.meta
        return result

    @property
    def code(self):
        return self.error_map[key]['code']

    @property
    def message(self):
        return self.error_map[key]['message']


def make_error_response(errors: list) -> dict:
    """Return a JSONAPI compliant error response."""
    return {'errors': [dict(error) for error in errors]}
