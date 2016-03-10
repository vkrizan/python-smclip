Simple Multi Command Line Parser
================================

.. image:: https://travis-ci.org/vkrizan/python-smclip.svg?branch=master
    :target: https://travis-ci.org/vkrizan/python-smclip

.. image:: https://codecov.io/github/vkrizan/python-smclip/coverage.svg?branch=master
    :target: https://codecov.io/github/vkrizan/python-smclip?branch=master

SMCLIP is a simple framework for parsing multi command line arguments using
python's builtin ArgumentParser.  With SMCLIP you are able to built git-like
commands.  Commands are created by inheriting from base Command classes and
extending their callbacks.

Core features includes:

- building trees of multi-level sub-commands
- support for default sub-commands (e.g. ``git stash [save]``)
- support for fallback sub-commands (when sub-command is not found; e.g.
  catching ID)
- support for chained sub-commands
- sub-command lazy loading


Differences with ...
--------------------

Why you should choose SMCLIP when [X] supports sub-commands?

ArgumentParser
^^^^^^^^^^^^^^

https://docs.python.org/3/library/argparse.html#sub-commands

Python's ArgumentParser support sub-commands by adding sub-parsers to
the parent parser.  The ArgumentParser with sub-commands considers
that a CLI application is simple and does simple operations.
A CLI application starts can get confusing to users (in help) when
there are more and more sub-commands being added.

Subparsers of ArgumentParser should be constructed prior to
calling the base parser.  Subparsers don not support any routing
based on the commands.


Click
^^^^^

http://click.pocoo.org/latest/

Click utilizes Python's decorators to create sub-commands hierarchy.
Using decorators makes the code more readable.  On the other hand,
extending Click is done by creating new decorators.
Supporting new parsing techniques (default or fallback commands) and
conditional callback triggering is not done simplistically.


Cement
^^^^^^

http://builtoncement.com/

Cement is a framework intended for complex CLI applications. Cement
comes with multiple set of utilities (logging, caching).  Command line
parsing is a one part of Cement framework.  Cement support sub-commands
by nesting controllers.  Default and fallback commands and conditional
callback triggering is done by extending core controllers.


Argument Examples
-----------------

::

  # Simple command
  (1)$ app help
           *--*
             +---- sub-command of base application

  # Two commands
  (2)$ app task list
  (3)$ app --debug task list --listopt
       *----+----* *--* *-----+------*
             \       \         \
              \       \         +------- list sub-command with option
               \       +---------------- task command
                +----------------------- application with its own option

  # fallback command
  (4)$ app task 1234 --viewopt
                *-----+------*
                       \
                        +------- fallback command catching ID

  # chained commands
  (5)$ app task 1234 change --state ASSIGNED assign person
                     *----------+----------* *-----+-----*
                                |                   \
                                 \                   +------ chained command
                                  \                          with positional
                                   \                         argument
                                    \
                                     +---------------------- chained command
                                                             with option

Callbacks
---------

``preprocess``
^^^^^^^^^^^^^^

``preprocess`` is called after successful parsing of command's arguments.
Invocation is done even when a sub-command is being called.
``preprocess`` is not called when default command is in effect.


``this_action``
^^^^^^^^^^^^^^^

``this_action`` is a main callback for actions in current command.
This callback is called after ``preprocess`` and only when current command
is final (no other sub-commands are being invoked).  Exceptions are
chained command, in which the ``this_action`` is invoked every time.


``results_callback``
^^^^^^^^^^^^^^^^^^^^

(commands group only)

``results_callback`` is called after a sub-command invocation is done.
A return value from sub-command, returned by ``this_action`` callback,
is passed as a positional argument.  Results from chained commands
are wrapped and passed in ``ChainedOutputResults`` class object.
