"""marshmallow-jsonapi schema translation module."""
from jsonapi_query.errors import DataError, PathError
from jsonapi_query.translation.view import BaseViewDriver


def remove_inflection(text):
    """Replace hyphens with underscores."""
    return text.replace('-', '_')


class MarshmallowJSONAPIDriver(BaseViewDriver):
    """Schema translation handler."""

    fields = []
    field_names = []
    schemas = []

    def initialize_path(self, path):
        """Initialize a specified attribute path."""
        self.fields = []
        self.field_names = []
        self.schemas = []

        path = remove_inflection(path)
        if path == '':
            return self

        stones = path.split('.')
        relationships, attribute = stones[:-1], stones[-1]

        schema = self.view
        for field_name in relationships:
            field = self._get_relationship(field_name, schema)
            self._append_field_meta(field, field_name)
            schema = field.schema
            self.schemas.append(schema)

        field = self._get_field(attribute, schema)
        if self._is_relationship(field):
            self.schemas.append(field.schema)
        self._append_field_meta(field, attribute)
        return self

    def _append_field_meta(self, field, field_name):
        self.fields.append(field)
        self.field_names.append(field.attribute or field_name)

    def get_model_path(self):
        """Return a model-safe path."""
        return '.'.join(self.field_names)

    def deserialize_values(self, values):
        """Deserialize a set of values into their appropriate types."""
        new = []
        for value in values:
            new.append(self.deserialize_value(self.fields[-1], value))
        return new

    def deserialize_value(self, field, value):
        """Deserialize a string value to the appropriate type."""
        try:
            if value == '':
                return None
            return field._deserialize(value, None, None)
        except:
            raise DataError('Invalid value specified.')

    def _get_field(self, attribute, schema):
        try:
            return schema._declared_fields[attribute]
        except KeyError:
            raise PathError('Invalid path specified.')

    def _get_relationship(self, attribute, schema):
        field = self._get_field(attribute, schema)
        if not self._is_relationship(field):
            raise PathError('Invalid field type specified.')
        return field

    def _is_relationship(self, field):
        return hasattr(field, 'schema')
