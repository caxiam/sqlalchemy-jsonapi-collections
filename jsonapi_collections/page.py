# -*- coding: utf-8 -*-
"""JSONAPI pagination implementation.

This module validates, exposes, and acts upon pagination related data.
"""
import urllib


class Pagination(object):
    _limit = 100
    _offset = 0

    def __init__(self, parameters):
        self.parameters = parameters

    @property
    def limit(self):
        """The amount to limit a query by."""
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    @property
    def offset(self):
        """The amount to offset a query by."""
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def strategy_limit(self):
        """Return the valid keys for a limit and offset based strategy."""
        return ['page[limit]', 'page[offset]']

    @property
    def strategy_page(self):
        """Return the valid keys for a page based strategy."""
        return ['page[size]', 'page[number]']

    @property
    def strategy_cursor(self):
        """Return the valid keys for a cusor based strategy.

        Cursor based strategies have not been implemented.
        """
        return ['page[cursor]']

    def get_links_object(self, base_url, total):
        """Return a pagination links object."""
        def get_page(offset):
            if offset == 0:
                return 1
            return (offset / self.limit) + 1

        parameters = self.parameters
        if ('page[offset]' not in parameters and
                'page[number]' not in parameters):
            parameters['page[offset]'] = self.offset
        if 'page[limit]' not in parameters and 'page[size]' not in parameters:
            parameters['page[limit]'] = self.limit

        last_offset = total - self.limit
        next_offset = min(self.offset + self.limit, total - self.limit)
        prev_offset = max(self.offset - self.limit, 0)

        self_params = urllib.urlencode(parameters)

        first_obj = parameters
        first_obj = self._update_if_exists('page[offset]', 0, first_obj)
        first_obj = self._update_if_exists('page[number]', 1, first_obj)
        first_params = urllib.urlencode(first_obj)

        last_obj = parameters
        last_obj = self._update_if_exists(
            'page[offset]', last_offset, last_obj)
        last_obj = self._update_if_exists(
            'page[number]', get_page(last_offset), last_obj)
        last_params = urllib.urlencode(last_obj)

        next_obj = parameters
        next_obj = self._update_if_exists(
            'page[offset]', next_offset, next_obj)
        next_obj = self._update_if_exists(
            'page[number]', get_page(next_offset), next_obj)
        next_params = urllib.urlencode(next_obj)

        prev_obj = parameters
        prev_obj = self._update_if_exists(
            'page[offset]', prev_offset, prev_obj)
        prev_obj = self._update_if_exists(
            'page[number]', get_page(prev_offset), prev_obj)
        prev_params = urllib.urlencode(prev_obj)

        return {
            'self': '{}?{}'.format(base_url, self_params),
            'first': '{}?{}'.format(base_url, first_params),
            'last': '{}?{}'.format(base_url, last_params),
            'next': '{}?{}'.format(base_url, next_params),
            'prev': '{}?{}'.format(base_url, prev_params)
        }

    def get_pagination_values(self):
        """Return the limit and offset values."""
        return self.limit, self.offset

    def set_pagination_values(self):
        """Set the limit and offset values."""
        pagination_keys = self._extract_pagination_keys()
        for key in pagination_keys:
            value = self.parameters.get(key)
            if not value:
                continue
            if key in ['page[limit]', 'page[size]']:
                self.limit = int(value)
            else:
                self.offset = int(value)
        if 'page[number]' in pagination_keys:
            self.offset = max(self.offset * self.limit - self.limit, 1)
        return self

    def paginate_query(self, query):
        """Return a paginated query object."""
        return query.offset(self.offset).limit(self.limit)

    def validate_parameters(self):
        """Validate the provided pagination strategy."""
        errors = []
        pagination_keys = self._extract_pagination_keys()
        errors.extend(self._validate_pagination_keys(pagination_keys))
        errors.extend(self._validate_pagination_values(pagination_keys))
        return errors

    def _extract_pagination_keys(self):
        pagination_keys = []
        for parameter in self.parameters:
            if parameter in self.strategy_limit:
                pagination_keys.append(parameter)
            elif parameter in self.strategy_page:
                pagination_keys.append(parameter)
        return pagination_keys

    def _update_if_exists(self, key, value, obj):
        if key in obj:
            obj[key] = value
        return obj

    def _validate_pagination_keys(self, pagination_keys):
        errors = []
        if len(pagination_keys) > 2:
            for key in pagination_keys:
                errors.append({
                    'detail': 'More than one pagination strategy specified.',
                    'source': {'parameter': key}
                })
        elif (len(pagination_keys) == 2 and
                set(pagination_keys) != set(self.strategy_page) and
                set(pagination_keys) != set(self.strategy_limit)):
            for key in pagination_keys:
                errors.append({
                    'detail': 'Mismatched pagination strategies specified.',
                    'source': {'parameter': key}
                })
        return errors

    def _validate_pagination_values(self, pagination_keys):
        errors = []
        for key, value in self.parameters.iteritems():
            if key not in pagination_keys:
                continue
            try:
                if not value:
                    continue
                int(value)
            except ValueError:
                errors.append({
                    'detail': 'Value must be type number.',
                    'source': {'parameter': key}
                })
        return errors
