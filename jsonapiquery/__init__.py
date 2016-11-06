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

    def make_filter_fields(self):
        """Return a list of parsed filters."""
        filters = []
        for filter in self.filters:
            filters.append(self.make_filter_field(*filter))
        return filters

    def make_filter_field(self, path, strategy, values):
        """Return a tuple of fields, strategy, and typed values."""
        fields = self.view_driver.make_from_path(path, self.view)
        values = fields[-1].deserialize_values(values)
        return Filter(fields, strategy, values)

    def make_sort_fields(self):
        """Return a list of parsed sorts."""
        sorts = []
        for sort in self.sorts:
            sorts.append(self.make_sort_field(*sort))
        return sorts

    def make_sort_field(self, path, direction):
        """Return a tuple of fields, strategy, and typed values."""
        fields = self.view_driver.make_from_path(path, self.view)
        return Sort(fields, direction)

    def make_include_fields(self):
        """Return a list of parsed includes."""
        includes = OrderedDict()
        for include in self.includes:
            fields = self.make_include_field(include)
            includes.update(((str(field), field) for field in fields))

        fields = list(includes.values())
        return Includes(fields)

    def make_include_field(self, path):
        """Return a tuple of fields."""
        return self.view_driver.make_from_path(path, self.view)

    def make_schemas_from_fields(self, fields):
        """Return a list of schema instances."""
        return [field.related_class for field in fields]

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
