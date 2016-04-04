# -*- coding: utf-8 -*-
from jsonapi_collections.drivers import BaseDriver


class MarshmallowDriver(BaseDriver):
    """Marshmallow bindings."""

    def get_column(self, field):
        """Return a column instance."""
        column_name = getattr(self.get_field(field), 'attribute', None)
        if column_name is not None:
            field = column_name
        return getattr(self.collection.model, field)

    def get_field(self, field_name):
        """Return a marshmallow field instance."""
        return getattr(self.collection.schema, field_name, None)

    def deserialize(self, field, values):
        """Deserialize a given set of values into their python types."""
        if isinstance(field, str):
            field = self.get_field(field)
        return [field.deserialize(value) for value in values]
