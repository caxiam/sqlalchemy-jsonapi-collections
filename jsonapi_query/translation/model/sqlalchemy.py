"""SQLAlchemy model translation module."""
from jsonapi_query.translation.model import BaseModelDriver


class SQLAlchemyModelDriver(BaseModelDriver):
    """Translate string paths to column references."""

    def parse_path(self, path):
        """Parse a string path to a column attribute.

        Return a triple of a column attribute, the intermediary models,
        and the list of joins required to get the attribute.

        :param path: A dot seperated string representing the attributes
                     of a model class.
        """
        stones = path.split('.')
        relationships, attribute = stones[:-1], stones[-1]

        model = self.model
        models = []
        for relationship in relationships:
            reference = getattr(model, relationship)
            if not self._is_relationship(reference):
                raise TypeError('Invalid relationship specified.')
            model = self._get_relationship_class(reference)
            models.append(model)

        column = getattr(model, attribute)
        if self._is_relationship(column):
            model = self._get_relationship_class(column)
            models.append(model)
            column = getattr(model, self.default_attribute)
        return (column, models)

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
