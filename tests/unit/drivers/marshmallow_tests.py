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

        assert old_type.source == new_type.source
        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Relationship)
        assert old_type.attribute != new_type.attribute
        assert isinstance(new_type.attribute, Attribute)
        assert old_type.value == new_type.value

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

        assert old_type.source == new_type.source
        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Relationship)
        assert old_type.attribute != new_type.attribute
        assert isinstance(new_type.attribute, Attribute)
        assert old_type.direction == new_type.direction

    def test_relationship(self):
        """Test Relationship type."""
        field = Person().declared_fields['student']
        relationship = Relationship('student', Person())

        assert isinstance(relationship.type, Student)
        assert relationship.model_attribute == 'student'
        assert isinstance(relationship.field, field.__class__)

    def test_attribute(self):
        """Test Attribute type."""
        field = Person().declared_fields['kids_name']
        attribute = Attribute('kids_name', Person())

        assert attribute.model_attribute == 'name'
        assert isinstance(attribute.field, field.__class__)

    def test_attribute_deserialize(self):
        """Test Attribute value deserialization."""
        field = Attribute('name', Person())
        value = field.deserialize_value('Test')
        assert value == 'Test'

        field = Attribute('age', Person())
        value = field.deserialize_value('10')
        assert value == 10

        field = Attribute('birth-date', Person())
        value = field.deserialize_value('2018-01-01')
        assert value == date(2018, 1, 1)

        field = Attribute('updated-at', Person())
        value = field.deserialize_value('2018-01-01T00:00:00.000000')
        assert value == datetime(2018, 1, 1, 0, 0, 0, 0)
