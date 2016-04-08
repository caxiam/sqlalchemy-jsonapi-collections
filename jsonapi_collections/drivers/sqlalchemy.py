# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal, InvalidOperation

from jsonapi_collections.drivers import BaseDriver
from jsonapi_collections.errors import FieldError

import json



class UnsafeEncoder(json.JSONEncoder):
    """Do not use an encoder like this in production.  You need to have
    your own specialized security concious encoder.
    """

    def default(self, obj):
        fields = {}
        columns = [
            x for x in dir(obj) if not x.startswith('_') and
            x != 'metadata']
        for column in columns:
            data = obj.__getattribute__(column)
            try:
                json.dumps(data)
                fields[column] = data
            except TypeError:
                fields[column] = None
        return fields


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
        field = getattr(schema or self.collection.model, field_name, None)
        if field is None:
            raise FieldError('Invalid field specified.')
        return field

    def get_related_schema(self, field):
        """Return a related schema reference."""
        return self.get_column_model(field)

    def deserialize(self, field_name, values, schema=None):
        """Deserialize a set of values."""
        field = self.get_field(field_name, schema)
        return [self._deserialize(field, value) for value in values]

    def _deserialize(self, column, value):
        """Deserialize a value into its Python type."""
        if self.is_enum(column) and value not in self._enum_choices(column):
            raise FieldError('Not a valid choice.')

        if value == '':
            return None

        column_type = self.get_column_type(column)
        try:
            if column_type == datetime:
                return datetime.strptime(value, '%Y-%m-%d')
            elif column_type in [bool, int, Decimal]:
                return column_type(value)
        except (ValueError, InvalidOperation) as exc:
            raise FieldError(exc.message)
        return value

    def _enum_choices(self, column):
        """Return a set of choices."""
        return column.property.columns[0].type.enums

    def serialize(self, schema, items):
        """Dangerously serialize `SQLAlchemy` model instance."""
        return [json.dumps(item, cls=UnsafeEncoder) for item in items]
