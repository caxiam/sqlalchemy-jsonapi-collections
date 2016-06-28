from datetime import date

from jsonapi_query.translation.view.marshmallow_jsonapi import (
    MarshmallowJSONAPIDriver)
from tests.marshmallow_jsonapi import (
    BaseMarshmallowJSONAPITestCase, Person, School, Student)


class MarshmallowJSONAPIViewTestCase(BaseMarshmallowJSONAPITestCase):

    def setUp(self):
        super().setUp()
        self.driver = MarshmallowJSONAPIDriver(Person())

    def test_initialize_path(self):
        """Test initializing a path."""
        self.driver.initialize_path('student.school.title')

        self.assertTrue(len(self.driver.fields) == 3)
        self.assertTrue(
            self.driver.field_names == ['student', 'school', 'name'])
        self.assertTrue(self.driver.schemas == [Student, School])

    def test_initialize_dasherized_path(self):
        """Test initializing a dasherized path."""
        self.driver.initialize_path('birth-date')

        self.assertTrue(
            self.driver.fields == [Person._declared_fields['birth_date']])
        self.assertTrue(self.driver.field_names == ['birth_date'])
        self.assertTrue(self.driver.schemas == [])

    def test_initializing_multiple_paths(self):
        """Test initializing multiple paths."""
        self.driver.initialize_path('student.school.title')
        self.driver.initialize_path('birth-date')

        self.assertTrue(
            self.driver.fields == [Person._declared_fields['birth_date']])
        self.assertTrue(self.driver.field_names == ['birth_date'])
        self.assertTrue(self.driver.schemas == [])

    def test_get_model_path(self):
        """Test getting a model-safe path."""
        self.driver.initialize_path('student.school.title')

        path = self.driver.get_model_path()
        self.assertTrue(path == 'student.school.name')

    def test_deserialize_values(self):
        """Test deserializing a list of values."""
        self.driver.initialize_path('birth-date')
        values = self.driver.deserialize_values(['2014-01-01'])
        self.assertTrue(values == [date(2014, 1, 1)])

        self.driver.initialize_path('student.school.title')
        values = self.driver.deserialize_values(['PS #118'])
        self.assertTrue(values == ['PS #118'])

    def test_deserialize_value(self):
        """Test deserializing a single value."""
        self.driver.initialize_path('birth-date')
        field = self.driver.fields[-1]

        value = self.driver.deserialize_value(field, '2014-01-01')
        self.assertTrue(value == date(2014, 1, 1))
