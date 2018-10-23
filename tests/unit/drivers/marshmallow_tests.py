from datetime import date, datetime

from jsonapiquery.drivers.schema import DriverSchemaMarshmallow
from jsonapiquery.drivers.schema.marshmallow import Relationship, Attribute
from jsonapiquery.types import *
from tests.marshmallow_jsonapi import *


class DriverSchemaMarshmallowTestCase(BaseMarshmallowJSONAPITestCase):

    @property
    def driver(self):
        return DriverSchemaMarshmallow(Person())

    def test_parse_filter(self):
        """Test parse Filter type."""
        old_type = Filter(
            'filter[student.school.title]', ['student', 'school'], 'title',
            'test')
        new_type = self.driver.parse(old_type)

        assert new_type.source == old_type
        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Relationship)
        assert old_type.attribute != new_type.attribute
        assert isinstance(new_type.attribute, Attribute)
        assert new_type.value == ('eq', [old_type.value])

    def test_parse_include(self):
        """Test parse Include type."""
        old_type = Include('include', ['student', 'school'])
        new_type = self.driver.parse(old_type)

        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Relationship)

    def test_parse_sort(self):
        """Test parse Sort type."""
        old_type = Sort('sort', ['student', 'school'], 'title', '+')
        new_type = self.driver.parse(old_type)

        assert new_type.source == old_type
        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Relationship)
        assert old_type.attribute != new_type.attribute
        assert isinstance(new_type.attribute, Attribute)
        assert old_type.direction == new_type.direction

    def test_relationship(self):
        """Test Relationship type."""
        field = Person().declared_fields['student']
        relationship = Relationship('student', Person(), None)

        assert isinstance(relationship.type, Student)
        assert relationship.super_attribute == 'student'
        assert isinstance(relationship.field, field.__class__)

    def test_attribute(self):
        """Test Attribute type."""
        field = Person().declared_fields['kids_name']
        attribute = Attribute('kids_name', Person(), None)

        assert attribute.super_attribute == 'name'
        assert isinstance(attribute.field, field.__class__)

    def test_attribute_deserialize(self):
        """Test Attribute value deserialization."""
        field = Attribute('name', Person(), None)
        value = field.deserialize_value('Test')
        assert value == ('eq', ['Test'])

        field = Attribute('age', Person(), None)
        value = field.deserialize_value('10')
        assert value == ('eq', [10])

        field = Attribute('birth-date', Person(), None)
        value = field.deserialize_value('2018-01-01')
        assert value == ('eq', [date(2018, 1, 1)])

        field = Attribute('updated-at', Person(), None)
        value = field.deserialize_value('eq:2018-01-01T00:00:00.000000')
        assert value == ('eq', [datetime(2018, 1, 1, 0, 0, 0, 0)])
