#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#

from enum import IntEnum
from . import console

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
            console.logdebug(self.prefix + msg)

    def info(self, msg):
        global level
        if level < Level.WARN:
            console.loginfo(self.prefix + msg)

    def warning(self, msg):
        global level
        if level < Level.ERROR:
            console.logwarn(self.prefix + msg)

    def error(self, msg):
        console.logerror(self.prefix + msg)
