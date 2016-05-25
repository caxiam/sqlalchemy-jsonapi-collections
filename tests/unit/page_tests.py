# -*- coding: utf-8 -*-
"""JSONAPI pagination implementation testing.

This module is dedicated to testing against the various pagination
strategies described in the JSONAPI 1.0 specification.
"""
from urlparse import parse_qs, urlparse

from jsonapi_collections import Resource, JSONAPIError
from tests import UnitTestCase
from tests.mock import PersonModel


class PaginationTestCase(UnitTestCase):
    """Pagination test case."""

    def setUp(self):
        """Establish some helpful model and query shortcuts."""
        super(PaginationTestCase, self).setUp()
        self.model = PersonModel
        self.query = PersonModel.query

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

    def test_blank_limit_values(self):
        """Test defaulting blank limit values."""
        parameters = {'page[limit]': ''}
        limit, _ = Resource(self.model, parameters).get_pagination_values()
        self.assertTrue(limit == 100)

        parameters = {'page[size]': ''}
        limit, _ = Resource(self.model, parameters).get_pagination_values()
        self.assertTrue(limit == 100)

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

        parameters = {'page[number]': '2', 'page[size]': '1'}
        query = Resource(self.model, parameters).paginate_query(self.query)

        result = query.all()
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].name == 'Second')

    def test_blank_offset_values(self):
        """Test defaulting blank offset values."""
        parameters = {'page[offset]': ''}
        _, offset = Resource(self.model, parameters).get_pagination_values()
        self.assertTrue(offset == 0)

        parameters = {'page[number]': ''}
        _, offset = Resource(self.model, parameters).get_pagination_values()
        self.assertTrue(offset == 1)

    def test_mismatched_strategies(self):
        """Test erroring when mismatched strategies are provided."""
        try:
            parameters = {'page[offset]': '1', 'page[size]': '1'}
            Resource(self.model, parameters).paginate_query(self.query)
        except JSONAPIError as exc:
            self.assertIn('detail', exc.message['errors'][0])
            self.assertIn('source', exc.message['errors'][0])
            self.assertIn('parameter', exc.message['errors'][0]['source'])

            self.assertIn('detail', exc.message['errors'][1])
            self.assertIn('source', exc.message['errors'][1])
            self.assertIn('parameter', exc.message['errors'][1]['source'])

        try:
            parameters = {'page[number]': '1', 'page[limit]': '1'}
            Resource(self.model, parameters).paginate_query(self.query)
        except JSONAPIError as exc:
            self.assertIn('detail', exc.message['errors'][0])
            self.assertIn('source', exc.message['errors'][0])
            self.assertIn('parameter', exc.message['errors'][0]['source'])

            self.assertIn('detail', exc.message['errors'][1])
            self.assertIn('source', exc.message['errors'][1])
            self.assertIn('parameter', exc.message['errors'][1]['source'])

    def test_invalid_value(self):
        """Test paginating with invalid parameter values."""
        try:
            parameters = {'page[offset]': 'x'}
            Resource(self.model, parameters).paginate_query(self.query)
        except JSONAPIError as exc:
            self.assertIn('detail', exc.message['errors'][0])
            self.assertIn('source', exc.message['errors'][0])
            self.assertIn('parameter', exc.message['errors'][0]['source'])
            self.assertTrue(
                exc.message['errors'][0]['source']['parameter'] ==
                'page[offset]')

    def test_get_links_object_paged(self):
        """Test retrieving the pagination links object for page strategies."""
        url = 'google.com'

        parameters = {'page[number]': '10', 'page[size]': '5'}
        links = Resource(self.model, parameters).get_pagination_links(url, 100)
        for key, value in links.iteritems():
            value = parse_qs(urlparse(value).query)
            number = value['page[number]'][0]
            if key == 'self':
                self.assertTrue(number == '10')
            elif key == 'first':
                self.assertTrue(number == '1')
            elif key == 'last':
                self.assertTrue(number == '20')
            elif key == 'next':
                self.assertTrue(number == '11')
            elif key == 'prev':
                self.assertTrue(number == '9')
            self.assertTrue(value['page[size]'][0] == '5')

    def test_get_links_object_limited(self):
        """Test retrieving the pagination links object for limit strategies."""
        url = 'google.com'

        parameters = {'page[offset]': '50', 'page[limit]': '5'}
        links = Resource(self.model, parameters).get_pagination_links(url, 100)
        for key, value in links.iteritems():
            value = parse_qs(urlparse(value).query)
            offset = value['page[offset]'][0]
            if key == 'self':
                self.assertTrue(offset == '50')
            elif key == 'first':
                self.assertTrue(offset == '0')
            elif key == 'last':
                self.assertTrue(offset == '95')
            elif key == 'next':
                self.assertTrue(offset == '55')
            elif key == 'prev':
                self.assertTrue(offset == '45')
            self.assertTrue(value['page[limit]'][0] == '5')
