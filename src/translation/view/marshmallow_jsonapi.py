"""marshmallow-jsonapi schema translation module."""
from src.translation.view import BaseViewDriver


class MarshmallowJSONAPIDriver(BaseViewDriver):
    """Schema translation handler."""

    def replace_path(self, path):
        """Replace the provided view path with a model path."""
        stones = path.split('.')
        relationships, attribute = stones[:-1], stones[-1]

        path = ''
        schema = self.view
        for relationship in relationships:
            field = self._get_field(relationship, schema)
            if not self._is_relationship(field):
                raise TypeError('Invalid relationship field specified.')
            name = field.attribute or relationship
            if path:
                path = '{}.{}'.format(path, name)
            else:
                path = name
            schema = field.schema
        field = self._get_field(attribute, schema)
        if path:
            path = '{}.{}'.format(path, field.attribute or attribute)
        else:
            path = field.attribute or attribute
        return path

    def deserialize_from_path(self, path, values):
        """Deserialize a set of values from the given path."""
        field = self._get_field_from_path(path)
        return self.deserialize_values(field, values)

    def deserialize_values(self, field, values):
        """Deserialize a set of values into their appropriate types."""
        new = []
        for value in values:
            new.append(self.deserialize_value(field, value))
        return new

    def deserialize_value(self, field, value):
        """Deserialize a string value to the appropriate type."""
        return field.deserialize(value)

    def _get_field_from_path(self, path):
        field = None
        schema = self.view
        for field_name in path.split('.'):
            field = self._get_field(field_name, schema)
            if self._is_relationship(field):
                schema = field.schema
        return field

    def _get_field(self, attribute, schema):
        return schema._declared_fields[attribute]

    def _is_relationship(self, field):
        return hasattr(field, 'related_schema')
