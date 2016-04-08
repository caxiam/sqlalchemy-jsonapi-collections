# -*- coding: utf-8 -*-
from jsonapi_collections.drivers import BaseDriver
from jsonapi_collections.errors import FieldError


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
        field = schema._declared_fields.get(field_name)
        if field is None:
            raise FieldError('Invalid field specified.')
        return field

    def get_related_schema(self, field):
        """Return a related schema reference."""
        schema = getattr(field, 'schema', None)
        if schema is None:
            raise FieldError('Invalid relationship specified.')
        return schema

    def deserialize(self, field, values):
        """Deserialize a given set of values into their python types."""
        try:
            return [field.deserialize(value) for value in values]
        except Exception as exc:
            if exc.__class__.__name__ == 'ValidationError':
                raise FieldError(exc)
            raise

    def serialize(self, schema, items):
        return schema(many=True).dump(items).data.get('data', [])
