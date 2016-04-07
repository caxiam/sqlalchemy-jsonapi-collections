# -*- coding: utf-8 -*-


class FieldError(Exception):
    pass


class JSONAPIError(Exception):

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
