# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, or_


class FilterParameter(object):
    """Formulate a query filter."""

    def __init__(self, driver, field_name, values):
        """Set the column, driver, many, and values attributes.

        :param driver: `jsonapi_collections` driver instance.
        :param field_name: A string representation of a schema field.
        :param values: A list of typed values to filter by.
        """
        self.driver = driver
        self.many = len(values) > 1

        if "." in field_name:
            relationship_name, field_name = field_name.split('.')

            relationship_column_name = self.driver.get_column_name(
                relationship_name)
            self.relationship = self.driver.get_column(
                relationship_column_name)

            relationship_field = self.driver.get_field(relationship_name)
            related_schema = self.driver.get_related_schema(relationship_field)
            field = self.driver.get_field(field_name, related_schema)

            model = self.driver.get_column_model(self.relationship)
            column_name = self.driver.get_column_name(
                field_name, related_schema)
            self.column = self.driver.get_column(column_name, model)
        else:
            field = self.driver.get_field(field_name)

            column_name = self.driver.get_column_name(field_name)
            self.column = self.driver.get_column(column_name)
            self.relationship = None

        self.values = self.driver.deserialize(field, values)

    def __call__(self):
        """Generate a `SQLAlchemy` filter."""
        filters = self._prepare_strategies(self.values)

        if self.relationship is None:
            if self.many:
                return or_(*filters)
            return filters[0]

        if self.relationship.property.uselist:
            wrapper = self.relationship.any
        else:
            wrapper = self.relationship.has

        if self.many:
            return wrapper(or_(*filters))
        return wrapper(*filters)

    @property
    def column_type(self):
        """Extract the column's type."""
        return self.driver.get_column_type(self.column)

    def _prepare_strategies(self, values):
        filters = []
        for value in values:
            filters.append(self._prepare_strategy(value))
        return filters

    def _prepare_strategy(self, value):
        if self.driver.is_enum(self.column) or value is None:
            return self.column == value

        if self.column_type == str:
            return self.column.ilike('%{}%'.format(value))
        elif self.column_type == bool:
            return self.column.is_(value)
        elif self.column_type == datetime:
            tomorrow = value + timedelta(days=1)
            return and_(self.column >= value, self.column < tomorrow)
        return self.column == value

    @classmethod
    def generate(cls, driver, parameters):
        """Parse a dictionary into `FilterParameter` instances.

        :param driver: `jsonapi_collections` driver instance.
        :param parameters: A dictionary of field, value pairs.
        """
        filters = []
        for field_name, values in parameters.iteritems():
            filters.append(cls(driver, field_name, values))
        return filters

    @staticmethod
    def filter_by(query, filters):
        """Apply a series of `FilterParameter` instances as query filters.

        :param query: A `SQLAlchemy` query object.
        :param filters: A list of `FilterParameter` instances.
        """
        for filter in filters:
            query = query.filter(filter())
        return query
