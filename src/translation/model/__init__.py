

class BaseModelDriver(object):
    """Base model driver."""

    def __init__(self, model):
        """Setup the driver.

        :param model: SQLAlchemy model reference.
        """
        self.model = model

    def parse_filters(self, filters):
        """Parse a set of filter triples."""
        raise NotImplementedError

    def parse_filter(self, path, strategy, values):
        """Parse a filter triple's path to a column reference."""
        raise NotImplementedError

    def parse_sorts(self, sorts):
        """Parse a set of sort doubles."""
        raise NotImplementedError

    def parse_sort(self, path, direction):
        """Parse a sort double's path to a column reference."""
        raise NotImplementedError
