"""End to end query testing."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker

from jsonapi_query import JSONAPIQuery
from jsonapi_query.database.sqlalchemy import group_and_remove, QueryMixin
from jsonapi_query.drivers.model import SQLAlchemyDriver
from jsonapi_query.drivers.view import MarshmallowDriver
from tests.marshmallow_jsonapi import Person as PersonSchema
from tests.sqlalchemy import *


class SQLAQuery(JSONAPIQuery):
    model_driver = SQLAlchemyDriver
    view_driver = MarshmallowDriver


class SQLAlchemyTestCase(BaseSQLAlchemyTestCase):
    model = Person
    view = PersonSchema

    def setUp(self):
        super().setUp()

        class BaseQuery(QueryMixin, Query):
            pass

        self.session = sessionmaker(bind=self.engine, query_cls=BaseQuery)()
        self.session.begin_nested()

        date = datetime.strptime('2014-01-01', "%Y-%m-%d").date()
        fred = Person(name='Fred', age=5, birth_date=date)
        self.session.add(fred)

        date = datetime.strptime('2015-01-01', "%Y-%m-%d").date()
        carl = Person(name='Carl', age=10, birth_date=date)
        self.session.add(carl)

        school = School(name='School')
        self.session.add(school)
        school = School(name='College')
        self.session.add(school)

        student = Student(school_id=1, person_id=1)
        self.session.add(student)

        student = Student(school_id=2, person_id=2)
        self.session.add(student)

    def test_query_filter(self):
        """Test filtering a query."""
        queries = []
        jquery = SQLAQuery({'filter[age]': 'lt:10'}, self.model, self.view)
        for filter in jquery.make_filter_fields():
            query = jquery.make_query_from_fields(filter.fields)
            queries.append((query.column, filter.strategy, filter.values, query.joins))

        models = self.session.query(Person).apply_filters(queries).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].age == 5)

    def test_query_complex_filter(self):
        """Test filtering a query with complex requirements."""
        params = {'filter[student.school.title]': 'eq:School'}
        jquery = SQLAQuery(params, self.model, self.view)

        queries = []
        for filter in jquery.make_filter_fields():
            query = jquery.make_query_from_fields(filter.fields)
            queries.append((query.column, filter.strategy, filter.values, query.joins))

        models = self.session.query(Person).apply_filters(queries).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_sort(self):
        """Test sorting a query."""
        params = {'sort': '-age'}
        jquery = SQLAQuery(params, self.model, self.view)

        queries = []
        for sort in jquery.make_sort_fields():
            query = jquery.make_query_from_fields(sort.fields)
            queries.append((query.column, sort.direction, query.joins))

        models = self.session.query(Person).apply_sorts(queries).all()
        self.assertTrue(len(models) == 2)
        self.assertTrue(models[1].name == 'Fred')
        self.assertTrue(models[0].name == 'Carl')

    def test_query_complex_sort(self):
        """Test sorting a query with complex requirements."""
        params = {'sort': '-student.school.title'}
        jquery = SQLAQuery(params, self.model, self.view)

        queries = []
        for sort in jquery.make_sort_fields():
            query = jquery.make_query_from_fields(sort.fields)
            queries.append((query.column, sort.direction, query.joins))

        models = self.session.query(Person).apply_sorts(queries).all()
        self.assertTrue(len(models) == 2)
        self.assertTrue(models[0].name == 'Fred')
        self.assertTrue(models[1].name == 'Carl')

    def test_paginate_query_by_limit(self):
        """Test paginating a query by the limit strategy."""
        params = {'page[limit]': 1, 'page[offset]': 1}
        jquery = SQLAQuery(params, self.model, self.view)

        models = self.session.query(Person).apply_paginators(jquery.paginators).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_paginate_query_by_page(self):
        """Test paginating a query by the number strategy."""
        params = {'page[size]': 1, 'page[number]': 2}
        jquery = SQLAQuery(params, self.model, self.view)

        models = self.session.query(Person).apply_paginators(jquery.paginators).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_complex_include(self):
        """Test sorting a query with complex requirements."""
        params = {'include': 'student.school,student'}
        jquery = SQLAQuery(params, self.model, self.view)

        includes = jquery.make_include_fields()
        query = jquery.make_query_from_fields(includes)

        items = self.session.query(Person).filter_by(id=1).include(query.joins).all()
        self.assertTrue(len(items) == 1)
        self.assertTrue(len(items[0]) == 3)

        items = group_and_remove(items, [Person] + query.selects)[1:]
        schemas = jquery.make_schemas_from_fields(includes)
        included = []
        for position, columns in enumerate(items):
            schema = schemas[position]
            included.extend(schema.dump(columns, many=True).data['data'])

        self.assertTrue(len(schemas) == 2)
        self.assertTrue(len(query.selects) == 2)
        self.assertTrue(len(items) == 2)
        self.assertTrue(len(items[0]) == 1)
        self.assertTrue(len(included) == 2)

        self.assertIn('id', included[0])
        self.assertIn('type', included[0])
        self.assertIn('relationships', included[0])

        self.assertIn('id', included[1])
        self.assertIn('type', included[1])
        self.assertIn('attributes', included[1])
