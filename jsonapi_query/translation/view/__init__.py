

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
