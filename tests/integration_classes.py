
import smclip

try:
    import unittest.mock as mock
except ImportError:
    import mock


class MyApplication(smclip.CommandGroup):

    def __init__(self):
        parent = super(MyApplication, self)
        parent.__init__(app=self)

        self.name = 'myapp'

        self.register(SimpleCommand)
        self.register(ItemGroupCommand)
        self.register(ItemGroupCommandDefault)
        self.register(EmptyChainedGroup)
        self.register(PreprocessingCommand)
        self.register(BadPreprocessingCommand)

        # Mock methods
        self.preprocess = mock.Mock(wraps=parent.preprocess)
        self.this_action = mock.Mock(wraps=parent.this_action)
        self.results_callback = mock.Mock(wraps=parent.results_callback)

    def add_arguments(self, parser):
        super(MyApplication, self).add_arguments(parser)  # noop
        parser.add_argument('--appopt')


class SimpleCommand(smclip.Command):
    """Print help"""

    default_name = 'help'
    default_aliases = ['docs']

    def __init__(self, *args, **kwargs):
        super(SimpleCommand, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock()

    def add_arguments(self, parser):
        parser.add_argument('--helpopt')


class BadPreprocessingCommand(smclip.Command):
    """Print help"""

    default_name = 'badoverride'

    def __init__(self, *args, **kwargs):
        super(BadPreprocessingCommand, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=False)


class PreprocessingCommand(smclip.Command):
    """Print help"""

    default_name = 'override'

    def __init__(self, *args, **kwargs):
        super(PreprocessingCommand, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=dict(replaced='othervalue'))
        self.this_action = mock.Mock()

    def add_arguments(self, parser):
        parser.add_argument('--toreplace')

class ItemGroupCommand(smclip.CommandGroup):
    """Print help"""

    default_name = 'group'
    default_aliases = ['task']

    def __init__(self, *args, **kwargs):
        super(ItemGroupCommand, self).__init__(*args, **kwargs)

        self.register(ListCommand)
        self.register(CreateCommand)
        self.register(ViewEditCommand, is_fallback=True)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock()
        self.results_callback = mock.Mock()

    def add_arguments(self, parser):
        parser.add_argument('--groupopt')


class ItemGroupCommandDefault(smclip.CommandGroup):
    """Item Group with List command as default"""

    default_name = 'listdefault'

    def __init__(self, *args, **kwargs):
        super(ItemGroupCommandDefault, self).__init__(*args, **kwargs)

        self.register(ListCommand, is_default=True)  # set list as default
        self.register(CreateCommand)
        self.register(ViewEditCommand, is_fallback=True)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock()

    def add_arguments(self, parser):
        parser.add_argument('--groupopt')


class ListCommand(smclip.Command):

    default_name = 'list'
    default_aliases = ['table']

    def __init__(self, *args, **kwargs):
        super(ListCommand, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock()

    def add_arguments(self, parser):
        parser.add_argument('--listopt')


class CreateCommand(smclip.Command):

    default_name = 'create'
    default_aliases = ['new']

    def __init__(self, *args, **kwargs):
        super(CreateCommand, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock()

    def add_arguments(self, parser):
        parser.add_argument('--createopt')


class ViewEditCommand(smclip.ChainedCommandGroup):

    default_name = 'ID'

    def __init__(self, *args, **kwargs):
        super(ViewEditCommand, self).__init__(*args, **kwargs)

        self.register(ItemChange)
        self.register(ItemMove)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock()
        self.results_callback = mock.Mock(wraps=self._results_callback)

    def add_arguments(self, parser):
        parser.add_argument('--vieweditopt')

    def _results_callback(self, rv):
        # Help to identify problems with assertions here
        assert isinstance(rv, smclip.ChainedOutputResults)


class ItemChange(smclip.ChainedCommand):

    default_name = 'change'
    default_aliases = ['edit']

    def __init__(self, *args, **kwargs):
        super(ItemChange, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock(return_value='rv-from-change')

    def add_arguments(self, parser):
        parser.add_argument('--changeopt')


class ItemMove(smclip.ChainedCommand):

    default_name = 'move'
    default_aliases = ['relocate']

    def __init__(self, *args, **kwargs):
        super(ItemMove, self).__init__(*args, **kwargs)

        # Mock methods
        self.preprocess = mock.Mock(return_value=None)
        self.this_action = mock.Mock(return_value='rv-from-move')

    def add_arguments(self, parser):
        parser.add_argument('--moveopt')
        parser.add_argument('where')


class EmptyChainedGroup(smclip.ChainedCommandGroup):

    default_name = 'empty'
