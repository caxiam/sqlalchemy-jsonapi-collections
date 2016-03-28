.. _quick_start:

Quick Start
===========

==========
Filtering:
==========

For a given set of query parameters, pass a parameters dictionary object and the marshmallow schema to the `FilterParameter`'s `generate` classmethod.  Determine if the returned errors object is acceptable and raise appropriately.

::

    parameters = {
        "filter[id]": "1,2,10",
        "q": "xyz",
        "sort": "-id"
    }
    filters, errors = FilterParameter.generate(schema, parameters)

Apply the returned filteres by calling the `FilterParameter`'s `filter_by` staticmethod.

query = FilterParameter.filter_by(query, filters)

========
Sorting:
========

Retrieve the values from the `sort` parameter and parse it into a list.

::

    values = request.args.get('sort').split(',')

Pass both the values and the marshmallow schema to the `SortValue`'s `generate` classmethod.  Determine if the returned errors object is acceptable and raise appropriately.

::

    sorts, errors = SortValue.generate(schema, values)

Apply the returned sorts by calling the `SortValue`'s `sort_by` staticmethod.

::

    query = SortValue.sort_by(query, sorts)

==========
Including:
==========

Query the database and return a model.

::

    model = Product.query.first()

Retrieve the values from the `include` parameter and parse it into a list.

::

    values = request.args.get('include').split(',')

Pass both the values and the marshmallow schema to the `IncludeValue`'s `generate` classmethod.  Determine if the returned errors object is acceptable and raise appropriately.

::

    includes, errors = IncludeValue.generate(schema, values)

Apply the returned includes by calling the `IncludeValue`'s `include` staticmethod.

::

    serialized_result = self.include(includes, model)

Append the result to your the JSON object you intend to return.

::

    result['included'] = serialized_result
    return result
