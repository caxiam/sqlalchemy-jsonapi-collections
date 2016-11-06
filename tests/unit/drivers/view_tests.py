from datetime import date

from jsonapiquery.drivers.view import MarshmallowDriver
from tests.marshmallow_jsonapi import *


class MarshmallowJSONAPIViewTestCase(BaseMarshmallowJSONAPITestCase):

    def test_column_name(self):
        """Test `column_name` property."""
        field = MarshmallowDriver('name', Person)
        self.assertTrue(field.column_name == 'name')

        field = MarshmallowDriver('kids_name', Person)
        self.assertTrue(field.column_name == 'name')

    def test_related_class(self):
        """Test `related_class` property."""
        field = MarshmallowDriver('student', Person)
        self.assertTrue(isinstance(field.related_class, Student))

    def test_is_relationship(self):
        """Test `is_relationship` property."""
        field = MarshmallowDriver('name', Person)
        self.assertTrue(not field.is_relationship)

        field = MarshmallowDriver('student', Person)
        self.assertTrue(field.is_relationship)

    def test_deserialize_values(self):
        """Test deserializing a list of values."""
        field = MarshmallowDriver('birth_date', Person)
        values = field.deserialize_values(['2014-01-01'])
        self.assertTrue(values == [date(2014, 1, 1)])

        field = MarshmallowDriver('age', Person)
        values = field.deserialize_values(['10', 12, '00991'])
        self.assertTrue(values == [10, 12, 991])

    def test_deserialize_value(self):
        """Test deserializing a value."""
        field = MarshmallowDriver('birth_date', Person)
        value = field.deserialize_value('2014-01-01')
        self.assertTrue(value == date(2014, 1, 1))

    def test_make_from_path(self):
        """Test returning a set of fields from a dot-seperated path."""
        fields = MarshmallowDriver.make_from_path('student.school.id', Person)
        self.assertTrue(len(fields) == 3)
        self.assertTrue(fields[0].field == Person._declared_fields['student'])
        self.assertTrue(fields[1].field == Student._declared_fields['school'])
        self.assertTrue(fields[2].field == School._declared_fields['id'])

    def test_make_from_dasherized_path(self):
        """Test returning a field from a dasherized input."""
        fields = MarshmallowDriver.make_from_path('birth-date', Person)
        self.assertTrue(len(fields) == 1)
        self.assertTrue(fields[0].field == Person._declared_fields['birth_date'])

    def test_send_to_path(self):
        """Test returning a dot-seperated column path."""
        fields = [
            MarshmallowDriver('person', Student),
            MarshmallowDriver('kids_name', Person)]
        path = MarshmallowDriver.send_to_path(fields)
        self.assertTrue(path == 'person.name')

    def test_invalid_field(self):
        """Test initializing an invalid field name."""
        try:
            MarshmallowDriver('unknown', Person)
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_invalid_relationship(self):
        """Test getting a related schema with an invalid relationship."""
        try:
            MarshmallowDriver('id', Person).related_class
        except AttributeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
