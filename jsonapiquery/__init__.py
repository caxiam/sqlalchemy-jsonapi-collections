from jsonapiquery import url
from urllib.parse import urlencode


def iter_by_type(iterator, params, drivers):
    for item in iterator(params):
        for driver in drivers:
            item = driver.parse(item)
        yield item


def filter_query(query, params, drivers):
    filters = iter_by_type(url.iter_filters, params, drivers)
    filters = list(filters)
    return query.apply_filters(filters), filters


def sort_query(query, params, drivers):
    sorts = iter_by_type(url.iter_sorts, params, drivers)
    sorts = list(sorts)
    return query.apply_sorts(sorts), sorts


def include_query(query, params, drivers):
    includes = iter_by_type(url.iter_includes, params, drivers)
    includes = list(includes)
    return query.apply_includes(includes), includes


def paginate_query(query, params, max_size=None, max_depth=None):
    paginators = url.iter_paginators(params)
    paginators = list(paginators)
    return query.apply_paginators(paginators, max_size, max_depth), paginators


def serialize_includes(includes, models):
    output = []
    for include in includes:
        mapping = zip(include.relationships, include.source.relationships)
        included = models
        for mapper, relationship in mapping:
            data, included = serialize_models(mapper, relationship, included)
            output.extend(data)
    return output


def serialize_models(mapper, relationship, models):
    included_data = []
    related_models = []
    for model in models:
        data, related = serialize_relationship(mapper, relationship, model)
        included_data.extend(data)
        related_models.extend(related)
    return included_data, related_models


def serialize_relationship(mapper, relationship, model):
    models = getattr(model, mapper.attribute_name)
    if models is None:
        return [], []

    if not isinstance(models, list):
        models = [models]
    return relationship.serialize(models), models


def make_pagination_links(base_url, paginators, parameters, total):
    if 'page[number]' in parameters:
        links = _paginate_number(base_url, paginators, parameters, total)
    else:
        links = _paginate_offset(base_url, paginators, parameters, total)

    links['self'] = base_url
    return links


def _paginate_offset(base_url, paginators, parameters, total):
    limit, offset = 50, 0
    for paginator in paginators:
        if paginator.strategy == 'limit':
            limit = int(paginator.value)
        elif paginator.strategy == 'offset':
            offset = int(paginator.value)

    url = base_url + '?{}'
    values = _build_page_offset_values(total, limit, offset)
    return _build_urls(_encode_page_offset, url, parameters, values)


def _paginate_number(base_url, paginators, parameters, total):
    limit, page = 50, 1
    for paginator in paginators:
        if paginator.strategy == 'limit':
            limit = int(paginator.value)
        elif paginator.strategy == 'number':
            page = int(paginator.value)

    url = base_url + '?{}'
    values = _build_page_number_values(total, limit, page)
    return _build_urls(_encode_page_number, url, parameters, values)


def _build_urls(fn, base_url, parameters, values):
    return {
        'first': base_url.format(fn(parameters, values[0])),
        'last': base_url.format(fn(parameters, values[1])),
        'next': base_url.format(fn(parameters, values[2])),
        'prev': base_url.format(fn(parameters, values[3]))
    }


def _build_page_offset_values(total, limit, offset):
    return 0, max(total - limit, 0), offset + limit, max(offset - limit, 0)


def _build_page_number_values(total, limit, current):
    return 1, max(total / limit, 1), current + 1, max(current - 1, 1)


def _encode_page_offset(params, value):
    return _encode_parameters(params, 'page[offset]', value)


def _encode_page_number(params, value):
    return _encode_parameters(params, 'page[number]', value)


def _encode_parameters(params, key, value):
    params[key] = value
    return urlencode(params)
