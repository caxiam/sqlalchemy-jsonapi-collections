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
    def make_from_fields(cls, fields, model, default_attribute='id'):
        """Return a `Query` tuple from a list of fields."""
        if len(fields) == 0:
            return Query(None, [], []), None
        names = [field.column_name for field in fields]
        return cls.make_from_names(names, model, default_attribute)

    @classmethod
    def make_from_path(cls, path, model, default_attribute='id'):
        """Return a `Query` tuple from a dot seperated path."""
        if path == '':
            return Query(None, [], []), None
        names = path.split('.')
        return cls.make_from_names(names, model, default_attribute)

    @classmethod
    def make_from_names(cls, names, model, default_attribute='id'):
        """Return a `Query` tuple from a list of attribute names."""
        relationships = names
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
        return Query(column.column, joins, selects), column


class SQLAlchemyDriver(BaseModelDriver):
    """SQLAlchemy model driver implementation."""

    def __init__(self, name, model):
        self.column = getattr(model, name)
        self.model = model

    @property
    def is_enum(self):
        """Return `True` if the column is an `Enum` type."""
        return hasattr(self.type, 'enums')

    @property
    def is_foreign_key(self):
        """Return `True` if the column is a foreign key."""
        if self.column.property.columns[0].foreign_keys:
            return True
        return False

    @property
    def is_mapper(self):
        """Return `True` if the column is a mapper."""
        return hasattr(self.column.property, 'mapper')

    @property
    def is_primary_key(self):
        """Return `True` if the column is primary key within the table."""
        try:
            return self.column.property.columns[0].primary_key
        except AttributeError:
            return False

    @property
    def join(self):
        """Return the column's join condition.

        Typically, the join condition is just the mapper-type column.
        However, in instances where the mapper is self-referential, it
        is important to join on the backref or back-populates key.
        """
        # Re evaluating self-referential logic.
        # if self.related_class == self.model:
        #     if self.column.property.backref:
        #         return getattr(self.model, self.column.property.backref)
        #     return getattr(self.model, self.column.property.back_populates)
        return self.column

    @property
    def python_type(self):
        """Return the column's python type."""
        return self.type.python_type

    @property
    def related_class(self):
        """Return the related column class."""
        return self.column.property.mapper.class_

    @property
    def type(self):
        """Return column type."""
        return self.column.property.columns[0].type

    def get_default_strategy(self):
        """Return a strategy key based on the column's type."""
        if self.is_enum or self.is_foreign_key or self.is_primary_key:
            return 'eq'
        elif self.python_type == str:
            return 'ilike'
        return 'eq'

    def validate_strategy(self, strategy):
        """Ensure the specified strategy is appropriate."""
        if self.is_enum and strategy != 'eq':
            return False
        elif self.python_type != str and strategy in ['like', 'ilike']:
            return False
        return True
