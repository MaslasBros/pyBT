#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#

##############################################################################
# Description
##############################################################################

"""
Simple colour definitions and syntax highlighting for the console.

----

**Colour Definitions**

The current list of colour definitions include:

 * ``Regular``: black, red, green, yellow, blue, magenta, cyan, white,
 * ``Bold``: bold, bold_black, bold_red, bold_green, bold_yellow, bold_blue, bold_magenta, bold_cyan, bold_white

These colour definitions can be used in the following way:

.. code-block:: python

   import py_trees.console as console
   print(console.cyan + "    Name" + console.reset + ": " + console.yellow + "Dude" + console.reset)

"""

##############################################################################
# Imports
##############################################################################
import sys

reset = ""
bold = ""
dim = ""
underlined = ""
blink = ""
black, red, green, yellow, blue, magenta, cyan, white = ["" for i in range(30, 38)]
bold_black, bold_red, bold_green, bold_yellow, bold_blue, bold_magenta, bold_cyan, bold_white = ["" for i in range(30, 38)]

colours = [bold, dim, underlined, blink,
           black, red, green, yellow, blue, magenta, cyan, white,
           bold_black, bold_red, bold_green, bold_yellow, bold_blue, bold_magenta, bold_cyan, bold_white
           ]
"""List of all available colours."""

def pretty_print(msg, colour=white):
        sys.stdout.write(msg)

def pretty_println(msg, colour=white):
        sys.stdout.write(msg)

##############################################################################
# Console
##############################################################################

def banner(msg):
    print(green + "\n" + 80 * "*" + reset)
    print(green + "* " + bold_white + msg.center(80) + reset)
    print(green + 80 * "*" + "\n" + reset)


def debug(msg):
    print(green + msg + reset)


def warning(msg):
    print(yellow + msg + reset)


def info(msg):
    print(msg)


def error(msg):
    print(red + msg + reset)


def logdebug(message):
    '''
    Prefixes ``[DEBUG]`` and colours the message green.

    Args:
        message (:obj:`str`): message to log.
    '''
    print(green + "[DEBUG] " + message + reset)


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
    print(yellow + "[ WARN] " + message + reset)


def logerror(message):
    '''
    Prefixes ``[ERROR]`` and colours the message red.

    Args:
        message (:obj:`str`): message to log.
    '''
    print(red + "[ERROR] " + message + reset)


def logfatal(message):
    '''
    Prefixes ``[FATAL]`` and colours the message bold red.

    Args:
        message (:obj:`str`): message to log.
    '''
    print(bold_red + "[FATAL] " + message + reset)