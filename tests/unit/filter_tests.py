# -*- coding: utf-8 -*-
from datetime import date

from jsonapi_collections import Resource
from jsonapi_collections.drivers.marshmallow import MarshmallowDriver
from jsonapi_collections.errors import JSONAPIError
from tests import UnitTestCase
from tests.mock import CompanyModel, EmployeeModel, PersonModel, PersonSchema


class FilterTestCase(UnitTestCase):

    def setUp(self):
        super(FilterTestCase, self).setUp()
        self.model = PersonModel
        self.query = PersonModel.query


class SQLAlchemyTestCase(FilterTestCase):
    """Test filtering with the `SQLAlchemy` driver."""

    def test_filter_string_field(self):
        """Test filtering by a string field."""
        PersonModel.mock(name='A PRODUCT Wildcard')

        parameters = {'filter[name]': 'prod'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_multiple_string_field(self):
        """Test filtering by multiple string fields."""
        PersonModel.mock(name='A PRODUCT Wildcard')

        parameters = {'filter[name]': 'prod,test,card'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_enum_field(self):
        """Test filtering by an enum field."""
        PersonModel.mock(gender='male')

        parameters = {'filter[gender]': 'male'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_enum_field_invalid_value(self):
        """Test filtering by an invalid enum value."""
        PersonModel.mock(gender='male')

        try:
            parameters = {'filter[gender]': 'mal'}
            Resource(self.model, parameters).filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[gender]')

    def test_filter_decimal_field(self):
        """Test filtering by a decimal field."""
        PersonModel.mock(rate='12.51')

        parameters = {'filter[rate]': '12.51'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_decimal_field_invalid_value(self):
        """Test filtering by an invalid decimal value."""
        PersonModel.mock(rate='12.51')

        try:
            parameters = {'filter[rate]': 'a'}
            Resource(self.model, parameters).filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'filter[rate]')

    def test_filter_boolean_field(self):
        """Test filtering by a boolean field."""
        PersonModel.mock(is_employed=True)

        parameters = {'filter[is_employed]': '1'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_datetime_field(self):
        """Test filtering by a datetime field."""
        PersonModel.mock()

        parameters = {'filter[created_at]': date.today().strftime('%Y-%m-%d')}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_integer_field(self):
        """Test filtering by an integer field."""
        PersonModel.mock(age=80)

        parameters = {'filter[age]': '80'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_computed_field(self):
        """Test filtering by a computed field."""
        PersonModel.mock(is_employed=True)

        parameters = {'filter[employed_integer]': '1'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_one_to_many_relationship(self):
        """Test filtering by a foreign key relationship field."""
        person = PersonModel.mock()
        EmployeeModel.mock(name="employee", person_id=person.id)

        parameters = {'filter[employee.name]': 'EMPLOYEE'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_many_to_many_relationship(self):
        """Test filtering by a many-to-many relationship field."""
        company = CompanyModel.mock(name="company")
        PersonModel.mock(companies=[company])

        parameters = {'filter[companies.name]': 'COMPANY'}
        query = Resource(self.model, parameters).filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_invalid_field_parameter(self):
        """Test filtering by an unknown field."""
        try:
            parameters = {'filter[xyz]': 'value'}
            Resource(self.model, parameters).filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'filter[xyz]')

    def test_filter_invalid_relationship_parameter(self):
        """Test filtering by an invalid relationship field."""
        try:
            parameters = {'filter[employee.xyz]': 'value'}
            Resource(self.model, parameters).filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[employee.xyz]')

    def test_filter_invalid_relationship(self):
        """Test filtering by an invalid relationship value."""
        try:
            parameters = {'filter[rate.name]': 'whatever'}
            Resource(self.model, parameters).filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[rate.name]')

    def test_filter_invalid_value_type(self):
        """Test filtering by an invalid field value."""
        try:
            parameters = {'filter[datetime]': 'notadate'}
            Resource(self.model, parameters).filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[datetime]')


class MarshmallowTestCase(FilterTestCase):
    """Test filtering with the `marshmallow` driver."""

    def test_filter_string_field(self):
        """Test filtering by a string field."""
        PersonModel.mock(name='A PRODUCT Wildcard')

        parameters = {'filter[name]': 'prod'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_multiple_string_field(self):
        """Test filtering by multiple string fields."""
        PersonModel.mock(name='A PRODUCT Wildcard')

        parameters = {'filter[name]': 'prod,test,card'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_enum_field(self):
        """Test filtering by an enum field."""
        PersonModel.mock(gender='male')

        parameters = {'filter[gender]': 'male'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_enum_field_invalid_value(self):
        """Test filtering by an invalid enum value."""
        PersonModel.mock(gender='male')

        try:
            parameters = {'filter[gender]': 'mal'}
            Resource(
                self.model, parameters, MarshmallowDriver, PersonSchema).\
                filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[gender]')

    def test_filter_decimal_field(self):
        """Test filtering by a decimal field."""
        PersonModel.mock(rate='12.51')

        parameters = {'filter[rate]': '12.51'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_decimal_field_invalid_value(self):
        """Test filtering by an invalid decimal value."""
        PersonModel.mock(rate='12.51')

        try:
            parameters = {'filter[rate]': 'a'}
            Resource(
                self.model, parameters, MarshmallowDriver, PersonSchema).\
                filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'filter[rate]')

    def test_filter_boolean_field(self):
        """Test filtering by a boolean field."""
        PersonModel.mock(is_employed=True)

        parameters = {'filter[is_employed]': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_datetime_field(self):
        """Test filtering by a datetime field."""
        PersonModel.mock()

        parameters = {'filter[created_at]': date.today().strftime('%Y-%m-%d')}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_integer_field(self):
        """Test filtering by an integer field."""
        PersonModel.mock(age=80)

        parameters = {'filter[age]': '80'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_computed_field(self):
        """Test filtering by a computed field."""
        PersonModel.mock(is_employed=True)

        parameters = {'filter[employed_integer]': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_one_to_many_relationship(self):
        """Test filtering by a foreign key relationship field."""
        person = PersonModel.mock()
        EmployeeModel.mock(name="employee", person_id=person.id)

        parameters = {'filter[employee.name]': 'EMPLOYEE'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_many_to_many_relationship(self):
        """Test filtering by a many-to-many relationship field."""
        company = CompanyModel.mock(name="company")
        PersonModel.mock(companies=[company])

        parameters = {'filter[companies.name]': 'COMPANY'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_invalid_field_parameter(self):
        """Test filtering by an unknown field."""
        try:
            parameters = {'filter[xyz]': 'value'}
            Resource(
                self.model, parameters, MarshmallowDriver, PersonSchema).\
                filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'filter[xyz]')

    def test_filter_invalid_relationship_attribute(self):
        """Test filtering by an invalid relationship field."""
        try:
            parameters = {'filter[employee.xyz]': 'value'}
            Resource(
                self.model, parameters, MarshmallowDriver, PersonSchema).\
                filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[employee.xyz]')

    def test_filter_invalid_relationship(self):
        """Test filtering by an invalid relationship value."""
        try:
            parameters = {'filter[rate.name]': 'whatever'}
            Resource(
                self.model, parameters, MarshmallowDriver, PersonSchema).\
                filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[rate.name]')

    def test_filter_invalid_value_type(self):
        """Test filtering by an invalid field value."""
        try:
            parameters = {'filter[datetime]': 'notadate'}
            Resource(
                self.model, parameters, MarshmallowDriver, PersonSchema).\
                filter_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(
                message['errors'][0]['source']['parameter'] ==
                'filter[datetime]')
