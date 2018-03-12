from jsonapiquery import errors

from . import remove_inflection, SchemaDriverBase


class SchemaDriverMarshmallow(SchemaDriverBase):

    def parse_attribute(self, field_name, schema):
        return Attribute(field_name, schema)

    def parse_relationship(self, field_name, schema):
        return Relationship(field_name, schema)


class Field(object):

    def __init__(self, field_name, schema):
        self.field_name = remove_inflection(field_name)
        self.schema = schema
        self.field = self.schema.declared_fields[field_name]


class Attribute(Field):

    def deserialize_values(self, values):
        """Deserialize a set of values into their appropriate types."""
        return [self.deserialize_value(value) for value in values]

    def deserialize_value(self, value):
        """Deserialize a string value to the appropriate type."""
        if value == '':
            return None
        return self.field._deserialize(value, None, None)


class Relationship(Field):

    @property
    def type(self):
        return self.field.schema
