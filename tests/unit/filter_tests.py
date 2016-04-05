# -*- coding: utf-8 -*-
from datetime import date, timedelta

from jsonapi_collections import Collection
from jsonapi_collections.drivers.marshmallow import MarshmallowDriver
from tests import UnitTestCase
from tests.mock import CompanyModel, EmployeeModel, PersonModel, PersonSchema


class FilterTestCase(UnitTestCase):

    def setUp(self):
        super(FilterTestCase, self).setUp()
        self.model = PersonModel
        self.query = PersonModel.query

    def test_filter_string_field(self):
        """Test filtering a string value against the name column"""
        PersonModel.mock(name='A PRODUCT Wildcard', gender='male')

        parameters = {'filter[name]': 'prod'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_multiple_string_field(self):
        """Test filtering a list of string values against the name
        column
        """
        PersonModel.mock(name='A PRODUCT Wildcard')

        parameters = {'filter[name]': 'prod,test,card'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_enum_field(self):
        """Test filtering a string value against an enum column"""
        PersonModel.mock(gender='male')

        parameters = {'filter[gender]': 'MaLe'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    # def test_filter_enum_field_invalid_value(self):
    #     """Test filtering an unsupported string value against an enum
    #     column
    #     """
    #     PersonModel.mock(gender='male')

    #     parameters = {'filter[gender]': 'mal'}
    #     query = Collection(
    #         self.model, parameters, MarshmallowDriver, PersonSchema).\
    #         filter_query(query)
    #     self.assertEqual(len(errors), 1)

    def test_filter_decimal_field(self):
        """Test filtering a string value against a decimal column"""
        PersonModel.mock(rate='12.51')

        parameters = {'filter[rate]': '12.51'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    # def test_filter_decimal_field_invalid_value(self):
    #     """Test filtering an alpha string value against a decimal
    #     column
    #     """
    #     PersonModel.mock(rate='12.51')

    #     parameters = {'filter[rate]': 'a'}
    #     query = Collection(
    #         self.model, parameters, MarshmallowDriver, PersonSchema).\
    #         filter_query(query)
    #     self.assertEqual(len(errors), 1)

    def test_filter_decimal_range(self):
        """Test filtering an integer value against a decimal column.
        Ensure that the result set includes all decimal numbers for the
        given whole number.
        """
        PersonModel.mock(rate='12.51')
        PersonModel.mock(rate='12.99')

        parameters = {'filter[rate]': '12'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 2)

        parameters = {'filter[rate]': '12.51'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

        parameters = {'filter[rate]': '12.00'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 0)

        parameters = {'filter[rate]': '13'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 0)

    def test_filter_boolean_field(self):
        """Test filtering a is_employed value against a is_employed column"""
        PersonModel.mock(is_employed=True)

        parameters = {'filter[is_employed]': '1'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_datetime_field(self):
        """Test filtering a date value against the created_at column"""
        PersonModel.mock()

        today = date.today()
        parameters = {'filter[created_at]': today.strftime('%Y-%m-%d')}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

        tomorrow = today + timedelta(days=1)
        parameters = {'filter[created_at]': tomorrow.strftime('%Y-%m-%d')}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 0)

    def test_filter_integer_field(self):
        """Test filtering an integer value against the age column"""
        PersonModel.mock(age=80)

        parameters = {'filter[age]': '80'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_computed_field(self):
        PersonModel.mock(is_employed=True)

        parameters = {'filter[employed_integer]': '1'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

        parameters = {'filter[employed_integer]': '0'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 0)

    def test_filter_one_to_many_relationship(self):
        """Test filtering a string value across a one-to-many
        relationship
        """
        person = PersonModel.mock()
        EmployeeModel.mock(name="employee", person_id=person.id)

        parameters = {'filter[employee.name]': 'EMPLOYEE'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    def test_filter_many_to_many_relationship(self):
        """Test filtering a string value across a many-to-many
        relationship
        """
        company = CompanyModel.mock(name="company")
        PersonModel.mock(companies=[company])

        parameters = {'filter[companies.name]': 'COMPANY'}
        query = Collection(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            filter_query(query)

        result = query.all()
        self.assertEqual(len(result), 1)

    # def test_filter_invalid_field_parameter(self):
    #     """Test detecting and raising an error in response to an
    #     invalid column
    #     """
    #     parameters = {'filter[xyz]': 'value'}
    #     query = Collection(
    #         self.model, parameters, MarshmallowDriver, PersonSchema).\
    #         filter_query(query)
    #     self.assertEqual(len(errors), 1)

    # def test_filter_invalid_relationship_parameter(self):
    #     """Test detecting and raising an error in response to an
    #     invalid column on a relationship's model
    #     """
    #     parameters = {'filter[employee.xyz]': 'value'}
    #     query = Collection(
    #         self.model, parameters, MarshmallowDriver, PersonSchema).\
    #         filter_query(query)
    #     self.assertEqual(len(errors), 1)

    # def test_filter_invalid_value_type(self):
    #     """Test detecting and raising an error in response to an
    #     invalid value for a specified column's type
    #     """
    #     parameters = {'filter[datetime]': 'notadate'}
    #     query = Collection(
    #         self.model, parameters, MarshmallowDriver, PersonSchema).\
    #         filter_query(query)
    #     self.assertEqual(len(errors), 1)
