#!/usr/bin/env python3
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
.. argparse::
   :module: py_trees.demos.display_modes
   :func: command_line_argument_parser
   :prog: py-trees-demo-display-modes

.. figure:: images/display_modes.png
   :align: center

   Console Screenshot
"""

##############################################################################
# Imports
##############################################################################

import itertools
import py_trees_rebuilt

from py_trees_rebuilt.nodes.sequence import Sequence
from py_trees_rebuilt.behaviours.count import Count
from py_trees_rebuilt.trees import BehaviourTree
from py_trees_rebuilt.visitors.snapshotVisitor import SnapshotVisitor

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates usage of the ascii/unicode display modes.\n"
    content += "\n"
    content += "...\n"
    content += "...\n"
    s = content
    return s

def create_root() -> py_trees_rebuilt.behaviour.Behaviour:
    """
    Create the tree to be ticked/displayed.

    Returns:
        the root of the tree
    """
    root = Sequence(name="root")
    child = Sequence(name="child1")
    child2 = Sequence(name="child2")
    child3 = Sequence(name="child3")
    root.add_child(child)
    root.add_child(child2)
    root.add_child(child3)

    child.add_child(Count(name='Count', fail_until=0, running_until=1, success_until=6,))
    child2.add_child(Count(name='Count', fail_until=0, running_until=1, success_until=6,))
    child2_child1 = Sequence(name="Child2_child1")
    child2_child1.add_child(Count(name='Count', fail_until=0, running_until=1, success_until=6,))
    child2.add_child(child2_child1)
    child3.add_child(Count(name='Count', fail_until=0, running_until=1, success_until=6,))
    return root


##############################################################################
# Main
##############################################################################


def main():
    """
    Entry point for the demo script.
    """
    print(description())
    print("-------------------------------------------------------------------------------")
    print("$ py_trees.blackboard.Client(name='Blackboard')")
    print("$ foo.register_key(key='dude', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/dudette', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/foo/bar/wow', access=py_trees.common.Access.WRITE)")
    print("-------------------------------------------------------------------------------")

    snapshot_visitor = SnapshotVisitor()
    tree = BehaviourTree(create_root())
    tree.add_visitor(snapshot_visitor)

    for tick in range(2):
        tree.tick()
        for show_visited, show_status in itertools.product([False, True], [False, True]):
            py_trees_rebuilt.console.banner("Tick {} / show_only_visited=={} / show_status=={}".format(tick, show_visited, show_status))
            print(
                py_trees_rebuilt.display.unicode_tree(
                    tree.root,
                    show_status=show_status,
                    show_only_visited=show_visited,
                    visited=snapshot_visitor.visited,
                    previously_visited=snapshot_visitor.previously_visited
                )
            )
            print()
