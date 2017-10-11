# Copyright (c) 2016 Red Hat, Inc.
# Author: Viliam Krizan
# License: LGPLv3+

import argparse

from .exceptions import *
from .parsers import ArgparserSub, split_docstring

__all__ = ['Command', 'CommandGroup', 'ChainedCommand', 'ChainedCommandGroup',
           'ChainedOutputResults']


class Command(object):
    """Command with action

    Command contains its own parser with defined arguments.
    Default parser is custom `Argparser`.

    Commands are lazy loaded.  Each command, when created
    by parent command, is created with its name and alias.
    Alias is filled with name from which it was invoked with.

    Title and description are filled based on current class
    docstring.

    To create a custom command, extend these methods:
        * `add_arguments`
        * `this_action`
        * `preprocess`
        * `results_callback`

    Class Attributes:
        default_name (str): default real command name
        default_aliases (list): default command aliases

    Attributes:
        name (str): real command name
        alias (str): invoked name
        parent (Command): parent command
        app (object): application object
        title (str): header of current class docstring
        description (str): body of current class docstring
        parser_cls (object): argument parser's class (default: ArgumentParser)
        parser (object): lazy loaded parser instance
    """

    default_name = None
    default_aliases = None

    def __init__(self, name=None, alias=None, parser_cls=None, app=None):
        self.name = name or self.default_name
        self.alias = alias
        self._parser = None
        self.parent = None
        self.app = app

        title, description = split_docstring(self.__class__.__doc__)
        self.title = title
        self.description = description

        if not parser_cls:
            parser_cls = argparse.ArgumentParser

        self.parser_cls = parser_cls

    @property
    def parser(self):
        if not self._parser:
            self._parser = self.create_parser()
        return self._parser

    def create_parser(self, **custom_opts):
        """Creates parser and adds all defined arguments"""
        parser_opts = self.get_parser_options()
        parser_opts.update(custom_opts)
        parser = self.parser_cls(**parser_opts)
        self.add_arguments(parser)
        return parser

    def get_parser_options(self):
        """Returns dictionary of options for parser creation"""
        opts = {
            'prog': self._generate_usage_prefix(),
            'description': self.title,
            'epilog': self.description,
        }
        if not issubclass(self.parser_cls, ArgparserSub):
            opts['formatter_class'] = argparse.RawDescriptionHelpFormatter
        return opts

    def _generate_usage_prefix(self):
        if self.name:
            parent_names = [self.name]
            parent_names.extend(self.get_parent_names())
            prog = ' '.join(reversed(parent_names))
            return prog

    def get_parent_names(self, real_names_only=True):
        """Returns list of parent names

        Args:
            real_names_only (bool): if True it returns real names
                                    rather than names from which
                                    they were invoked

        Returns:
            list of parent names (str), youngest first
        """
        parent_names = []
        parent = self.parent
        while parent:
            parent_name = parent.name
            if not real_names_only and parent.alias:
                parent_name = parent.alias

            parent_names.append(parent_name)
            parent = parent.parent
        return parent_names

    def add_arguments(self, parser):
        """Abstract function for adding arguments to parser invoked
        right after parser is created.

        Args:
            parser: instance of argument parser

        """
        pass

    def invoke(self, raw_args):
        """Command invocation method.

        Args:
            raw_args (list): list of raw command arguments
        """
        namespace = self.parser.parse_args(raw_args)
        parsed_args, _ = self._extract_parsed_args(namespace)

        return self.invoke_callbacks(parsed_args)

    def invoke_callbacks(self, parsed_args):
        """Invoke preprocess and this_action callback and
        return value from this_action callback"""

        preprocessed_args = self.preprocess(**dict(parsed_args))
        if isinstance(preprocessed_args, dict):
            action_args = dict(preprocessed_args)
        elif preprocessed_args is None:
            action_args = dict(parsed_args)
        else:
            raise AssertionError('Expected preprocess to return dict or None, {} returned instead!'
                                 .format(type(preprocessed_args)))

        rv = self.this_action(**action_args)
        return rv

    def _extract_parsed_args(self, namespace):
        args = dict(vars(namespace))
        remaining = args.pop(ArgparserSub.REMAINING_ARGS, None)
        return args, remaining

    def commands_for_args(self, raw_args):
        """Return current command and possible subcommands for the set of arguments

        Returns:
            (list) of Command objects
        """
        return [self]

    def preprocess(self, **args):
        """Callback invoked before action callback

        This callback is only called when there is no error
        from argument parsing.
        Preprocess callback may return a dictionary of new
        arguments that will be passed to ``this_action``
        callback.

        Args:
            **args: parsed arguments
        """
        pass

    def this_action(self, **args):
        """Action process for this command.

        This callback is only called when there is no error
        from argument parsing.

        Args:
            **args: parsed or preprocessed arguments
        """
        pass


class CommandGroup(Command):
    """Command with subcommands

    It behaves identically to simple Command on certain conditions
    and above that it supports a subcommad.

    Each subcommands can be registered with `register` method.
    When no subcommand is provided then action for this command
    is invoked.  `preprocess` and `results_callback` are invoked
    every time (when no argument errors are present).

    Command Group supports registering a command as default or
    as a fallback command.  A default command replaces `this_action`
    of this group with a set of all pre-, action- and post-callbacks of
    the default command.  A fallback command is as subcommand that is
    invoked when a user defined subcommand does not exists.

    Command Group uses, by default, ArgparseSub for parsing the
    arguments.  The remainder after parsing is used to determine
    a subcommand and its arguments.  The first positional argument
    is a name/alias of a subcommand and the rest are its non-parsed
    arguments.  Non-parsed arguments are then passed to the subcommand's
    invocation method.

    If a subcommand is not found then CommandNotFound is risen, but only
    when no fallback or default commands are registered.  If only a default
    command is register then it is its responsiblity to resolved this situation.

    Command Group contains a attribute `invoked_subcommand` which holds
    an instance to a command that is being invoked. This attribute is
    filled in before calling a `preprocess` method.

    `results_callback` is called after a subcommand or current command
    action is done and it is filled with an argument containing a result
    value from (sub)command action method.  `results_callback` is not
    called when default command is in effect!

    To create a custom command group, extend these methods:
        * `add_arguments`
        * `this_action`
        * `preprocess`

    Attributes:
        subcmds_cls (dict): mapping of commands [name] => [command class]
        subcmd_aliases (dict): mapping of commands based on aliases
                               [name] => [command class]
        invoked_subcommand (Command): a command instance that is being
                                      invoked as subcommand

    Keyword Args:
        parser_cls (class): argument parser class (default: ArgparseSub)
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('parser_cls', ArgparserSub)
        super(CommandGroup, self).__init__(*args, **kwargs)
        self.subcmds_cls = {}
        self.subcmd_aliases = {}
        self._subcmd_names = {}

        self._fallback_subcmd_cls = None
        self._default_subcmd_cls = None

        self.invoked_subcommand = None

    def register(self, command_cls, name=None, aliases=None, is_default=False, is_fallback=False):
        """Register a new subcommand with its class

        Name and aliases are optional, and defaults to the class
        `default_name` and `default_aliases`.

        Args:
            command_cls (class): a subcommand class
            name (str): optional name of command (default: None)
            aliases: optional aliases (default: None)
            is_default: make this command as default (default: False)
            is_fallback: make this command as fallback (default: False)
        """
        name = name or command_cls.default_name
        aliases = aliases or command_cls.default_aliases or tuple()

        if not name and not command_cls.default_name:
            raise RuntimeError('No name specified for command class {}'.format(command_cls.__name__))

        if name in self.subcmds_cls:
            raise RuntimeError('Command with name {} is already registered!'.format(name))

        self.subcmds_cls[name] = command_cls
        self._subcmd_names[command_cls] = name

        for alias in aliases:
            if alias in self.subcmds_cls:
                raise RuntimeError('Alias {} is already registered as command!'.format(name))
            if alias in self.subcmd_aliases:
                raise RuntimeError('Alias with name {} is already registered!'.format(name))

            self.subcmd_aliases[alias] = command_cls

        if is_fallback:
            self._fallback_subcmd_cls = command_cls

        if is_default:
            self._default_subcmd_cls = command_cls

    def get_parser_options(self):
        opts = super(CommandGroup, self).get_parser_options()

        # pass subcommands to parser for showing help
        opts['subcommands'] = self.subcmds_cls
        return opts

    def create_parser(self, **custom_opts):
        parser = super(CommandGroup, self).create_parser(**custom_opts)
        parser.add_argument(ArgparserSub.REMAINING_ARGS, nargs=argparse.REMAINDER)
        return parser

    def invoke(self, raw_args):
        namespace, unknown_args = self.parser.parse_known_args(raw_args)
        parsed_args, sub_args = self._extract_parsed_args(namespace)

        try:
            is_default, command = self.parse_and_get_command(raw_args, namespace, unknown_args)
        except CommandError as e:
            e.parser.error(str(e))

        if not command:
            # no subcommand was issues, call current one
            return self.invoke_callbacks(parsed_args)

        if is_default:
            return self.invoke_default(raw_args)
        else:
            self.preprocess(**dict(parsed_args))
            rv = command.invoke(sub_args)  # Subcommand invocation
            self.results_callback(rv)
            return rv

    def parse_and_get_command(self, raw_args, namespace, unknown_args):
        """Parse raw arguments and return subcommand object

        Returns:
            tuple: (is_default, command)
        """
        parsed_args, sub_args = self._extract_parsed_args(namespace)

        if unknown_args:
            if self._default_subcmd_cls:
                return True, self._new_default_subcommand(raw_args)

            else:
                raise CommandUnrecognizedArgs(self.default_name,
                                              parent=self.parent,
                                              parser=self.parser,
                                              unknown_args=unknown_args)

        if sub_args:
            subcmd_name = sub_args.pop(0)
            subcmd_cls = (self.subcmds_cls.get(subcmd_name)
                          or self.subcmd_aliases.get(subcmd_name))

            if not subcmd_cls:
                if self._fallback_subcmd_cls:
                    subcmd_cls = self._fallback_subcmd_cls
                else:
                    raise CommandNotFound(subcmd_name,
                                          parent=self,
                                          parser=self.parser)

            real_name = self.get_subcmd_real_name(subcmd_cls)
            subcmd = self.new_subcommand(subcmd_cls, real_name, subcmd_name)

            self.invoked_subcommand = subcmd
            subcmd.parent = self

            return False, subcmd

        elif self._default_subcmd_cls:
            return True, self._new_default_subcommand(raw_args)

        return False, None

    def new_subcommand(self, subcmd_cls, real_name, aliased_name=None, **kwargs):
        kwargs['app'] = self.app
        return subcmd_cls(real_name, aliased_name, **kwargs)

    def _new_default_subcommand(self, raw_args):
        subcmd_cls = self._default_subcmd_cls
        real_name = self.get_subcmd_real_name(subcmd_cls)

        subcmd = self.new_subcommand(subcmd_cls, real_name)
        subcmd.parent = self
        self.invoked_subcommand = subcmd
        return subcmd

    def invoke_default(self, raw_args):
        """Invoke subcommand that was registered as default"""
        subcmd = self._new_default_subcommand(raw_args)
        return subcmd.invoke(raw_args)

    def get_subcmd_real_name(self, subcmd_cls):
        return self._subcmd_names.get(subcmd_cls)

    def commands_for_args(self, raw_args):
        self._parser = self.create_parser(add_help=False)
        namespace, unknown_args = self.parser.parse_known_args(raw_args)
        parsed_args, sub_args = self._extract_parsed_args(namespace)

        is_default, command = self.parse_and_get_command(raw_args, namespace, unknown_args)
        if command and not is_default:
            return command.commands_for_args(sub_args)
        else:
            commands = [self]
            subcommand_cls = self.subcmds_cls.values()
            commands.extend(cls() for cls in subcommand_cls)
            return commands

    def possible_command_names(self, raw_args):
        """Return possible subcommand names for a set of arguments

        Returns:
            (list) of strings of command names,
            None on failure in case of bad arguments.
        """
        try:
            commands = self.commands_for_args(raw_args)
        except CommandError:
            return
        except SystemExit as e:
            # handle bad arguments
            if e.code == 2:
                return
            raise

        command_names = [cmd.name for cmd in commands]
        if not command_names:
            return []

        command_names.pop(0)  # remove command that is currently in effect
        command_names.sort()
        return command_names

    def results_callback(self, rv):
        """Callback for collecting results from subcommands.

        This callback is only called when a subcommand is in effect.

        Args:
            rv: result value
        """
        pass


class ChainedCommand(Command):

    def create_parser(self, **custom_opts):
        parser = super(ChainedCommand, self).create_parser(**custom_opts)
        parser.add_argument(ArgparserSub.REMAINING_ARGS, nargs=argparse.REMAINDER)
        return parser

    def commands_for_args(self, raw_args):
        if self.parent:
            commands = [self]
            chained_cls = self.parent.subcmds_cls.values()
            commands.extend(cls() for cls in chained_cls)
            return commands
        else:
            return [self]


class ChainedCommandGroup(CommandGroup):
    """Command that supports chained sub commands

    Chained commads are commands at the same level invoked one by
    one.  The results from all chained commands are pushed into
    `results_callback` as an instance of `ChainedOutputResults` class.

    Invoked subcommands have to be final, cannot be groups for
    holding other subcommands.

    Attributes:
        invoked_subcommand: is set to True when any subcommand is being invoked
        invoked_subcommands (list): list of commands instances being invoked
    """

    def __init__(self, *args, **kwargs):
        super(ChainedCommandGroup, self).__init__(*args, **kwargs)
        self.invoked_subcommands = None

    def register(self, command_cls, **kwargs):
        assert issubclass(command_cls, ChainedCommand), \
            'Only Commands type of ChainedCommand can be registered!'
        assert not kwargs.get('is_default'), \
            '{} does not support default commands'.format(self.__class__.__name__)
        assert not kwargs.get('is_fallback'), \
            '{} does not support fallback commands'.format(self.__class__.__name__)

        super(ChainedCommandGroup, self).register(command_cls, **kwargs)

    def get_parser_options(self):
        opts = super(ChainedCommandGroup, self).get_parser_options()
        opts['subcmds_help_title'] = 'chained subcommands'
        return opts

    def invoke(self, raw_args):
        namespace = self.parser.parse_args(raw_args)
        parsed_args, remaining = self._extract_parsed_args(namespace)

        try:
            chained_cmd_args = self.parse_and_get_chain(remaining)
        except CommandError as e:
            e.parser.error(str(e))

        if chained_cmd_args:
            self.preprocess(**dict(parsed_args))
            results = ChainedOutputResults()

            for subcmd, sub_args in chained_cmd_args:
                # Our Chained command invocation
                subrv = subcmd.invoke_callbacks(sub_args)
                results.add_result(subcmd, subrv)

            rv = results
            self.results_callback(rv)

        else:
            # Callback
            rv = self.invoke_callbacks(parsed_args)

        return rv

    def parse_and_get_chain(self, remaining):
        if not remaining:
            return

        chained_cmd_args = []
        self.invoked_subcommand = True
        self.invoked_subcommands = []

        while remaining:

            subcmd_name = remaining.pop(0)
            subcmd_cls = (self.subcmds_cls.get(subcmd_name)
                          or self.subcmd_aliases.get(subcmd_name))
            if not subcmd_cls:
                raise CommandNotFound(subcmd_name,
                                      parent=self,
                                      parser=self.parser)

            real_name = self.get_subcmd_real_name(subcmd_cls)
            subcmd = self.new_subcommand(subcmd_cls, real_name, subcmd_name)

            # set references
            subcmd.parent = self
            self.invoked_subcommands.append(subcmd)

            sub_namespace, unknown_args = subcmd.parser.parse_known_args(remaining)
            if unknown_args:
                raise CommandUnrecognizedArgs(subcmd_name,
                                              parent=self.parent,
                                              parser=subcmd.parser,
                                              unknown_args=unknown_args)

            sub_args, remaining = self._extract_parsed_args(sub_namespace)
            chained_cmd_args.append((subcmd, sub_args))

        return chained_cmd_args


class ChainedOutputResults(object):
    """Holder of result from chained commands

    Attributes:
        results: list of paired (command_obj, rv)
    """

    def __init__(self):
        self.results = []

    def add_result(self, command, rv):
        """

        Args:
            command (Command): command instance
            rv: result value
        """
        self.results.append((command, rv))

    def __iter__(self):
        return self.results.__iter__()
