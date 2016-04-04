# -*- coding: utf-8 -*-
from jsonapi_collections.filter import FilterParameter
from jsonapi_collections.sort import SortValue


class Collection(object):
    """JSONAPI resource collection handler."""

    def __init__(self, model, parameters, view=None):
        """Initialize the collection controller.

        :param model: SQLAlchemy model class.
        :param parameters: Dictionary of parameter, value pairs.
        :param view: Schema to validate against.
            If `None`, the filter key, value pairs will be validated
            against the model.
        """
        self.model = model
        self.parameters = self._handle_parameters(parameters)

        if self.view is None:
            self.view = model
        else:
            self.view = view

    def get_filters(self):
        """Return a list of filters."""
        filters, errors = FilterParameter.generate(self.view, self.parameters)
        if errors:
            raise Exception(errors)
        return filters

    def get_sorts(self):
        """Return a list of sorts."""
        fields = self.parameters.get('sort', '')
        if fields == '':
            return []

        sorts, errors = SortValue.generate(self.view, fields.split(','))
        if errors:
            raise Exception(errors)
        return sorts

    def _validate_fields(self):
        """Validate the provided fields."""
        pass

    def _handle_parameters(self, parameters):
        """."""
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
