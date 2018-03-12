from jsonapiquery.errors import JSONAPIQueryError
from jsonapiquery.schema.drivers import SchemaDriverBase

from collections import namedtuple


Filter = namedtuple('Filter', ['source', 'relationships', 'attribute', 'strategy', 'value'])
Include = namedtuple('Include', ['source', 'relationships'])
Sort = namedtuple('Sort', ['source', 'relationships', 'attribute', 'direction'])


def iter_filters(filters, driver: SchemaDriverBase):
    for result, item, error in iter_schema_fields(filters, driver):
        if error:
            strategy, value = driver.split_strategy_value(item.value)
            value = result.attribute.deserialize(value)
            yield Filter(item.source, result.relationships, result.attribute, strategy, value), None
        else:
            yield None, error


def iter_includes(includes, driver: SchemaDriverBase):
    for result, item, error in iter_schema_fields(includes, driver):
        yield Include(item.source, result.relationships), None


def iter_sorts(sorts, driver: SchemaDriverBase):
    for result, item, error in iter_schema_fields(sorts, driver):
        yield Sort(item.source, result.relationships, result.attribute, item.direction), None


def iter_schema_fields(iterator, driver: SchemaDriverBase):
    for item in iterator:
        try:
            yield driver.parse(item), item, None
        except (AttributeError, KeyError):
            yield None, item, JSONAPIQueryError('KEY_PARSE_ERROR', item.source)

