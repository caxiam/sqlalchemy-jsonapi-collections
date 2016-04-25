# -*- coding: utf-8 -*-
from jsonapi_collections.errors import FieldError


class IncludeValue(object):
    """Validate and include a given relationship field.

    The `IncludeValue` object is responsible for validating the
    provided fields and including a properly serialized data response
    based on the relationships present on the primary resource.
    """

    error = 'Invalid relationship specified: {}.'

    def __init__(self, driver, field_name, id_field='id'):
        """Validate the inputs.

        :param schema: Marshmallow schema reference.
        :param value: String name of a relationship field.
        :param id_field: Optionally specified `ID` field to query.
        """
        self.driver = driver
        self.column_name = driver.get_column_name(field_name)
        self.id_field = id_field

        field = driver.get_field(field_name)
        self.view = driver.get_related_schema(field)

        column = driver.get_column(self.column_name)
        self.model = driver.get_column_model(column)

    def __call__(self, model):
        """Dump an `IncludeValue` instance to a dictionary.

        :param model: `SQLAlchemy` model instance.
        """
        values = getattr(model, self.column_name)
        if not isinstance(values, list):
            values = [values]

        ids = []
        for value in values:
            if isinstance(value, str) or isinstance(value, int):
                ids.append(value)
            elif value is not None:
                ids.append(getattr(value, self.id_field))

        if len(ids) == 0:
            return {}
        items = self.model.query.filter(self.model.id.in_(ids)).all()
        return self.driver.serialize(self.view, items)

    @classmethod
    def generate(cls, driver, values):
        """Parse a series of strings into `IncludeValue` instances.

        :param driver: `jsonapi_collections` driver instance.
        :param values: String list of relationship fields to include.
        """
        includes = []
        errors = []
        for value in values:
            try:
                includes.append(cls(driver, value))
            except FieldError as exc:
                errors.append(exc.message)
        if errors:
            return includes, {
                "source": {"parameter": 'include'}, "detail": errors}
        return includes, None

    @staticmethod
    def include(model, includes):
        """Dump a series of `IncludeValue` instances to a dictionary.

        :param includes: List of `IncludeValue` instances.
        :param model: `SQLAlchemy` model instance.
        """
        included = []
        for include in includes:
            included.extend(include(model))
        return included
