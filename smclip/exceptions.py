# Copyright (c) 2016 Red Hat, Inc.
# Author: Viliam Krizan
# License: LGPLv3+

__all__ = ['CommandNotFound']


class CommandNotFound(Exception):

    def __init__(self, command_name, parent):
        super(CommandNotFound, self).__init__()
        self.command_name = command_name
        self.parent = parent
        self.message = "Unknown command `{}'".format(command_name)
