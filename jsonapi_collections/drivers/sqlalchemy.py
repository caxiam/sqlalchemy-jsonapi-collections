# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal

from jsonapi_collections.drivers import BaseDriver


class SQLAlchemyDriver(BaseDriver):
    """SQLAlchemy bindings."""

    def get_column(self, column_name, model=None):
        """Return a column instance."""
        return self.get_field(column_name, model)

    def get_column_name(self, field_name, schema=None):
        """Return a string reference to a model column."""
        return field_name

    def get_field(self, field_name, schema=None):
        """Return a SQLAlchemy column instance.

        :param field_name: A string reference to a field's name.
        """
        return getattr(schema or self.collection.model, field_name, None)

    def get_related_schema(self, field):
        """Return a related schema reference."""
        return self.get_column_model(field)

    def deserialize(self, field, values):
        """Deserialize a set of values."""
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
