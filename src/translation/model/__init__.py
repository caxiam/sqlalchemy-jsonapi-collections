

class BaseModelDriver(object):
    """Base model driver."""

    def __init__(self, model, default_attribute='id'):
        """Setup the driver.

        :param model: SQLAlchemy model reference.
        """
        self.model = model
        self.default_attribute = default_attribute

    def parse_path(self, path):
        """Parse a string path to a column attribute."""
        raise NotImplementedError
