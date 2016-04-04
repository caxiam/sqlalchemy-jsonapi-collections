# -*- coding: utf-8 -*-
from jsonapi_collections import IncludeValue
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

    def test_include_foreign_key(self):
        """Test including a foreign key relationship field."""
        PersonModel.mock()
        model = EmployeeModel.mock(person_id=1)

        include = ['person']
        iv_objects, errors = IncludeValue.generate(EmployeeSchema, include)
        data = IncludeValue.include(iv_objects, model)

        self.assertTrue(errors == [])
        self.assertTrue(len(data) == 1)

    def test_include_one_to_many_relationship(self):
        """Test including a one to many relationship field."""
        model = PersonModel.mock()
        EmployeeModel.mock(person_id=1)

        include = ['employee']
        iv_objects, errors = IncludeValue.generate(self.view, include)
        data = IncludeValue.include(iv_objects, model)

        self.assertTrue(errors == [])
        self.assertTrue(len(data) == 1)

    def test_include_many_to_many_relationship(self):
        """Test including a many to many relationship field."""
        company_1 = CompanyModel.mock()
        company_2 = CompanyModel.mock()
        model = PersonModel.mock(companies=[company_1, company_2])

        include = ['companies']
        iv_objects, errors = IncludeValue.generate(self.view, include)
        data = IncludeValue.include(iv_objects, model)

        self.assertTrue(errors == [])
        self.assertTrue(len(data) == 2)

    def test_include_multiple_relationships(self):
        """Test including multiple relationship fields of differing
        types.
        """
        company = CompanyModel.mock()
        model = PersonModel.mock(companies=[company])
        EmployeeModel.mock(person_id=1)

        include = ['companies', 'employee']
        iv_objects, errors = IncludeValue.generate(self.view, include)
        data = IncludeValue.include(iv_objects, model)

        self.assertTrue(errors == [])
        self.assertTrue(len(data) == 2)

    def test_include_attribute(self):
        """Test including an attribute field."""
        include = ['name']
        iv_objects, errors = IncludeValue.generate(self.view, include)
        self.assertTrue(len(errors) == 1)

    def test_include_bogus_value(self):
        """Test including a non-existant field."""
        include = ['xyz']
        iv_objects, errors = IncludeValue.generate(self.view, include)
        self.assertTrue(len(errors) == 1)

    def test_include_missing_schema(self):
        """Test including a relationship that has not defined the
        related_schema property.
        """
        include = ['person_id']
        iv_objects, errors = IncludeValue.generate(EmployeeSchema, include)
        self.assertTrue(len(errors) == 1)
