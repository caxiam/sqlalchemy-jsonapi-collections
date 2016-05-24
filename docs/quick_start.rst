.. _quick_start:

Quick Start
===========

====================
Managing Collections
====================

To manage a query collection, instantiate a `Collection` object with the `model` and `parameters` arguments specified.

::

    from jsonapi_collections import Collection

    params = {'sort': 'attr_1,attr_2', 'filter[attr_1]': 'test'}
    c = Collection(my_model, params)

You can optionally specify `driver` and `schema` arguments.  The driver acts as an intermediary between properity method calls.  The driver bindings supply a simple interface for the filter, sort, and include classes while also providing developers with the ability to use their own schema implementations.

With your collection instantiated, we can now create query filters and sorts.

**Filtering**

To filter we call the `filter_query` method.

::

    query = c.filter_query(query)

This will return a permutated query object or raise a `JSONAPIError`.

**Sorting**

To sort we call the `sort_query` method.

::

    query = c.sort_query(query)

This will return a permutated query object or raise a `JSONAPIError`.

================
Creating Drivers
================

Drivers are a crucial part of the `jsonapi_collections` ecosystem.  To create your own driver for a custom schema implementation you need to complete the following:

First, you must create a class the inherits from the `BaseDriver`.
Second, you must override the unimplemented methods provided by the `BaseDriver`.

Once you have a driver, you can pass a reference to the object in the `Collection` initialization process.  If the driver requires the use of a proprietary schema, then you need to pass that schema into the `Collection` object.

::

    c = Collection(my_model, params, MyCustomDriver, my_optional_schema)
