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

A JSONAPI URL parameter handling library.

=====
Usage
=====

**Filtering collections.**


.. code-block:: python

    from flask import request


    def filter(query, schema):
        """Extract all `filter[]` key, value pairs and filter them."""
        filters, err = FilterParameter.generate(schema, request.args)
        if err:
            self.errors.extend(err)
        return FilterParameter.filter_by(query, filters)

**Sorting collections.**


.. code-block:: python

    from flask import request


    def sort(query, schema):
        """Get the value of the sort parameter, generate some SortValue
        instances and return a sorted query.
        """
        fields = request.args.get('sort')
        if not fields:
            return query

        sorts, err = SortValue.generate(schema, fields.split(','))
        if err:
            raise Exception(err)
        return SortValue.sort_by(query, sorts)

**Including resources.**


.. code-block:: python

    from flask import request


    def include(model, schema):
        """Get the value of the include parameter and include related
        resources.
        """
        fields = request.args.get('include')
        if not fields:
            return []

        includes, errors = IncludeValue.generate(schema, fields.split(','))
        if errors:
            raise Exception(errors)
        return IncludeValue.include(includes, model)

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
Tested with Python 2.7.

**Requires:**

* Flask
* Marshmallow
* Marshmallow-JSONAPI
* SQLAlchemy

=====
Links
=====
http://jsonapi.org/

=======
License
=======
MIT
