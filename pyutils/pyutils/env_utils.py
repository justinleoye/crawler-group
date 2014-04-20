#modified from
#https://github.com/rconradharris/envparse/blob/master/envparse.py

import os
import types
import unittest


NOTSET = object()


def env(var, cast=None, default=NOTSET):
    """Return value for given environment variable.

    :param cast: Type to cast return value as.
    :param default: If var not present in environ, return this instead.

    :returns: Value from environment or default (if set)
    """
    var = var.upper()
    try:
        value = os.environ[var]
    except KeyError:
        if default is NOTSET:
            raise

        value = default

    # Resolve any proxied values
    if hasattr(value, 'startswith') and value.startswith('$'):
        value = value.lstrip('$')
        value = env(value, cast=cast, default=default)

    # Don't cast if we're returning a default value
    if value != default:
        if cast is bool:
            value = int(value) != 0
        elif isinstance(cast, list):
            value = map(cast[0], [x for x in value.split(',') if x])
        elif cast:
            value = cast(value)

    return value


class Env(object):
    """Provide schema-based lookups of environment variables so that each
    caller doesn't have to pass in `cast` and `default` parameters.

    Usage:

        schema={mail_enabled=bool, smtp_login=(str, 'default')}
        env = Env(schema=schema)
        if env('mail_enabled'):
            ...
    """
    def __init__(self, prefix='', schema={}):
        if prefix and not prefix.endswith('_'):
            prefix = prefix + '_'
        self.prefix = prefix.upper()
        self.schema = schema

    def __getitem__(self, var):
        return self.__call__(var, default=None)

    def get(self, var, default=None):
        return self.__call__(var, default=default)

    def __call__(self, var, cast=None, default=NOTSET):
        if var in self.schema:
            var_info = self.schema[var]

            try:
                has_default = len(var_info) == 2
            except TypeError:
                has_default = False

            if has_default:
                if not cast:
                    cast = var_info[0]

                if default is NOTSET:
                    try:
                        default = var_info[1]
                    except IndexError:
                        pass
            else:
                if not cast:
                    cast = var_info

        return env(self.prefix + var, cast=cast, default=default)

