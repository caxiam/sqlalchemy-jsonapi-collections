"""SQLAlchemy model driver module."""
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
        column, models, joins = self.driver.parse_path('name')

        self.assertTrue(column == Person.name)
        self.assertTrue(models == [])
        self.assertTrue(joins == [])

    def test_nested_attribute_column(self):
        """Test getting a related attribute column."""
        column, models, joins = self.driver.parse_path('student.school_id')

        self.assertTrue(column == Student.school_id)
        self.assertTrue(models == [Student])
        self.assertTrue(joins == ['student'])

    def test_deeply_nested_attribute_column(self):
        """Test getting a deeply related attribute column."""
        column, models, joins = self.driver.parse_path('student.school.name')

        self.assertTrue(column == School.name)
        self.assertTrue(models == [Student, School])
        self.assertTrue(joins == ['student', 'school'])

    def test_missing_attribute_column(self):
        """Test getting a missing attribute's default column."""
        column, models, joins = self.driver.parse_path('student')

        self.assertTrue(column == Student.id)
        self.assertTrue(models == [Student])
        self.assertTrue(joins == ['student'])

    def test_unknown_attribute(self):
        """Test getting an attribute that doesn't exist on the object."""
        try:
            self.driver.parse_path('height')
            self.assertTrue(False)
        except AttributeError:
            self.assertTrue(True)

    def test_column_as_relationship(self):
        """Test getting a relationshiup that doesn't exist on the model."""
        try:
            self.driver.parse_path('age.id')
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)