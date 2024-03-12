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


# module variable - unused in pybt
level = Level.DEBUG

class Logger(object):
    """
    :cvar override: whether or not the default python logger has been overridden.
    :vartype override: bool
    """

    def __init__(self, name=None, logger = None):
        self.prefix = '{:<20}'.format(name.replace("\n", " ")) + " : " if name else ""
        self.logger = logger

    def debug(self, msg):
        console.logdebug(self.prefix + msg, self.logger)

    def info(self, msg):
        console.loginfo(self.prefix + msg, self.logger)

    def warning(self, msg):
        console.logwarn(self.prefix + msg, self.logger)

    def error(self, msg):
        console.logerror(self.prefix + msg, self.logger)
