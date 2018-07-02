"""SQLAlchemy model driver module."""
from datetime import date

from jsonapiquery.drivers.model import DriverModelSQLAlchemy
from jsonapiquery.drivers.model.sqlalchemy import Mapper, Column
from jsonapiquery.drivers.schema.marshmallow import Relationship, Attribute
from jsonapiquery.types import *
from tests.sqlalchemy import Person, Student, BaseSQLAlchemyTestCase
from tests.marshmallow_jsonapi import (
    Person as PersonSchema, Student as StudentSchema, School as SchoolSchema)


class DriverModelSQLAlchemyTestCase(BaseSQLAlchemyTestCase):

    @property
    def driver(self):
        return DriverModelSQLAlchemy(Person)

    def test_parse_filter(self):
        """Test parse Filter type."""
        old_type = Filter(
            'filter[student.school.title]', [
                Relationship('student', PersonSchema()),
                Relationship('school', StudentSchema())],
            Attribute('title', SchoolSchema()), 'test')
        new_type = self.driver.parse(old_type)
        
        assert old_type.source == new_type.source
        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Mapper)
        assert old_type.attribute != new_type.attribute
        assert isinstance(new_type.attribute, Column)
        assert old_type.value == new_type.value

    def test_parse_include(self):
        """Test parse Include type."""
        old_type = Include('include', [
            Relationship('student', PersonSchema()),
            Relationship('school', StudentSchema())])
        new_type = self.driver.parse(old_type)

        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Mapper)

    def test_parse_sort(self):
        """Test parse Sort type."""
        old_type = Sort('sort', [
            Relationship('student', PersonSchema()),
            Relationship('school', StudentSchema())],
            Attribute('title', SchoolSchema()), '+')
        new_type = self.driver.parse(old_type)

        assert old_type.source == new_type.source
        assert old_type.relationships != new_type.relationships
        assert isinstance(new_type.relationships[0], Mapper)
        assert old_type.attribute != new_type.attribute
        assert isinstance(new_type.attribute, Column)
        assert old_type.direction == new_type.direction

    def test_mapper(self):
        mapper = Mapper('student', Person)

        assert mapper.attribute is Person.student
        assert mapper.type == Student

    def test_column(self):
        column = Column('image_id', Person)

        assert column.is_enum is False
        assert column.is_foreign_key is True
        assert column.is_primary_key is True
