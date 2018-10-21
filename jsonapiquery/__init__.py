from jsonapiquery import url


def iter_by_type(iterator, params, drivers):
    for item in iterator(params):
        for driver in drivers:
            item = driver.parse(item)
        yield item


def filter_query(query, params, drivers):
    filters = iter_by_type(url.iter_filters, params, drivers)
    return query.apply_filters(filters)


def sort_query(query, params, drivers):
    sorts = iter_by_type(url.iter_sorts, params, drivers)
    return query.apply_sorts(sorts)


def include_query(query, params, drivers):
    includes = iter_by_type(url.iter_includes, params, drivers)
    return query.apply_includes(includes)


def paginate_query(query, params):
    paginators = url.iter_paginators(params)
    return query.apply_paginators(paginators)
