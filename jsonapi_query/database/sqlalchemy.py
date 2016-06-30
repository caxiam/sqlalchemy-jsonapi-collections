"""SQLAlchemy jsonapi-query adapter."""
from jsonapi_query.database import BaseQueryMixin


class QueryMixin(BaseQueryMixin):
    """SQLAlchemy query class mixin."""

    default_limit = 50
    default_offset = 0

    def apply_filters(self, filters):
        """Return a query object filtered by a set of column, value pairs.

        :param filters: Triple of column, strategy, and values arguments.
        """
        for column, strategy, values, joins in filters:
            self = self.apply_filter(column, strategy, values, joins)
        return self

    def apply_filter(self, column, strategy, values, joins=[]):
        """Return a query object filtered by a column, value pair.

        :param column: SQLAlchemy column object.
        :param strategy: Query filter string name reference.
        :param values: List of typed values.
        :param joins: List of SQLAlchemy model objects.
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
        for join in joins:
            self = self.join(join)
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

        :param sorts: Triple of direction, column, and joins arguments.
        """
        for direction, column, joins in sorts:
            self = self.apply_sort(direction, column, joins)
        return self

    def apply_sort(self, column, direction, joins=[]):
        """Return a query object sorted by a column.

        :param column: SQLAlchemy column object.
        :param direction: Query sort direction reference.
        :param join: List of SQLAlchemy model objects.
        """
        if direction == '-':
            column = column.desc()
        for join in joins:
            self = self.join(join)
        return self.order_by(column)

    def apply_paginators(self, paginators):
        """Return a query object paginated by a limit and offset value.

        :param paginators: List of stategy and value arguments.
        """
        pagination = {
            'limit': self.default_limit,
            'offset': self.default_offset
        }
        pagination.update({
            strategy: int(value) for strategy, value in paginators})
        if 'number' in pagination:
            limit = pagination['limit']
            pagination['offset'] = pagination['number'] * limit - limit
        return self.limit(pagination['limit']).offset(pagination['offset'])


def include(session, model, columns, ids):
    """Query a list of models restricted by the filter_model's ID.

    :param session: SQLAlchemy query session.
    :param models: A list of SQLAlchemy model objects.
    :param filter_model: SQLAlchemy model object.
    :param ids: A list of IDs to filter by.
    """
    if columns == [] or ids == []:
        return []

    query = session.query(*columns).join(model).filter(model.id.in_(ids))
    if len(columns) > 1:
        for column in columns[1:]:
            query = query.join(column)
    return group_by_column(query.all())


def group_by_column(items):
    """Group a tuple of different columns into lists of like columns.

    Items is submitted as a list of tuples: [(1, 2), (3, 4)].  It is
    returned as a list of lists: [[1, 3], [2, 4]].  The items are
    grouped by their position within the tuple.

    :param items: List of tuples.
    """
    if isinstance(items[0], tuple):
        return _group_by_many(items)
    return _group_by_single(items)


def _group_by_many(items):
    rows = []
    for i in range(len(items[0])):
        rows.append([])
    for item in items:
        for position, member in enumerate(item):
            rows[position].append(member)
    return rows


def _group_by_single(items):
    rows = [[]]
    for item in items:
        rows[0].append(item)
    return rows
