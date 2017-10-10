import sys
import os
import pytest

sys.path.append(os.path.dirname(__file__))

from integration_classes import MyApplication, _split_cmd_args


@pytest.fixture(scope='function')
def myapp():
    return MyApplication()
