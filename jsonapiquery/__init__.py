from collections import namedtuple, OrderedDict

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
