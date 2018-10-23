from abc import ABCMeta, abstractmethod


class DriverBase(metaclass=ABCMeta):

    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return f'{self.__class__.__name__}(type={self.obj})'

    def init_type(self, item_type, **init_kwargs):
        """Initialize a new item_type.

        :param item_type: Type of namedtuple.
        :param init_kwargs: Type keyword arguments.
        """
        return item_type(**init_kwargs)

    def parse(self, item):
        """Return a new typed item instance."""
        relationships, obj = self.parse_relationships(item, self.obj)

        init_kwargs = item._asdict()
        init_kwargs['source'] = item
        init_kwargs['relationships'] = relationships
        init_kwargs.update(self.parse_if_attribute(item, obj))

        return self.init_type(type(item), **init_kwargs)

    def parse_relationships(self, item, obj):
        relationships = []
        for relationship in item.relationships:
            relationship = self.parse_relationship(relationship, obj, item)
            relationships.append(relationship)
            obj = relationship.type
        return relationships, obj

    def parse_if_attribute(self, item, obj):
        init_kwargs = {}
        if hasattr(item, 'attribute'):
            attribute = self.parse_attribute(item.attribute, obj, item)
            init_kwargs['attribute'] = attribute
        return init_kwargs

    @abstractmethod
    def parse_attribute(self, attribute, type, item):
        return None

    @abstractmethod
    def parse_relationship(self, relationship, type, item):
        return None


from .model import *
from .schema import *
