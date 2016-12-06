.. _quick_start:

Quick Start
===========

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

To use the JSONAPIQuery class, you must first define a subclass of it with the "model_driver" and "view_driver" attributes defined.  With your newly created orchestration subclass, initialize the class with the requested query parameters, the model class to query from, and the view class to parse the request arguments with.

::

    from jsonapiquery import JSONAPIQuery
    from jsonapiquery.drivers.model import SQLAlchemyDriver
    from jsonapiquery.drivers.view import MarshmallowDriver


    class MyJSONAPIQuery(JSONAPIQuery):
        model_driver = SQLAlchemyDriver
        view_driver = MarshmallowDriver


    jsonapiquery = MyJSONAPIQuery(query_parameters, PersonModel, PersonView)

It should be noted that the orchestration object is entirely optional.  You do not have to use the drivers, the database mixin, or the URL parsing module.  Everything within this library is optional.

Filtering
=========

**Loading filter field sets:**

Initialize the JSONAPIQuery orchestration class with a parameters dictionary containing filters.  You must also specify the model to query from and the view to validate the parameters against.  The model and view can be any Python object from any library.

::

    jsonapiquery = JSONAPIQuery({'filter[age]': 'lt:10'}, model, view)
    field_sets, errors = jsonapiquery.make_filter_fields()

**Building query filters:**

::

    filters = []
    for field_set in field_sets:
        query, driver = jsonapiquery.make_query_from_fields(field_set.fields)
        filters.append((query.column, field_set.strategy, field_set.values, query.joins))

**Applying query filters:**

::

    # Using the SQLAlchemy database driver
    response = session.query(AbcModel).apply_filters(filters).all()

Sorting
=======

**Loading sort field sets:**

::

    jsonapiquery = JSONAPIQuery({'sort': 'last-name,first-name,-age'}, model, view)
    field_sets, errors = jsonapiquery.make_sort_fields()

**Building query sorts:**

::

    sorts = []
    for field_set in field_sets:
        query, driver = jsonapiquery.make_query_from_fields(field_set.fields)
        sorts.append((query.column, field_set.direction, query.joins))

**Applying query sorts:**

::

    # Using the SQLAlchemy database driver
    response = session.query(AbcModel).apply_sorts(sorts).all()

Compounding
===========

**Loading include field sets:**

::

    jsonapiquery = JSONAPIQuery({'include': 'student.school,parents'}, model, view)
    field_sets, errors = jsonapiquery.make_include_fields()

**Building query includes:**

::

    code

**Applying query includes:**

::

    # Using the SQLAlchemy database driver
    response = session.query(AbcModel).include(sorts).all()

Pagination
==========

**Loading pagination field sets:**

::

    jsonapiquery = JSONAPIQuery({'page[limit]': 1, 'page[offset]': 1}, model, view)

**Applying query pagination:**

::

    # Using the SQLAlchemy database driver
    response = session.query(AbcModel).apply_paginators(jsonapiquery.paginators).all()
