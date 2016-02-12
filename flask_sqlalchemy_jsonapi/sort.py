# -*- coding: utf-8 -*-
from sqlalchemy import desc
from flask_sqlalchemy_jsonapi.errors import FieldError


class SortValue(object):

    """The SortValue object is responsible for formatting a field value
    as a valid, sorted query expression.

    :param schema: A marshmallow schema object.
    :param value: A string value that represents a path to a field.
        Values can be specified with a `.` which will represent
        a logical break between the relationship field and its related
        schema's attribute.
    """
    attribute = None
    descending = False
    join = None

    def __init__(self, schema, value):
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
        column = getattr(self.schema.Meta.model, self.attribute)
        if self.descending:
            return desc(column)
        return column

    def _get_field(self, field, schema):
        """Ensure the field exists within the declared fields
        dictionary or err.

        :param field: A string that represents a declared field.
        :param schema: A marshmallow schema object.
        """
        if field not in schema._declared_fields:
            raise FieldError(
                'Invalid field specified: {}.'.format(self.value))
        return schema._declared_fields[field]

    @classmethod
    def generate(cls, schema, values):
        """A SortValue generator method. This method takes a given set
        of strings and converts them into SortValue objects. If the
        string can not be converted, an error is marshaled as a member
        of a string list.

        :param schema: A marshmallow schema object.
        :param values: A list of strings that represent field names on
                       the provided schema.
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
        """A sorting helper function that joins the appropriate tables and
        implements column sorting through the preferred approach.

        :param query: A SQLAlchemy query object.
        :param values: A list of SortValue instances.
        """
        sorts = []
        for value in values:
            if value.join is not None:
                query = query.join(value.join)
            sorts.append(value.column)
        return query.order_by(*sorts)
