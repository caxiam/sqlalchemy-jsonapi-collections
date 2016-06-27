"""Test database interactions."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker

from jsonapi_query.database.sqlalchemy import QueryMixin
from tests.sqlalchemy import BaseSQLAlchemyTestCase, Person, School, Student


class BaseDatabaseSQLAlchemyTests(BaseSQLAlchemyTestCase):
    """Base database SQLAlchemy test case for establishing mock environment."""

    def setUp(self):
        """Set the query class and create a set of rows to test against."""
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

        student = Student(school_id=1, person_id=1)
        self.session.add(student)

        student = Student(school_id=1, person_id=2)
        self.session.add(student)


class FilterSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test query filtering related methods."""

    def test_query_filter_strategy_eq(self):
        """Test filtering a query with the `eq` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.name, 'eq', ['Fred']).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_strategy_negation(self):
        """Test filtering a query with a negated strategy."""
        models = self.session.query(
            Person).apply_filter(Person.name, '~eq', ['Fred']).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_filter_strategy_gt(self):
        """Test filtering a query with the `gt` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.age, 'gt', [5]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].age == 10)

    def test_query_filter_strategy_gte(self):
        """Test filtering a query with the `gte` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.age, 'gte', [5]).all()
        self.assertTrue(len(models) == 2)

    def test_query_filter_strategy_lt(self):
        """Test filtering a query with the `lt` strategy."""
        date = datetime.strptime('2015-01-01', "%Y-%m-%d").date()
        models = self.session.query(
            Person).apply_filter(Person.birth_date, 'lt', [date]).all()
        self.assertTrue(len(models) == 1)

    def test_query_filter_strategy_lte(self):
        """Test filtering a query with the `lte` strategy."""
        date = datetime.strptime('2015-01-01', "%Y-%m-%d").date()
        models = self.session.query(
            Person).apply_filter(Person.birth_date, 'lte', [date]).all()
        self.assertTrue(len(models) == 2)

    def test_query_filter_strategy_like(self):
        """Test filtering a query with the `like` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.name, 'like', ['Fred']).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_strategy_ilike(self):
        """Test filtering a query with the `ilike` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.name, 'ilike', ['fred']).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_multiple_values(self):
        """Test filtering a query by multiple values."""
        models = self.session.query(
            Person).apply_filter(Person.name, 'eq', ['Fred', 'Carl']).all()
        self.assertTrue(len(models) == 2)


class SortSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test query sorting related methods."""

    def test_query_sort_attribute_ascending(self):
        """Test sorting a query by an ascending column."""
        models = self.session.query(Person).apply_sort(Person.name, '+').all()
        self.assertTrue(models[0].name == 'Carl')
        self.assertTrue(models[1].name == 'Fred')

    def test_query_sort_attribute_descending(self):
        """Test sorting a query by a descending column."""
        models = self.session.query(Person).apply_sort(Person.name, '-').all()
        self.assertTrue(models[0].name == 'Fred')
        self.assertTrue(models[1].name == 'Carl')

    def test_query_sort_relationship_ascending(self):
        """Test sorting a query by an ascending relationship column."""
        models = self.session.query(
            Student).apply_sort(Person.name, '+', [Person]).all()
        self.assertTrue(models[0].person.name == 'Carl')
        self.assertTrue(models[1].person.name == 'Fred')

    def test_query_sort_relationship_descending(self):
        """Test sorting a query by a descending relationship column."""
        models = self.session.query(
            Student).apply_sort(Person.name, '-', [Person]).all()
        self.assertTrue(models[0].person.name == 'Fred')
        self.assertTrue(models[1].person.name == 'Carl')


class PaginateSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test query pagination related methods."""

    def test_query_paginate_limit(self):
        """Test limiting a query."""
        models = self.session.query(
            Person).apply_paginators([('limit', 1)]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_paginate_offset(self):
        """Test offsetting a query."""
        models = self.session.query(
            Person).apply_paginators([('offset', 1)]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_paginate_number(self):
        """Test offsetting a query by page number."""
        models = self.session.query(
            Person).apply_paginators([('number', 2), ('limit', 1)]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')
