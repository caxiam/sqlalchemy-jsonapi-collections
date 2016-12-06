from abc import abstractmethod
from collections import namedtuple
from urllib.parse import urlencode

from jsonapiquery import url

import functools


Filter = namedtuple('Filter', ['fields', 'strategy', 'values'])
Sort = namedtuple('Sort', ['fields', 'direction'])


class JSONAPIQuery(object):
    """JSONAPI query orchestration class."""

    model_driver = None
    view_driver = None

    def __init__(self, parameters, model, view):
        self.parameters = parameters
        self.model = model
        self.view = view

    @property
    @functools.lru_cache()
    def filters(self):
        """Return a list of filter parameters paths."""
        return url.get_filters(self.parameters)

    @property
    @functools.lru_cache()
    def sorts(self):
        """Return a list of sort paramter paths."""
        return url.get_sorts(self.parameters)

    @property
    @functools.lru_cache()
    def includes(self):
        """Return a list of include parameter paths."""
        return url.get_includes(self.parameters)

    @property
    @functools.lru_cache()
    def paginators(self):
        """Return a list of page parameters paths."""
        return url.get_paginators(self.parameters)

    def make_error(self, parameter, message):
        """Return a JSONAPI compliant parameter error object."""
        return {
            'source': {'parameter': parameter},
            'detail': message
        }

    def make_filter_fields(self):
        """Return a list of parsed filters."""
        filters, errors = [], []
        for filter in self.filters:
            filter, error = self.make_filter_field(*filter)
            filters.append(filter)
            errors.extend(error)
        return filters, errors

    def make_filter_field(self, path, strategy, values):
        """Return a tuple of fields, strategy, and typed values."""
        try:
            fields = self.view_driver.make_from_path(path, self.view)
        except AttributeError as exc:
            return None, [self.make_error('filter[{}]'.format(path), str(exc))]
        try:
            values = fields[-1].deserialize_values(values)
        except Exception as exc:
            return None, [self.make_error('filter[{}]'.format(path), str(exc))]
        return Filter(fields, strategy, values), []

    def make_sort_fields(self):
        """Return a list of parsed sorts."""
        sorts, errors = [], []
        for sort in self.sorts:
            sort, error = self.make_sort_field(*sort)
            sorts.append(sort)
            errors.extend(error)
        return sorts, errors

    def make_sort_field(self, path, direction):
        """Return a tuple of fields, strategy, and typed values."""
        try:
            fields = self.view_driver.make_from_path(path, self.view)
            return Sort(fields, direction), []
        except AttributeError as exc:
            return None, [self.make_error('sort', str(exc))]

    def make_include_fields(self):
        """Return a list of parsed includes."""
        includes, errors = [], []
        for include in self.includes:
            fields, error = self.make_include_field(include)
            includes.append(Includes(fields))
            errors.extend(error)
        return includes, errors

    def make_include_field(self, path):
        """Return a tuple of fields."""
        try:
            return self.view_driver.make_from_path(path, self.view), []
        except AttributeError as exc:
            return [], [self.make_error('include', str(exc))]

    def make_query_from_fields(self, fields):
        """Return a `Query` tuple from a set of fields."""
        return self.model_driver.make_from_fields(fields, self.model)

    def make_included_response(self, response, models, schemas):
        """Return a compounded response."""
        included = self.serialize_included(models, schemas)
        if included:
            response['included'] = included
        return response

    @abstractmethod
    def serialize_included(self, models, schemas):
        """Return a serialized set of included objects.

        Keyword arguments:
            models (list): List of lists of like model instances.
            schemas (lust): List of schemas instances.
        """
        return

    def make_paginated_response(self, response, total):
        """Return a paginated response."""
        if total is not None:
            links = self.make_pagination_links(self.parameters, total)
            response['meta'] = {'total': total}
            response['links'] = links
        return response

    def make_pagination_links(self, base_url, parameters, total):
        """Return a dictionary of pagination links.

        Based on the pagination strategy, calculate the correct limits
        and offsets and encode the parameters into a URL safe format.
        """
        if 'page[number]' in parameters:
            return self._paginate_number(base_url, parameters, total)
        return self._paginate_offset(base_url, parameters, total)

    def _paginate_offset(self, base_url, params, total):
        limit, offset = 50, 0
        for strategy, value in self.paginators:
            if strategy == 'limit':
                limit = int(value)
            elif strategy == 'offset':
                offset = int(value)

        url = base_url + '?{}'
        values = self._build_page_offset_values(total, limit, offset)
        return {
            'first': url.format(self._encode_page_offset(params, values[0])),
            'last': url.format(self._encode_page_offset(params, values[1])),
            'next': url.format(self._encode_page_offset(params, values[2])),
            'prev': url.format(self._encode_page_offset(params, values[3])),
            'self': base_url
        }

    def _paginate_number(self, base_url, params, total):
        limit, page = 50, 1
        for strategy, value in self.paginators:
            if strategy == 'limit':
                limit = int(value)
            elif strategy == 'number':
                page = int(value)

        url = base_url + '?{}'
        values = self._build_page_number_values(total, limit, page)
        return {
            'first': url.format(self._encode_page_number(params, values[0])),
            'last': url.format(self._encode_page_number(params, values[1])),
            'next': url.format(self._encode_page_number(params, values[2])),
            'prev': url.format(self._encode_page_number(params, values[3])),
            'self': base_url
        }

    def _build_page_offset_values(self, total, limit, offset):
        """Return a tuple of offset values.

        The response, in order of position, is `first`, `last`, `next`,
        and `prev`.
        """
        return 0, max(total - limit, 0), offset + limit, max(offset - limit, 0)

    def _build_page_number_values(self, total, limit, current):
        """Return a tuple of page number values.

        The response, in order of position, is `first`, `last`, `next`,
        and `prev`.
        """
        return 1, max(total / limit, 1), current + 1, max(current - 1, 1)

    def _encode_page_offset(self, params, value):
        """Return encoded page[offset] parameters."""
        return self._encode_parameters(params, 'page[offset]', value)

    def _encode_page_number(self, params, value):
        """Return encoded page[number] parameters."""
        return self._encode_parameters(params, 'page[number]', value)

    def _encode_parameters(self, params, key, value):
        """Return a URL encoded parameter object."""
        params = params.copy()
        params[key] = value
        return urlencode(params)

    def _validate_paginators(self):
        errors = []
        for key, value in self.paginators:
            errors.extend(self._validate_paginator(key, value))
        return errors

    def _validate_paginator(self, key, value):
        error = 'Invalid value "{}" specified.'.format(value)
        if not value.isdigit():
            return [self.make_error('page[{}]'.format(key), error)]
        return []


class Includes(object):

    def __init__(self, fields):
        self.fields = fields

    def __len__(self):
        return len(self.fields)

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        return self.fields[index]

    @property
    @functools.lru_cache()
    def schemas(self):
        """Return a list of schema instances."""
        return [field.related_class for field in self.fields]
