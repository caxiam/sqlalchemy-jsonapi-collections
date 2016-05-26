# -*- coding: utf-8 -*-
from jsonapi_collections import Resource
from jsonapi_collections.drivers import marshmallow
from jsonapi_collections.errors import JSONAPIError
from tests import UnitTestCase
from tests.mock import CompanyModel, EmployeeModel, PersonModel, PersonSchema


class IncludeTestCase(UnitTestCase):

    def setUp(self):
        super(IncludeTestCase, self).setUp()
        self.model = PersonModel
        self.view = PersonSchema
        self.query = PersonModel.query
        self.driver = marshmallow.MarshmallowDriver


class MarshmallowIncludeTestCase(IncludeTestCase):

    def test_include_nested(self):
        """Test including a nested relationship."""
        company = CompanyModel.mock()
        model = PersonModel.mock(companies=[company])
        EmployeeModel.mock(person_id=model.id)

        parameters = {'include': 'employee.person.companies'}
        included = Resource(self.model, parameters, self.driver, self.view).\
            compound_response(model)
        self.assertTrue(len(included) == 3)

        for pos, item in enumerate(included):
            if item['type'] == 'companies':
                companies = pos
            elif item['type'] == 'people':
                person = pos
            elif item['type'] == 'employees':
                employee = pos

        data = included[employee]
        self.assertIn('id', data)
        self.assertIn('type', data)

        attributes = data['attributes']
        self.assertIn('name', attributes)
        self.assertIn('months_of_service', attributes)
        self.assertIn('is_manager', attributes)
        self.assertIn('created_at', attributes)

        relationships = data['relationships']
        self.assertIn('person', relationships)
        self.assertIn('person_id', relationships)

        data = included[person]
        self.assertIn('id', data)
        self.assertIn('type', data)

        attributes = data['attributes']
        self.assertIn('name', attributes)
        self.assertIn('age', attributes)
        self.assertIn('is_employed', attributes)
        self.assertIn('gender', attributes)
        self.assertIn('rate', attributes)
        self.assertIn('employed_integer', attributes)
        self.assertIn('created_at', attributes)

        relationships = data['relationships']
        self.assertIn('companies', relationships)
        self.assertIn('employee', relationships)

        data = included[companies]
        self.assertIn('id', data)
        self.assertIn('type', data)

        attributes = data['attributes']
        self.assertIn('name', attributes)
        self.assertIn('year_established', attributes)
        self.assertIn('is_profitable', attributes)
        self.assertIn('created_at', attributes)

    def test_include_one_to_one(self):
        """Test including a one-to-one relationship."""
        model = PersonModel.mock()
        EmployeeModel.mock(person_id=1)

        parameters = {'include': 'employee'}
        included = Resource(
            self.model, parameters, self.driver, self.view).\
            compound_response(model)
        self.assertTrue(len(included) == 1)

        data = included[0]
        self.assertIn('id', data)
        self.assertIn('type', data)

        attributes = data['attributes']
        self.assertIn('name', attributes)
        self.assertIn('months_of_service', attributes)
        self.assertIn('is_manager', attributes)
        self.assertIn('created_at', attributes)

        relationships = data['relationships']
        self.assertIn('person', relationships)
        self.assertIn('person_id', relationships)

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
        self.assertTrue(len(included) == 3)

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
