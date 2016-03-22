import argparse
import pytest
from smclip.parsers import ArgparserSub, split_docstring


def test_ArgparseSub():

    parser = ArgparserSub()
    parser.add_argument(ArgparserSub.REMAINING_ARGS, nargs=argparse.REMAINDER)
    parser.add_argument('--arg', nargs=1)

    args = '--arg value subcommand --subarg'.split(' ')

    namespace, leftover = parser.parse_known_args(args)
    args_dict = vars(namespace)
    assert len(args_dict) == 2
    assert not leftover
    assert args_dict['arg'] == ['value']
    assert args_dict[ArgparserSub.REMAINING_ARGS] == ['subcommand', '--subarg']


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
