"""SQLAlchemy jsonapi-query adapter."""
from sqlalchemy.orm import aliased
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
        :param joins: List of SQLAlchemy mapper objects.
        """
        column, classes = self._alias_mappers(column, joins)
        for pos, class_ in enumerate(classes):
            self = self.join(class_, joins[pos])

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
        column, classes = self._alias_mappers(column, joins)
        for pos, class_ in enumerate(classes):
            self = self.join(class_, joins[pos])

        if direction == '-':
            column = column.desc()
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

    def include(self, mappers):
        """Return an additional set of data with the query.

        For a given query, join a set of mappers and select an aliased
        entity.  The mappers may chain off one another.

        This method does not return a stable data-type.  If no mappers
        are included, the response type will be a model instance or a
        list of model instances.  With a set of mappers a tuple or set
        of tuples will be returned of length `mappers` + 1.

        Note, if at any point you intend to use `filter_by(column=value)`,
        it is highly recommend you call it prior to calling the include
        method. Using `filter_by` will select from the most recently
        joined aliased model.  Using `filter(Model.column == value)` is
        safe and will filter as expected.

        :param mappers: A list of SQLAlchemy mapper objects.
        """
        if mappers == []:
            return self

        selects = [aliased(_get_mapper_class(mapper)) for mapper in mappers]
        for pos, select in enumerate(selects):
            self = self.join(select, mappers[pos]).add_entity(select)
        return self

    def _alias_mappers(self, column, mappers):
        classes = [aliased(_get_mapper_class(mapper)) for mapper in mappers]
        for pos, class_ in enumerate(classes):
            if column.class_ == _get_aliased_class(class_):
                column = getattr(class_, column.property.class_attribute.key)
        return column, classes


def group_and_remove(items, models):
    """Group and restructure a list of tuples by like items.

    This function groups a list of tuples by their model type.  Tuple
    members that do not match any of the provided models will be not
    be returned.

    :param items: A list of rows containing column tuples.
    :param models: A list of SQLAlchemy model classes.
    """
    response = []
    for model in models:
        response.append([])
    for item in items:
        for member in item:
            position = models.index(member.__class__)
            if member not in response[position]:
                response[position].append(member)
    return response


def _get_aliased_class(x):
    return x._aliased_insp.class_


def _get_mapper_class(mapper):
    return mapper.property.mapper.class_
