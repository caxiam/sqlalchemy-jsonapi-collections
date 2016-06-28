from abc import abstractmethod, ABCMeta


class BaseViewDriver(metaclass=ABCMeta):
    """Base view driver."""

    def __init__(self, view):
        """Setup the view driver.

        :param view: Schema object reference.
        """
        self.view = view

    @abstractmethod
    def initialize_path(self, path):
        """Initialize a specified attribute path."""
        return

    @abstractmethod
    def get_model_path(self):
        """Return a model-safe path."""
        return

    @abstractmethod
    def deserialize_values(self, values):
        """Deserialize a set of values into their appropriate types."""
        return

    @abstractmethod
    def deserialize_value(self, field, value):
        """Deserialize a string value to the appropriate type."""
        return
