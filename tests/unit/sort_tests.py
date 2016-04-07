# -*- coding: utf-8 -*-
from jsonapi_collections import Collection
from jsonapi_collections.drivers import marshmallow
from jsonapi_collections.errors import JSONAPIError
from tests import UnitTestCase
from tests.mock import CompanyModel, PersonModel, PersonSchema


class SortTestCase(UnitTestCase):

    def setUp(self):
        super(SortTestCase, self).setUp()
        self.model = PersonModel
        self.view = PersonSchema
        self.query = PersonModel.query


class SQLAlchemySortTestCase(SortTestCase):
    """Test sorting with the SQLAlchemy driver."""

    def test_sort_field_ascending(self):
        """Test sorting a field in ascending order."""
        PersonModel.mock(name="A")
        PersonModel.mock(name="B")

        parameters = {'sort': 'name'}
        query = Collection(self.model, parameters).sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].name, 'A')

    def test_sort_field_descending(self):
        """Test sorting a field in descending order."""
        PersonModel.mock(name="A")
        PersonModel.mock(name="B")

        parameters = {'sort': '-name'}
        query = Collection(self.model, parameters).sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].name, 'B')

    def test_sort_relationship_ascending(self):
        """Test sorting a relationhip's field in descending order."""
        a = CompanyModel.mock(name="Last")
        b = CompanyModel.mock(name="First")
        PersonModel.mock(name="A", companies=[a])
        PersonModel.mock(name="B", companies=[b])

        parameters = {'sort': 'companies.name'}
        query = Collection(self.model, parameters).sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].companies[0].name, 'First')

    def test_sort_relationship_descending(self):
        """Test sorting a relationhip's field in descending order."""
        a = CompanyModel.mock(name="Last")
        b = CompanyModel.mock(name="First")
        PersonModel.mock(name="A", companies=[a])
        PersonModel.mock(name="B", companies=[b])

        parameters = {'sort': '-companies.name'}
        query = Collection(self.model, parameters).sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].companies[0].name, 'Last')

    def test_sort_invalid_field(self):
        """Test sorting against non-existant attribute."""
        PersonModel.mock()

        try:
            parameters = {'sort': 'x'}
            Collection(self.model, parameters).sort_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'sort')
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(isinstance(message['errors'][0]['detail'], list))

    def test_sort_invalid_relationship(self):
        """Test sorting against non-existant relationship attribute."""
        PersonModel.mock()

        try:
            parameters = {'sort': 'companies.x'}
            Collection(self.model, parameters).sort_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'sort')
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(isinstance(message['errors'][0]['detail'], list))


class MarshmallowSortTestCase(SortTestCase):
    """Test sorting with the marshmallow driver."""

    def test_sort_field_ascending(self):
        """Test sorting a field in ascending order."""
        PersonModel.mock(name="A")
        PersonModel.mock(name="B")

        parameters = {'sort': 'name'}
        query = Collection(
            self.model, parameters, marshmallow.MarshmallowDriver, self.view).\
            sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].name, 'A')

    def test_sort_field_descending(self):
        """Test sorting a field in descending order."""
        PersonModel.mock(name="A")
        PersonModel.mock(name="B")

        parameters = {'sort': '-name'}
        query = Collection(
            self.model, parameters, marshmallow.MarshmallowDriver, self.view).\
            sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].name, 'B')

    def test_sort_relationship_ascending(self):
        """Test sorting a relationhip's field in descending order."""
        a = CompanyModel.mock(name="Last")
        b = CompanyModel.mock(name="First")
        PersonModel.mock(name="A", companies=[a])
        PersonModel.mock(name="B", companies=[b])

        parameters = {'sort': 'companies.name'}
        query = Collection(
            self.model, parameters, marshmallow.MarshmallowDriver, self.view).\
            sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].companies[0].name, 'First')

    def test_sort_relationship_descending(self):
        """Test sorting a relationhip's field in descending order."""
        a = CompanyModel.mock(name="Last")
        b = CompanyModel.mock(name="First")
        PersonModel.mock(name="A", companies=[a])
        PersonModel.mock(name="B", companies=[b])

        parameters = {'sort': '-companies.name'}
        query = Collection(
            self.model, parameters, marshmallow.MarshmallowDriver, self.view).\
            sort_query(self.query)

        result = query.all()
        self.assertEqual(result[0].companies[0].name, 'Last')

    def test_sort_invalid_field(self):
        """Test sorting against non-existant attribute."""
        PersonModel.mock()

        try:
            parameters = {'sort': 'x'}
            Collection(
                self.model, parameters, marshmallow.MarshmallowDriver,
                self.view).sort_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'sort')
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(isinstance(message['errors'][0]['detail'], list))

    def test_sort_invalid_relationship(self):
        """Test sorting against non-existant relationship attribute."""
        PersonModel.mock()

        try:
            parameters = {'sort': 'companies.x'}
            Collection(
                self.model, parameters, marshmallow.MarshmallowDriver,
                self.view).sort_query(self.query)
        except JSONAPIError as exc:
            message = exc.message
            self.assertTrue(
                message['errors'][0]['source']['parameter'] == 'sort')
            self.assertIn('detail', message['errors'][0])
            self.assertTrue(isinstance(message['errors'][0]['detail'], list))
