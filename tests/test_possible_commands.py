import pytest

from integration_classes import *
from integration_classes import _split_cmd_args


@pytest.mark.parametrize('cmdargs,current_command_name,subcommand_names', [
    ('', None, ['help', 'group', 'listdefault', 'empty', 'override', 'badoverride']),
    ('help', 'help', []),
    ('docs', 'help', []),  # aliased
    ('override --toreplace', 'override', []),
    ('group', 'group', ['list', 'create', 'ID']),
    ('task', 'group', ['list', 'create', 'ID']),  # aliased
    ('group --groupopt val',  'group', ['list', 'create', 'ID']),
    ('group list', 'list', []),
    ('group table', 'list', []),  # aliased
    ('group --groupopt val list', 'list', []),
    ('group --groupopt val list --listopt', 'list', []),
    ('listdefault', 'listdefault', ['list', 'create', 'ID']),
    ('listdefault --groupopt val create', 'create', []),
    ('listdefault --unkarg', 'listdefault', ['list', 'create', 'ID']),  # unknown argument
    ('listdefault create', 'create', []),
    ('listdefault create --unkarg', 'create', []),
    ('listdefault new', 'create', []),  # aliased
    ('listdefault anyvalue', 'ID', ['change', 'move']),  # chained command
    ('listdefault anyvalue change', 'change', ['change', 'move']),  # chained command
    ('empty', 'empty', []),
])
def test_possible_commands(myapp, cmdargs, current_command_name, subcommand_names):
    args = _split_cmd_args(cmdargs)
    cmd_names = myapp.possible_command_names(args)

    assert cmd_names is not None
    assert set(cmd_names) == set(subcommand_names)

    possible_commands = myapp.commands_for_args(args)
    assert len(possible_commands) > 0
    assert possible_commands[0].default_name == current_command_name, \
        'Current command was not included'


@pytest.mark.parametrize('cmdargs', [
    'nonexisting',  # unknown command
    '--unkarg',
    '--appopt',  # missing value for argument
    'group --unkarg',  # unknown argument
    'group nonexisting',  # unknown command
    'group --unkarg list',   # unknown argument
    'listdefault anyvalue nonexisting',  # unknown command
])
def test_bad_arguments_for_command_names(myapp, cmdargs):
    cmd_names = myapp.possible_command_names(_split_cmd_args(cmdargs))

    assert cmd_names is None
