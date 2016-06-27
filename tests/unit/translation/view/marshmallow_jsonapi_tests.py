"""."""
from src.translation.view.marshmallow_jsonapi import MarshmallowJSONAPIDriver
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

    def test_deserialize_from_path(self):
        """Test deserializing a list of values from a string path."""
        values = self.driver.deserialize_from_path('student.school.id', ['1'])
        self.assertTrue(values == [1])

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
