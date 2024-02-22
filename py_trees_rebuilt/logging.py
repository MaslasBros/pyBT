#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
from enum import IntEnum

""" import typing
import uuid

from . import behaviour
from . import blackboard
from . import common
from . import composites
from . import decorators
from . import utilities """

# levels
class Level(IntEnum):
    """
    An enumerator representing the logging level.
    Not valid if you override with your own loggers.
    """
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


# module variable
level = Level.INFO

def banner(msg):
    print("\n" + 80 * "*")
    print("* " + msg.center(80))
    print( 80 * "*" + "\n")


def debug(msg):
    print(msg)


def warning(msg):
    print(msg)


def info(msg):
    print(msg)


def error(msg):
    print(msg)


def logdebug(message):
    '''
    Prefixes ``[DEBUG]`` and colours the message green.

    Args:
        message (:obj:`str`): message to log.
    '''
    print("[DEBUG] " + message)


def loginfo(message):
    '''
    Prefixes ``[ INFO]`` to the message.

    Args:
        message (:obj:`str`): message to log.
    '''
    print("[ INFO] " + message)


def logwarn(message):
    '''
    Prefixes ``[ WARN]`` and colours the message yellow.

    Args:
        message (:obj:`str`): message to log.
    '''
    print("[ WARN] " + message)


def logerror(message):
    '''
    Prefixes ``[ERROR]`` and colours the message red.

    Args:
        message (:obj:`str`): message to log.
    '''
    print("[ERROR] " + message)


def logfatal(message):
    '''
    Prefixes ``[FATAL]`` and colours the message bold red.

    Args:
        message (:obj:`str`): message to log.
    '''
    print("[FATAL] " + message)

class Logger(object):
    """
    :cvar override: whether or not the default python logger has been overridden.
    :vartype override: bool
    """

    def __init__(self, name=None):
        self.prefix = '{:<20}'.format(name.replace("\n", " ")) + " : " if name else ""

    def debug(self, msg):
        global level
        if level < Level.INFO:
            logdebug(self.prefix + msg)

    def info(self, msg):
        global level
        if level < Level.WARN:
            loginfo(self.prefix + msg)

    def warning(self, msg):
        global level
        if level < Level.ERROR:
            logwarn(self.prefix + msg)

    def error(self, msg):
        logerror(self.prefix + msg)
