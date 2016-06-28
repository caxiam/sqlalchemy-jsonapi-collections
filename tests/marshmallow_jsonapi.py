"""Base marshmallow-jsonapi test case module."""
from marshmallow import class_registry
from marshmallow.base import SchemaABC
from marshmallow.compat import basestring
from marshmallow_jsonapi import fields, Schema

from tests.unit import UnitTestCase


def dasherize(text):
    """Replace underscores with hyphens."""
    return text.replace('_', '-')


class Relationship(fields.Relationship):

    def __init__(self, related_schema=None, **kwargs):
        self.related_schema = related_schema
        self.__schema = None
        super().__init__(**kwargs)

    @property
    def schema(self):
        if isinstance(self.related_schema, SchemaABC):
            self.__schema = self.related_schema
        elif (isinstance(self.related_schema, type) and
                issubclass(self.related_schema, SchemaABC)):
            self.__schema = self.related_schema
        elif isinstance(self.related_schema, basestring):
            if self.related_schema == 'self':
                parent_class = self.parent.__class__
                self.__schema = parent_class
            else:
                schema_class = class_registry.get_class(self.related_schema)
                self.__schema = schema_class
        return self.__schema


class Person(Schema):
    id = fields.Integer()
    name = fields.String()
    age = fields.Integer()
    birth_date = fields.Date()
    updated_at = fields.DateTime()
    student = Relationship('Student')

    class Meta:
        inflect = dasherize
        type_ = 'people'


class Student(Schema):
    id = fields.Integer()
    school = Relationship(
        'School', include_resource_linkage=True, type_='schools')
    person = Relationship(
        'Person', include_resource_linkage=True, type_='people')

    class Meta:
        inflect = dasherize
        type_ = 'students'


class School(Schema):
    id = fields.Integer()
    title = fields.String(attribute='name')
    students = Relationship('Student')

    class Meta:
        inflect = dasherize
        type_ = 'schools'


class BaseMarshmallowJSONAPITestCase(UnitTestCase):
    pass
