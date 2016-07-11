"""Test database interactions."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker

from jsonapi_query.database.sqlalchemy import QueryMixin
from tests.sqlalchemy import (
    BaseSQLAlchemyTestCase, Category, Person, Product, School, Student)


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
        school = School(name='College')
        self.session.add(school)

        student = Student(school_id=1, person_id=1)
        self.session.add(student)

        student = Student(school_id=2, person_id=2)
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

    def test_query_filter_in_values(self):
        """Test filtering a query by the `in` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.name, 'in', ['Fred']).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_not_in_values(self):
        """Test filtering a query by the `~in` strategy."""
        models = self.session.query(
            Person).apply_filter(Person.name, '~in', ['Fred']).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Carl')

    def test_query_filter_multiple_values(self):
        """Test filtering a query by multiple values."""
        models = self.session.query(
            Person).apply_filter(Person.name, 'eq', ['Fred', 'Carl']).all()
        self.assertTrue(len(models) == 2)

    def test_query_filter_invalid_strategy(self):
        """Test filtering a query by an invalid strategy."""
        try:
            self.session.query(
                Person).apply_filter(Person.name, 'qq', ['Fred']).all()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def test_query_filter_multiple_joins(self):
        """Test filtering a query with multiple join conditions."""
        models = self.session.query(Person).apply_filter(
            School.name, 'eq', ['School'],
            [Person.student, Student.school]).all()
        self.assertTrue(len(models) == 1)
        self.assertTrue(models[0].name == 'Fred')

    def test_query_filter_ambiguous_join_conditions(self):
        """Test filtering a query under ambiguous join conditions."""
        a = Category(name='Category A')
        self.session.add(a)
        b = Category(name='Category B', category_id=1)
        self.session.add(b)
        p = Product(primary_category_id=1, secondary_category_id=2, name='Tst')
        self.session.add(p)

        model = self.session.query(Product).apply_filters([
            (Category.name, 'eq', ['Category A'], [Product.primary_category]),
            (Category.name, 'eq', ['Category B'], [Product.secondary_category])
        ]).first()
        self.assertTrue(isinstance(model, Product))
        self.assertTrue(model.name == 'Tst')


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
            Student).apply_sort(Person.name, '+', [Student.person]).all()
        self.assertTrue(models[0].person.name == 'Carl')
        self.assertTrue(models[1].person.name == 'Fred')

    def test_query_sort_relationship_descending(self):
        """Test sorting a query by a descending relationship column."""
        models = self.session.query(
            Student).apply_sort(Person.name, '-', [Student.person]).all()
        self.assertTrue(models[0].person.name == 'Fred')
        self.assertTrue(models[1].person.name == 'Carl')

    def test_query_sort_over_multiple_joins(self):
        """Test sorting a query with multiple join conditions."""
        models = self.session.query(Person).apply_sort(
            School.name, '+', [Person.student, Student.school]).all()
        self.assertTrue(models[0].name == 'Carl')
        self.assertTrue(models[1].name == 'Fred')

    def test_query_sort_ambiguous_join_conditions(self):
        """Test filtering a query under ambiguous join conditions."""
        a = Category(name='Category A')
        self.session.add(a)
        b = Category(name='Category B', category_id=1)
        self.session.add(b)
        p = Product(primary_category_id=1, name='A')
        self.session.add(p)
        p = Product(primary_category_id=2, name='B')
        self.session.add(p)

        models = self.session.query(Product).apply_sort(
            Category.name, '-', [Product.primary_category]).all()
        self.assertTrue(models[0].name == 'B')
        self.assertTrue(models[1].name == 'A')


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


class IncludeSQLAlchemyTestCase(BaseDatabaseSQLAlchemyTests):
    """Test constructing an included query."""

    def test_include_one_column(self):
        """Test including a single relationship."""
        models = self.session.query(Person).include([Person.student]).first()
        self.assertTrue(isinstance(models[0], Person))
        self.assertTrue(isinstance(models[1], Student))
        self.assertTrue(models[1].person_id == 1)

    def test_include_multiple_columns(self):
        """Test including multiple relationships."""
        models = self.session.query(Person).include([
            Person.student, Student.school]).first()
        self.assertTrue(isinstance(models[0], Person))
        self.assertTrue(isinstance(models[1], Student))
        self.assertTrue(isinstance(models[2], School))

    def test_include_self_referential_relationship(self):
        """Test including a self-referential relationship."""
        a = Category(name='Category A')
        self.session.add(a)
        b = Category(name='Category B', category_id=1)
        self.session.add(b)
        c = Category(name='Category C', category_id=2)
        self.session.add(c)

        models = self.session.query(Category).filter(Category.id == 2).include(
            [Category.category, Category.categories]).first()
        self.assertTrue(len(models) == 3)

        self.assertTrue(isinstance(models[0], Category))
        self.assertTrue(models[0].id == 2)

        self.assertTrue(isinstance(models[1], Category))
        self.assertTrue(models[1].id == 1)

        self.assertTrue(isinstance(models[2], Category))
        self.assertTrue(models[2].id == 3)

    def test_include_ambiguous_join_conditions(self):
        """Test including a model when a join can be made multiple ways."""
        a = Category(name='Category A')
        self.session.add(a)
        b = Category(name='Category B', category_id=1)
        self.session.add(b)
        p = Product(primary_category_id=1, secondary_category_id=2, name='Tst')
        self.session.add(p)

        models = self.session.query(Product).include([
            Product.primary_category, Product.secondary_category]).first()
        self.assertTrue(isinstance(models[1], Category))
        self.assertTrue(isinstance(models[2], Category))

    def test_include_no_mappers(self):
        """Test including an empty set of relationships."""
        models = self.session.query(Person).include([]).first()
        self.assertTrue(isinstance(models, Person))
