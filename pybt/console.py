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

##############################################################################
# Console
##############################################################################

def logdebug(message, logger):
    '''
    Prefixes ``[DEBUG]`` and colours the message green.

    Args:
        message (:obj:`str`): message to log.
    '''
    logger.Log("[DEBUG] " + message)


def loginfo(message, logger):
    '''
    Prefixes ``[ INFO]`` to the message.

    Args:
        message (:obj:`str`): message to log.
    '''
    logger.Log("[ INFO] " + message)


def logwarn(message, logger):
    '''
    Prefixes ``[ WARN]`` and colours the message yellow.

    Args:
        message (:obj:`str`): message to log.
    '''
    logger.LogWarning("[ WARN] " + message)


def logerror(message, logger):
    '''
    Prefixes ``[ERROR]`` and colours the message red.

    Args:
        message (:obj:`str`): message to log.
    '''
    logger.LogError("[ERROR] " + message)


def logfatal(message, logger):
    '''
    Prefixes ``[FATAL]`` and colours the message bold red.

    Args:
        message (:obj:`str`): message to log.
    '''
    logger.LogError("[FATAL] " + message)