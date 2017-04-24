from alembic import config as alembic_cfg
import inspect
import os

from oslo_config import cfg
from oslo_utils import importutils

from mistral.db.v2 import api as db_api
from mistral.exceptions import NotFoundException
from mistral.services.action_manager import register_action_class
from mistral.utils import inspect_utils as i_utils

import mistral_actions
import mistral_actions.utils as utils

CONF = cfg.CONF
ROOT_NAMESPACE = 'int32bit'


def extract_actions_from_module(module):
    action_list = []
    for member in inspect.getmembers(module):
        if inspect.isclass(member[1]) and hasattr(
                member[1], '__export__') and hasattr(member[1], 'run'):
            action = {}
            cls = member[1]
            module_name = cls.__module__
            action['name'] = (ROOT_NAMESPACE +
                              module_name[module_name.index('.'):] + '.'
                              + utils.convert_to_snake_case(cls.__name__))
            action['action_class_str'] = cls.__module__ + '.' + cls.__name__
            action['attributes'] = i_utils.get_public_fields(cls)
            action['description'] = i_utils.get_docstring(cls)
            action['input_str'] = i_utils.get_arg_list_as_str(cls.__init__)
            action_list.append(action)
    return action_list


def extract_all_actions():
    path = os.path.dirname(mistral_actions.__file__)
    base_len = len(path[:-len(mistral_actions.__name__)])
    action_list = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.py') and not f.startswith('_'):
                module_name = (root + '/' + f)[base_len:-len('.py')].replace(
                    '/', '.')
                module = importutils.import_module(module_name)
                action_list.extend(extract_actions_from_module(module))
    return action_list


def clear_actions():
    actions = extract_all_actions()
    for action in actions:
        try:
            db_api.delete_action_definition(action['name'])
        except NotFoundException:
            pass


def register_actions():
    actions = extract_all_actions()
    print("\nRegister follow actions: ")
    for action in actions:
        print('\t' + action['name'])
        register_action_class(**action)


def sync_db():
    with db_api.transaction():
        clear_actions()
    with db_api.transaction():
        register_actions()


def dump():
    # Order by name asc
    actions = extract_all_actions()
    fileds = ['name', 'input_str', 'description']
    utils.print_list(actions, fileds, sortby_index=0)


def dump_as_list():
    sorted_actions = sorted(extract_all_actions(), key=lambda a: a['name'])
    for action in sorted_actions:
        print("%(name)s(%(args)s): %(desc)s" %
              {'name': action['name'],
               'args': action['input_str'],
               'desc': action['description'].split('\n')[0]})


def dump_as_md_table():
    sorted_actions = sorted(extract_all_actions(), key=lambda a: a['name'])
    print('| name | input | description |')
    print('|----|----|----|')
    for action in sorted_actions:
        print("|%(name)s|(%(args)s)|%(desc)s|" %
              {'name': action['name'],
               'args': action['input_str'],
               'desc': action['description'].split('\n')[0]})


def main():
    config = alembic_cfg.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini'))
    config.set_main_option(
        'script_location',
        'mistral.db.sqlalchemy.migration:alembic_migrations')
    # attach the Mistral conf to the Alembic conf
    config.mistral_config = CONF

    CONF(project='mistral')
    # CONF.command.func(config, CONF.command.name)
    sync_db()
    dump()
    # dump_as_list()
    # dump_as_md_table()


if __name__ == '__main__':
    main()
