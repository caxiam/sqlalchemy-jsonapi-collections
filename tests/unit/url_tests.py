from nose.tools import assert_raises

from jsonapiquery import url
from tests.unit import UnitTestCase


class URLTestCase(UnitTestCase):

    def test_iter_fieldsets(self):
        params = {'fields[users]': 'age,birthday,first-name'}
        fields = url.iter_fieldsets(params)

        field = next(fields)
        self.assertTrue(field.source == 'fields[users]')
        self.assertTrue(field.type == 'users')
        self.assertTrue(field.fields == ['age', 'birthday', 'first-name'])

    def test_iter_filters(self):
        params = {'filter[user.email.email-address]': 'a@b.com'}
        filters = url.iter_filters(params)

        filter = next(filters)
        self.assertTrue(filter.source == 'filter[user.email.email-address]')
        self.assertTrue(filter.relationships == ['user', 'email'])
        self.assertTrue(filter.attribute == 'email-address')
        self.assertTrue(filter.value == 'a@b.com')

    def test_iter_paginators(self):
        params = {'page[limit]': '100'}
        paginators = url.iter_paginators(params)

        paginator = next(paginators)
        self.assertTrue(paginator.source == 'page[limit]')
        self.assertTrue(paginator.strategy == 'limit')
        self.assertTrue(paginator.value == '100')

    def test_iter_includes(self):
        params = {'include': 'user.email,contacts'}
        includes = url.iter_includes(params)

        include = next(includes)
        self.assertTrue(include.source == 'include')
        self.assertTrue(include.relationships == ['user', 'email'])

        include = next(includes)
        self.assertTrue(include.source == 'include')
        self.assertTrue(include.relationships == ['contacts'])

    def test_iter_sorts(self):
        params = {'sort': '+a.b,-c.d,e'}
        sorts = url.iter_sorts(params)

        sort = next(sorts)
        self.assertTrue(sort.source == 'sort')
        self.assertTrue(sort.direction == '+')
        self.assertTrue(sort.relationships == ['a'])
        self.assertTrue(sort.attribute == 'b')

        sort = next(sorts)
        self.assertTrue(sort.source == 'sort')
        self.assertTrue(sort.direction == '-')
        self.assertTrue(sort.relationships == ['c'])
        self.assertTrue(sort.attribute == 'd')

        sort = next(sorts)
        self.assertTrue(sort.source == 'sort')
        self.assertTrue(sort.direction == '+')
        self.assertTrue(sort.relationships == [])
        self.assertTrue(sort.attribute == 'e')

    def test_iter_namespace(self):
        params = {'fields[a]': 'b', 'filter[c]': 'd'}
        fields = url.iter_namespace(params, 'fields')

        field = next(fields)
        self.assertTrue(field[0] == 'a')
        self.assertTrue(field[1] == 'b')

        assert_raises(StopIteration, next, fields)
