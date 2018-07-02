from sqlalchemy.orm import Query, sessionmaker

from jsonapiquery import JSONAPIQuery
from jsonapiquery.database.sqlalchemy import QueryMixin
from jsonapiquery.drivers.model import SQLAlchemyDriver
from jsonapiquery.drivers.schema import MarshmallowDriver
from tests.marshmallow_jsonapi import (
    Person as PersonSchema, Student as StudentSchema)
from tests.sqlalchemy import (
    BaseSQLAlchemyTestCase, Person as PersonModel, Student as StudentModel)


class JSONAPI(JSONAPIQuery):
    model_driver = SQLAlchemyDriver
    view_driver = MarshmallowDriver

    def make_errors(self, errors):
        return Exception(errors)

    def serialize_included(self, schema, models):
        return schema.dump(models, many=True).data['data']


class JSONAPIQueryTestCase(BaseSQLAlchemyTestCase):
    model = PersonModel
    parameters = {
        'filter[age]': '10',
        'sort': 'age',
        'include': 'student',
        'page[limit]': '10'
    }
    view = PersonSchema

    def setUp(self):
        super().setUp()

        class BaseQuery(QueryMixin, Query):
            pass

        self.session = sessionmaker(bind=self.engine, query_cls=BaseQuery)()

    @property
    def query(self):
        return self.session.query(self.model)

    def make_jsonapi(self, parameters, model=None, view=None):
        """Return a JSONAPI instance."""
        model = model or self.model
        view = view or self.view
        return JSONAPI(parameters, model, view)

    def test_filters(self):
        """Assert only `filter` values are returned."""
        jsonapi = self.make_jsonapi(self.parameters)
        self.assertTrue(jsonapi.filters == [('age', None, ['10'])])

    def test_sorts(self):
        """Assert only `sort` values are returned."""
        jsonapi = self.make_jsonapi(self.parameters)
        self.assertTrue(jsonapi.sorts == [('age', '+')])

    def test_includes(self):
        """Assert only `include` values are returned."""
        jsonapi = self.make_jsonapi(self.parameters)
        self.assertTrue(jsonapi.includes == ['student'])

    def test_paginators(self):
        """Assert only `paginator` values are returned."""
        jsonapi = self.make_jsonapi(self.parameters)
        self.assertTrue(jsonapi.paginators == [('limit', '10')])

    def test_filter(self):
        """Assert the query is filtered."""
        jsonapi = self.make_jsonapi(self.parameters)
        query, errors = jsonapi.filter(self.query, [])

        self.assertTrue(query != self.query)
        self.assertTrue(errors == [])

    def test_failed_filter(self):
        """Assert parameters errors are returned."""
        jsonapi = self.make_jsonapi({'filter[x]': '1'})
        query, errors = jsonapi.filter(self.query, [])

        self.assertTrue(len(errors) == 1)
        self.assertTrue(errors[0]['source']['parameter'] == 'filter[x]')

    def test_sort(self):
        """Assert the query is sorted."""
        jsonapi = self.make_jsonapi(self.parameters)
        query, errors = jsonapi.sort(self.query, [])

        self.assertTrue(query != self.query)
        self.assertTrue(errors == [])

    def test_failed_sort(self):
        """Assert parameters errors are returned."""
        jsonapi = self.make_jsonapi({'sort': 'x'})
        query, errors = jsonapi.sort(self.query, [])

        self.assertTrue(len(errors) == 1)
        self.assertTrue(errors[0]['source']['parameter'] == 'sort')

    def test_include(self):
        """Assert the query includes related models."""
        jsonapi = self.make_jsonapi(self.parameters)
        query, selects, schemas, errors = jsonapi.include(self.query, [])

        self.assertTrue(query != self.query)
        self.assertTrue(errors == [])
        self.assertTrue(selects == [StudentModel])
        self.assertTrue(len(schemas) == 1)
        self.assertTrue(isinstance(schemas[0], StudentSchema))

    def test_failed_include(self):
        """Assert parameters errors are returned."""
        jsonapi = self.make_jsonapi({'include': 'x'})
        query, selects, schemas, errors = jsonapi.include(self.query, [])

        self.assertTrue(selects == [])
        self.assertTrue(schemas == [])
        self.assertTrue(len(errors) == 1)
        self.assertTrue(errors[0]['source']['parameter'] == 'include')

    def test_paginate(self):
        """Assert the query is paginated."""
        jsonapi = self.make_jsonapi(self.parameters)
        query, total, errors = jsonapi.paginate(self.query, [])

        self.assertTrue(query != self.query)
        self.assertTrue(errors == [])
        self.assertTrue(total == 0)

    def test_failed_paginator(self):
        """Assert parameters errors are returned."""
        jsonapi = self.make_jsonapi({'page[limit]': 'abc'})
        query, total, errors = jsonapi.paginate(self.query, [])

        self.assertTrue(total is None)
        self.assertTrue(len(errors) == 1)
        self.assertTrue(errors[0]['source']['parameter'] == 'page[limit]')

    def test_make_query(self):
        """Assert the query has been altered."""
        jsonapi = self.make_jsonapi(self.parameters)
        query, total, selects, schemas = jsonapi.make_query(self.query, {})

        self.assertTrue(query != self.query)
        self.assertTrue(total == 0)
        self.assertTrue(selects == [StudentModel])
        self.assertTrue(len(schemas) == 1)
        self.assertTrue(isinstance(schemas[0], StudentSchema))

    def test_failed_make_query(self):
        """Assert all parameter errors are returned."""
        try:
            jsonapi = self.make_jsonapi({
                'filter[x]': '1', 'sort': 'x', 'include': 'x',
                'page[limit]': 'abc'})
            jsonapi.make_query(self.query, {})
        except Exception as exc:
            self.assertTrue(len(exc.args[0]) == 4)
        else:
            self.assertTrue(False)

    def test_make_included_response(self):
        """Assert document was compounded."""
        jsonapi = self.make_jsonapi(self.parameters)
        response = jsonapi.make_included_response(
            {}, [[PersonModel()]], [PersonSchema()])

        self.assertTrue('included' in response)
        self.assertTrue(len(response['included']) == 1)
        self.assertTrue('id' in response['included'][0])
        self.assertTrue('type' in response['included'][0])

    def test_make_paginated_response(self):
        """Assert document was paginated."""
        jsonapi = self.make_jsonapi(self.parameters)
        response = jsonapi.make_paginated_response({}, 'www.google.com', 1000)

        self.assertTrue('meta' in response)
        self.assertTrue('total' in response['meta'])
        self.assertTrue(response['meta']['total'] == 1000)

        self.assertTrue('links' in response)
        self.assertTrue('first' in response['links'])
        self.assertTrue('last' in response['links'])
        self.assertTrue('next' in response['links'])
        self.assertTrue('prev' in response['links'])
        self.assertTrue('self' in response['links'])
