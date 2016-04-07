# -*- coding: utf-8 -*-


class FieldError(Exception):
    """Raised when one or more query parameters could not be found.

    The `FieldError` exception is exclusively used within driver
    classes. Failing to find the specified attribute, relationship
    attribute, or relationship schema constitues raising a
    `FieldError`.
    """

    pass


class JSONAPIError(Exception):
    """Raised when one or more field errors have been found.

    The `JSONAPIError` exception aggregates a collection of JSONAPI
    formatted error messages.  If the specified error message is a
    string, instead of a list, the message is encapsulated within an
    object with a key of `detail`.
    """

    def __init__(self, message, code=400):
        """Format the error's message to match the JSONAPI 1.0 spec.

        :param message: A list errors or a string message.
        :param code: HTTP status code.
        """
        data = {'status': code}
        if isinstance(message, str):
            data.update({'errors': {'detail': message}})
        else:
            data.update({'errors': message})
        self.message = data
        super(JSONAPIError, self).__init__(data)
