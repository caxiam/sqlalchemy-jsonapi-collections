"""SQLAlchemy jsonapi-query adapter."""
from src.database import BaseQueryMixin


class QueryMixin(BaseQueryMixin):
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
            if negated:
                return self.filter(~column.in_(values))
            return self.filter(column.in_(values))

        if strategy == 'eq':
            strategy = self._filter_eq
        elif strategy == 'gt':
            strategy = self._filter_gt
        elif strategy == 'gte':
            strategy = self._filter_gte
        elif strategy == 'lt':
            strategy = self._filter_lt
        elif strategy == 'lte':
            strategy = self._filter_lte
        elif strategy == 'like':
            strategy = self._filter_like
        elif strategy == 'ilike':
            strategy = self._filter_ilike
        else:
            raise ValueError('Invalid query strategy: {}'.format(strategy))

        filters = self._get_filters(column, values, strategy, negated)
        return self.filter(filters)

    def _get_filters(self, column, values, strategy, negated=False):
        filters = None
        for value in values:
            expression = strategy(column, value)
            if negated:
                expression = ~expression
            if filters is None:
                filters = expression
            else:
                filters = filters | expression
        return filters

    def _filter_eq(self, column, value):
        return column == value

    def _filter_gt(self, column, value):
        return column > value

    def _filter_gte(self, column, value):
        return column >= value

    def _filter_lt(self, column, value):
        return column < value

    def _filter_lte(self, column, value):
        return column <= value

    def _filter_like(self, column, value):
        return column.contains(value)

    def _filter_ilike(self, column, value):
        return column.ilike('%{}%'.format(value))

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
