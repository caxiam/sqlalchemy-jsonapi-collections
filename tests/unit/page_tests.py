# -*- coding: utf-8 -*-
"""JSONAPI pagination implementation testing.

This module is dedicated to testing against the various pagination
strategies described in the JSONAPI 1.0 specification.
"""
from jsonapi_collections import Resource
from jsonapi_collections.drivers.marshmallow import MarshmallowDriver
from tests import UnitTestCase
from tests.mock import PersonModel, PersonSchema


class PaginationTestCase(UnitTestCase):
    """Base pagination test case."""

    def setUp(self):
        """Establish some helpful model and query shortcuts."""
        super(PaginationTestCase, self).setUp()
        self.model = PersonModel
        self.query = PersonModel.query


class SQLAlchemyPaginationTestCase(PaginationTestCase):
    """SQLAlchemy driver pagination tests."""

    def test_page_limit(self):
        """Test limiting a page by the page[limit] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[limit]': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'First')

    def test_page_size(self):
        """Test limiting a page by the page[size] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[size]': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'First')

    def test_limit(self):
        """Test limiting a page by the limit parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'limit': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'First')

    def test_page_offset(self):
        """Test offsetting a page by the page[offset] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[offset]': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')

    def test_page_number(self):
        """Test offsetting a page by the page[number] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[number]': '1', 'page[size]': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')

    def test_offset(self):
        """Test offsetting a page by the offset parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'offset': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')


class MarshmallowPaginationTestCase(PaginationTestCase):
    """Marshmallow driver pagination tests."""

    def test_page_limit(self):
        """Test limiting a page by the page[limit] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[limit]': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'First')

    def test_page_size(self):
        """Test limiting a page by the page[size] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[size]': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'First')

    def test_limit(self):
        """Test limiting a page by the limit parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'limit': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'First')

    def test_page_offset(self):
        """Test offsetting a page by the page[offset] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[offset]': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')

    def test_page_number(self):
        """Test offsetting a page by the page[number] parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'page[number]': '1', 'page[size]': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')

    def test_offset(self):
        """Test offsetting a page by the offset parameter."""
        PersonModel.mock(name='First')
        PersonModel.mock(name='Second')

        parameters = {'offset': '1'}
        query = Resource(
            self.model, parameters, MarshmallowDriver, PersonSchema).\
            paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')
