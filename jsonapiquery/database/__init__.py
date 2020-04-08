from abc import abstractmethod, ABCMeta


class BaseQueryMixin(metaclass=ABCMeta):
    """Base query class mixin."""

    @abstractmethod
    def apply_filters(self):
        return

    @abstractmethod
    def apply_filter(self):
        return

    @abstractmethod
    def apply_sorts(self):
        return

    @abstractmethod
    def apply_sort(self):
        return

    @abstractmethod
    def apply_paginators(self):
        return
