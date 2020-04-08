from collections import namedtuple


FieldSet = namedtuple('FieldSet', ['source', 'type', 'fields'])
Filter = namedtuple('Filter', ['source', 'relationships', 'attribute', 'value'])
Include = namedtuple('Include', ['source', 'relationships'])
Sort = namedtuple('Sort', ['source', 'relationships', 'attribute', 'direction'])
Paginator = namedtuple('Paginator', ['source', 'strategy', 'value'])
