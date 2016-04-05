# -*- coding: utf-8 -*-
from jsonapi_collections.drivers.sqlalchemy import SQLAlchemyDriver
from jsonapi_collections.filter import FilterParameter
from jsonapi_collections.sort import SortValue


class Collection(object):
    """JSONAPI resource collection handler."""

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

        driver = driver or SQLAlchemyDriver
        self.driver = driver(self)

    def filter_query(self, query):
        """Permutate `SQLAlchemy` query with filtering."""
        field_names = self.parameters.get('filters', {})
        filters = FilterParameter.generate(self.driver, field_names)
        return FilterParameter.filter_by(query, filters)

    def sort_query(self, query):
        """Permutate `SQLAlchemy` query with sorting."""
        field_names = self.parameters.get('sort', [])
        sorts = SortValue.generate(self.driver, field_names)
        return SortValue.sort_by(query, sorts)

    def _handle_parameters(self, parameters):
        """Return a formatted JSONAPI parameters object."""
        return {
            'sort': self._get_sorted_fields(parameters),
            'filters': self._get_filtered_fields(parameters)
        }

    def _get_sorted_fields(self, parameters):
        """Return a list of fields to sort by."""
        sort = parameters.pop('sort', '')
        if sort == '':
            return []
        return sort

    def _get_filtered_fields(self, parameters):
        """Return a dictionary of field, value pairs to filter by."""
        filters = {}
        for key, value in parameters.iteritems():
            if not key.startswith('filter'):
                continue
            if value == '':
                value = None
            else:
                value = value.split(',')
            filters[key[7:-1]] = value
        return filters
