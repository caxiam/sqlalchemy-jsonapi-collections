"""End to end query testing."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker

from jsonapi_query import url
from jsonapi_query.database.sqlalchemy import QueryMixin
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

        school = School(name='School 1')
        self.session.add(school)

        school = School(name='School 2')
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
            path = self.v_driver.replace_path(fltr[0])
            values = self.v_driver.deserialize_from_path(fltr[0], fltr[2])
            filters.append((path, fltr[1], values))

        new = []
        for fltr in filters:
            column, models = self.m_driver.parse_path(fltr[0])
            new.append((column, fltr[1], fltr[2], models))

        models = self.session.query(Person).apply_filters(new).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].age == 5)

    def test_filter_query_deeply_nested(self):
        """Test filtering a query by a deeply nested url string."""
        link = 'testsite.com/people?filter[student.school.title]=School 1'
        params = url.get_parameters(link)

        filters = []
        for fltr in url.get_filters(params):
            path = self.v_driver.replace_path(fltr[0])
            values = self.v_driver.deserialize_from_path(fltr[0], fltr[2])
            filters.append((path, fltr[1], values))

        new = []
        for fltr in filters:
            column, models = self.m_driver.parse_path(fltr[0])
            new.append((column, fltr[1], fltr[2], models))

        models = self.session.query(Person).apply_filters(new).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_sort_query(self):
        """Test sorting by an attribute."""
        link = 'testsite.com/people?sort=age'
        params = url.get_parameters(link)

        sorts = []
        for sort in url.get_sorts(params):
            path = self.v_driver.replace_path(sort[0])
            sorts.append((path, sort[1]))

        new = []
        for sort in sorts:
            column, models = self.m_driver.parse_path(sort[0])
            new.append((column, sort[1], models))

        models = self.session.query(Person).apply_sorts(new).all()
        self.assertTrue(len(models) == 2)
        self.assertTrue(models[0].name == 'Fred')

    def test_sort_query_deeply_nested(self):
        """Test sorting by a deeply nested attribute."""
        link = 'testsite.com/people?sort=-student.school.title'
        params = url.get_parameters(link)

        sorts = []
        for sort in url.get_sorts(params):
            path = self.v_driver.replace_path(sort[0])
            sorts.append((path, sort[1]))

        new = []
        for sort in sorts:
            column, models = self.m_driver.parse_path(sort[0])
            new.append((column, sort[1], models))

        models = self.session.query(Person).apply_sorts(new).all()
        self.assertTrue(len(models) == 2)
        self.assertTrue(models[0].name == 'Carl')

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
