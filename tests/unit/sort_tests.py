# -*- coding: utf-8 -*-
from flask_sqlalchemy_jsonapi import SortValue
from tests import UnitTestCase
from tests.mock import CompanyModel, PersonModel, PersonSchema


class SortTestCase(UnitTestCase):

    def setUp(self):
        super(SortTestCase, self).setUp()
        self.model = PersonModel
        self.view = PersonSchema
        self.query = PersonModel.query

    def test_sort_field_ascending(self):
        """Test sorting a result set in ascending order by the name
        column.
        """
        PersonModel.mock(name="A")
        PersonModel.mock(name="B")

        values, errors = SortValue.generate(self.view, ['name'])
        query = SortValue.sort_by(self.model.query, values)

        self.assertTrue(errors == [])
        result = query.all()
        self.assertEqual(result[0].name, 'A')

    def test_sort_field_descending(self):
        """Test sorting a result set in descending order by the name
        column.
        """
        PersonModel.mock(name="A")
        PersonModel.mock(name="B")

        values, errors = SortValue.generate(self.view, ['-name'])
        query = SortValue.sort_by(self.model.query, values)

        self.assertTrue(errors == [])
        result = query.all()
        self.assertEqual(result[0].name, 'B')

    def test_sort_relationship_ascending(self):
        """Test sorting a result set in ascending order by the
        companies column.
        """
        a = CompanyModel.mock(name="A")
        b = CompanyModel.mock(name="B")

        PersonModel.mock(name="A", companies=[a])
        PersonModel.mock(name="B", companies=[b])

        values, errors = SortValue.generate(self.view, ['companies.name'])
        query = SortValue.sort_by(self.model.query, values)

        self.assertTrue(errors == [])
        result = query.all()
        self.assertEqual(result[0].name, 'A')

    def test_sort_relationship_descending(self):
        """Test sorting a result set in descending order by the
        companies column.
        """
        a = CompanyModel.mock(name="A")
        b = CompanyModel.mock(name="B")

        PersonModel.mock(name="A", companies=[a])
        PersonModel.mock(name="B", companies=[b])

        values, errors = SortValue.generate(self.view, ['-companies.name'])
        query = SortValue.sort_by(self.model.query, values)

        self.assertTrue(errors == [])
        result = query.all()
        self.assertEqual(result[0].name, 'B')

    def test_sort_invalid_field(self):
        """Test detecting and raising an error in response to an
        invalid column name.
        """
        PersonModel.mock()

        values, errors = SortValue.generate(self.view, ['-x'])
        self.assertTrue(len(errors) == 1)
        self.assertTrue(values == [])

    def test_sort_invalid_relationship(self):
        """Test detecting and raising an error in response to an
        invalid relationship attribute name.
        """
        PersonModel.mock()

        values, errors = SortValue.generate(self.view, ['companies.x'])
        self.assertTrue(len(errors) == 1)
        self.assertTrue(values == [])
