.. _quick_start:

***********
Quick Start
***********

Setup
=====

**Creating a session factory:**

Using SQLAlchemy as our example, import the "Query" class from SQLAlchemy and the "QueryMixin" class from the jsonapiquery database module.  Create a "BaseClass" and use it within the session factory "sessionmaker" function.

::

    from jsonapiquery.database.sqlalchemy import QueryMixin
    from sqlalchemy.orm import Query, sessionmaker


    class BaseQuery(QueryMixin, Query):
        pass


    session_factory = sessionmaker(bind=engine, query_cls=BaseQuery)
    session = session_factory()

**Initializing JSONAPIQuery:**

To use the JSONAPIQuery class, you must first define a subclass of it with the "model_driver" and "view_driver" attributes defined as well as the "make_errors", "serialize_included" abstractmethods.  With your newly created orchestration subclass, initialize the class with the requested query parameters, the model class to query from, and the view class to parse the request arguments with.

::

    from jsonapiquery import JSONAPIQuery
    from jsonapiquery.drivers.model import SQLAlchemyDriver
    from jsonapiquery.drivers.view import MarshmallowDriver


    class MyJSONAPIQuery(JSONAPIQuery):
        model_driver = SQLAlchemyDriver
        view_driver = MarshmallowDriver

        def make_errors(self, errors):
            return MyExceptionClass(errors)

        def serialize_included(self, schema, models):
            return schema.dump(models, many=True).data['data']


    jsonapiquery = MyJSONAPIQuery(query_parameters, PersonModel, PersonView)

It should be noted that the orchestration object is entirely optional.  You do not have to use the drivers, the database mixin, or the URL parsing module.  Everything within this library is optional.

Quick Handling
==============

For quick JSONAPI query handling, the "make_query" method can be used to automatically handle parameter errors.  The "make_errors" method is used to raise the generated errors and the "serialize_included" method is used to serialized the included rows.

"make_query" accepts two parameters: an ORM query object and a dictionary of query options.

::

    options = {
        "can_compound": True,
        "can_filter": False,
        "can_paginate": False,
        "can_sort": True
    }
    jsonapiquery = JSONAPIQuery({}, model, view)
    return query, total, selects, schemas = jsonapiquery.make_query(query, options)

Filtering
=========

The "filter" method accepts an ORM query object as its first parameter and optionally allows an errors list to be passed to it.  If errors are raised during execution, they will be added to the provided errors list and returned.

::

    jsonapiquery = JSONAPIQuery({'filter[age]': 'lt:10'}, model, view)
    query, errors = jsonapiquery.filter(query)

Sorting
=======

The "sort" method accepts an ORM query object as its first parameter and optionally allows an errors list to be passed to it.  If errors are raised during execution, they will be added to the provided errors list and returned.

::

    jsonapiquery = JSONAPIQuery({'sort': 'last-name,first-name,-age'}, model, view)
    query, errors = jsonapiquery.sort(query)

Including
=========

The "include" method accepts an ORM query object as its first parameter and optionally allows an errors list to be passed to it.  If errors are raised during execution, they will be added to the provided errors list and returned.

Additionally, the "include" method returns a set of models and schemas.  These models and schemas are used to serailize the included relationships.

::

    jsonapiquery = JSONAPIQuery({'include': 'student.school,parents'}, model, view)
    query, models, schemas, errors = jsonapiquery.include(query)

Construction of the document can be done using the "make_included_response" method.  The method accepts three arguments: the response dictionary, the models to serialize and the schemas to serialize them with.

::

    models = [[<ModelA1>, <ModelA2>], [<ModelB1>]]
    schemas = [<SchemaA()>, <SchemaB()>]
    response = jsonapiquery.make_included_response({}, models, schemas)
    """
    The "included" list will contain each other the models
    serialized by the appropriate schema.

    response = {
        'included': [
            {'id': '1', 'type': 'teachers'},
            {'id': '2', 'type': 'teachers'},
            {'id': '1', 'type': 'students'}
        ]
    }
    """

Paginating
==========

The "paginate" method accepts an ORM query object as its first parameter and optionally allows an errors list to be passed to it.  If errors are raised during execution, they will be added to the provided errors list and returned.

Additionally, the "paginate" method returns a total value.  The total value is used to populate the "meta" object.

::

    jsonapiquery = JSONAPIQuery({"page[limit]": 1, "page[offset]": 2}, model, view)
    query, total, errors = jsonapiquery.paginate(query)

Construction of the document can be done using the "make_paginated_response" method.  The method accepts three arguments: the response dictionary, the base request URL, and the row count.

::

    base_url = "http://site.com/api/v1/endpoint"
    total = 1000
    response = jsonapiquery.make_paginated_response({"data": []}, base_url, total)
    """
    The "links" object and "meta" object have been added to the
    provided response object.  In a machine generated result, the
    individual URLs will be encoded.

    response = {
        "links": {
            "first": "http://site.com/api/v1/endpoint?page[limit]=1&page[offset]=0",
            "last": "http://site.com/api/v1/endpoint?page[limit]=1&page[offset]=999",
            "next": "http://site.com/api/v1/endpoint?page[limit]=1&page[offset]=3",
            "prev": "http://site.com/api/v1/endpoint?page[limit]=1&page[offset]=1",
            "self": "http://site.com/api/v1/endpoint",
        },
        "meta": {"total": 1000},
        "data": []
    }
    """
