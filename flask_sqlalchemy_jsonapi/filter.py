# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import and_, or_
from flask_sqlalchemy_jsonapi.errors import FieldError

import re


class FilterParameter(object):

    """The FilterParameter object is responsible for generating a
    filter for exactly one query parameter, value pair.

    :param field: A string reference to a marshmallow schema field.
    :param values: A string-list of values delineated by a comma.
    :param schema: A marshmallow schema object.
    """
    column = None
    relationship = None

    def __init__(self, field, schema, values):
        self.schema = schema

        if "." in field:
            table, column = field.split('.', 1)

            self.field = self._get_field(table, schema)
            column_name = self.field.attribute or table
            self.relationship = getattr(schema.Meta.model, table)

            attribute = self._get_field(column, self.field.schema)
            column_name = attribute.attribute or column
            self.column = getattr(self.field.schema.Meta.model, column_name)
        else:
            self.field = self._get_field(field, schema)

            column_name = self.field.attribute or field
            self.column = getattr(schema.Meta.model, column_name)

        self.values, errors = self.prepare_values(values.lower().split(','))
        if errors:
            raise FieldError(errors)

        if len(values) > 1:
            self.many = True
        else:
            self.many = False

    @property
    def column_type(self):
        return self.column.property.columns[0].type.python_type

    @property
    def enum_choices(self):
        if self.is_enum:
            return self.column.property.columns[0].type.enums
        return None

    @property
    def is_enum(self):
        if hasattr(self.column.property.columns[0].type, 'enums'):
            return True
        return False

    @property
    def filter(self):
        filters = self.prepare_strategies(self.values)

        if self.relationship is None:
            if self.many:
                return or_(*filters)
            return filters[0]

        if self.relationship.property.uselist:
            wrapper = self.relationship.any
        else:
            wrapper = self.relationship.has

        if self.many:
            return wrapper(or_(*filters))
        return wrapper(*filters)

    def _get_field(self, field, schema):
        if field not in schema._declared_fields:
            raise FieldError('Invalid field specified: {}.'.format(field))
        return schema._declared_fields[field]

    def prepare_values(self, values):
        """For a given set of values, cast each value according to the
        column being filtered's type.

        :param values: A list of string values to cast.
        """
        errors = []
        for index, value in enumerate(values):
            try:
                values[index] = self._prepare_value(value)
            except (ValueError, InvalidOperation):
                errors.append('Invalid value specified: {}.'.format(value))
        return values, errors

    def _prepare_value(self, value):
        if value == '':
            return None

        if self.is_enum and value not in self.enum_choices:
            raise ValueError

        if self.column_type == bool:
            return bool(value)
        elif self.column_type == int:
            return int(value)
        elif self.column_type == datetime:
            return datetime.strptime(value, '%Y-%m-%d')
        elif self.column_type == Decimal:
            return Decimal(value)
        return str(value)

    def prepare_strategies(self, values):
        """Takes a list of values and applies a query filter based on
        the column being filtered's type.

        :param values: A list of type appropriate values to sort by.
        """
        filters = []
        for value in values:
            filters.append(self._prepare_strategy(value))
        return filters

    def _prepare_strategy(self, value):
        if self.is_enum or value is None:
            return self.column == value

        if self.column_type == str:
            return self.column.ilike('%{}%'.format(value))
        elif self.column_type == bool:
            return self.column.is_(value)
        elif self.column_type == datetime:
            tomorrow = value + timedelta(days=1)
            return and_(self.column >= value, self.column < tomorrow)
        elif self.column_type == Decimal:
            base = int(value)
            if value.as_tuple().exponent == 0:
                return and_(self.column >= base, self.column < base + 1)
        return self.column == value

    @classmethod
    def generate(cls, schema, parameters):
        """A FilterParameter generator method. This method takes a
        dictionary of parameter, value pairs, finds all the fields
        wrapped in `filter[]`, and filters the field by the given
        values.

        :param schema: A marshmallow schema object.
        :param parameters: A dictionary of parameter, value pairs.
        """
        errors = []
        filters = []
        for key, value in parameters.iteritems():
            field = re.compile(r'filter\[(.*)\]', re.DOTALL).search(key)
            if field is None:
                continue
            try:
                filters.append(cls(field.group(1), schema, value))
            except FieldError as err:
                errors.append(err.message)
        return filters, errors

    @staticmethod
    def filter_by(query, values):
        """A filtering helper function that applies a set of objects
        filter parameters to a given query object.

        :param query: A SQLAlchemy query object.
        :param values: A list of FilterParameter instances.
        """
        for value in values:
            query = query.filter(value.filter)
        return query
