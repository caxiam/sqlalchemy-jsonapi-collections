from jsonapiquery.errors import JSONAPIQueryError
from jsonapiquery.model.drivers import ModelDriverBase


def iter_filters(filters, driver: ModelDriverBase):
    yield from iter_model_fields(filters, driver)


def iter_includes(includes, driver: ModelDriverBase):
    yield from iter_model_fields(includes, driver)


def iter_sorts(sorts, driver: ModelDriverBase):
    yield from iter_model_fields(sorts, driver)


def iter_model_fields(iterator, driver: ModelDriverBase):
    for item in iterator:
        try:
            yield driver.parse(item), None
        except (AttributeError, KeyError):
            yield None, JSONAPIQueryError('KEY_PARSE_ERROR', item.source)

