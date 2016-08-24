"""End to end query testing."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker

from jsonapi_query import url
from jsonapi_query.database.sqlalchemy import group_and_remove, QueryMixin
from jsonapi_query.translation.model.sqlalchemy import SQLAlchemyModelDriver
from jsonapi_query.translation.view.marshmallow_jsonapi import (
    MarshmallowJSONAPIDriver)
from tests.marshmallow_jsonapi import Person as PersonSchema
from tests.sqlalchemy import BaseSQLAlchemyTestCase, Person, School, Student


class SQLAlchemyTestCase(BaseSQLAlchemyTestCase):

    def setUp(self):
        super().setUp()
        self.m_driver = SQLAlchemyModelDriver(Person)
        self.v_driver = MarshmallowJSONAPIDriver(PersonSchema)

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

    def test_filter_query(self):
        """Test filtering a query by a url string."""
        link = 'testsite.com/people?filter[age]=lt:10'
        params = url.get_parameters(link)

        filters = []
        for fltr in url.get_filters(params):
            self.v_driver.initialize_path(fltr[0])
            path = self.v_driver.get_model_path()
            values = self.v_driver.deserialize_values(fltr[2])
            filters.append((path, fltr[1], values))

        new = []
        for fltr in filters:
            column, models, joins = self.m_driver.parse_path(fltr[0])
            new.append((column, fltr[1], fltr[2], joins))

        models = self.session.query(Person).apply_filters(new).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].age == 5)

    def test_filter_query_deeply_nested(self):
        """Test filtering a query by a deeply nested url string."""
        link = 'testsite.com/people?filter[student.school.title]=eq:School'
        params = url.get_parameters(link)

        filters = []
        for fltr in url.get_filters(params):
            self.v_driver.initialize_path(fltr[0])
            path = self.v_driver.get_model_path()
            values = self.v_driver.deserialize_values(fltr[2])
            filters.append((path, fltr[1], values))

        new = []
        for fltr in filters:
            column, models, joins = self.m_driver.parse_path(fltr[0])
            new.append((column, fltr[1], fltr[2], joins))

        models = self.session.query(Person).apply_filters(new).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_sort_query(self):
        """Test sorting by an attribute."""
        link = 'testsite.com/people?sort=age'
        params = url.get_parameters(link)

        sorts = []
        for sort in url.get_sorts(params):
            self.v_driver.initialize_path(sort[0])
            path = self.v_driver.get_model_path()
            sorts.append((path, sort[1]))

        new = []
        for sort in sorts:
            column, models, joins = self.m_driver.parse_path(sort[0])
            new.append((column, sort[1], joins))

        models = self.session.query(Person).apply_sorts(new).all()
        self.assertTrue(len(models) == 2)
        self.assertTrue(models[0].name == 'Fred')

    def test_sort_query_deeply_nested(self):
        """Test sorting by a deeply nested attribute."""
        link = 'testsite.com/people?sort=-student.school.title'
        params = url.get_parameters(link)

        sorts = []
        for sort in url.get_sorts(params):
            self.v_driver.initialize_path(sort[0])
            path = self.v_driver.get_model_path()
            sorts.append((path, sort[1]))

        new = []
        for sort in sorts:
            column, models, joins = self.m_driver.parse_path(sort[0])
            new.append((column, sort[1], joins))

        models = self.session.query(Person).apply_sorts(new).all()
        self.assertTrue(len(models) == 2)
        self.assertTrue(models[0].name == 'Fred')
        self.assertTrue(models[1].name == 'Carl')

    def test_paginate_query_by_limit(self):
        """Test paginating a query by the limit strategy."""
        link = 'testsite.com/people?page[limit]=1&page[offset]=1'
        params = url.get_parameters(link)

        paginators = url.get_paginators(params)

        models = self.session.query(Person).apply_paginators(paginators).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_paginate_query_by_page(self):
        """Test paginating a query by the number strategy."""
        link = 'testsite.com/people?page[size]=1&page[number]=2'
        params = url.get_parameters(link)

        paginators = url.get_paginators(params)

        models = self.session.query(Person).apply_paginators(paginators).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_include_single_column(self):
        """Test including a relationship."""
        link = 'testsite.com/people?include=student'
        params = url.get_parameters(link)

        includes = []
        schemas = []
        for include_ in url.get_includes(params):
            self.v_driver.initialize_path(include_)
            includes.append(self.v_driver.get_model_path())
            schemas.extend(self.v_driver.schemas)

        included_models = []
        mappers = []
        for include_ in includes:
            _, models, joins = self.m_driver.parse_path(include_)
            included_models.extend(models)
            mappers.extend(joins)

        items = self.session.query(
            Person).filter_by(id=1).include(mappers).all()
        items = group_and_remove(items, [Person] + included_models)[1:]
        included = []
        for position, columns in enumerate(items):
            schema = schemas[position]
            included.extend(schema.dump(columns, many=True).data['data'])

        self.assertTrue(len(schemas) == 1)
        self.assertTrue(len(included_models) == 1)
        self.assertTrue(len(items) == 1)
        self.assertTrue(len(items[0]) == 1)
        self.assertTrue(len(included) == 1)

    def test_include_multiple_columns(self):
        """Test including a list of relationships."""
        def unique(items):
            unqiues = []
            for item in items:
                if item not in unqiues:
                    unqiues.append(item)
            return unqiues

        link = 'testsite.com/people?include=student.school,student'
        params = url.get_parameters(link)

        includes = []
        schemas = []
        for include_ in url.get_includes(params):
            self.v_driver.initialize_path(include_)
            includes.append(self.v_driver.get_model_path())
            schemas.extend(self.v_driver.schemas)
        schemas = unique(schemas)

        included_models = []
        mappers = []
        for include_ in includes:
            _, models, joins = self.m_driver.parse_path(include_)
            included_models.extend(models)
            mappers.extend(joins)
        included_models = unique(included_models)

        items = self.session.query(
            Person).filter_by(id=1).include(mappers).all()
        items = group_and_remove(items, [Person] + included_models)[1:]
        included = []
        for position, columns in enumerate(items):
            schema = schemas[position]
            included.extend(schema.dump(columns, many=True).data['data'])

        self.assertTrue(len(schemas) == 2)
        self.assertTrue(len(included_models) == 2)
        self.assertTrue(len(items) == 2)
        self.assertTrue(len(items[0]) == 1)
        self.assertTrue(len(included) == 2)

        self.assertIn('id', included[0])
        self.assertIn('type', included[0])
        self.assertIn('relationships', included[0])

        self.assertIn('id', included[1])
        self.assertIn('type', included[1])
        self.assertIn('attributes', included[1])
