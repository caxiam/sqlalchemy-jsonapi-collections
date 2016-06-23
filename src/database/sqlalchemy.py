"""SQLAlchemy jsonapi-query adapter."""
from sqlalchemy import or_


class QueryMixin(object):
    """SQLAlchemy query class mixin."""

    default_limit = 50
    default_offset = 0

    def apply_filters(self, filters):
        """Return a query object filtered by a set of column, value pairs.

        :param filters: Triple of column, strategy, and values arguments.
        """
        for column, strategy, values in filters:
            self = self.apply_filter(column, strategy, values)
        return self

    def apply_filter(self, column, strategy, values):
        """Return a query object filtered by a column, value pair.

        :param column: SQLAlchemy column object.
        :param strategy: Query filter string name reference.
        :param values: List of typed values.
        """
        negated = strategy.startswith('~')
        if negated:
            strategy = strategy[1:]

        if strategy == 'in':
            return self.filter(column.in_(values))

        expressions = []
        for value in values:
            if strategy == 'eq':
                expression = column == value
            elif strategy == 'gt':
                expression = column > value
            elif strategy == 'gte':
                expression = column >= value
            elif strategy == 'lt':
                expression = column < value
            elif strategy == 'lte':
                expression = column <= value
            elif strategy == 'like':
                expression = column.contains(value)
            elif strategy == 'ilike':
                expression = column.ilike('%{}%'.format(value))
            else:
                raise ValueError('Invalid query strategy: {}'.format(strategy))
            if negated:
                expression = ~expression
            expressions.append(expression)
        return self.filter(or_(*expressions))

    def apply_sorts(self, sorts):
        """Return a query object sorted by a set of columns.

        :param sorts: Triple of direction, column, and table arguments.
        """
        for direction, column, table in sorts:
            self.apply_sort(direction, column, table)
        return self

    def apply_sort(self, column, direction, table=None):
        """Return a query object sorted by a column.

        :param column: SQLAlchemy column object.
        :param direction: Query sort direction reference.
        :param table: String reference to SQLAlchemy table name.
        """
        if direction == '-':
            column = column.desc()
        if table is not None:
            self = self.join(table)
        return self.order_by(column)

    def apply_paginators(self, paginators):
        """Return a query object paginated by a limit and offset value.

        :param paginators: List of stategy and value arguments.
        """
        pagination = {
            'limit': self.default_limit,
            'offset': self.default_offset
        }
        pagination.update({strategy: value for strategy, value in paginators})
        if 'number' in pagination:
            limit = pagination['limit']
            pagination['offset'] = pagination['number'] * limit - limit
        return self.limit(pagination['limit']).offset(pagination['offset'])
