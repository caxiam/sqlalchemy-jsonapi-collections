# -*- coding: utf-8 -*-
from sqlalchemy import desc
from jsonapi_collections.errors import FieldError


class SortValue(object):
    """Validate and sort a provided `marshmallow` schema field name."""

    attribute = None
    descending = False
    join = None

    def __init__(self, schema, value):
        """Set the `SQLAlchemy` column name from the provided attribute.

        Dot seperated strings are understood to be the attributes of a
        related schema.  If the preceding name does not match a valid
        relationship field an error will be thrown.  If the proceeding
        name does not match an attribute on the related schema an error
        will be thrown.

        :param schema: `marshmallow` schema object.
        :param value: String path to sorted schema attribute.
        """
        self.schema = schema
        self.value = value

        self.descending = value.startswith('-')
        if self.descending:
            value = value[1:]

        if "." in value:
            table, column = value.split('.', 1)

            relationship = self._get_field(table, schema)
            field = self._get_field(column, relationship.schema)

            self.attribute = field.attribute or column
            self.join = table
        else:
            field = self._get_field(value, schema)
            self.attribute = field.attribute or value

    @property
    def column(self):
        """A sorted `SQLAlchemy` column reference."""
        column = getattr(self.schema.Meta.model, self.attribute)
        if self.descending:
            return desc(column)
        return column

    def _get_field(self, field, schema):
        """Get the schema field associated with the specified name.

        :param field: String name of a declared attribute.
        :param schema: `marshmallow` schema object.
        """
        if field not in schema._declared_fields:
            raise FieldError(
                'Invalid field specified: {}.'.format(self.value))
        return schema._declared_fields[field]

    @classmethod
    def generate(cls, schema, values):
        """Parse a series of strings into `SortValue` instances.

        Dot notation can be used to sort by the attributes of a related
        schema.  E.g. `relationship.attribute`.

        If the string can not be converted, an error is marshaled as a
        member of a string list.

        :param schema: `marshmallow` schema reference.
        :param values: String list of attributes.
        """
        errors = []
        fields = []
        for value in values:
            try:
                fields.append(cls(schema, value))
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
            sorts.append(value.column)
        return query.order_by(*sorts)
