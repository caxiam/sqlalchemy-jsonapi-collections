from jsonapiquery.url import (
    get_parameters, get_includes, get_sorts, get_filters, get_paginators)
from tests.unit import UnitTestCase


class URLTestCase(UnitTestCase):
    pass


class ParametersURLTestCase(URLTestCase):

    def test_get_parameters(self):
        base_url = 'http://www.test.com/1'
        query = '?filter[field]=1&page[size]=100&sort=field&include=field'
        parameters = get_parameters(base_url + query)

        self.assertTrue(isinstance(parameters, dict))
        self.assertIn('page[size]', parameters)
        self.assertIn('filter[field]', parameters)
        self.assertIn('sort', parameters)
        self.assertIn('include', parameters)


class IncludeURLTestCase(URLTestCase):

    def test_get_includes(self):
        parameters = {'include': 'relationship,nested.relationship'}
        includes = get_includes(parameters)

        self.assertTrue(isinstance(includes, list))
        self.assertTrue(len(includes) == 2)

        self.assertTrue(includes[0] == 'relationship')
        self.assertTrue(includes[1] == 'nested.relationship')


class SortURLTestCase(URLTestCase):

    def test_get_descending_sort(self):
        parameters = {'sort': '-field'}
        sorts = get_sorts(parameters)

        self.assertTrue(isinstance(sorts, list))
        self.assertTrue(len(sorts) == 1)
        self.assertTrue(sorts[0][0] == 'field')
        self.assertTrue(sorts[0][1] == '-')

    def test_get_ascending_sort(self):
        parameters = {'sort': '+field'}
        sorts = get_sorts(parameters)

        self.assertTrue(isinstance(sorts, list))
        self.assertTrue(len(sorts) == 1)
        self.assertTrue(sorts[0][0] == 'field')
        self.assertTrue(sorts[0][1] == '+')

    def test_get_sort(self):
        parameters = {'sort': 'field'}
        sorts = get_sorts(parameters)

        self.assertTrue(isinstance(sorts, list))
        self.assertTrue(len(sorts) == 1)
        self.assertTrue(sorts[0][0] == 'field')
        self.assertTrue(sorts[0][1] == '+')

    def test_get_multiple_sorts(self):
        parameters = {'sort': 'field,-relationship.field'}
        sorts = get_sorts(parameters)

        self.assertTrue(isinstance(sorts, list))
        self.assertTrue(len(sorts) == 2)
        self.assertTrue(sorts[0][0] == 'field')
        self.assertTrue(sorts[0][1] == '+')
        self.assertTrue(sorts[1][0] == 'relationship.field')
        self.assertTrue(sorts[1][1] == '-')


class PageURLTestCase(URLTestCase):

    def test_get_paginator_limit(self):
        parameters = {'page[limit]': '100'}
        pages = get_paginators(parameters)

        self.assertTrue(isinstance(pages, list))
        self.assertTrue(len(pages) == 1)

        self.assertTrue(isinstance(pages[0], tuple))
        self.assertTrue(pages[0][0] == 'limit')
        self.assertTrue(pages[0][1] == '100')

    def test_get_paginator_size(self):
        parameters = {'page[size]': '100'}
        pages = get_paginators(parameters)

        self.assertTrue(isinstance(pages, list))
        self.assertTrue(len(pages) == 1)

        self.assertTrue(isinstance(pages[0], tuple))
        self.assertTrue(pages[0][0] == 'limit')
        self.assertTrue(pages[0][1] == '100')

    def test_get_paginator_offset(self):
        parameters = {'page[offset]': '100'}
        pages = get_paginators(parameters)

        self.assertTrue(isinstance(pages, list))
        self.assertTrue(len(pages) == 1)

        self.assertTrue(isinstance(pages[0], tuple))
        self.assertTrue(pages[0][0] == 'offset')
        self.assertTrue(pages[0][1] == '100')

    def test_get_paginator_number(self):
        parameters = {'page[number]': '100'}
        pages = get_paginators(parameters)

        self.assertTrue(isinstance(pages, list))
        self.assertTrue(len(pages) == 1)

        self.assertTrue(isinstance(pages[0], tuple))
        self.assertTrue(pages[0][0] == 'number')
        self.assertTrue(pages[0][1] == '100')


class FilterURLTestCase(URLTestCase):

    def test_get_filter(self):
        parameters = {'filter[field]': 'gte:100'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field')
        self.assertTrue(filters[0][1] == 'gte')
        self.assertTrue(filters[0][2] == ['100'])

    def test_get_filter_negated_strategy(self):
        parameters = {'filter[field.id]': '~in:1,2,3'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field.id')
        self.assertTrue(filters[0][1] == '~in')
        self.assertTrue(filters[0][2] == ['1', '2', '3'])

    def test_get_filter_multiple_fields(self):
        parameters = {'filter[field1,field2]': '1'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field1,field2')
        self.assertTrue(filters[0][1] is None)
        self.assertTrue(filters[0][2] == ['1'])

    def test_get_filter_multiple_strategies(self):
        parameters = {'filter[field]': 'eq:gte:test'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field')
        self.assertTrue(filters[0][1] == 'eq')
        self.assertTrue(filters[0][2] == ['gte:test'])

    def test_get_filter_multiple_values(self):
        parameters = {'filter[field]': '1,2,hello'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field')
        self.assertTrue(filters[0][1] is None)
        self.assertTrue(filters[0][2] == ['1', '2', 'hello'])

    def test_get_filter_default_strategy(self):
        parameters = {'filter[field]': 'hello'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field')
        self.assertTrue(filters[0][1] is None)
        self.assertTrue(filters[0][2] == ['hello'])

    def test_get_filter_invalid_strategy(self):
        parameters = {'filter[field]': 'invalid:strategy'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 1)

        self.assertTrue(isinstance(filters[0], tuple))
        self.assertTrue(filters[0][0] == 'field')
        self.assertTrue(filters[0][1] is None)
        self.assertTrue(filters[0][2] == ['invalid:strategy'])

    def test_skip_invalid_filter(self):
        parameters = {'filter[field]t': 'eq:hello'}
        filters = get_filters(parameters)

        self.assertTrue(isinstance(filters, list))
        self.assertTrue(len(filters) == 0)
