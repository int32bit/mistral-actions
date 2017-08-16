import argparse
import sys

from oslo_utils import encodeutils
from oslo_utils import importutils

import mistral_actions.utils as utils

DISCORVERED_COMMANDS = []


class MistralActionsClientArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(MistralActionsClientArgumentParser, self).__init__(
            *args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, ("error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                      " for more information.\n") % {
                          'errmsg': message.split(choose_from)[0],
                          'mainp': progparts[0],
                          'subp': progparts[2]})

    def _get_option_tuples(self, option_string):
        """returns (action, option, value) candidates for an option prefix

        Returns [first candidate] if all candidates refers to current and
        deprecated forms of the same options parsing succeed.
        """
        option_tuples = (super(MistralActionsClientArgumentParser, self)
                         ._get_option_tuples(option_string))
        if len(option_tuples) > 1:
            normalizeds = [
                option.replace('_', '-')
                for action, option, value in option_tuples
            ]
            if len(set(normalizeds)) == 1:
                return option_tuples[:1]
        return option_tuples


class MistralActionShell(object):
    def _append_global_identity_args(self, parser, argv):
        # Register the CLI arguments that have moved to the session object.
        pass

    def get_base_parser(self, argv):
        if __doc__:
            description = __doc__.strip()
        else:
            description = ""
        parser = MistralActionsClientArgumentParser(
            prog='mistral-actions',
            description=description,
            epilog='See "mistral-actions help COMMAND" '
            'for help on a specific command.',
            add_help=False,
            formatter_class=MistralActionHelpFormatter, )

        # Global arguments
        parser.add_argument(
            '-h',
            '--help',
            action='store_true',
            help=argparse.SUPPRESS, )

        self._append_global_identity_args(parser, argv)

        return parser

    def get_subcommand_parser(self, do_help=False, argv=None):
        parser = self.get_base_parser(argv)

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        actions_module = importutils.import_module(
            "mistral_actions.client.shell")

        self._find_actions(subparsers, actions_module, do_help)
        self._find_actions(subparsers, self, do_help)
        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=MistralActionHelpFormatter)
        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _remove_commands_from_args(self):
        for command in DISCORVERED_COMMANDS:
            try:
                sys.argv.remove(command)
            except ValueError:
                pass

    def _find_actions(self, subparsers, actions_module, do_help):
        global DISCORVERED_COMMANDS
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hyphen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            DISCORVERED_COMMANDS.append(command)
            # commands.append(command)
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=action_help,
                description=desc,
                add_help=False,
                formatter_class=MistralActionHelpFormatter)
            subparser.add_argument(
                '-h',
                '--help',
                action='help',
                help=argparse.SUPPRESS, )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def main(self, argv):
        # Parse args once to find version and debug settings
        parser = self.get_base_parser(argv)
        (args, args_list) = parser.parse_known_args(argv)
        do_help = ('help' in argv) or ('--help' in argv) or (
            '-h' in argv) or not argv

        subcommand_parser = self.get_subcommand_parser(
            do_help=do_help, argv=argv)
        self.parser = subcommand_parser

        if args.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        self._remove_commands_from_args()
        args.func(args)

    def do_bash_completion(self, _args):
        """Prints all of the commands and options to stdout."""
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print(' '.join(commands | options))

    @utils.arg(
        'command',
        metavar='<subcommand>',
        nargs='?',
        help='Display help for <subcommand>.')
    def do_help(self, args):
        """Display help about this program or one of its subcommands. """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                print("'%s' is not a valid subcommand" % args.command)
        else:
            self.parser.print_help()


# I'm picky about my shell help.
class MistralActionHelpFormatter(argparse.HelpFormatter):
    def __init__(self,
                 prog,
                 indent_increment=2,
                 max_help_position=32,
                 width=None):
        super(MistralActionHelpFormatter, self).__init__(
            prog, indent_increment, max_help_position, width)

    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(MistralActionHelpFormatter, self).start_section(heading)


def main():
    try:
        argv = [encodeutils.safe_decode(a) for a in sys.argv[1:]]
        MistralActionShell().main(argv)
    except KeyboardInterrupt:
        print("... terminating harbor client")


if __name__ == "__main__":
    main()
