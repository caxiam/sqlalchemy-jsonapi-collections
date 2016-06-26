"""."""
from src.translation.model.sqlalchemy import SQLAlchemyModelDriver
from tests.sqlalchemy import BaseSQLAlchemyTestCase, Person, School, Student


class SQLAlchemyModelTestCase(BaseSQLAlchemyTestCase):
    """Test converting attribute paths and adding join conditions."""

    def setUp(self):
        """Ran before every test."""
        super().setUp()
        # Create a row to initiate the mappers.
        self.session.add(Person(name='Fred'))
        self.driver = SQLAlchemyModelDriver(Person)

    def test_attribute_column(self):
        """Test getting an attribute column."""
        sort = ('name', '+')
        column, _, joins = self.driver.parse_sort(*sort)

        self.assertTrue(column == Person.name)
        self.assertTrue(joins == [])

    def test_nested_attribute_column(self):
        """Test getting a related attribute column."""
        sort = ('student.school_id', '+')
        column, _, joins = self.driver.parse_sort(*sort)

        self.assertTrue(column == Student.school_id)
        self.assertTrue(joins == ['student'])

    def test_deeply_nested_attribute_column(self):
        """Test getting a deeply related attribute column."""
        sort = ('student.school.name', '+')
        column, _, joins = self.driver.parse_sort(*sort)

        self.assertTrue(column == School.name)
        self.assertTrue(joins == ['student', 'school'])

    def test_missing_attribute_column(self):
        """Test getting a missing attribute's default column."""
        sort = ('student', '+')
        column, _, joins = self.driver.parse_sort(*sort)

        self.assertTrue(column == Student.id)
        self.assertTrue(joins == ['student'])
