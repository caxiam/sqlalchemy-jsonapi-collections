from abc import abstractmethod, ABCMeta


class BaseModelDriver(metaclass=ABCMeta):
    """Base model driver."""

    def __init__(self, model, default_attribute='id'):
        """Setup the driver.

        :param model: SQLAlchemy model reference.
        """
        self.model = model
        self.default_attribute = default_attribute

    @abstractmethod
    def parse_path(self, path):
        """Parse a string path to a column attribute."""
        return
