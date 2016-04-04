# -*- coding: utf-8 -*-
from jsonapi_collections.drivers import BaseDriver


class MarshmallowDriver(BaseDriver):
    """Marshmallow bindings."""

    def get_column(self, field, model=None):
        """Return a column instance."""
        column_name = getattr(field, 'attribute', None)
        if column_name is not None:
            field = column_name
        return getattr(model or self.collection.model, field)

    def get_column_name(self, field_name, schema=None):
        """Return a string reference to a model column."""
        field = self.get_field(field_name, schema)
        return field.attribute or field_name

    def get_field(self, field_name, schema=None):
        """Return a marshmallow field instance."""
        return getattr(schema or self.collection.schema, field_name, None)

    def get_related_schema(self, field):
        """Return a related schema reference."""
        return getattr(field, 'schema')

    def deserialize(self, field, values):
        """Deserialize a given set of values into their python types."""
        if isinstance(field, str):
            field = self.get_field(field)
        return [field.deserialize(value) for value in values]
