"""SQLAlchemy model driver module."""
from datetime import date

from jsonapi_query.drivers.model import SQLAlchemyDriver
from tests.sqlalchemy import (
    BaseSQLAlchemyTestCase, Person, School, Student, Category)


class SQLAlchemyDriverTestCase(BaseSQLAlchemyTestCase):
    """Test converting attribute paths and adding join conditions."""

    def test_is_foreign_key(self):
        """Test `is_foreign_key` property."""
        column = SQLAlchemyDriver('person_id', Student)
        self.assertTrue(column.is_foreign_key)

        column = SQLAlchemyDriver('id', Student)
        self.assertTrue(column.is_foreign_key is False)

    def test_is_mapper(self):
        """Test `is_mapper` property."""
        column = SQLAlchemyDriver('person', Student)
        self.assertTrue(column.is_mapper)

        column = SQLAlchemyDriver('id', Student)
        self.assertTrue(column.is_mapper is False)

    def test_is_primary_key(self):
        """Test `is_primary_key` property."""
        column = SQLAlchemyDriver('id', Student)
        self.assertTrue(column.is_primary_key)

        column = SQLAlchemyDriver('person', Student)
        self.assertTrue(column.is_primary_key is False)

    def test_python_type(self):
        """Test `python_type` property."""
        column = SQLAlchemyDriver('id', Person)
        self.assertTrue(column.python_type == int)

        column = SQLAlchemyDriver('name', Person)
        self.assertTrue(column.python_type == str)

        column = SQLAlchemyDriver('birth_date', Person)
        self.assertTrue(column.python_type == date)

        column = SQLAlchemyDriver('person_id', Student)
        self.assertTrue(column.python_type == int)

    def test_related_class(self):
        """Test `related_class` property."""
        column = SQLAlchemyDriver('school', Student)
        self.assertTrue(column.related_class == School)

        column = SQLAlchemyDriver('person', Student)
        self.assertTrue(column.related_class == Person)

    def test_is_enum(self):
        """Test `is_enum` property."""
        column = SQLAlchemyDriver('status', Person)
        self.assertTrue(column.is_enum)

        column = SQLAlchemyDriver('id', Person)
        self.assertTrue(column.is_enum is False)

    def test_join(self):
        """Test `join` property."""
        column = SQLAlchemyDriver('person', Student)
        self.assertTrue(column.join is Student.person)

        column = SQLAlchemyDriver('category', Category)
        self.assertTrue(column.join is Category.categories)

        column = SQLAlchemyDriver('categories', Category)
        self.assertTrue(column.join is Category.category)

    def test_factory(self):
        """Test `factory` classmethod."""
        components = SQLAlchemyDriver.factory('person.name', Student)
        self.assertTrue(components.column == Person.name)
        self.assertTrue(components.joins == [Student.person])
        self.assertTrue(components.selects == [Person])

    def test_factory_default(self):
        """Test `factory` classmethod default attribute."""
        components = SQLAlchemyDriver.factory('person', Student, 'status')
        self.assertTrue(components.column == Person.status)
        self.assertTrue(components.joins == [Student.person])
        self.assertTrue(components.selects == [Person])

    def test_missing_column(self):
        """Test getting unknown column."""
        try:
            SQLAlchemyDriver('unknown', Person)
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
