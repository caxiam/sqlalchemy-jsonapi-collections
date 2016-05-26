# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import case, orm
from marshmallow import class_registry, validate
from marshmallow.base import SchemaABC
from marshmallow_jsonapi import fields, Schema

from tests.database import db, save


person_company = db.Table(
    'person_company',
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'))
)


class PersonModel(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    is_employed = db.Column(db.Boolean)
    gender = db.Column(db.Enum('male', 'female', name='person_gender'))
    rate = db.Column(db.Numeric(12, 2))
    employed_integer = orm.column_property(
        case([(is_employed.is_(True), 1)], else_=0))
    created_at = db.Column(db.DateTime, default=datetime.now())

    companies = db.relationship(
        'CompanyModel', secondary=person_company, backref='persons')
    employee = db.relationship(
        'EmployeeModel', uselist=False, back_populates='person')

    @classmethod
    def mock(cls, **kwargs):
        data = {
            'name': kwargs.pop('name', 'Test'),
            'age': kwargs.pop('age', 10),
            'is_employed': kwargs.pop('is_employed', True),
            'companies': kwargs.pop('companies', []),
            'gender': kwargs.pop('gender', 'male'),
            'rate': kwargs.pop('rate', '1.00')
        }
        model = cls(**data)
        save(model)
        return model


class EmployeeModel(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer(), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    name = db.Column(db.String)
    months_of_service = db.Column(db.Integer)
    is_manager = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.now())

    person = db.relationship('PersonModel', back_populates='employee')

    @classmethod
    def mock(cls, **kwargs):
        data = {
            'name': kwargs.pop('name', 'Test'),
            'months_of_service': kwargs.pop('months_of_service', 10),
            'is_manager': kwargs.pop('is_manager', True),
            'person_id': kwargs.pop('person_id', None)
        }
        model = cls(**data)
        save(model)
        return model


class CompanyModel(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String)
    year_established = db.Column(db.Integer)
    is_profitable = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.now())

    @classmethod
    def mock(cls, **kwargs):
        data = {
            'name': kwargs.pop('name', 'Test'),
            'year_established': kwargs.pop('year_established', 10),
            'is_profitable': kwargs.pop('is_profitable', True)
        }
        model = cls(**data)
        save(model)
        return model


class SchemaRelationship(fields.Relationship):

    def __init__(self, dump_to=None, related_schema=None, **kwargs):
        self.related_schema = related_schema
        self.__schema = None
        super(SchemaRelationship, self).__init__(**kwargs)

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


class EmployeeSchema(Schema):
    id = fields.String()
    name = fields.String()
    months_of_service = fields.Integer()
    is_manager = fields.Boolean()
    created_at = fields.DateTime()

    person = SchemaRelationship(
        include_data=True, type_='people', related_schema='PersonSchema')
    person_id = SchemaRelationship(include_data=True, type_='people')

    class Meta:
        model = EmployeeModel
        type_ = 'employees'
        ordered = True


class CompanySchema(Schema):
    id = fields.String()
    name = fields.String()
    year_established = fields.Integer()
    is_profitable = fields.Boolean()
    created_at = fields.DateTime()

    class Meta:
        model = CompanyModel
        type_ = 'companies'
        ordered = True


class PersonSchema(Schema):
    id = fields.String()
    name = fields.String()
    age = fields.Integer()
    is_employed = fields.Boolean()
    gender = fields.String(validate=validate.OneOf(['male', 'female']))
    rate = fields.Decimal(as_string=True, places=2)
    employed_integer = fields.Integer()
    created_at = fields.DateTime(format='%Y-%m-%d')

    companies = SchemaRelationship(
        include_data=True, type_='companies', many=True,
        related_schema=CompanySchema)
    employee = SchemaRelationship(
        include_data=True, type_='employees', many=False,
        related_schema=EmployeeSchema)
    employee_id = SchemaRelationship(many=False, related_schema=EmployeeSchema)

    class Meta:
        model = PersonModel
        type_ = 'people'
        ordered = True
