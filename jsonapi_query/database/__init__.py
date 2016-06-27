

class BaseQueryMixin(object):
    """Base query class mixin."""

    def apply_filters(self):
        raise NotImplementedError

    def apply_filter(self):
        raise NotImplementedError

    def apply_sorts(self):
        raise NotImplementedError

    def apply_sort(self):
        raise NotImplementedError

    def apply_paginators(self):
        raise NotImplementedError
