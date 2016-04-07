# -*- coding: utf-8 -*-
from jsonapi_collections.drivers.sqlalchemy import SQLAlchemyDriver
from jsonapi_collections.errors import JSONAPIError
from jsonapi_collections.filter import FilterParameter
from jsonapi_collections.sort import SortValue


class Collection(object):
    """The `Collection` object acts as the central orchestration object.

    Supplying the minimum set of a arguments, `model` and `parameters`,
    offers the full suite of filtering and sorting capability to
    `SQLAlchemy` query objects.  Optionally specifying a `driver` and
    `schema` allows for intermediary libraries and implementations to
    control how `SQLAlchemy` columns are accessed from their JSONAPI
    field representations.

    To use the `Collection` object you must first initialize it.  Once
    initialized, call the `filter_query` or `sort_query` methods
    against a `SQLAlchemy` query object.  The response from both
    methods will be a permutated query object.
    """

    def __init__(self, model, parameters, driver=None, schema=None):
        """Initialize the collection controller.

        :param model: SQLAlchemy model class.
        :param parameters: Dictionary of parameter, value pairs.
        :param driver: `jsonapi_collections` driver instance.
        :param schema: Schema to validate against.
            If `None`, the key, value pairs will be validated against
            the model.
        """
        self.model = model
        self.parameters = self._handle_parameters(parameters)
        self.schema = schema or model
        self.driver = driver(self) if driver else SQLAlchemyDriver(self)

    def filter_query(self, query):
        """Filter a given query by a set of parameters or error.

        A successful call to this method will result in a permutated
        filtered query object.  You can filter or sort your query
        object at any point before or after calling this method. The
        ordering of the filters and sorts are irrelevant.

        A failed call will result in suppressed FieldError messages
        being marshaled to the current context. The list of errors are
        formatted according to the JSONAPI 1.0 specification. The
        `generate` method will return a list of errors each pointing to
        the specific parameter that caused the failure.

        Errors raised by this method are intended for general, public
        view and should not be suppressed by default.

        :param query: `SQLAlchemy` query object.
        """
        field_names = self.parameters.get('filters', {})
        filters, errors = FilterParameter.generate(self.driver, field_names)
        if errors:
            raise JSONAPIError(errors)
        return FilterParameter.filter_by(query, filters)

    def sort_query(self, query):
        """Sort a given query by a set of the `sort` parameter or error.

        A successful call to this method will result in a permutated,
        sorted query object. You can filter or sort your query object
        at any point before or after calling this method. The ordering
        of the filters and sorts are irrelevant.

        A failed call will result in suppressed FieldError messages
        being marshaled to the current context. The list of error
        messages are formatted according to the JSONAPI 1.0
        specification. The `generate` method will return exactly one
        error regardless of the number of sorts. The number of errors
        detected can be measured by the length of the error message
        list.

        Errors raised by this method are intended for general, public
        view and should not be suppressed by default.

        :param query: `SQLAlchemy` query object.
        """
        field_names = self.parameters.get('sort', [])
        sorts, error = SortValue.generate(self.driver, field_names)
        if error:
            raise JSONAPIError([error])
        return SortValue.sort_by(query, sorts)

    def _handle_parameters(self, parameters):
        """Return a formatted JSONAPI parameters object."""
        return {
            'sort': self._get_sorted_fields(parameters),
            'filters': self._get_filtered_fields(parameters)
        }

    def _get_sorted_fields(self, parameters):
        """Return a list of field names to sort by.

        If the `sort` parameter is specified but does not contain a
        value then the `sort` key will be ignored.

        :param parameters: A dictionary of parameters specified during init.
        """
        sort = parameters.pop('sort', '')
        if sort == '':
            return []
        return sort.split(',')

    def _get_filtered_fields(self, parameters):
        """Return a dictionary of field, value pairs to filter by.

        By specifying a parameter, you are requesting for it to be
        filtered. Empty strings are interpreted as being `None` type
        filters. The following `filter[field]=` is interpreted as
        `WHERE field IS NULL`.

        :param parameters: A dictionary of parameters specified during init.
        """
        filters = {}
        for key, value in parameters.iteritems():
            if not key.startswith('filter['):
                continue
            if value == '':
                value = None
            else:
                value = value.split(',')
            filters[key[7:-1]] = value
        return filters
