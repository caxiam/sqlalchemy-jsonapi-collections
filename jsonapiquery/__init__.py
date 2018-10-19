from jsonapiquery import url


def filter_query(query, params, drivers):
    for filter_ in iter_filters(params):
        for driver in drivers:
            filter_ = driver.parse(filter_)
        query = query.apply_filter(filter_)
    return query
