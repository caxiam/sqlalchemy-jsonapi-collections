from jsonapiquery.types import FieldSet, Filter, Include, Sort, Paginator
from typing import Any, Generator, List


def iter_fieldsets(params: dict) -> Generator[FieldSet, None, None]:
    """Return a generator of fieldset instructions."""
    for key, value in iter_namespace(params, 'fields'):
        yield FieldSet('fields[{}]'.format(key), key, value.split(','))


def iter_filters(params: dict) -> Generator[Filter, None, None]:
    """Return a generator of filter instructions."""
    for key, value in iter_namespace(params, 'filter'):
        if key != '':
            yield parse_filter(key, value)


def iter_filters_only(
    params: dict,
    only: List[str]
) -> Generator[Filter, None, None]:
    """Return a generator of restricted filter instructions."""
    for key in only:
        filter_key = 'filter[{}]'.format(key)
        if filter_key in params:
            yield parse_filter(key, params.get(filter_key))


def parse_filter(key: str, value: str) -> Filter:
    relationships = key.split('.')
    attribute = relationships.pop()
    yield Filter('filter[{}]'.format(key), relationships, attribute, value)


def iter_paginators(params: dict) -> Generator[Paginator, None, None]:
    """Return a generator of pagination instructions."""
    for key, value in iter_namespace(params, 'page'):
        if key not in ['number', 'size', 'offset', 'limit', 'cursor']:
            continue
        yield Paginator('page[{}]'.format(key), key, value)


def iter_includes(params: dict) -> Generator[Include, None, None]:
    """Return a generator of include instructions."""
    includes = params.get('include', '')
    includes = includes.split(',')
    for include in includes:
        if include == '':
            continue
        yield Include('include', include.split('.'))


def iter_sorts(params: dict) -> Generator[Sort, None, None]:
    """Return a generator of sort instructions."""
    sorts = params.get('sort', '')
    sorts = sorts.split(',')
    for sort in sorts:
        if sort == '':
            continue

        direction = '+'
        if sort.startswith('-') or sort.startswith('+'):
            direction, sort = sort[0], sort[1:]

        relationships = sort.split('.')
        attribute = relationships.pop()
        yield Sort('sort', relationships, attribute, direction)


def iter_namespace(params: dict, namespace: str) -> Generator[Any, None, None]:
    """Return a generator of namespaced instructions."""
    for key, value in params.items():
        if key.startswith('{}['.format(namespace)) and key.endswith(']'):
            yield key[len(namespace) + 1: -1], value
