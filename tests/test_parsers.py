import argparse
from smclip.parsers import ArgparserSub


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
