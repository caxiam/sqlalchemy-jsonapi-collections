from jsonapiquery import errors
from jsonapiquery.drivers import DriverBase
from marshmallow import ValidationError
from marshmallow_jsonapi import fields


class DriverSchemaMarshmallow(DriverBase):

    def parse_if_attribute(self, item, obj):
        init_kwargs = super().parse_if_attribute(item, obj)
        if hasattr(item, 'value'):
            attribute = init_kwargs['attribute']
            init_kwargs['value'] = attribute.deserialize_value(item.value)
        return init_kwargs

    def parse_attribute(self, field_name, schema, item):
        return Attribute(field_name, schema, item)

    def parse_relationship(self, field_name, schema, item):
        return Relationship(field_name, schema, item)

    def __repr__(self):
        return '{}(schema={})'.format(self.__class__.__name__, self.obj)


class Field:

    def __init__(self, field_name, schema, item):
        self.request_name = field_name
        self.field_name = self.normalize_text(field_name)
        self.item = item
        self.schema = schema

        try:
            self.field = self.schema.declared_fields[self.field_name]
        except KeyError:
            message = 'Invalid field specified: {}.'.format(self.request_name)
            raise errors.InvalidPath(message, self.item)

    @property
    def super_attribute(self):
        return self.field.attribute or self.field_name

    def normalize_text(self, field_name):
        """Dedasherize field names."""
        return field_name.replace('-', '_')

    def __repr__(self):
        return '{}.{}'.format(self.schema, self.field_name)


class Attribute(Field):
    DEFAULT_STRATEGY_TYPE = 'eq'
    STRATEGY_TYPES = [
        'eq', '~eq', 'ne', 'gt', '~gt', 'gte', '~gte', 'lt', '~lt', 'lte',
        '~lte', 'like', '~like', 'ilike', '~ilike', 'in', '~in']
    STRATEGY_PARTITION = ':'
    VALUE_PARTITION = ','

    def deserialize_value(self, value):
        """Deserialize a string value to the appropriate type."""
        strategy, separator, value = value.partition(self.STRATEGY_PARTITION)
        if separator == '':
            strategy, value = self.DEFAULT_STRATEGY_TYPE, strategy
        elif strategy not in self.STRATEGY_TYPES:
            strategy = self.DEFAULT_STRATEGY_TYPE
            value = '{}{}{}'.format(strategy, separator, value)

        values = value.split(self.VALUE_PARTITION)
        values = [self._deserialize_value(value) for value in values]
        return strategy, values

    def _deserialize_value(self, value):
        if value == '':
            return None

        try:
            return self.field._deserialize(value, None, None)
        except ValidationError:
            message = 'Invalid value for field type.'
            raise errors.InvalidValue(message, self.item)


class Relationship(Field):

    @property
    def type(self):
        try:
            return self.field.schema
        except AttributeError:
            message = 'Field "{}" is not a relationship.'.format(self.request_name)
            raise errors.InvalidFieldType(message, self.item)

    def serialize(self, models):
        data, errors = self.type.dump(models, many=True)
        if errors:
            raise ValueError(errors)
        return data.get('data', [])
