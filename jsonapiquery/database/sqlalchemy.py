"""SQLAlchemy jsonapi-query adapter."""
from sqlalchemy.orm import aliased, joinedload
from jsonapiquery.database import BaseQueryMixin


class QueryMixin(BaseQueryMixin):
    """SQLAlchemy query class mixin."""

    DEFAULT_LIMIT = 50
    DEFAULT_OFFSET = 0

    def apply_filters(self, filters):
        """Return a query object filtered by a set of column, value pairs."""
        for filter_ in filters:
            self = self.apply_filter(filter_)
        return self

    def apply_filter(self, filter_):
        """Return a query object filtered by a column, value pair."""
        column = filter_.attribute.attribute
        mapper = None
        for mapper in filter_.relationships:
            self = self.outerjoin(mapper.aliased_type, mapper.attribute)

        if mapper:
            column_name = column.property.class_attribute.key
            column = getattr(mapper.aliased_type, column_name)

        expressions = filter_.attribute.expression(column, filter_.value)
        return self.filter(expressions)

    def apply_sorts(self, sorts):
        """Return a query object sorted by a set of columns."""
        for sort in sorts:
            self = self.apply_sort(sort)
        return self

    def apply_sort(self, sort):
        """Return a query object sorted by a column."""
        column = sort.attribute.attribute
        mapper = None
        for mapper in sort.relationships:
            self = self.outerjoin(mapper.aliased_type, mapper.attribute)

        if mapper:
            column_name = column.property.class_attribute.key
            column = getattr(mapper.aliased_type, column_name)
        if sort.direction == '-':
            column = column.desc()
        return self.order_by(column)

    def apply_paginators(self, paginators):
        """Return a query object paginated by a limit and offset value.

        :param paginators: List of stategy and value arguments.
        """
        pagination = {
            'limit': self.DEFAULT_LIMIT,
            'offset': self.DEFAULT_OFFSET
        }
        for paginator in paginators:
            pagination[paginator.strategy] = int(paginator.value)
        if 'number' in pagination:
            limit = pagination['limit']
            pagination['offset'] = pagination['number'] * limit - limit
        return self.limit(pagination['limit']).offset(pagination['offset'])

    def apply_includes(self, includes):
        for include in includes:
            self = self.apply_include(include)
        return self

    def apply_include(self, include):
        """Implicitly join a chain of mappers."""
        opts = None
        for relationship in include.relationships:
            if not relationship.can_joinedload:
                break
            if opts is None:
                opts = joinedload(relationship.joinedload)
            else:
                opts = opts.joinedload(relationship.joinedload)
        if opts:
            self = self.options(opts)
        return self
