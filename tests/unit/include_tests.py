# -*- coding: utf-8 -*-
from jsonapi_collections import Resource
from jsonapi_collections.drivers import marshmallow
from jsonapi_collections.errors import JSONAPIError
from tests import UnitTestCase
from tests.mock import (
    CompanyModel, EmployeeModel, EmployeeSchema, PersonModel, PersonSchema
)


class IncludeTestCase(UnitTestCase):

    def setUp(self):
        super(IncludeTestCase, self).setUp()
        self.model = PersonModel
        self.view = PersonSchema
        self.query = PersonModel.query
        self.driver = marshmallow.MarshmallowDriver


class MarshmallowIncludeTestCase(IncludeTestCase):

    def test_include_one_to_one(self):
        """Test including a one-to-one relationship."""
        model = PersonModel.mock()
        EmployeeModel.mock(person_id=1)

        parameters = {'include': 'employee'}
        included = Resource(
            self.model, parameters, self.driver, self.view).\
            compound_response(model)
        self.assertTrue(len(included) == 1)

    def test_include_many_to_many(self):
        """Test including a many-to-many relationship."""
        company = CompanyModel.mock()
        model = PersonModel.mock(companies=[company])

        parameters = {'include': 'companies'}
        included = Resource(
            self.model, parameters, self.driver, self.view).\
            compound_response(model)
        self.assertTrue(len(included) == 1)

    def test_include_attribute(self):
        """Test including an attribute."""
        model = PersonModel.mock()

        try:
            parameters = {'include': 'name'}
            Resource(
                self.model, parameters, self.driver, self.view).\
                compound_response(model)
            self.assertTrue(False)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'include')
            self.assertIn('detail', message['errors'][0])

    def test_include_missing_field(self):
        """Test including an unknown field."""
        model = PersonModel.mock()

        try:
            parameters = {'include': 'wxyz'}
            Resource(
                self.model, parameters, self.driver, self.view).\
                compound_response(model)
            self.assertTrue(False)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'include')
            self.assertIn('detail', message['errors'][0])


class SQLAlchemyIncludeTestCase(IncludeTestCase):

    def test_include_nested(self):
        """Test including a nested relationship."""
        company = CompanyModel.mock()
        model = PersonModel.mock(companies=[company])
        EmployeeModel.mock(person_id=model.id)

        parameters = {'include': 'employee.person.companies'}
        included = Resource(self.model, parameters).compound_response(model)
        self.assertTrue(len(included) == 1)

    def test_include_one_to_one(self):
        """Test including a one-to-one relationship."""
        model = PersonModel.mock()
        EmployeeModel.mock(person_id=1)

        parameters = {'include': 'employee'}
        included = Resource(self.model, parameters).compound_response(model)
        self.assertTrue(len(included) == 1)

    def test_include_many_to_many(self):
        """Test including a many-to-many relationship."""
        company = CompanyModel.mock()
        model = PersonModel.mock(companies=[company])

        parameters = {'include': 'companies'}
        included = Resource(self.model, parameters).compound_response(model)
        self.assertTrue(len(included) == 1)

    def test_include_empty_relationship(self):
        """Test including an empty one-to-one relationship."""
        model = PersonModel.mock()

        parameters = {'include': 'employee'}
        included = Resource(self.model, parameters).compound_response(model)
        self.assertTrue(len(included) == 0)

    def test_include_attribute(self):
        """Test including an attribute."""
        model = PersonModel.mock()

        try:
            parameters = {'include': 'name'}
            Resource(self.model, parameters).compound_response(model)
            self.assertTrue(False)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'include')
            self.assertIn('detail', message['errors'][0])

    def test_include_missing_field(self):
        """Test including an unknown field."""
        model = PersonModel.mock()

        try:
            parameters = {'include': 'wxyz'}
            Resource(self.model, parameters).compound_response(model)
            self.assertTrue(False)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'include')
            self.assertIn('detail', message['errors'][0])
