# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal, InvalidOperation

from jsonapi_collections.drivers import BaseDriver


class SQLAlchemyDriver(BaseDriver):
    """SQLAlchemy bindings."""

    def get_column(self, field):
        """Return the provided field.

        We return the field because it is already a SQLAlchemy column
        instance.

        :param field: A `SQLAlchemy` column instance.
        """
        return field

    def get_field(self, field_name):
        """Return a SQLAlchemy column instance.
        
        :param field: A string reference to a column's name.
        """
        return getattr(self.collection.model, field, None)
        
    def get_related_schema(self, field):
        """Retrieve a related model from the provided field."""
        raise Exception(dir(field))

    def deserialize(self, field, values):
        """Deserialize a set of values."""
        if isinstance(field, str):
            field = self.get_column(field)
        return [self._deserialize(field, value) for value in values]

    def _deserialize(self, column, value):
        """Deserialize a value into its Python type."""
        if self.is_enum(column) and value not in self._enum_choices(column):
            raise ValueError

        if value == '':
            return None

        column_type = self.get_column_type(column)
        if column_type == datetime:
            return datetime.strptime(value, '%Y-%m-%d')
        elif column_type in [bool, int, Decimal]:
            return column_type(value)
        return value

    def _enum_choices(self, column):
        """Return a set of choices."""
        return self.column.property.columns[0].type.enums
