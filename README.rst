sqlalchemy-jsonapi-collections
==============================
.. image:: https://readthedocs.org/projects/sqlalchemy-jsonapi-collections/badge/?version=latest
    :target: http://sqlalchemy-jsonapi-collections.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://circleci.com/gh/caxiam/sqlalchemy-jsonapi-collections.svg?style=shield&circle-token=c2672a37e539b7cedb010c358cdb3d48eb781dbe
    :target: https://circleci.com/gh/caxiam/sqlalchemy-jsonapi-collections
.. image:: https://codeclimate.com/github/caxiam/sqlalchemy-jsonapi-collections/badges/gpa.svg
    :target: https://codeclimate.com/github/caxiam/sqlalchemy-jsonapi-collections
    :alt: Code Climate
.. image:: https://coveralls.io/repos/github/caxiam/sqlalchemy-jsonapi-collections/badge.svg?branch=master
    :target: https://coveralls.io/github/caxiam/sqlalchemy-jsonapi-collections?branch=master
    :alt: Code Coverage

A JSON:API URL parameter handling library.

=====
Usage
=====

Due to the amiguous nature of application structure jsonapiquery aims to provide core building blocks and simple defaults which can be expanded to fill a variety of usecases.  Before you can implement jsonapiquery, you must provide several key components:

- [ ] Have I created a SQL driver or can I use the one provided?
- [ ] Have I created a database schema driver or can I use the one provided?
- [ ] Do I have additional layers of my application which require a driver (such as a marshmallow schema) and have I created a driver for it?
- [ ] Have I written my implementation layer where I combine my drivers with the functions provided by jsonapiquery?

Below are several examples where you can gleam how a sample implementation would work.

**Database Layer**

.. code-block:: python

    import flask
    import jsonapiquery
    
    query, _ = jsonapiquery.filter_query(query, flask.request.args, DRIVERS)
    query, _ = jsonapiquery.sort_query(query, flask.request.args, DRIVERS)
    query, _ = jsonapiquery.include_query(query, flask.request.args, DRIVERS)
    query, _ = jsonapiquery.paginate_query(query, flask.request.args, DRIVERS)

**Serialization Layer**

By default, jsonapiquery provides "included" and "links" serialization.  "included" serialization has a hard dependency on the driver you use.

.. code-block:: python

    from flask import request

    import jsonapiquery
    
    # Construct your query and count the number of rows found prior to pagination.
    query = ...
    total = query.count()
    
    query, includes = jsonapiquery.include_query(query, request.args, DRIVERS)
    query, paginators = jsonapiquery.paginate_query(query, request.args, DRIVERS)
    
    # Fetch your models and serailize them *somehow*.  How you serialize is outside the
    # scope of this library.
    models = query.all()
    result = jsonapi_serialize(models)
    
    # Serialize JSON:API metadata.
    metadata = {
        'included': jsonapiquery.serialize_includes(includes, result),
        'links': jsonapiquery.make_pagination_links(request.base_url, paginators, request.args, total),
        'meta': {'total': total}
    }
    result.update(metadata)

**Builtin Drivers**

jsonapiquery comes with generic "sqlalchemy" and "marshmallow-jsonapi" drivers.  These drivers can be used to quickly integrate jsonapiquery into your project.  These drivers can also serve as guides when creating your own custom drivers.

.. code-block:: python

    from jsonapiquery.drivers.schema import DriverSchemaMarshmallow
    schema_driver = DriverSchemaMarshmallow(MySchema(only=('id', 'field_name')))
    
    from jsonapiquery.drivers.model import DriverModelSQLAlchemy
    model_driver = DriverModelSQLAlchemy(MyModel)
    
    # Construct a list of your drivers (of any length -- depending on your usecase).
    # The drivers are ordered by their precedence.  In this example, the schema driver
    # must run before the model driver.
    DRIVERS = [schema_driver, model_driver]
    
    # Elsewhere in your code you'll want to implement a custom query driver.  This query
    # driver is necessary to execute the necessary filters, sorts, and joins.
    class Query(jsonapiquery.database.sqlalchemy.QueryMixin, sqlalchemy.orm.Query):
        pass

**Custom Drivers**

Refer to "jsonapiquery/drivers/model/" and "jsonapiquery/drivers/schema/" for pre-built driver definitions.  These drivers can be useful in understanding the inner function of the jsonapiquery library.

.. code-block:: python

    import jsonapiquery
    
    class MyModelDriver(jsonapiquery.drivers.DriverBase):
    
        def parse_attribute(self, attribute_name, model, type):
            """Parse attribute types in this method.
            
            :params attribute_name (str): The string name of a model attribute.
            :params model: A database schema definition type.
            :params type: A namedtuple containing a set of attributes (they vary
                          depending on the URI parameter type).  Upon calling the "parse"
                          method which itself calls this method, the tuple will be
                          rewritten to contain the data generated within this method.
            """
            raise NotImplementedError

        def parse_relationship(self, relationship_name, model, type):
            raise NotImplementedError

=============
Documentation
=============

For more information visit: http://sqlalchemy-jsonapi-collections.readthedocs.org/en/latest/

============
Installation
============

::

    pip install git+git://github.com/caxiam/sqlalchemy-jsonapi-collections.git

============
Requirements
============
Tested with Python 3.6.4

=====
Links
=====
http://jsonapi.org/

=======
License
=======
Apache Version 2.0
