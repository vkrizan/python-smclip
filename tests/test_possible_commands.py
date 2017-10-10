import pytest

from integration_classes import *
from integration_classes import _split_cmd_args


@pytest.mark.parametrize('cmdargs,expected', [
    ('', ['help', 'group', 'listdefault', 'empty', 'override', 'badoverride']),
    ('help', ['help']),  # returns itself
    ('override --toreplace', ['override']),  # returns itself
    ('group', ['list', 'create', 'ID']),
    ('group --groupopt val', ['list', 'create', 'ID']),
    ('group list', ['list']),  # returns itself
    ('group --groupopt val list', ['list']),  # returns itself
    ('group --groupopt val list --listopt', ['list']),  # returns itself
    ('listdefault', ['list', 'create', 'ID']),
    ('listdefault --groupopt val create', ['create']),  # returns itself
    ('listdefault --unkarg', ['list', 'create', 'ID']),  # unknown argument
    ('listdefault create', ['create']),  # returns itself
    ('listdefault create --unkarg', ['create']),  # returns itself
    ('listdefault anyvalue', ['change', 'move']),  # chained command
    ('listdefault anyvalue change', ['change', 'move']),  # chained command
    ('empty', []),

])
def test_possible_command_names(myapp, cmdargs, expected):
    cmd_names = myapp.possible_command_names(_split_cmd_args(cmdargs))

    assert cmd_names is not None
    assert set(cmd_names) == set(expected)


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
