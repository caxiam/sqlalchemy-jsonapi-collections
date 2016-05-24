# -*- coding: utf-8 -*-
from jsonapi_collections.drivers.sqlalchemy import SQLAlchemyDriver
from jsonapi_collections.errors import JSONAPIError
from jsonapi_collections.filter import FilterParameter
from jsonapi_collections.include import IncludeValue
from jsonapi_collections.sort import SortValue


class Resource(object):
    """The `Resource` object acts as the central orchestration object.

    Supplying the minimum set of a arguments, `model` and `parameters`,
    offers the full suite of filtering and sorting capability to
    `SQLAlchemy` query objects.  Optionally specifying a `driver` and
    `schema` allows for intermediary libraries and implementations to
    control how `SQLAlchemy` columns are accessed from their JSONAPI
    field representations.

    To use the `Resource` object you must first initialize it.  Once
    initialized, call the `filter_query` or `sort_query` methods
    against a `SQLAlchemy` query object.  The response from both
    methods will be a permutated query object.
    """

    ERRORS = {
        'field': 'Invalid field specified: {}.',
        'parameter': 'Invalid parameter specified: {}.',
        'value': 'Invalid parameter value specified for {}.'
    }

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
        self.schema = schema or model
        self.driver = driver(self) if driver else SQLAlchemyDriver(self)
        self.parameters = self._handle_parameters(parameters)

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

    def paginate_query(self, query):
        """Paginate and retrieve a list of models."""
        page = self.parameters['page']
        return query.limit(page['limit']).offset(page['offset'])

    def compound_response(self, models):
        """Compound a response object.

        :params models: List of `SQLAlchemy` model instances.
        """
        if not isinstance(models, list):
            models = [models]
        field_names = self.parameters.get('include', [])
        includes, error = IncludeValue.generate(self.driver, field_names)
        if error:
            raise JSONAPIError([error])

        included = []
        for model in models:
            included.extend(IncludeValue.include(model, includes))
        return included

    def _handle_parameters(self, parameters):
        """Return a formatted JSONAPI parameters object."""
        errors = []

        filters, err = self._get_filtered_fields(parameters)
        errors.extend(err)

        include, err = self._get_included_parameters(parameters)
        errors.extend(err)

        sort, err = self._get_sorted_parameters(parameters)
        errors.extend(err)

        page, err = self._get_pagination_parameters(parameters)
        errors.extend(err)

        if errors:
            raise JSONAPIError(errors)
        return {
            'filters': filters, 'include': include, 'sort': sort, 'page': page
        }

    def _get_filtered_fields(self, parameters):
        """Return a dictionary of field, value pairs to filter by.

        By specifying a parameter, you are requesting for it to be
        filtered. Empty strings are interpreted as being `None` type
        filters. The following `filter[field]=` is interpreted as
        `WHERE field IS NULL`.

        :param parameters: A dictionary of parameters specified during init.
        """
        errors = []
        filters = {}
        for key, value in parameters.iteritems():
            if not key.startswith('filter['):
                continue

            if not self.driver.validate_attribute_path(key[7:-1]):
                errors.append({
                    'detail': self.ERRORS['parameter'].format(key),
                    'source': {'parameter': key}
                })
                continue

            if value == '':
                value = None
            else:
                value = value.split(',')
            filters[key[7:-1]] = value
        return filters, errors

    def _get_pagination_parameters(self, parameters):
        """Return a dictionary of parameter, value pairs to paginate by."""
        errors = []
        pagination_parameters = {}

        limits = ['limit', 'page[size]', 'page[limit]']
        offsets = ['offset', 'page[number]', 'page[offset]']
        for key, value in parameters.iteritems():
            if key not in limits and key not in offsets:
                continue
            try:
                pagination_parameters[key] = int(value)
            except ValueError:
                errors.append({
                    'detail': self.ERRORS['value'].format(key),
                    'source': {'parameter': key}
                })

        page = {'limit': 100, 'offset': 0}
        for key, value in pagination_parameters.iteritems():
            if key == 'page[limit]' or key == 'limit' or key == 'page[size]':
                page['limit'] = value
            elif key == 'page[offset]' or key == 'offset':
                page['offset'] = value
            elif key == 'page[number]':
                page['offset'] = value * parameters.get('page[size]', 0)
        return page, errors

    def _get_included_parameters(self, parameters):
        """Return a list of field names.

        If the `key` parameter is specified but does not contain a
        value then the `key` key will be ignored.

        :param key: String reference to dictionary key.
        :param parameters: Dictionary of parameters specified during init.
        """
        errors = []
        fields = parameters.get('include', '')
        if fields == '':
            return [], errors

        fields = fields.split(',')
        for field in fields:
            if not self.driver.validate_relationship_path(field):
                errors.append({
                    'detail': self.ERRORS['field'].format(field),
                    'source': {'parameter': 'include'}
                })
        return fields, errors

    def _get_sorted_parameters(self, parameters):
        """Return a list of field names.

        If the `key` parameter is specified but does not contain a
        value then the `key` key will be ignored.

        :param key: String reference to dictionary key.
        :param parameters: Dictionary of parameters specified during init.
        """
        errors = []
        fields = parameters.get('sort', '')
        if fields == '':
            return [], errors

        fields = fields.split(',')
        for field in fields:
            validated_field = field[1:] if field.startswith('-') else field
            if not self.driver.validate_attribute_path(validated_field):
                errors.append({
                    'detail': self.ERRORS['field'].format(field),
                    'source': {'parameter': 'sort'}
                })
        return fields, errors
