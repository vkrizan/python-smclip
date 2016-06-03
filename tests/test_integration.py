
import pytest

from integration_classes import *


def _split_cmd_args(cmdargs):
    if not cmdargs:
        return []
    else:
        return cmdargs.split(' ')


@pytest.fixture(scope='function')
def myapp():
    return MyApplication()


# ==========================================================
# TESTS
# ----------------------------------------------------------

# TODO test result_callback for all Command Groups

class TestApplication:

    @pytest.mark.parametrize('cmdargs,expected', [
        ('', None),
        ('--appopt value', 'value'),
    ])
    def test_correct(self, myapp, cmdargs, expected):

        myapp.invoke(_split_cmd_args(cmdargs))
        myapp.preprocess.assert_called_once_with(appopt=expected)
        myapp.this_action.assert_called_once_with(appopt=expected)

    def test_bad_option(self, myapp):

        with pytest.raises(SystemExit) as excinfo:
            myapp.invoke(_split_cmd_args('--badopt value'))

        assert excinfo.value.code == 2

    def test_unknown_command(self, myapp):

        with pytest.raises(smclip.CommandNotFound) as excinfo:
            myapp.invoke(_split_cmd_args('unknowncmd'))

        assert excinfo.value.command_name == 'unknowncmd'
        assert 'unknowncmd' in str(excinfo.value)


class TestSimpleCommand:

    @pytest.mark.parametrize('cmdargs,x_app_opt,x_sub_opt', [
        ('help', None, None),
        ('help --helpopt value', None, 'value'),
        ('--appopt A help', 'A', None),
        ('--appopt A help --helpopt value', 'A', 'value'),
        ('docs', None, None),
        ('docs --helpopt value', None, 'value'),
        ('--appopt A docs', 'A', None),
        ('--appopt A docs --helpopt value', 'A', 'value'),
    ])
    def test_correct(self, myapp, cmdargs, x_app_opt, x_sub_opt):

        myapp.invoke(_split_cmd_args(cmdargs))

        myapp.preprocess.assert_called_once_with(appopt=x_app_opt)
        assert myapp.this_action.call_count == 0

        assert isinstance(myapp.invoked_subcommand, SimpleCommand)
        helpcmd = myapp.invoked_subcommand
        helpcmd.preprocess.assert_called_once_with(helpopt=x_sub_opt)
        helpcmd.this_action.assert_called_once_with(helpopt=x_sub_opt)


class TestPreprocessArgsOverride:

    def test_correct(self, myapp):

        myapp.invoke(_split_cmd_args('override --toreplace value'))

        overridecmd = myapp.invoked_subcommand
        overridecmd.preprocess.assert_called_once_with(toreplace='value')
        overridecmd.this_action.assert_called_once_with(replaced='othervalue')

    def test_incorrect(self, myapp):
        with pytest.raises(AssertionError) as excinfo:
            myapp.invoke(_split_cmd_args('badoverride'))

        assert 'Expected preprocess' in str(excinfo.value)


class TestCommandGroup:

    @pytest.mark.parametrize('cmdargs,x_app_opt,x_grp_opt', [
        ('group', None, None),
        ('group --groupopt value', None, 'value'),
        ('--appopt A group', 'A', None),
        ('--appopt A group --groupopt value', 'A', 'value'),
    ])
    def test_group_invoke(self, myapp, cmdargs, x_app_opt, x_grp_opt):

        myapp.invoke(_split_cmd_args(cmdargs))

        myapp.preprocess.assert_called_once_with(appopt=x_app_opt)
        assert myapp.this_action.call_count == 0

        groupcmd = myapp.invoked_subcommand
        assert isinstance(groupcmd, ItemGroupCommand)
        groupcmd.preprocess.assert_called_once_with(groupopt=x_grp_opt)
        groupcmd.this_action.assert_called_once_with(groupopt=x_grp_opt)
        assert not groupcmd.invoked_subcommand

    @pytest.mark.parametrize('cmdargs,x_app_opt,x_sub_opt', [
        ('listdefault', None, None),
        ('listdefault --listopt value', None, 'value'),
        ('--appopt A listdefault', 'A', None),
        ('--appopt A listdefault --listopt value', 'A', 'value'),
    ])
    def test_group_default_invoke(self, myapp, cmdargs, x_app_opt, x_sub_opt):

        myapp.invoke(_split_cmd_args(cmdargs))

        myapp.preprocess.assert_called_once_with(appopt=x_app_opt)
        assert myapp.this_action.call_count == 0

        groupcmd = myapp.invoked_subcommand
        assert isinstance(groupcmd, ItemGroupCommandDefault)
        # Item group of chained commands with default command does not call its callbacks
        # when invoking default command
        assert groupcmd.preprocess.call_count == 0
        assert groupcmd.this_action.call_count == 0

        defaultgrpcmd = groupcmd.invoked_subcommand
        assert isinstance(defaultgrpcmd, ListCommand)
        assert groupcmd._default_subcmd_cls is defaultgrpcmd.__class__
        defaultgrpcmd.preprocess.assert_called_once_with(listopt=x_sub_opt)
        defaultgrpcmd.this_action.assert_called_once_with(listopt=x_sub_opt)

    @pytest.mark.parametrize('cmdargs,x_app_opt,x_grp_opt,x_sub_opt', [
        ('group create',
            None, None, None),
        ('group create --createopt S',
            None, None, 'S'),
        ('group --groupopt G create --createopt S',
            None, 'G', 'S'),
        ('--appopt A group create',
            'A', None, None),
        ('--appopt A group create --createopt S',
            'A', None, 'S'),
        ('--appopt A group --groupopt G create --createopt S',
            'A', 'G', 'S'),
        # Aliased group command
        ('task create',
            None, None, None),
        ('task create --createopt S',
            None, None, 'S'),
        ('task --groupopt G create --createopt S',
            None, 'G', 'S'),
        # Aliased create subcommand
        ('group new',
            None, None, None),
        ('group new --createopt S',
            None, None, 'S'),
        ('group --groupopt G new --createopt S',
            None, 'G', 'S'),
        # same subcommands but on group with default command
        ('listdefault create',
            None, None, None),
        ('listdefault create --createopt S',
            None, None, 'S'),
        ('listdefault --groupopt G create --createopt S',
            None, 'G', 'S'),
        ('--appopt A listdefault create',
            'A', None, None),
        ('--appopt A listdefault create --createopt S',
            'A', None, 'S'),
        ('--appopt A listdefault --groupopt G create --createopt S',
            'A', 'G', 'S'),
    ])
    def test_group_subcommand(self, myapp, cmdargs, x_app_opt, x_grp_opt, x_sub_opt):

        myapp.invoke(_split_cmd_args(cmdargs))
        myapp.preprocess.assert_called_once_with(appopt=x_app_opt)
        assert myapp.this_action.call_count == 0

        groupcmd = myapp.invoked_subcommand
        groupcmd.preprocess.assert_called_once_with(groupopt=x_grp_opt)
        assert groupcmd.this_action.call_count == 0

        subcmd = groupcmd.invoked_subcommand
        assert isinstance(subcmd, CreateCommand)
        subcmd.preprocess.assert_called_once_with(createopt=x_sub_opt)
        subcmd.this_action.assert_called_once_with(createopt=x_sub_opt)

    @pytest.mark.parametrize('cmdargs,real_names_only,expected', [
        ('group', False, ['myapp']),
        ('group', True, ['myapp']),
        ('group new', False, ['group', 'myapp']),
        ('group new', True, ['group', 'myapp']),
        ('task new', False, ['task', 'myapp']),
        ('task new', True, ['group', 'myapp']),
    ])
    def test_last_cmd_get_parent_names(self, myapp, cmdargs, real_names_only, expected):

        myapp.invoke(_split_cmd_args(cmdargs))

        lastcmd = myapp.invoked_subcommand
        while hasattr(lastcmd, 'invoked_subcommand') and lastcmd.invoked_subcommand:
            lastcmd = lastcmd.invoked_subcommand

        parent_names = lastcmd.get_parent_names(real_names_only=real_names_only)
        assert parent_names == expected


class TestChainedCommands:

    def _common_group_assertions(self, myapp):
        myapp.preprocess.assert_called_once_with(appopt=None)
        assert myapp.this_action.call_count == 0

        groupcmd = myapp.invoked_subcommand
        groupcmd.preprocess.assert_called_once_with(groupopt=None)
        assert groupcmd.this_action.call_count == 0

    @pytest.mark.parametrize('cmdargs,x_cmd_alias,x_cgrp_opt', [
        ('group ID', 'ID', None),
        ('group 1234', '1234', None),
        ('group 1234 --vieweditopt value', '1234', 'value'),
        ('group anything', 'anything', None),
    ])
    def test_direct_call(self, myapp, cmdargs, x_cmd_alias, x_cgrp_opt):

        myapp.invoke(_split_cmd_args(cmdargs))

        self._common_group_assertions(myapp)

        chainedgrp = myapp.invoked_subcommand.invoked_subcommand
        assert isinstance(chainedgrp, smclip.ChainedCommandGroup)
        assert chainedgrp.alias == x_cmd_alias  # tests fallback command
        assert not chainedgrp.invoked_subcommand
        chainedgrp.preprocess.assert_called_once_with(vieweditopt=x_cgrp_opt)
        chainedgrp.this_action.assert_called_once_with(vieweditopt=x_cgrp_opt)
        assert chainedgrp.results_callback.call_count == 0

    @pytest.mark.parametrize('cmdargs,x_cgrp_opt,x_results', [
        ('group 1234 change move here', None,
            [
                ('change', {'changeopt': None}, 'rv-from-change'),
                ('move', {'moveopt': None, 'where': 'here'}, 'rv-from-move'),
            ]
         ),
        ('group 1234 change --changeopt carg', None,
            [
                ('change', {'changeopt': 'carg'}, 'rv-from-change'),
            ]
         ),
        ('group 1234 move here move there', None,
            [
                ('move', {'moveopt': None, 'where': 'here'}, 'rv-from-move'),
                ('move', {'moveopt': None, 'where': 'there'}, 'rv-from-move'),
            ]
         ),
        ('group 1234 relocate here', None,
         [
             ('move', {'moveopt': None, 'where': 'here'}, 'rv-from-move'),
         ]
         ),
    ])
    def test_chained_combinations(self, myapp, cmdargs, x_cgrp_opt, x_results):

        myapp.invoke(_split_cmd_args(cmdargs))

        self._common_group_assertions(myapp)

        chainedgrp = myapp.invoked_subcommand.invoked_subcommand
        assert isinstance(chainedgrp, smclip.ChainedCommandGroup)
        assert chainedgrp.invoked_subcommand is True
        assert len(chainedgrp.invoked_subcommands) == len(x_results)
        chainedgrp.preprocess.assert_called_once_with(vieweditopt=x_cgrp_opt)
        assert chainedgrp.this_action.call_count == 0

        expected_rvs = smclip.ChainedOutputResults()

        for i, chainedcmd in enumerate(chainedgrp.invoked_subcommands):
            x_name, x_values, x_rv = x_results[i]
            assert chainedcmd.name == x_name
            chainedcmd.preprocess.assert_called_once_with(**x_values)
            chainedcmd.this_action.assert_called_once_with(**x_values)
            expected_rvs.add_result(chainedcmd, x_rv)

        assert chainedgrp.results_callback.call_count == 1
        assert len(chainedgrp.results_callback.call_args[0]) == 1
        result_obj = chainedgrp.results_callback.call_args[0][0]
        assert result_obj.results == expected_rvs.results
        assert iter(result_obj)

    def test_help(self, myapp):
        with pytest.raises(SystemExit):
            myapp.invoke(_split_cmd_args('group 1234 change --help'))

        chainedgrp = myapp.invoked_subcommand.invoked_subcommand
        assert chainedgrp.invoked_subcommands, 'Chained subcommand is not marked as called'

        first_chained_cmd = chainedgrp.invoked_subcommands[0]
        assert first_chained_cmd.parent is chainedgrp

    def test_unknown_command(self, myapp):

        with pytest.raises(smclip.CommandNotFound) as excinfo:
            myapp.invoke(_split_cmd_args('empty unknowncmd'))

        assert excinfo.value.command_name == 'unknowncmd'
