from sqlalchemy.orm import Query

from jsonapiquery.drivers import DriverModelSQLAlchemy, DriverSchemaMarshmallow
from jsonapiquery.database.sqlalchemy import QueryMixin
from jsonapiquery.types import *
from tests.marshmallow_jsonapi import Category as CategorySchema
from tests.sqlalchemy import *

import jsonapiquery


class SerializationTestCase(BaseSQLAlchemyTestCase):

    def setUp(self):
        """Set the query class and create a set of rows to test against."""
        super().setUp()

        class BaseQuery(QueryMixin, Query):
            pass
        self.session = sessionmaker(bind=self.engine, query_cls=BaseQuery)()
        self.session.begin_nested()

    def make_include(self, relationships, drivers):
        include = Include('include', relationships)
        for driver in drivers:
            include = driver.parse(include)
        return include

    def make_category_structure(self):
        category1 = Category(name='parent')
        self.session.add(category1)

        category2 = Category(name='child', category=category1)
        self.session.add(category2)
        self.session.commit()

        drivers = [
            DriverSchemaMarshmallow(CategorySchema()),
            DriverModelSQLAlchemy(Category)]
        return drivers, category1, category2

    def test_serialize_one_to_many_relationship(self):
        drivers, category1, category2 = self.make_category_structure()

        include = self.make_include(['category', 'categories'], drivers)
        result = jsonapiquery.serialize_includes([include], [category2])
        self.assertTrue(result == [
            {'type': 'categories', 'attributes': {'name': 'parent'}, 'id': 1},
            {'type': 'categories', 'attributes': {'name': 'child'}, 'id': 2}
        ])

    def test_serialize_null_one_to_many_relationship(self):
        drivers, category1, category2 = self.make_category_structure()

        include = self.make_include(['category', 'categories'], drivers)
        result = jsonapiquery.serialize_includes([include], [category1])
        self.assertTrue(result == [])

    def test_serialize_many_to_many_relationship(self):
        drivers, category1, category2 = self.make_category_structure()

        include = self.make_include(['categories', 'category'], drivers)
        result = jsonapiquery.serialize_includes([include], [category1])
        self.assertTrue(result == [
            {'type': 'categories', 'attributes': {'name': 'child'}, 'id': 2},
            {'type': 'categories', 'attributes': {'name': 'parent'}, 'id': 1}
        ])

    def test_serialize_null_many_to_many_relationship(self):
        drivers, category1, category2 = self.make_category_structure()

        include = self.make_include(['categories', 'category'], drivers)
        result = jsonapiquery.serialize_includes([include], [category2])
        self.assertTrue(result == [])
