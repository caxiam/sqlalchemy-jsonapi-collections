"""."""
from urllib.parse import parse_qsl, urlparse


DEFAULT_STRATEGY = 'eq'
STRATEGIES = ['eq', 'gt', 'gte', 'lt', 'lte', 'in', 'like', 'ilike']
STRATEGY_PARTITION = ':'


def get_parameters(url: str) -> dict:
    """Convert a URL into a dictionary of parameter, value pairs."""
    parsed_url = urlparse(url)
    return {key: value for key, value in parse_qsl(parsed_url.query)}


def get_includes(parameters: dict) -> list:
    """Return a list of relationships to include.

    :param parameters: Dictionary of parameter name, value pairs.
    """
    return parameters.get('include', '').split(',')


def get_sorts(parameters: dict) -> list:
    """Return a list of doubles to sort by.

    :param parameters: Dictionary of parameter name, value pairs.
    """
    sorts = []
    for sort in parameters.get('sort', '').split(','):
        if sort.startswith('-') or sort.startswith('+'):
            sorts.append((sort[1:], sort[:1]))
        elif sort != '':
            sorts.append((sort, '+'))
    return sorts


def get_filters(parameters: dict) -> list:
    """Return a list of triples to filter by.

    :param parameters: Dictionary of parameter name, value pairs.
    """
    filters = []
    for parameter, value in parameters.items():
        if parameter.startswith('filter[') and parameter.endswith(']'):
            filters.append(_get_filter(parameter, value))
    return filters


def _get_filter(key: str, value: str) -> tuple:
    """Return a triple to filter by."""
    strategy, partition, values = value.partition(STRATEGY_PARTITION)

    negated = strategy.startswith('~')
    if negated:
        strategy = strategy[1:]

    if partition == '':
        values = strategy
        strategy = DEFAULT_STRATEGY
    elif strategy not in STRATEGIES:
        values = ''.join((strategy, partition, values))
        strategy = DEFAULT_STRATEGY

    if negated:
        strategy = '~{}'.format(strategy)
    return key[7:-1], strategy, values.split(',')


def get_paginators(parameters: dict) -> dict:
    """Return a list of doubles to filter by.

    :param parameters: Dictionary of parameter name, value pairs.
    """
    paginators = []
    for key, value in parameters.items():
        if key in ['page[size]', 'page[limit]']:
            paginators.append(('limit', value))
        elif key == 'page[offset]':
            paginators.append(('offset', value))
        elif key == 'page[number]':
            paginators.append(('number', value))
    return paginators
