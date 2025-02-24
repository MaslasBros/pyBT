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
   :module: py_trees.demos.stewardship
   :func: command_line_argument_parser
   :prog: py-trees-demo-tree-stewardship

.. graphviz:: dot/demo-tree-stewardship.dot

.. image:: images/tree_stewardship.gif
"""

##############################################################################
# Imports
##############################################################################

import pybt
import time

from pybt.bb.blackboard import Blackboard
from pybt.trees import BehaviourTree
from pybt.visitors.debugVisitor import DebugVisitor
from pybt.visitors.displaySnapshotVisitor import DisplaySnapshotVisitor

from pybt.behaviours.behaviours import Success

from pybt.nodes.sequence import Sequence
from pybt.nodes.selector import Selector

##############################################################################
# Classes
##############################################################################


def description():
    content = "A demonstration of tree stewardship.\n\n"
    content += "A slightly less trivial tree that uses a simple stdout pre-tick handler\n"
    content += "and both the debug and snapshot visitors for logging and displaying\n"
    content += "the state of the tree.\n"
    content += "\n"
    content += "EVENTS\n"
    content += "\n"
    content += " -  3 : sequence switches from running to success\n"
    content += " -  4 : selector's first child flicks to success once only\n"
    content += " -  8 : the fallback idler kicks in as everything else fails\n"
    content += " - 14 : the first child kicks in again, aborting a running sequence behind it\n"
    content += "\n"
    s = content
    return s

def pre_tick_handler(behaviour_tree):
    print("\n--------- Run %s ---------\n" % behaviour_tree.count)

class SuccessEveryN(pybt.behaviours.successEveryN.SuccessEveryN):
    def __init__(self):
        super().__init__(name="EveryN", n=5)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("count", access=pybt.common.Access.WRITE)

    def update(self):
        status = super().update()
        self.blackboard.count = self.count
        return status


class PeriodicSuccess(pybt.behaviours.periodic.Periodic):
    def __init__(self):
        super().__init__(name="Periodic", n=3)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("period", access=pybt.common.Access.WRITE)

    def update(self):
        status = super().update()
        self.blackboard.period = self.period
        return status


class Finisher(pybt.behaviour.Behaviour):
    def __init__(self):
        super().__init__(name="Finisher")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("count", access=pybt.common.Access.READ)
        self.blackboard.register_key("period", access=pybt.common.Access.READ)

    def update(self):
        print("---------------------------")
        print("        Finisher")
        print("  Count : {}".format(self.blackboard.count))
        print("  Period: {}".format(self.blackboard.period))
        print("---------------------------")
        return pybt.common.Status.SUCCESS


def create_tree():
    every_n_success = SuccessEveryN()
    sequence = Sequence(name="Sequence")
    guard = Success("Guard")
    periodic_success = PeriodicSuccess()
    finisher = Finisher()
    sequence.add_child(guard)
    sequence.add_child(periodic_success)
    sequence.add_child(finisher)
    idle = Success("Idle")
    root = Selector(name="Demo Tree")
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
    print(description())

    ####################
    # Tree Stewardship
    ####################
    Blackboard.enable_activity_stream(100)
    behaviour_tree = BehaviourTree(tree)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(DebugVisitor())
    behaviour_tree.visitors.append(
        DisplaySnapshotVisitor(
            display_blackboard=True,
            display_activity_stream=True)
    )
    behaviour_tree.setup(timeout=15)

    ####################
    # Tick Tock
    ####################

    cnt = 0
    while cnt <= 10:
        behaviour_tree.tick()
        time.sleep(0.5)
        cnt +=1
    print("\n")
