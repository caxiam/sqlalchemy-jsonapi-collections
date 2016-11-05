

class BaseViewDriver(object):
    """Base view driver."""

    @classmethod
    def make_from_path(cls, path, schema):
        """Return a list of view driver instances."""
        if path == '':
            return []

        relationships = cls.remove_inflection(path).split('.')
        attribute = relationships.pop()

        fields = []
        for relationship in relationships:
            field = cls(relationship, schema)
            fields.append(field)
            schema = field.related_class
        fields.append(cls(attribute, schema))
        return fields

    @classmethod
    def send_to_path(cls, fields):
        """Send a list of field instances to a string column-name path."""
        column_names = []
        for field in fields:
            column_names.append(field.column_name)
        return '.'.join(column_names)

    @staticmethod
    def remove_inflection(text):
        """Replace hyphens with underscores."""
        return text.replace('-', '_')


class MarshmallowDriver(BaseViewDriver):
    field_error = 'Invalid field "{}" specified.'
    relationship_error = 'Invalid relationship "{}" specified.'

    def __init__(self, key, view):
        self.key = key
        self.view = view

        try:
            self.field = self.view._declared_fields[self.key]
        except KeyError:
            raise AttributeError(self.field_error.format(key))

    @property
    def column_name(self):
        """Return the field's column attribute name."""
        return self.field.attribute or self.key

    @property
    def related_class(self):
        """Return the related schema class of a relationship field."""
        if not self.is_relationship:
            raise AttributeError(self.relationship_error.format(self.key))
        return self.field.schema

    @property
    def is_relationship(self):
        """Return `True` if the field is a relationship."""
        return hasattr(self.field, 'schema')

    def deserialize_values(self, values):
        """Deserialize a set of values into their appropriate types."""
        return [self.deserialize_value(value) for value in values]

    def deserialize_value(self, value):
        """Deserialize a string value to the appropriate type."""
        if value == '':
            return None
        return self.field._deserialize(value, None, None)
