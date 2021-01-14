"""Base marshmallow-jsonapi test case module."""
from marshmallow_jsonapi import fields, Schema

from tests.unit import UnitTestCase


def dasherize(text):
    """Replace underscores with hyphens."""
    return text.replace('_', '-')


class Person(Schema):
    id = fields.Integer()
    name = fields.String()
    kids_name = fields.String(attribute='kid_name')
    age = fields.Integer()
    birth_date = fields.Date()
    updated_at = fields.DateTime()
    student = fields.Relationship(schema='Student')

    class Meta:
        inflect = dasherize
        type_ = 'people'


class Student(Schema):
    id = fields.Integer()
    school = fields.Relationship(
        schema='School', include_resource_linkage=True, type_='schools')
    person = fields.Relationship(
        schema='Person', include_resource_linkage=True, type_='people')

    class Meta:
        inflect = dasherize
        type_ = 'students'


class School(Schema):
    id = fields.Integer()
    title = fields.String(attribute='name')
    students = fields.Relationship(schema='Student')

    class Meta:
        inflect = dasherize
        type_ = 'schools'


class Category(Schema):
    id = fields.Integer()
    name = fields.String()
    category = fields.Relationship(schema='Category')
    categories = fields.Relationship(schema='Category')

    class Meta:
        inflect = dasherize
        type_ = 'categories'


class BaseMarshmallowJSONAPITestCase(UnitTestCase):
    pass
