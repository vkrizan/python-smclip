# Copyright (c) 2016 Red Hat, Inc.
# Author: Viliam Krizan
# License: LGPLv3+


class CommandError(Exception):

    def __init__(self, command_name, parent=None, parser=None):
        super(CommandError, self).__init__()
        self.command_name = command_name
        self.parent = parent
        self.parser = parser


class CommandNotFound(CommandError):
    def __str__(self):
        return "unknown command `{0}'".format(self.command_name)


class CommandUnrecognizedArgs(CommandError):
    def __init__(self, command_name, parent=None, parser=None, unknown_args=()):
        super(CommandUnrecognizedArgs, self).__init__(command_name, parent, parser)
        self.unknown_args = unknown_args

    def __str__(self):
        return 'unrecognized arguments: {0}'.format(' '.join(self.unknown_args))
