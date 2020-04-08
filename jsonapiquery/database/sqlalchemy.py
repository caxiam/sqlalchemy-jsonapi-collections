"""SQLAlchemy jsonapi-query adapter."""
from jsonapiquery import errors
from jsonapiquery.database import BaseQueryMixin
from sqlalchemy.orm import aliased, joinedload


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
        self, column = self.recurse_to_column(filter_)
        expressions = filter_.attribute.expression(column, filter_.value)
        return self.filter(expressions)

    def apply_sorts(self, sorts):
        """Return a query object sorted by a set of columns."""
        for sort in sorts:
            self = self.apply_sort(sort)
        return self

    def apply_sort(self, sort):
        """Return a query object sorted by a column."""
        self, column = self.recurse_to_column(sort)
        if sort.direction == '-':
            column = column.desc()
        return self.order_by(column)

    def apply_paginators(self, paginators, max_size=None):
        """Return a query object paginated by a limit and offset value.

        :param paginators: List of stategy and value arguments.
        """
        pagination = {
            'limit': self.DEFAULT_LIMIT,
            'offset': self.DEFAULT_OFFSET
        }
        for paginator in paginators:
            try:
                value = int(paginator.value)

                # Raise if the maximum page size was exceeded.
                if max_size is not None and \
                        paginator.strategy in ['limit', 'number'] and \
                        value > max_size:
                    raise ValueError('Maximum query size exceeded.')

                pagination[paginator.strategy] = value
            except ValueError:
                raise errors.InvalidPaginationValue(item=paginator)
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
        for mapper in include.relationships:
            if not mapper.can_join:
                break
            if opts is None:
                opts = joinedload(mapper.condition)
            else:
                opts = opts.joinedload(mapper.condition)
        if opts:
            self = self.options(opts)
        return self

    def recurse_to_column(self, item):
        mapper = None
        for mapper in item.relationships:
            self = self.outerjoin(mapper.aliased_type, mapper.condition)

        column = item.attribute.aliased_column(mapper)
        return self, column
