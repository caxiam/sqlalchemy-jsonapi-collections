"""."""
from datetime import date

from jsonapi_query.translation.view.marshmallow_jsonapi import (
    MarshmallowJSONAPIDriver)
from tests.marshmallow_jsonapi import BaseMarshmallowJSONAPITestCase, Person


class MarshmallowJSONAPIViewTestCase(BaseMarshmallowJSONAPITestCase):
    """."""

    def setUp(self):
        super().setUp()
        self.driver = MarshmallowJSONAPIDriver(Person())

    def test_replace_path(self):
        """Test replacing attribute path with model safe names."""
        path = self.driver.replace_path('student.school.title')
        self.assertTrue(path == 'student.school.name')

    def test_replace_dasherized_path(self):
        """Test replacing dasherized path with underscored model attribute."""
        path = self.driver.replace_path('birth-date')
        self.assertTrue(path == 'birth_date')

    def test_deserialize_from_path(self):
        """Test deserializing a list of values from a string path."""
        values = self.driver.deserialize_from_path('student.school.id', ['1'])
        self.assertTrue(values == [1])

    def test_deserialize_dasherized_path(self):
        """Test deserializing from a dasherized path."""
        values = self.driver.deserialize_from_path(
            'birth-date', ['2014-01-01'])
        self.assertTrue(values == [date(2014, 1, 1)])

    def test_deserialize_values(self):
        """Test deserializing a list of values."""
        values = self.driver.deserialize_values(
            Person._declared_fields['age'], ['12'])
        self.assertTrue(values == [12])

    def test_deserialize_value(self):
        """Test deserializing a single value."""
        value = self.driver.deserialize_value(
            Person._declared_fields['age'], '12')
        self.assertTrue(value == 12)
