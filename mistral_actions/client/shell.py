import sys

from mistral_actions.client import actions as actions_cli
import mistral_actions.utils as utils


def do_clear(args):
    """Unregister all actions from Mistral."""
    actions_cli.unregister_all()
    print("All actions are removed from Mistral successfully.")


@utils.arg(
    '--override',
    dest='override',
    action="store_true",
    default=False,
    help="Set true will override all actions exist in Mistral.")
def do_register(args):
    """Register all actions to Mistral."""
    override = args.override
    try:
        sys.argv.remove("--override")
    except ValueError:
        pass
    registered_actions = actions_cli.get_all_registered()
    discovered_actions = actions_cli.discover()
    registered_action_names = [a['name'] for a in registered_actions]
    discovered_action_names = [a['name'] for a in discovered_actions]
    intersection = set(registered_action_names) & set(discovered_action_names)
    if override:
        for name in intersection:
            actions_cli.unregister(name)
    else:
        discovered_actions = filter(
            lambda a: a['name'] not in registered_action_names,
            discovered_actions)
    if len(discovered_actions):
        try:
            actions_cli.register_all(discovered_actions)
            print("Follow actions have been registered: ")
            for action in discovered_actions:
                print("%(name)s(%(args)s): %(description)s" % {
                    'name': action['name'],
                    'args': action['input_str'],
                    'description': action['description'].split('\n')[0]
                })
        except Exception as ex:
            print("Fail to register actions: %s" % ex)
    else:
        print("No action need to register.")


def do_discover(args):
    """Discover all actions from this project."""
    discovered_actions = actions_cli.discover()
    fileds = ['name', 'description', 'input_str']
    print("Follow actions discovered: ")
    utils.print_list(discovered_actions, fileds, sortby_index=0)


@utils.arg('name', metavar='<name>', help='Name of action.')
def do_unregister(args):
    """Unregister a action from Mistral."""
    name = args.name
    sys.argv.remove(name)
    actions_cli.unregister(name)


def do_markdown_dump(args):
    """Dump all discovered actions to stdout as markdown table."""
    sorted_actions = sorted(actions_cli.discover(), key=lambda a: a['name'])
    fileds = ['name', 'description', 'input_str']
    utils.dump_as_markdown_table(sorted_actions, fileds)


def do_action_list(args):
    """List all actions have been registered in Mistral."""
    actions = actions_cli.get_all_registered()
    fileds = ['name', 'description', 'input_str']
    utils.print_list(actions, fileds, sortby_index=0)
