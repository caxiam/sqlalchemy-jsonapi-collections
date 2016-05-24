# -*- coding: utf-8 -*-
from sqlalchemy import desc

from jsonapi_collections.errors import FieldError


class SortValue(object):
    """Formulate a query sort."""

    def __init__(self, driver, field_name):
        """Set a join and a sort reference.

        :param driver: `jsonapi_collections` driver instance.
        :param field_name: A string representation of a schema field.
        """
        descending = field_name.startswith('-')
        if descending:
            field_name = field_name[1:]

        if "." in field_name:
            relationship_name, attribute_name = field_name.split('.')

            relationship_field = driver.get_field(relationship_name)
            relationship_column = driver.get_column(driver.get_column_name(
                relationship_name))
            relationship_schema = driver.get_related_schema(relationship_field)
            relationship_model = driver.get_column_model(relationship_column)

            column_name = driver.get_column_name(
                attribute_name, relationship_schema)
            column = driver.get_column(column_name, relationship_model)
            self.join = relationship_name
        else:
            column_name = driver.get_column_name(field_name)
            column = driver.get_column(column_name)
            self.join = None

        if descending:
            self.sort = desc(column)
        else:
            self.sort = column

    @classmethod
    def generate(cls, driver, field_names):
        """Parse a series of strings into `SortValue` instances.

        Dot notation can be used to sort by the attributes of a related
        schema.  E.g. `relationship.attribute`.

        If the string can not be converted, an error is marshaled as a
        member of a string list.

        :param driver: `jsonapi_collections` driver reference.
        :param field_names: String list of attributes.
        """
        sorts = []
        errors = []
        for field_name in field_names:
            try:
                sorts.append(cls(driver, field_name))
            except FieldError as exc:
                errors.append(exc.message)
        if errors:
            return sorts, {"source": {"parameter": 'sort'}, "detail": errors}
        return sorts, None

    @staticmethod
    def sort_by(query, values):
        """Apply a series of `SortValue` instances to a `SQLAlchemy` query.

        Dot seperated sorts will have the appropriate tables joined
        prior to applying the sort.

        :param query: `SQLAlchemy` query object.
        :param values: List of `SortValue` instances.
        """
        sorts = []
        for value in values:
            if value.join is not None:
                query = query.join(value.join)
            sorts.append(value.sort)
        return query.order_by(*sorts)
