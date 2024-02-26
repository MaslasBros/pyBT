#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
.. argparse::
   :module: py_trees.demos.selector
   :func: command_line_argument_parser
   :prog: py-trees-demo-selector

.. graphviz:: dot/demo-selector.dot

.. image:: images/selector.gif

"""
##############################################################################
# Imports
##############################################################################

import pybt
import time

from pybt.nodes.selector import Selector

from pybt.behaviours.count import Count
from pybt.behaviours.behaviours import Running

##############################################################################
# Classes
##############################################################################


def description():
    content = "Higher priority switching and interruption in the children of a selector.\n"
    content += "\n"
    content += "In this example the higher priority child is setup to fail initially,\n"
    content += "falling back to the continually running second child. On the third\n"
    content += "tick, the first child succeeds and cancels the hitherto running child.\n"
    s = content
    return s

def create_root():
    root = Selector("Selector")
    success_after_two = Count(name="Runs after two",
                                                  fail_until=2,
                                                  running_until=2,
                                                  success_until=10)
    always_running = Running(name="Running")
    root.add_children([success_after_two, always_running])
    return root


##############################################################################
# Main
##############################################################################

def main():
    """
    Entry point for the demo script.
    """
    print(description())
    pybt.logging.level = pybt.logging.Level.DEBUG

    root = create_root()

    ####################
    # Execute
    ####################
    root.setup_with_descendants()
    for i in range(1, 4):
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            root.tick_once()
            print("\n")
            print(pybt.display.unicode_tree(root=root, show_status=True))
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
    print("\n")
