from abc import ABCMeta, abstractmethod
from collections import namedtuple


ModelResult = namedtuple('ModelResult', ['relationships', 'attribute'])


class ModelDriverBase(metaclass=ABCMeta):

    def __init__(self, schema):
        self.schema = schema

    def __repr__(self):
        return '{}(schema={})'.format(self.__class__.__name__, self.schema)

    def parse(self, item):
        relationships = []
        schema = self.schema
        for relationship in item.relationships:
            relationship = self.parse_relationship(relationship, schema)
            relationships.append(relationship)
            schema = relationship.type
        else:
            attribute = self.parse_attribute(item.attribute, schema)
        return ModelResult(relationships, attribute)

    @abstractmethod
    def parse_attribute(self, field_name, schema):
        return None

    @abstractmethod
    def parse_relationship(self, field_name, schema):
        return None
