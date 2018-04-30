from jsonapiquery.drivers import DriverBase


class DriverModelSQLAlchemy(DriverBase):

    def parse_attribute(self, item, model):
        return Column(item.model_attribute, model)

    def parse_relationship(self, item, model):
        return Mapper(item.model_attribute, model)


class Attribute:

    def __init__(self, attribute_name, model):
        self.attribute_name = attribute_name
        self.model = model
        self.attribute = getattr(self.model, self.attribute_name)


class Column(Attribute):

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


class Mapper(Attribute):

    @property
    def type(self):
        return self.attribute.property.mapper.class_
