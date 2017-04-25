from alembic import config as alembic_cfg
import os
import prettytable
import re
import six

from mistral.db.v2 import api as db_api
from mistralclient.api import client
from oslo_config import cfg
from oslo_utils import encodeutils

CONF = cfg.CONF


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get('default', '')


def arg(*args, **kwargs):
    """Decorator for CLI args.

    Example:

    >>> @arg("name", help="Name of the new entity")
    ... def entity_create(args):
    ...     pass
    """

    def _decorator(func):
        add_arg(func, *args, **kwargs)
        return func

    return _decorator


def add_arg(func, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""

    if not hasattr(func, 'arguments'):
        func.arguments = []

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in func.arguments:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.arguments.insert(0, (args, kwargs))


def convert_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def db_transaction(function):
    @six.wraps(function)
    def inner(*args, **kwargs):
        config = alembic_cfg.Config(
            os.path.join(os.path.dirname(__file__), 'alembic.ini'))
        config.set_main_option(
            'script_location',
            'mistral.db.sqlalchemy.migration:alembic_migrations')
        # attach the Mistral conf to the Alembic conf
        config.mistral_config = CONF

        CONF(project='mistral')
        with db_api.transaction():
            return function(*args, **kwargs)

    return inner


def print_list(objs, fields, formatters={}, sortby_index=None):
    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if hasattr(o, '__getitem__'):
                    data = o[field]
                else:
                    data = getattr(o, field)
                if data is None:
                    data = '-'
                data = data.split('\n')[0]
                # '\r' would break the table, so remove it.
                data = six.text_type(data).replace("\r", "")
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = encodeutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = encodeutils.safe_encode(pt.get_string())

    if six.PY3:
        result = result.decode()

    print(result)


def _convert_to_md_row(fields):
    return '|' + '|'.join(fields) + '|'


def dump_as_markdown_table(objs, fields, formatters={}):
    print(_convert_to_md_row(fields))
    print(_convert_to_md_row(['---'] * len(fields)))
    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if hasattr(o, '__getitem__'):
                    data = o[field]
                else:
                    data = getattr(o, field)
                if data is None:
                    data = '-'
                data = data.split('\n')[0]
                # '\r' would break the table, so remove it.
                data = six.text_type(data).replace("\r", "")
                row.append(data)
        print(_convert_to_md_row(row))


def get_mistralclinet_from_env():
    username = env("OS_USERNAME", default=None)
    password = env("OS_PASSWORD", default=None)
    project_name = env("OS_TENANT_NAME", "OS_PROJECT_NAME", default=None)
    auth_url = env("OS_AUTH_URL", default=None)
    mistral_url = env("OS_MISTRAL_URL", default=None)
    mistralclient = client.client(
        mistral_url=mistral_url,
        username=username,
        api_key=password,
        project_name=project_name,
        auth_url=auth_url)
    return mistralclient
