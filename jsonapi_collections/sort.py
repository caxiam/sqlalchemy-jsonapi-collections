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
        descending = value.startswith('-')
        if descending:
            value = value[1:]

        if "." in value:
            relationship_name, attribute_name = value.split('.')

            relationship = driver.get_field(relationship_name)
            related_schema = driver.get_related_schema(relationship)

            field = getattr(attribute_name, related_schema)
            self.join = relationship_name
        else:
            field = driver.get_field(value)
            self.join = None

        column = driver.get_column(field)
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
        errors = []
        fields = []
        for field_name in field_names:
            try:
                fields.append(cls(schema, field_name))
            except FieldError as error:
                errors.append(error.message)
        return fields, errors

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
