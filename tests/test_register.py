
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

import smclip


def test_error_same_default_name_register():

    class Subcommand(smclip.Command):
        default_name = 'somename'

    class CommandGroup(smclip.CommandGroup):

        def __init__(self, *args, **kwargs):
            super(CommandGroup, self).__init__(*args, **kwargs)

            self.register(Subcommand)
            self.register(Subcommand)

    with pytest.raises(RuntimeError) as excinfo:
        CommandGroup()

    assert 'already registered' in str(excinfo.value)


def test_error_same_name_register():

    class Subcommand1(smclip.Command):
        default_name = 'somename'

    class Subcommand2(smclip.Command):
        default_name = 'somename2'

    class CommandGroup(smclip.CommandGroup):

        def __init__(self, *args, **kwargs):
            super(CommandGroup, self).__init__(*args, **kwargs)

            self.register(Subcommand1, name='samename')
            self.register(Subcommand2, name='samename')

    with pytest.raises(RuntimeError) as excinfo:
        CommandGroup()

    assert 'already registered' in str(excinfo.value)


def test_error_no_default_name():

    class SubcommandNonName(smclip.Command):
        pass

    class CommandGroup(smclip.CommandGroup):

        def __init__(self, *args, **kwargs):
            super(CommandGroup, self).__init__(*args, **kwargs)

            self.register(SubcommandNonName)

    with pytest.raises(RuntimeError) as excinfo:
        CommandGroup()

    assert 'No name' in str(excinfo.value)


def test_error_same_default_alias_register():

    class Subcommand(smclip.Command):
        default_name = 'somename'
        default_aliases = ['alias']

    class CommandGroup(smclip.CommandGroup):

        def __init__(self, *args, **kwargs):
            super(CommandGroup, self).__init__(*args, **kwargs)

            self.register(Subcommand)
            self.register(Subcommand, name='othername')

    with pytest.raises(RuntimeError) as excinfo:
        CommandGroup()

    assert 'already registered' in str(excinfo.value)


def test_error_same_alias_register():

    class Subcommand1(smclip.Command):
        default_name = 'somename'

    class Subcommand2(smclip.Command):
        default_name = 'somename2'

    class CommandGroup(smclip.CommandGroup):

        def __init__(self, *args, **kwargs):
            super(CommandGroup, self).__init__(*args, **kwargs)

            aliases = ['alias']
            self.register(Subcommand1, aliases=aliases)
            self.register(Subcommand2, aliases=aliases)

    with pytest.raises(RuntimeError) as excinfo:
        CommandGroup()

    assert 'already registered' in str(excinfo.value)


def test_error_same_alias_as_name_register():

    class Subcommand1(smclip.Command):
        default_name = 'one'

    class Subcommand2(smclip.Command):
        default_name = 'two'
        default_aliases = ['one']

    class CommandGroup(smclip.CommandGroup):

        def __init__(self, *args, **kwargs):
            super(CommandGroup, self).__init__(*args, **kwargs)

            self.register(Subcommand1)
            self.register(Subcommand2)

    with pytest.raises(RuntimeError) as excinfo:
        CommandGroup()

    assert 'already registered' in str(excinfo.value)
