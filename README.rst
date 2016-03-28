sqlalchemy-jsonapi-collections
==============================
A JSONAPI URL parameter handling library.

=====
Usage
=====

**Filtering collections.**

::

    from flask import request


    def filter(query, schema):
        """Extract all `filter[]` key, value pairs and filter them."""
        filters, err = FilterParameter.generate(schema, request.args)
        if err:
            self.errors.extend(err)
        return FilterParameter.filter_by(query, filters)

**Sorting collections.**

::

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

::

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

Link to docs when they're up.

============
Installation
============

`pip install git+git://github.com/caxiam/model-api.git`

============
Requirements
============
Tested with Python 2.7.

Requires:
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
