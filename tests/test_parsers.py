import argparse
import pytest
import smclip
from smclip.parsers import ArgparserSub, split_docstring


class TestArgparseSub():

    def _create_parser(self, **opts):
        parserobj = ArgparserSub(**opts)
        parserobj.add_argument(ArgparserSub.REMAINING_ARGS, nargs=argparse.REMAINDER)
        parserobj.add_argument('--arg', nargs=1)
        return parserobj

    def test_arg_parsing(self):
        parser = self._create_parser()
        args = '--arg value subcommand --subarg'.split(' ')

        namespace, leftover = parser.parse_known_args(args)
        args_dict = vars(namespace)
        assert len(args_dict) == 2
        assert not leftover
        assert args_dict['arg'] == ['value']
        assert args_dict[ArgparserSub.REMAINING_ARGS] == ['subcommand', '--subarg']

    def test_formatted_help(self):

        class MySubcommand(smclip.Command):
            """Subcommand help"""
            default_name = 'subcmd_name'

        subcommands = {MySubcommand.default_name: MySubcommand()}

        parser = self._create_parser(subcommands=subcommands)

        formatted_help = parser.format_help()
        print(formatted_help)
        assert formatted_help
        assert 'subcommands:' in formatted_help
        assert 'subcmd_name' in formatted_help, 'Subcommand not found in help'
        assert 'Subcommand help' in formatted_help, "Subcommand's help not found in common help"


@pytest.mark.parametrize('docstring', (
        """Title""",
        # ==
        """ Title """,
        # ==
        """
        Title""",
))
def test_split_docstring_title_only(docstring):
    title, description = split_docstring(docstring)
    assert title == 'Title'
    assert not description

@pytest.mark.parametrize('docstring', (
        """Title

        Some Description""",
        # ==
        """ Title

        Some Description
        """,
        # ==
        """
        Title

        Some Description
        """,
))
def test_split_docstring_description(docstring):
    title, description = split_docstring(docstring)
    assert title == 'Title'
    assert description == 'Some Description'
