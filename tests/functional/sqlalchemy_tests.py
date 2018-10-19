"""End to end query testing."""
from datetime import datetime

from sqlalchemy.orm import Query, sessionmaker, joinedload

from jsonapiquery.database.sqlalchemy import group_and_remove, QueryMixin
from tests.marshmallow_jsonapi import Person as PersonSchema, Student as StudentSchema
from tests.sqlalchemy import *


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

    def test(self):
        from jsonapiquery.types import Include
        from jsonapiquery.drivers.model.sqlalchemy import Mapper

        include = Include('', [Mapper('student', Person), Mapper('school', Student)])

        query = self.session.query(Person).include(include)
        print(query)
        model = query.first()
        print(model.student.school)
        self.assertTrue(False)

    # def test_query_filter(self):
    #     """Test filtering a query."""
    #     queries = []
    #     jquery = SQLAQuery({'filter[age]': 'lt:10'}, self.model, self.view)
    #     filters, errors = jquery.make_filter_fields()
    #     for filter in filters:
    #         query, driver = jquery.make_query_from_fields(filter.fields)
    #         queries.append((query.column, filter.strategy, filter.values, query.joins))

    #     models = self.session.query(Person).apply_filters(queries).all()
    #     self.assertTrue(len(models) == 1)
    #     self.assertTrue(models[0].age == 5)

    # def test_query_complex_filter(self):
    #     """Test filtering a query with complex requirements."""
    #     params = {'filter[student.school.title]': 'eq:School'}
    #     jquery = SQLAQuery(params, self.model, self.view)

    #     queries = []
    #     filters, errors = jquery.make_filter_fields()
    #     for filter in filters:
    #         query, driver = jquery.make_query_from_fields(filter.fields)
    #         queries.append((query.column, filter.strategy, filter.values, query.joins))

    #     models = self.session.query(Person).apply_filters(queries).all()
    #     self.assertTrue(len(models) == 1)
    #     self.assertTrue(models[0].name == 'Fred')

    # def test_query_sort(self):
    #     """Test sorting a query."""
    #     params = {'sort': '-age'}
    #     jquery = SQLAQuery(params, self.model, self.view)

    #     queries = []
    #     sorts, errors = jquery.make_sort_fields()
    #     for sort in sorts:
    #         query, driver = jquery.make_query_from_fields(sort.fields)
    #         queries.append((query.column, sort.direction, query.joins))

    #     models = self.session.query(Person).apply_sorts(queries).all()
    #     self.assertTrue(len(models) == 2)
    #     self.assertTrue(models[1].name == 'Fred')
    #     self.assertTrue(models[0].name == 'Carl')

    # def test_query_complex_sort(self):
    #     """Test sorting a query with complex requirements."""
    #     params = {'sort': '-student.school.title'}
    #     jquery = SQLAQuery(params, self.model, self.view)

    #     queries = []
    #     sorts, errors = jquery.make_sort_fields()
    #     for sort in sorts:
    #         query, driver = jquery.make_query_from_fields(sort.fields)
    #         queries.append((query.column, sort.direction, query.joins))

    #     models = self.session.query(Person).apply_sorts(queries).all()
    #     self.assertTrue(len(models) == 2)
    #     self.assertTrue(models[0].name == 'Fred')
    #     self.assertTrue(models[1].name == 'Carl')

    # def test_paginate_query_by_limit(self):
    #     """Test paginating a query by the limit strategy."""
    #     params = {'page[limit]': 1, 'page[offset]': 1}
    #     jquery = SQLAQuery(params, self.model, self.view)

    #     models = self.session.query(Person).apply_paginators(jquery.paginators).all()
    #     self.assertTrue(len(models) == 1)
    #     self.assertTrue(models[0].name == 'Carl')

    # def test_paginate_query_by_page(self):
    #     """Test paginating a query by the number strategy."""
    #     params = {'page[size]': 1, 'page[number]': 2}
    #     jquery = SQLAQuery(params, self.model, self.view)

    #     models = self.session.query(Person).apply_paginators(jquery.paginators).all()
    #     self.assertTrue(len(models) == 1)
    #     self.assertTrue(models[0].name == 'Carl')

    # def test_query_complex_include(self):
    #     """Test including a query with complex requirements."""
    #     params = {'include': 'student.school'}
    #     jquery = SQLAQuery(params, self.model, self.view)

    #     selects = []
    #     mappers = []
    #     schemas = []
    #     includes, errors = jquery.make_include_fields()
    #     for include in includes:
    #         query, driver = jquery.make_query_from_fields(include)
    #         mappers.extend(query.joins)
    #         selects.extend(query.selects)
    #         schemas.extend(include.schemas)

    #     mappers = list(set(mappers))
    #     selects = list(set(selects))
    #     schemas = list(set(schemas))

    #     items = self.session.query(Person).filter_by(id=1).include(mappers).all()
    #     self.assertTrue(len(items[0]) == 3)

    #     items = group_and_remove(items, [Person] + selects)[1:]
    #     included = []
    #     for position, columns in enumerate(items):
    #         schema = schemas[position]
    #         included.extend(schema.dump(columns, many=True).data['data'])

    #     self.assertTrue(len(schemas) == 2)
    #     self.assertTrue(len(selects) == 2)
    #     self.assertTrue(len(items) == 2)

    # def test_query_multiple_include(self):
    #     """Test including multiple different types."""
    #     params = {'include': 'person,school'}
    #     jquery = SQLAQuery(params, Student, StudentSchema)

    #     selects = []
    #     mappers = []
    #     schemas = []
    #     includes, errors = jquery.make_include_fields()
    #     for include in includes:
    #         query, driver = jquery.make_query_from_fields(include)
    #         mappers.extend(query.joins)
    #         selects.extend(query.selects)
    #         schemas.extend(include.schemas)

    #     items = self.session.query(Student).filter_by(id=1).include(mappers).all()
    #     self.assertTrue(len(items) == 1)
    #     self.assertTrue(len(items[0]) == 3)

    #     items = group_and_remove(items, [Student] + selects)[1:]
    #     included = []
    #     for position, columns in enumerate(items):
    #         schema = schemas[position]
    #         included.extend(schema.dump(columns, many=True).data['data'])

    #     self.assertTrue(len(schemas) == 2)
    #     self.assertTrue(len(selects) == 2)
    #     self.assertTrue(len(items) == 2)
    #     self.assertTrue(len(items[0]) == 1)
    #     self.assertTrue(len(items[1]) == 1)
    #     self.assertTrue(len(included) == 2)

    # def test_query_filter_invalid_field(self):
    #     """Test filtering a query with an invalid field."""
    #     jquery = SQLAQuery({'filter[invalid]': 'lt:10'}, self.model, self.view)
    #     filters, errors = jquery.make_filter_fields()
    #     self.assertTrue(len(errors) == 1)
    #     self.assertTrue(errors[0]['source']['parameter'] == 'filter[invalid]')

    # def test_query_filter_invalid_relationship(self):
    #     """Test filtering a query with an invalid relationship field."""
    #     jquery = SQLAQuery({'filter[age.id]': 'lt:10'}, self.model, self.view)
    #     filters, errors = jquery.make_filter_fields()
    #     self.assertTrue(len(errors) == 1)
    #     self.assertTrue(errors[0]['source']['parameter'] == 'filter[age.id]')

    # def test_query_filter_invalid_field_value(self):
    #     """Test filtering a query with an invalid field value."""
    #     jquery = SQLAQuery({'filter[age]': '2014-10-10'}, self.model, self.view)
    #     filters, errors = jquery.make_filter_fields()
    #     self.assertTrue(len(errors) == 1)
    #     self.assertTrue(errors[0]['source']['parameter'] == 'filter[age]')

    # def test_query_sort_invalid_field(self):
    #     """Test sorting a query with an invalid field."""
    #     jquery = SQLAQuery({'sort': 'invalid'}, self.model, self.view)
    #     filters, errors = jquery.make_sort_fields()
    #     self.assertTrue(len(errors) == 1)
    #     self.assertTrue(errors[0]['source']['parameter'] == 'sort')

    # def test_query_sort_multiple_invalid_field(self):
    #     """Test sorting a query with multiple invalid fields."""
    #     jquery = SQLAQuery({'sort': 'invalid,fake'}, self.model, self.view)
    #     filters, errors = jquery.make_sort_fields()
    #     self.assertTrue(len(errors) == 2)
    #     self.assertTrue(errors[0]['source']['parameter'] == 'sort')
    #     self.assertTrue(errors[1]['source']['parameter'] == 'sort')

    # def test_query_include_invalid_field(self):
    #     """Test including a query with an invalid field."""
    #     jquery = SQLAQuery({'include': 'invalid'}, self.model, self.view)
    #     filters, errors = jquery.make_include_fields()
    #     self.assertTrue(len(errors) == 1)
    #     self.assertTrue(errors[0]['source']['parameter'] == 'include')
