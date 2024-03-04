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
   :module: py_trees.demos.logging
   :func: command_line_argument_parser
   :prog: py-trees-demo-logging

.. graphviz:: dot/demo-logging.dot

.. image:: images/logging.gif
"""

##############################################################################
# Imports
##############################################################################

import functools
import json
import pybt
import time

import pybt.console as console

from pybt.nodes.selector import Selector
from pybt.nodes.sequence import Sequence
from pybt.nodes.parallel import Parallel
from pybt.nodes.decorator import Decorator

from pybt.behaviours.periodic import Periodic
from pybt.behaviours.successEveryN import SuccessEveryN
from pybt.behaviours.behaviours import Success

from pybt.trees import BehaviourTree

from pybt.visitors.debugVisitor import DebugVisitor
from pybt.visitors.displaySnapshotVisitor import DisplaySnapshotVisitor

##############################################################################
# Classes
##############################################################################


def description(root):
    content = "A demonstration of logging with trees.\n\n"
    content += "This demo utilises a SnapshotVisitor to trigger\n"
    content += "a post-tick handler to dump a serialisation of the\n"
    content += "tree to a json log file.\n"
    content += "\n"
    content += "This coupling of visitor and post-tick handler can be\n"
    content += "used for any kind of event handling - the visitor is the\n"
    content += "trigger and the post-tick handler the action. Aside from\n"
    content += "logging, the most common use case is to serialise the tree\n"
    content += "for messaging to a graphical, runtime monitor.\n"
    content += "\n"
    s = content
    return s

def logger(snapshot_visitor, behaviour_tree):
    """
    A post-tick handler that logs the tree (relevant parts thereof) to a yaml file.
    """
    if snapshot_visitor.changed:
        print(console.cyan + "Logging.......................yes\n" + console.reset)
        tree_serialisation = {
            'tick': behaviour_tree.count,
            'nodes': []
        }
        for node in behaviour_tree.root.iterate():
            node_type_str = "Behaviour"
            for behaviour_type in [ Sequence,
                                    Selector,
                                    Parallel,
                                    Decorator]:
                if isinstance(node, behaviour_type):
                    node_type_str = behaviour_type.__name__
            node_snapshot = {
                'name': node.name,
                'id': str(node.id),
                'parent_id': str(node.parent.id) if node.parent else "none",
                'child_ids': [str(child.id) for child in node.children],
                'tip_id': str(node.tip().id) if node.tip() else 'none',
                'class_name': str(node.__module__) + '.' + str(type(node).__name__),
                'type': node_type_str,
                'status': node.status.value,
                'message': node.feedback_message,
                'is_active': True if node.id in snapshot_visitor.visited else False
                }
            tree_serialisation['nodes'].append(node_snapshot)
        if behaviour_tree.count == 0:
            with open('dump.json', 'w+') as outfile:
                json.dump(tree_serialisation, outfile, indent=4)
        else:
            with open('dump.json', 'a') as outfile:
                json.dump(tree_serialisation, outfile, indent=4)
    else:
        print(console.yellow + "Logging.......................no\n" + console.reset)


def create_tree():
    every_n_success = SuccessEveryN("EveryN", 5)
    sequence = Sequence(name="Sequence")
    guard = Success("Guard")
    periodic_success = Periodic("Periodic", 3)
    finisher = Success("Finisher")
    sequence.add_child(guard)
    sequence.add_child(periodic_success)
    sequence.add_child(finisher)
    sequence.blackbox_level = pybt.common.BlackBoxLevel.COMPONENT
    idle = Success("Idle")
    root = Selector(name="Logging")
    root.add_child(every_n_success)
    root.add_child(sequence)
    root.add_child(idle)
    return root

##############################################################################
# Main
##############################################################################

def main():
    """
    Entry point for the demo script.
    """
    pybt.logging.level = pybt.logging.Level.DEBUG
    tree = create_tree()
    print(description(tree))

    ####################
    # Tree Stewardship
    ####################
    behaviour_tree = BehaviourTree(tree)

    debug_visitor = DebugVisitor()
    snapshot_visitor = DisplaySnapshotVisitor()

    behaviour_tree.visitors.append(debug_visitor)
    behaviour_tree.visitors.append(snapshot_visitor)

    behaviour_tree.add_post_tick_handler(functools.partial(logger, snapshot_visitor))

    behaviour_tree.setup(timeout=15)

    ####################
    # Tick Tock
    ####################
    cnt = 0
    while cnt <= 3:
        behaviour_tree.tick()
        time.sleep(0.5)
        cnt += 1
    print("\n")
