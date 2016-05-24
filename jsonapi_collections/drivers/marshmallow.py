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

    def deserialize(self, column, field_name, values, schema=None):
        """Deserialize a given set of values into their python types."""
        field = self.get_field(field_name, schema)
        try:
            return [field.deserialize(value) for value in values]
        except Exception as exc:
            if exc.__class__.__name__ == 'ValidationError':
                raise FieldError(exc)
            raise

    def serialize(self, schema, items):
        return schema(many=True).dump(items).data.get('data', [])

    def validate_attribute_path(self, path):
        """Return `False` if the provided path cannot be found."""
        fields = path.split('.')
        length = len(fields)

        model = None
        schema = None
        for pos, field in enumerate(fields, 1):
            try:
                column_name = self.get_column_name(field, schema)
                column = self.get_column(column_name, model)
            except FieldError:
                return False

            if pos != length:
                if not self.is_relationship(column):
                    return False
                model = column.property.mapper.class_
            if pos == length and self.is_relationship(column):
                return False
        return True

    def validate_relationship_path(self, path):
        """Return `False` if the path cannot be found."""
        model = None
        schema = None
        for field in path.split('.'):
            try:
                column_name = self.get_column_name(field, schema)
                column = self.get_column(column_name, model)
            except FieldError:
                return False

            if not self.is_relationship(column):
                return False
            model = self.get_column_model(column)
        return True
