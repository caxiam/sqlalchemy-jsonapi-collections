"""marshmallow-jsonapi schema translation module."""
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
        stones = path.split('.')
        relationships, attribute = stones[:-1], stones[-1]

        schema = self.view
        for field_name in relationships:
            field = self._get_field(field_name, schema)
            if not self._is_relationship(field):
                raise TypeError('Invalid relationship field specified.')
            self._append_field_meta(field, field_name)

            schema = field.schema
            self.schemas.append(schema)

        field = self._get_field(attribute, schema)
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
        return field.deserialize(value)

    def _get_field(self, attribute, schema):
        return schema._declared_fields[attribute]

    def _is_relationship(self, field):
        return hasattr(field, 'related_schema')
