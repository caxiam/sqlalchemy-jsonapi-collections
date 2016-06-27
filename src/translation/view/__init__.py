

class BaseViewDriver(object):
    """Base view driver."""

    def __init__(self, view):
        """Setup the view driver.

        :param view: Schema object reference.
        """
        self.view = view

    def replace_path(self, path):
        """Replace the provided view path with a model path."""
        raise NotImplementedError

    def deserialize_values(self, values):
        """Deserialize a set of values into their appropriate types."""
        raise NotImplementedError

    def deserialize_value(self, field, value):
        """Deserialize a string value to the appropriate type."""
        raise NotImplementedError
