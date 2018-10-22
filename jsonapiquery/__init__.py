from jsonapiquery import url


def iter_by_type(iterator, params, drivers):
    for item in iterator(params):
        for driver in drivers:
            item = driver.parse(item)
        yield item


def filter_query(query, params, drivers):
    filters = iter_by_type(url.iter_filters, params, drivers)
    return query.apply_filters(filters), filters


def sort_query(query, params, drivers):
    sorts = iter_by_type(url.iter_sorts, params, drivers)
    return query.apply_sorts(sorts), sorts


def include_query(query, params, drivers):
    includes = iter_by_type(url.iter_includes, params, drivers)
    return query.apply_includes(includes), includes


def paginate_query(query, params):
    paginators = url.iter_paginators(params)
    return query.apply_paginators(paginators), paginators


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
    if not isinstance(models, list):
        models = [models]
    return relationship.serialize(models), models
