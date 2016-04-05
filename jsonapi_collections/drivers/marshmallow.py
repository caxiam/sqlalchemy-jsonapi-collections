# -*- coding: utf-8 -*-
from jsonapi_collections.drivers import BaseDriver


class MarshmallowDriver(BaseDriver):
    """Marshmallow bindings."""

    def get_column(self, column_name, model=None):
        """Return a column instance."""
        return getattr(model or self.collection.model, column_name)

    def get_column_name(self, field_name, schema=None):
        """Return a string reference to a model column."""
        field = self.get_field(field_name, schema)
        return field.attribute or field_name

    def get_field(self, field_name, schema=None):
        """Return a marshmallow field instance."""
        schema = schema or self.collection.schema
        return schema._declared_fields.get(field_name)

    def get_related_schema(self, field):
        """Return a related schema reference."""
        return getattr(field, 'schema')

    def deserialize(self, field, values):
        """Deserialize a given set of values into their python types."""
        return [field.deserialize(value) for value in values]
