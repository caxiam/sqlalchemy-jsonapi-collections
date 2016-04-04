# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import and_, or_
from flask_sqlalchemy_jsonapi.errors import FieldError

import re


class FilterParameter(object):
    """Validate and filter a provided `marshmallow` schema field name."""

    column = None
    relationship = None

    def __init__(self, field, schema, values):
        """Validate the provided column and filters.

        :param field: String path to a schema attribute.
        :param values: String list of `OR` values.
        :param schema: `marshmallow` schema object.
        """
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

        self.values, errors = self._prepare_values(values.lower().split(','))
        if errors:
            raise FieldError(errors)

        if len(values) > 1:
            self.many = True
        else:
            self.many = False

    @property
    def column_type(self):
        """Extract a column's type."""
        return self.column.property.columns[0].type.python_type

    @property
    def enum_choices(self):
        """Return a set of choices."""
        if self.is_enum:
            return self.column.property.columns[0].type.enums
        return None

    @property
    def is_enum(self):
        """Determine if a column is an enumeration."""
        if hasattr(self.column.property.columns[0].type, 'enums'):
            return True
        return False

    @property
    def filter(self):
        """Generate a `SQLAlchemy` filter."""
        filters = self._prepare_strategies(self.values)

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

    def _prepare_values(self, values):
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

    def _prepare_strategies(self, values):
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
        """Parse a dictionary into `FilterParameter` instances.

        The `parameters` dictionary's keys must be attributes of the
        provided schema.  The attribute name must start with `filter[`
        and end with `]` to be evaluated.

        The `parameters` dictionary's values must be comma-seperated
        string lists.  E.g. `1,2` or `1`

        :param schema: `marshmallow` schema object.
        :param parameters: A dictionary of column names and filters.
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
        """Apply a series of `FilterParameter` instances as query filters.

        :param query: `SQLAlchemy` query object.
        :param values: List of `FilterParameter` instances.
        """
        for value in values:
            query = query.filter(value.filter)
        return query
