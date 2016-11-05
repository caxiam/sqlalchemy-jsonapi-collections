from collections import namedtuple


"""Query namedtuple.

The `column` key contains a reference to the column to be filtered or
sorted against.  The column is unnecessary for include operations.

The `joins` key contains a list of relationship mappings.  The
mappings are used to join the query against the appropriate foreign
keys.  Joins are required for all operation types.

The `selects` key contains a list of tables to select from. Selects
are only used within include operations.
"""
Query = namedtuple('Query', ['column', 'joins', 'selects'])


class BaseModelDriver(object):
    """Base model driver."""

    @classmethod
    def factory(cls, path, model, default_attribute='id'):
        """Return a list of `Column` instances."""
        if path == '':
            return Query(None, [], [])

        relationships = path.split('.')
        attribute = relationships.pop()

        joins = []
        selects = []
        for relationship in relationships:
            column = cls(relationship, model)
            joins.append(column.join)
            model = column.related_class
            selects.append(model)

        column = cls(attribute, model)
        if column.is_mapper:
            joins.append(column.join)
            model = column.related_class
            selects.append(model)
            column = cls(default_attribute, model)
        return Query(column.column, joins, selects)
