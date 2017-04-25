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


def _extract_actions_from_module(module):
    action_list = []
    for member in inspect.getmembers(module):
        if inspect.isclass(member[1]) and hasattr(
                member[1], '__export__') and hasattr(member[1], 'run'):
            action = {}
            cls = member[1]
            module_name = cls.__module__
            action['name'] = (
                ROOT_NAMESPACE + module_name[module_name.index('.'):] + '.' +
                utils.convert_to_snake_case(cls.__name__))
            action['action_class_str'] = cls.__module__ + '.' + cls.__name__
            action['attributes'] = i_utils.get_public_fields(cls)
            action['description'] = i_utils.get_docstring(cls)
            action['input_str'] = i_utils.get_arg_list_as_str(cls.__init__)
            action_list.append(action)
    return action_list


def _extract_all_actions():
    path = os.path.dirname(mistral_actions.__file__)
    base_len = len(path[:-len(mistral_actions.__name__)])
    action_list = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.py') and not f.startswith('_'):
                module_name = (root + '/' + f)[base_len:-len('.py')].replace(
                    '/', '.')
                module = importutils.import_module(module_name)
                action_list.extend(_extract_actions_from_module(module))
    return action_list


@utils.db_transaction
def unregister(name):
    try:
        db_api.delete_action_definition(name)
    except NotFoundException:
        print("Fail to remove action '%s', NOT FOUND!" % name)


@utils.db_transaction
def unregister_all():
    actions = get_all_registered()
    for action in actions:
        try:
            db_api.delete_action_definition(action['name'])
            print("Remove action '%s' successfully." % action['name'])
        except NotFoundException:
            print("Fail to remove action '%s', NOT FOUND!" % action['name'])


@utils.db_transaction
def register(action):
    register_action_class(**action)


@utils.db_transaction
def register_all(actions):
    for action in actions:
        register_action_class(**action)


def discover():
    return _extract_all_actions()


def get_all_registered():
    actions = utils.get_mistralclinet_from_env().actions.list()
    filtered_actions = filter(lambda a: a.name.startswith(ROOT_NAMESPACE),
                              actions)
    resetset = []
    for a in filtered_actions:
        action = {
            'name': a.name,
            'description': a.description,
            'input_str': a.input
        }
        resetset.append(action)

    return resetset
