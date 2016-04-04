# -*- coding: utf-8 -*-


class BaseDriver(object):
    """Extensible driver template for interacting with SQLAlchemy."""

    def __init__(self, collection):
        """DO NOT OVERRIDE.

        :param collection: A `jsonapi_collections` Collection instance.
        """
        self.collection = collection

    def get_column_model(self, relationship):
        """Get the parent model of a relationship."""
        return relationship.property.mapper.class_

    def get_column_type(self, column):
        """Return the column's Python type."""
        return self.column.property.columns[0].type.python_type

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

    def deserialize(self, column, values):
        """Parse a set of values into the appropriate type."""
        raise NotImplementedError
