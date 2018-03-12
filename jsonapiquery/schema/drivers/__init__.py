from abc import ABCMeta, abstractmethod


def remove_inflection(text):
    """Replace hyphens with underscores."""
    return text.replace('-', '_')


class SchemaDriverBase(metaclass=ABCMeta):

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
        
        if item.attribute:
            attribute = self.parse_attribute(item.attribute, schema)
        else:
            attribute = None
        return relationships, attribute

    @abstractmethod
    def parse_attribute(self, field_name, schema):
        return None

    @abstractmethod
    def parse_relationship(self, field_name, schema):
        return None
