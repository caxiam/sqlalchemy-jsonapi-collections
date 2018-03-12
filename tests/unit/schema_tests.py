from nose.tools import assert_raises

from jsonapiquery import schema, url
from jsonapiquery.schema.drivers import marshmallow
from tests.marshmallow_jsonapi import Person
from tests.unit import UnitTestCase


class SchemaTestCase(UnitTestCase):
    driver = marshmallow.SchemaDriverMarshmallow(Person())

    def test_iter_filters(self):
        params = {'filter[student.school.title]': 'Ridgefield High'}
        filters = url.iter_filters(params)
        filters = schema.iter_filters(filters, self.driver)

        result, item, error = next(filters)
        self.assertTrue(isinstance(result.relationships[0], marshmallow.Relationship))
        self.assertTrue(isinstance(result.relationships[1], marshmallow.Relationship))
        self.assertTrue(isinstance(result.attribute, marshmallow.Attribute))
        self.assertTrue(isinstance(item, url.Filter))
        self.assertTrue(error is None)
