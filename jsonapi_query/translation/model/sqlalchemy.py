"""SQLAlchemy model translation module."""
from jsonapi_query.errors import PathError
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
        if path == '':
            return (None, [])

        stones = path.split('.')
        relationships, attribute = stones[:-1], stones[-1]

        model = self.model
        joins = []
        models = []
        for relationship in relationships:
            reference = self._get_relationship(relationship, model)
            joins.append(self._extract_join(reference, model))
            model = self._get_relationship_class(reference)
            models.append(model)

        column = self._get_column(attribute, model)
        if self._is_relationship(column):
            joins.append(self._extract_join(column, model))
            model = self._get_relationship_class(column)
            models.append(model)
            column = self._get_column(self.default_attribute, model)
        return (column, models, joins)

    def _get_column(self, attribute, model):
        try:
            return getattr(model, attribute)
        except AttributeError:
            raise PathError('Invalid path specified.')

    def _get_relationship(self, attribute, model):
        column = self._get_column(attribute, model)
        if not self._is_relationship(column):
            raise PathError('Invalid field type specified.')
        return column

    def _get_relationship_class(self, relationship):
        """Return the class reference of the given relationship."""
        return relationship.property.mapper.class_

    def _is_relationship(self, relationship):
        """Return `True` if a relationship mapper was specified."""
        try:
            self._get_relationship_class(relationship)
        except AttributeError:
            return False
        return True

    def _extract_join(self, mapper, model):
        """Extract the join condition for a given relationship mapper."""
        # If the mapper is not self-referential we can return it.
        if model != self._get_relationship_class(mapper):
            return mapper

        # If the mapper is self-referential we want to join its backref.
        if mapper.property.backref is not None:
            return mapper.property.backref
        else:
            return mapper.property.back_populates
