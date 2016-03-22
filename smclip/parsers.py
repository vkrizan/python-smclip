# Copyright (c) 2016 Red Hat, Inc.
# Author: Viliam Krizan
# License: LGPLv3+

import re
import argparse


class ArgparserSub(argparse.ArgumentParser):
    """Argparser with support for support for printing subcommands in help.

    Subcommands should be defined as remainder argument (defined by
    ArgparseSub.REMAINING_ARGS).
    """

    REMAINING_ARGS = '_subcommand'

    def __init__(self, subcommands=None, subcmds_help_title=None, **kwargs):
        if subcommands is None:
            subcommands = {}
        self._subcommands = subcommands
        self._subcmds_help_title = subcmds_help_title or 'subcommands'

        kwargs.setdefault('formatter_class', GroupHelpFormatter)
        super(ArgparserSub, self).__init__(**kwargs)

    def format_help(self):

        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        self.format_custom_sections(formatter)

        # epilog
        formatter.add_text(self.epilog)

        return formatter.format_help()

    def format_custom_sections(self, formatter):
        # Subcommands section
        formatter.start_section(self._subcmds_help_title)
        formatter.add_subcommands(self._subcommands)
        formatter.end_section()


class GroupHelpFormatter(argparse.HelpFormatter):
    """HelpFormatter with support for subcommands"""

    def _format_subcommand(self, subcmd_name, subcmd):
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2,
                            self._max_help_position)
        help_width = max(self._width - help_position, 11)
        subcmd_width = help_position - self._current_indent - 2
        subcmd_header = subcmd_name

        help_line = split_docstring(subcmd.__doc__)[0]

        if not help_line:
            tup = self._current_indent, '', subcmd_header
            subcmd_header = '%*s%s\n' % tup

        elif len(subcmd_header) <= subcmd_width:
            tup = self._current_indent, '', subcmd_width, subcmd_header
            subcmd_header = '%*s%-*s  ' % tup
            indent_first = 0

        else:
            tup = self._current_indent, '', subcmd_header
            subcmd_header = '%*s%s\n' % tup
            indent_first = help_position

        # collect the pieces of the action help
        parts = [subcmd_header]

        # if there was help for the action, add lines of help text
        if help_line:
            if len(help_line) > help_width:
                new_width = help_width-3
                help_line = '%s...' % help_line[0:new_width]

            parts.append('%*s%s\n' % (indent_first, '', help_line))

        # or add a newline if the description doesn't end with one
        elif not subcmd_header.endswith('\n'):
            parts.append('\n')

        # return a single string
        return self._join_parts(parts)

    def add_subcommand(self, subcmd_name, subcmd):

        # update the maximum item length
        name_length = len(subcmd_name)
        action_length = name_length + self._current_indent
        self._action_max_length = max(self._action_max_length,
                                      action_length)

        # add the item to the list
        self._add_item(self._format_subcommand, [subcmd_name, subcmd])

    def add_subcommands(self, subcommands):
        for subcmd_name in subcommands:
            subcmd = subcommands[subcmd_name]
            self.add_subcommand(subcmd_name, subcmd)


def split_docstring(string):
    """Split docstring to header and description

    Separator between header and description is one blank line.
    When no separator is found, then description is None.

    Args:
        string (str): docstring

    Returns:
        title, description
    """

    if not string:
        return None, None

    parts = re.split(r'(?:\n|\r|\r\n)[ \t]*(?:\n|\r|\r\n)', string, 1)
    if len(parts) == 1:
        # header is considered also as description
        title = str(parts[0]).strip()
        return title, None

    title = str(parts[0]).strip()
    description = str(parts[1]).strip()
    return title, description
