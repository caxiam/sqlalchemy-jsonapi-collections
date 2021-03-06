from jsonapiquery import errors
from jsonapiquery.drivers import DriverBase
from sqlalchemy import orm, or_

import operator


class DriverModelSQLAlchemy(DriverBase):

    def parse_attribute(self, field, model, item):
        return Column(field.super_attribute, model, item)

    def parse_relationship(self, field, model, item):
        return Mapper(field.super_attribute, model, item)

    def __repr__(self):
        return '{}(model={})'.format(self.__class__.__name__, self.obj)


class Attribute:

    def __init__(self, attribute_name, model, item):
        self.attribute_name = attribute_name
        self.model = model
        self.item = item
        self.attribute = getattr(self.model, self.attribute_name)

    def __repr__(self):
        return '{}.{}'.format(self.model, self.attribute_name)


class Column(Attribute):

    VALUE_PARTITION = ','
    STRATEGY_PARTITION = ':'
    STRATEGIES = {
        'eq': operator.eq,
        '~eq': operator.ne,
        'ne': operator.ne,
        'gt': operator.gt,
        '~gt': operator.le,
        'gte': operator.ge,
        '~gte': operator.lt,
        'lt': operator.lt,
        '~lt': operator.ge,
        'lte': operator.le,
        '~lte': operator.gt,
        'like': lambda column, value: column.contains(value),
        '~like': lambda column, value: ~contains(column, value),
        'ilike': lambda column, value: column.ilike('%{}%'.format(value)),
        '~ilike': lambda column, value: ~like(column, value),
        'in': lambda column, value: column.in_(value),
        '~in': lambda column, value: column.notin_(value),
    }

    @property
    def column(self):
        return self.attribute.property.columns[0]

    @property
    def default_strategy(self):
        if self.is_enum or self.is_foreign_key or self.is_primary_key:
            return 'eq'
        if self.python_type == str:
            return 'ilike'
        return 'eq'

    @property
    def enums(self):
        return self.type.enums

    @property
    def is_enum(self):
        return hasattr(self.type, 'enums')

    @property
    def is_foreign_key(self):
        return bool(self.column.foreign_keys)

    @property
    def is_primary_key(self):
        return hasattr(self.column, 'primary_key')

    @property
    def type(self):
        return self.column.type

    @property
    def python_type(self):
        return self.type.python_type

    def aliased_column(self, mapper):
        column = self.attribute
        if not hasattr(column.property, 'columns'):
            raise errors.InvalidQuery(item=self.item)
        if mapper:
            column = getattr(mapper.aliased_type, self.attribute_name)
        return column

    def validate_value(self, value):
        if self.is_enum and value not in self.enums:
            return False
        return True

    def validate_strategy(self, strategy):
        if self.is_enum and strategy != 'eq':
            return False
        elif self.python_type != str and strategy in ['like', 'ilike']:
            return False
        return True

    def expression(self, column, value):
        """Return a query expression."""
        strategy_name, values = value

        if strategy_name in self.STRATEGIES:
            strategy = self.STRATEGIES[strategy_name]
        else:
            raise errors.InvalidValue('Unknown strategy specified.', self.item)

        if strategy_name in ['in', '~in']:
            return strategy(column, values)
        elif len(values) == 1:
            return strategy(column, values[0])

        expressions = [strategy(column, value) for value in values]
        return or_(*expressions)


class Mapper(Attribute):

    @property
    def can_join(self):
        """Return "True" if the mapper can be joined to a query."""
        try:
            self.type
        except errors.JSONAPIQueryError:
            return False
        else:
            return True

    @property
    def condition(self):
        """Return the mapper's join condition."""
        return self.attribute

    @property
    def type(self):
        """Return the table of the mapper."""
        try:
            return self.attribute.property.mapper.class_
        except AttributeError:
            raise errors.InvalidQuery(item=self.item)

    @property
    def aliased_type(self):
        """Return the aliased table of the mapper."""
        if not hasattr(self, '_aliased_type'):
            self._aliased_type = orm.aliased(self.type)
        return self._aliased_type
