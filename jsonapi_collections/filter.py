# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from jsonapi_collections.errors import FieldError
from sqlalchemy import and_, or_


class FilterParameter(object):
    """Formulate a query filter."""

    relationship = None

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

            column_name = self.driver.get_column_name(relationship_name)
            self.relationship = self.driver.get_column(column_name)

            relationship_field = self.driver.get_field(relationship_name)
            schema = self.driver.get_related_schema(relationship_field)

            model = self.driver.get_column_model(self.relationship)
            column_name = self.driver.get_column_name(field_name, schema)
            self.column = self.driver.get_column(column_name, model)
        else:
            column_name = self.driver.get_column_name(field_name)
            self.column = self.driver.get_column(column_name)
            schema = None

        self.values = self.driver.deserialize(
            self.column, field_name, values, schema)

    def __call__(self):
        """Create a `SQLAlchemy` query expression.

        Filters are constructed with three considerations:
            * Is this query occuring across a relationship?
            * Is this query one-to-many or many-to-many?
            * Does the query need to evaluate more than one value?

        If the query is not filtering across a relationship column, we
        can return the filters formulated by the `_prepare_strategies`
        call.  Multiple strategies are wrapped in an `or_` function.

        If the query is a relationship, we determine whether or not the
        relationship has many related models or has one related model.

        If a many-to-many relationship is detected, we query the values
        with the `any` method.  If a one-to-many relationship is
        detected, we query the values with the `has` method.

        If the query has more than one strategy it needs to executed
        as an argument to the `or_` function.
        """
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
        """Return a set of filters.

        The `_prepare_strategies` method calls `_prepare_strategy` in a
        loop and returns the aggregate set of strategies.

        :param values: List of typed values to filter with.
        """
        filters = []
        for value in values:
            filters.append(self._prepare_strategy(value))
        return filters

    def _prepare_strategy(self, value):
        """Return a `SQLAlchemy` query expression.

        The `_prepare_strategy` method considers three things:
            * Are you filtering against an Enum column instance?
            * Are you filtering with a `None` type value.
            * Are you filtering against some specifically handled type.

        If the column is determined to be an enumeration then no
        meaningful filtering can occur other than a simple equality
        check.

        If the value is determined to be a `None` type then no
        meaningful filtering can occur other than a simple equality
        check.

        If the column's type is determined to be one of the special
        cases, specialized filtering can occur. This filtering is not
        specified by the JSONAPI 1.0 specification.  Strings columns
        are filtered as a wildcard search.  Boolean columns are
        filtered using the `is_` method. Datetime columns retrieve all
        datetimes within the current day.

        If the column is not a special type, a simple equality check
        against the value is returned.

        :param value: Typed value to filter with.
        """
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
        """Parse field, value pairs into `FilterParameter` instances.

        The `generate` classmethod bulk initializes a set of field,
        value pairs into the `FilterParameter` class.

        A successful generation results in the `filters` list being
        appended the newly formed instance.  A failed generation
        results in a JSONAPI 1.0 specification error object being
        appended to the errors list.

        This method can return both a set of filters and a set of
        errors.  It is recommended that you evaluate the errors
        recieved before continuing.

        :param driver: `jsonapi_collections` driver instance.
        :param parameters: A dictionary of field, value pairs.
        """
        filters = []
        errors = []
        for field_name, values in parameters.items():
            try:
                filters.append(cls(driver, field_name, values))
            except FieldError as exc:
                message = {
                    "source": {
                        "parameter": 'filter[{}]'.format(field_name)
                    },
                    "detail": exc.message
                }
                errors.append(message)
        return filters, errors

    @staticmethod
    def filter_by(query, filters):
        """Apply a series of `FilterParameter` instances as query filters.

        The `filter_by` staticmethod acts as a helper method to always
        ensure that API changes do not disrupt the general process of
        filter application.

        :param query: `SQLAlchemy` query object.
        :param filters: List of `FilterParameter` instances.
        """
        for filter in filters:
            query = query.filter(filter())
        return query
