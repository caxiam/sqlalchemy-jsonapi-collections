# -*- coding: utf-8 -*-
from marshmallow_jsonapi.fields import BaseRelationship
from flask_sqlalchemy_jsonapi.errors import FieldError


class IncludeValue(object):

    """The IncludeValue object is responsible for validating the
    provided fields and including a properly serialized data response
    based on the relationships present on the primary resource.

    :param schema: A marshmallow schema object.
    :param value: A string value representing a relationship field on
        the provided marshmallow schema.
    :param id_field: A string representation of a SQLAlchemy model
        column primary key.
    """

    error = 'Invalid relationship specified: {}.'
    id_field = 'id'

    def __init__(self, schema, value, id_field='id'):
        field = schema._declared_fields.get(value)
        if value is None:
            raise FieldError(self.error.format(value))
        if not isinstance(field, BaseRelationship):
            raise FieldError(self.error.format(value))

        if getattr(field, 'related_schema') is None:
            raise FieldError('Unsupported include: {}.'.format(value))

        self.attribute = field.attribute or value
        self.schema = field.schema
        self.id_field = id_field

    def __call__(self, model):
        """Returns a set of serialized relationship model instances.

        :param model: A SQLAlchemy model instance.
        """
        values = getattr(model, self.attribute)
        if not isinstance(values, list):
            values = [values]

        ids = []
        for value in values:
            if isinstance(value, str) or isinstance(value, int):
                ids.append(value)
            else:
                ids.append(value.id)

        include_model = self.schema.Meta.model
        if len(ids) == 0:
            return {}

        items = include_model.query.filter(include_model.id.in_(ids)).all()
        return self.schema(many=True).dump(items).data.get('data', [])

    @classmethod
    def generate(cls, schema, values):
        errors = []
        includes = []
        for value in values:
            try:
                includes.append(cls(schema, value))
            except FieldError as exc:
                errors.append(exc.message)
        return includes, errors

    @staticmethod
    def include(includes, model):
        """An including helper function that constructs the proper
        include response.

        :param includes: A list of IncludeValue instances.
        :param model: A SQLAlchemy model instance.
        """
        included = []
        for include in includes:
            included.extend(include(model))
        return included
