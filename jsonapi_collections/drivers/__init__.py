# -*- coding: utf-8 -*-
from jsonapi_collections.errors import FieldError


class BaseDriver(object):
    """Extensible driver template for interacting with `SQLAlchemy`.

    Drivers act a bindings for validating and extracting relationship
    and attribute data.

    The `BaseDriver` template provides generic `SQLAlchemy` bindings as
    well as overridable methods for interacting with third-party schemas.
    """

    def __init__(self, collection):
        """DO NOT OVERRIDE.

        :param collection: A `jsonapi_collections` Collection instance.
        """
        self.collection = collection

    def get_column_model(self, column):
        """Get the parent model of a relationship."""
        if self.is_relationship(column):
            return column.property.mapper.class_
        raise FieldError('Invalid relationship specified.')

    def is_relationship(self, column):
        """Determine if a field is a relationship."""
        return hasattr(column.property, 'mapper')

    def get_column_type(self, column):
        """Return the column's Python type."""
        return column.property.columns[0].type.python_type

    def is_enum(self, column):
        """Determine if a column is an enumeration."""
        if hasattr(column.property.columns[0].type, 'enums'):
            return True
        return False

    def get_column(self, field):
        """Return a `SQLAlchemy` column instance.

        :param field: A schema field instance.
        """
        raise NotImplementedError

    def get_column_name(self, field_name):
        """Return a string reference to a model column."""
        raise NotImplementedError

    def get_field(self, field_name):
        """Return a schema field instance.

        :param field_name: A string reference to a schema's field name.
        """
        raise NotImplementedError

    def get_related_schema(self, field):
        """Return a related schema reference."""
        raise NotImplementedError

    def deserialize(self, column, values, schema=None):
        """Parse a set of values into the appropriate type."""
        raise NotImplementedError

    def serialize(self, models):
        """Serialize a set of SQLAlchemy instances."""
        raise NotImplementedError

    def validate_attribute_path(self, path):
        """Return `False` if the last member is not a valid attribute."""
        raise NotImplementedError

    def validate_relationship_path(self, path):
        """Return `False` if all members are not valid relationships."""
        raise NotImplementedError
