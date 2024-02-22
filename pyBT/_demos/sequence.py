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
   :module: py_trees.demos.sequence
   :func: command_line_argument_parser
   :prog: py-trees-demo-sequence

.. graphviz:: dot/demo-sequence.dot

.. image:: images/sequence.gif
"""

##############################################################################
# Imports
##############################################################################

import py_trees_rebuilt
import time

from py_trees_rebuilt.behaviours.count import Count
from py_trees_rebuilt.nodes.sequence import Sequence

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates sequences in action.\n\n"
    content += "A sequence is populated with 2-tick jobs that are allowed to run through to\n"
    content += "completion.\n"
    s = content
    return s

def create_root():
    root = Sequence("Sequence", memory=True)
    for action in ["Action 1", "Action 2", "Action 3"]:
        success_after_two = Count(name=action,
                                                      fail_until=0,
                                                      running_until=1,
                                                      success_until=10)
        root.add_child(success_after_two)
    return root


##############################################################################
# Main
##############################################################################

def main():
    """
    Entry point for the demo script.
    """
    print(description())
    py_trees_rebuilt.logging.level = py_trees_rebuilt.logging.Level.DEBUG

    root = create_root()

    ####################
    # Execute
    ####################
    root.setup_with_descendants()
    for i in range(1, 6):
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            root.tick_once()
            print(py_trees_rebuilt.display.unicode_tree(root=root, show_status=True))
            time.sleep(1)
        except KeyboardInterrupt:
            break
    print("\n")
