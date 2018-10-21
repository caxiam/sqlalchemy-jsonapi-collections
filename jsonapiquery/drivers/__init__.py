from abc import ABCMeta, abstractmethod


class DriverBase(metaclass=ABCMeta):

    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return '{}(type={})'.format(self.__class__.__name__, self.obj)

    def init_type(self, type, **init_kwargs):
        """Initialize a new type.

        :param type: Type of namedtuple.
        :param init_kwargs: Type keyword arguments.
        """
        return type(**init_kwargs)

    def parse(self, item):
        """Return a new typed item instance."""
        obj = self.obj

        relationships = []
        for relationship in item.relationships:
            relationship = self.parse_relationship(relationship, obj)
            relationships.append(relationship)
            obj = relationship.type

        init_kwargs = item._asdict()
        init_kwargs['relationships'] = relationships
        if hasattr(item, 'attribute'):
            attribute = self.parse_attribute(item.attribute, obj)
            init_kwargs['attribute'] = attribute
        return self.init_type(type(item), **init_kwargs)

    @abstractmethod
    def parse_attribute(self, attribute, type):
        return None

    @abstractmethod
    def parse_relationship(self, relationship, type):
        return None


from .model import *
from .schema import *
