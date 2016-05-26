# -*- coding: utf-8 -*-
from jsonapi_collections.errors import FieldError


class IncludeValue(object):
    """Validate and include a given relationship field.

    The `IncludeValue` object is responsible for validating the
    provided fields and including a properly serialized data response
    based on the relationships present on the primary resource.
    """

    def __init__(self, driver, field_name):
        """Validate the inputs.

        :param schema: Marshmallow schema reference.
        :param value: String name of a relationship field.
        :param id_field: Optionally specified `ID` field to query.
        """
        self.driver = driver
        self.field_name = field_name

    def __call__(self, model):
        """Return the serailized output of a related field."""
        data = self._get_included_values(
            self.field_name.split('.'), self.driver.collection.schema, [model])
        return data

    def _get_included_values(self, path, schema, values):
        """Return a set of model instances and a related serializer.

        :param path: List of schema field names.
        :param schema: Serializer class object.
        :param values: List of `SQLAlchemy` model instances.
        """
        data = []
        for field_name in path:
            column_name = self.driver.get_column_name(field_name, schema)
            values = self._get_nested_values(values, column_name)
            field = self.driver.get_field(field_name, schema)
            schema = self.driver.get_related_schema(field)
            data.extend(self.driver.serialize(schema, values))
        return data

    def _get_nested_values(self, values, name):
        """Return a set of `SQLAlchemy` model instances.

        This method iterates through a set of relationships and returns
        the value of each relationship's specified attribute in a
        combined set.

        This method normalizes the value of each relationship to ensure
        it is of a list-type.  `None` type relationships are skipped
        and `one-to-many` and `one-to-one` relationships are typed as a
        list.

        :param values: List of `SQLAlchemy` model instances.
        :param name: String name of the relationship column to extract.
        """
        new_values = []
        for value in values:
            relationship = getattr(value, name)
            if relationship is None:
                continue
            elif not isinstance(relationship, list):
                relationship = [relationship]
            new_values.extend(relationship)
        return new_values

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
            return [], {"source": {"parameter": 'include'}, "detail": errors}
        return includes, {}

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
