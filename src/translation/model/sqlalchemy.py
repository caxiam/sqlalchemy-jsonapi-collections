"""SQLAlchemy translation module."""
from src.translation.model import BaseModelDriver


class SQLAlchemyModelDriver(BaseModelDriver):
    """Translate string paths to column references."""

    default_attribute = 'id'

    def parse_filters(self, filters):
        """Parse a set of filter triples."""
        parsed_filters = []
        for path, strategy, values in filters:
            parsed_filters.append(self.parse_filter(path, strategy, values))
        return parsed_filters

    def parse_filter(self, path, strategy, values):
        """Parse a filter triple's path to a column reference."""
        reference = self.model
        for stone in path.split('.'):
            reference = getattr(reference, stone)
        return reference

    def parse_sorts(self, sorts):
        """Parse a set of sort doubles."""
        parsed_sorts = []
        for path, direction in sorts:
            parsed_sorts.append(self.parse_sort(path, direction))
        return parsed_sorts

    def parse_sort(self, path, direction):
        """Parse a sort double's path to a column reference."""
        stones = path.split('.')
        relationships, attribute = stones[:-1], stones[-1]

        joins = []
        model = self.model
        for relationship in relationships:
            reference = getattr(model, relationship)
            if not self._is_relationship(reference):
                raise TypeError('Invalid relationship specified.')
            model = self._get_relationship_class(reference)
            joins.append(model.__tablename__)
        column = getattr(model, attribute)
        if self._is_relationship(column):
            model = self._get_relationship_class(column)
            column = getattr(model, self.default_attribute)
            joins.append(model.__tablename__)
        return (column, direction, joins)

    def _is_relationship(self, relationship):
        """Return `True` if a relationship mapper was specified."""
        try:
            self._get_relationship_class(relationship)
        except AttributeError:
            return False
        return True

    def _get_relationship_class(self, relationship):
        """Return the class reference of the given relationship."""
        return relationship.property.mapper.class_
