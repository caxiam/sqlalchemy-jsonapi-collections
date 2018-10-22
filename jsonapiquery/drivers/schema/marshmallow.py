from jsonapiquery.drivers import DriverBase
from marshmallow_jsonapi import fields


class DriverSchemaMarshmallow(DriverBase):

    def parse_if_attribute(self, item, obj):
        init_kwargs = super().parse_if_attribute(item, obj)
        if hasattr(item, 'value'):
            attribute = init_kwargs['attribute']
            init_kwargs['value'] = attribute.deserialize_value(item.value)
        return init_kwargs

    def parse_attribute(self, field_name, schema):
        return Attribute(field_name, schema)

    def parse_relationship(self, field_name, schema):
        return Relationship(field_name, schema)


class Field:

    def __init__(self, field_name, schema):
        self.field_name = self.normalize_text(field_name)
        self.schema = schema
        self.field = self.schema.declared_fields[self.field_name]

    @property
    def super_attribute(self):
        return self.field.attribute or self.field_name

    def normalize_text(self, field_name):
        """Dedasherize field names."""
        return field_name.replace('-', '_')


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
        return self.field._deserialize(value, None, None)


class Relationship(Field):

    @property
    def type(self):
        if not isinstance(self.field, fields.Relationship):
            raise TypeError
        return self.field.schema

    def serialize(self, models):
        data, errors = self.type.dump(models, many=True)
        if errors:
            raise ValueError(errors)
        return data.get('data', [])
