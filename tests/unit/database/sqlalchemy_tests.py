"""Test database interactions."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker

from jsonapiquery.database.sqlalchemy import QueryMixin
from jsonapiquery.drivers.model.sqlalchemy import Mapper, Column as ColumnType
from jsonapiquery.types import Filter, Include, Sort, Paginator
from jsonapiquery.utils import QueryCounter
from tests.sqlalchemy import *


class BaseDatabaseSQLAlchemyTests(BaseSQLAlchemyTestCase):
    """Base database SQLAlchemy test case for establishing mock environment."""

    def setUp(self):
        """Set the query class and create a set of rows to test against."""
        super().setUp()

        class BaseQuery(QueryMixin, Query):
            pass

        self.session = sessionmaker(bind=self.engine, query_cls=BaseQuery)()
        self.session.begin_nested()

        self.counter = QueryCounter(self.session)

        image_1 = Image()
        self.session.add(image_1)
        image_2 = Image()
        self.session.add(image_2)

        date = datetime.strptime('2014-01-01', "%Y-%m-%d").date()
        fred = Person(name='Fred', age=5, birth_date=date, image=image_1)
        self.session.add(fred)

        date = datetime.strptime('2015-01-01', "%Y-%m-%d").date()
        carl = Person(name='Carl', age=10, birth_date=date, image=image_1)
        self.session.add(carl)

        school = School(name='School', image=image_2)
        self.session.add(school)
        school = School(name='College', image=image_2)
        self.session.add(school)

        student = Student(school_id=1, person_id=1)
        self.session.add(student)

        student = Student(school_id=2, person_id=2)
        self.session.add(student)
        self.session.commit()


class FilterSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test query filtering related methods."""

    def test_query_filter_strategy_eq(self):
        """Test filtering a query with the `eq` strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), 'Fred')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_strategy_negation(self):
        """Test filtering a query with a negated strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), 'ne:Fred')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_filter_strategy_gt(self):
        """Test filtering a query with the `gt` strategy."""
        filter_ = Filter('', [], ColumnType('age', Person), 'gt:5')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].age == 10)

    def test_query_filter_strategy_gte(self):
        """Test filtering a query with the `gte` strategy."""
        filter_ = Filter('', [], ColumnType('age', Person), 'gte:5')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 2)

    def test_query_filter_strategy_lt(self):
        """Test filtering a query with the `lt` strategy."""
        filter_ = Filter(
            '', [], ColumnType('birth_date', Person), 'lt:2015-01-01')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)

    def test_query_filter_strategy_lte(self):
        """Test filtering a query with the `lte` strategy."""
        filter_ = Filter(
            '', [], ColumnType('birth_date', Person), 'lte:2015-01-01')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 2)

    def test_query_filter_strategy_like(self):
        """Test filtering a query with the `like` strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), 'like:red')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_strategy_ilike(self):
        """Test filtering a query with the `ilike` strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), 'like:RED')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_in_values(self):
        """Test filtering a query by the `in` strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), 'in:Fred')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_not_in_values(self):
        """Test filtering a query by the `~in` strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), '~in:Fred')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_filter_multiple_values(self):
        """Test filtering a query by multiple values."""
        filter_ = Filter('', [], ColumnType('name', Person), 'Fred,Carl')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 2)

    def test_query_filter_invalid_strategy(self):
        """Test filtering a query by an invalid strategy."""
        filter_ = Filter('', [], ColumnType('name', Person), 'qq:Fred,Carl')

        try:
            self.session.query(Person).apply_filter(filter_).all()
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_query_filter_joined(self):
        """Test filtering a query with multiple join conditions."""
        filter_ = Filter(
            '', [Mapper('student', Person), Mapper('school', Student)],
            ColumnType('name', School), 'School')

        models = self.session.query(Person).apply_filter(filter_).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')


class SortSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test query sorting related methods."""

    def test_query_sort_attribute_ascending(self):
        """Test sorting a query by an ascending column."""
        sort = Sort('', [], ColumnType('name', Person), '+')

        models = self.session.query(Person).apply_sort(sort).all()
        self.assertTrue(models[0].name == 'Carl')
        self.assertTrue(models[1].name == 'Fred')

    def test_query_sort_attribute_descending(self):
        """Test sorting a query by a descending column."""
        sort = Sort('', [], ColumnType('name', Person), '-')

        models = self.session.query(Person).apply_sort(sort).all()
        self.assertTrue(models[0].name == 'Fred')
        self.assertTrue(models[1].name == 'Carl')

    def test_query_sort_relationship_ascending(self):
        """Test sorting a query by an ascending relationship column."""
        sort = Sort(
            '', [Mapper('person', Student)], ColumnType('name', Person), '+')

        models = self.session.query(Student).apply_sort(sort).all()
        self.assertTrue(models[0].person.name == 'Carl')
        self.assertTrue(models[1].person.name == 'Fred')

    def test_query_sort_relationship_descending(self):
        """Test sorting a query by a descending relationship column."""
        sort = Sort(
            '', [Mapper('person', Student)], ColumnType('name', Person), '-')

        models = self.session.query(Student).apply_sort(sort).all()
        self.assertTrue(models[0].person.name == 'Fred')
        self.assertTrue(models[1].person.name == 'Carl')

    def test_query_sort_over_multiple_joins(self):
        """Test sorting a query with multiple join conditions."""
        sort = Sort(
            '', [Mapper('student', Person), Mapper('school', Student)],
            ColumnType('name', School), '+')

        models = self.session.query(Person).apply_sort(sort).all()
        self.assertTrue(models[0].name == 'Carl')
        self.assertTrue(models[1].name == 'Fred')


class IncludeSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):

    def test_include_one_column(self):
        """Test including a single relationship."""
        include = Include('', [Mapper('student', Person)])

        with self.counter as query_counter:
            model = self.session.query(Person).first()
            model.student
            self.assertTrue(query_counter.count == 2)

        with self.counter as query_counter:
            model = self.session.query(Person).include(include).first()
            model.student
            self.assertTrue(query_counter.count == 1)

    def test_include_multiple_columns(self):
        """Test including multiple relationships."""
        include = Include(
            '', [Mapper('student', Person), Mapper('school', Student)])

        with self.counter as query_counter:
            model = self.session.query(Person).first()
            model.student
            model.student[0].school
            self.assertTrue(query_counter.count == 3)
        
        with self.counter as query_counter:
            model = self.session.query(Person).include(include).first()
            model.student
            model.student[0].school
            self.assertTrue(query_counter.count == 1)

    def test_include_self_referential_relationship(self):
        """Test including a self-referential relationship."""
        self.session.add(Category(name='Category A'))
        self.session.add(Category(name='Category B', category_id=1))
        self.session.add(Category(name='Category C', category_id=2))
        self.session.commit()

        include = Include(
            '', [Mapper('category', Category), Mapper('categories', Category)])

        with self.counter as query_counter:
            model = self.session.query(
                Category).filter(Category.id == 2).first()
            model.category
            model.category.categories
            self.assertTrue(query_counter.count == 4)

        with self.counter as query_counter:
            model = self.session.query(
                Category).filter(Category.id == 2).include(include).first()
            model.category
            model.category.categories
            self.assertTrue(query_counter.count == 1)

    def test_include_polymorphic_model(self):
        """Test including polymorphic relationships."""
        self.session.add(Rose(person_id=1, kind='rose'))
        self.session.add(Sunflower(person_id=1, kind='sunflower'))
        self.session.commit()

        include = Include('', [Mapper('flowers', Person)])

        with self.counter as query_counter:
            model = self.session.query(Person).first()
            model.flowers
            self.assertTrue(query_counter.count == 3)

        with self.counter as query_counter:
            model = self.session.query(Person).include(include).first()
            model.flowers
            self.assertTrue(query_counter.count == 1)


class PaginateSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test query pagination related methods."""

    def test_query_paginate_limit(self):
        """Test limiting a query."""
        paginator = Paginator('', 'limit', '1')

        models = self.session.query(Person).apply_paginators([paginator]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_paginate_offset(self):
        """Test offsetting a query."""
        paginator = Paginator('', 'offset', '1')

        models = self.session.query(Person).apply_paginators([paginator]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_paginate_number(self):
        """Test offsetting a query by page number."""
        p1 = Paginator('', 'limit', '1')
        p2 = Paginator('', 'number', '2')

        models = self.session.query(Person).apply_paginators([p1, p2]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_paginate_number_invalid_value(self):
        """Test offsetting a query by page number."""
        p1 = Paginator('', 'limit', 'q')

        try:
            models = self.session.query(Person).apply_paginators([p1]).all()
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
