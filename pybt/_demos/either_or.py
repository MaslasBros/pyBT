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
   :module: py_trees.demos.either_or
   :func: command_line_argument_parser
   :prog: py-trees-demo-either-or

.. graphviz:: dot/demo-either-or.dot

.. image:: images/either_or.gif
"""

##############################################################################
# Imports
##############################################################################

import functools
import operator
import time
import pybt

from pybt.common import *

from pybt.nodes.sequence import Sequence
from pybt.trees import BehaviourTree
from pybt.visitors.snapshotVisitor import SnapshotVisitor
from pybt.visitors.debugVisitor import DebugVisitor

from pybt.nodes.parallel import Parallel
from pybt.nodes.selector import Selector
from pybt.nodes.failureIsRunning import FailureIsRunning

from pybt.behaviours.successEveryN import SuccessEveryN
from pybt.behaviours.setBlackboardVariable import SetBlackboardVariable
from pybt.behaviours.tickCounter import TickCounter
from pybt.behaviours.behaviours import Running

##############################################################################
# Classes
##############################################################################


def description(root):
    content = "A demonstration of the 'either_or' idiom.\n\n"
    content += "This behaviour tree pattern enables triggering of subtrees\n"
    content += "with equal priority (first in, first served).\n"
    content += "\n"
    content += "EVENTS\n"
    content += "\n"
    content += " -  3 : joystick one enabled, task one starts\n"
    content += " -  5 : task one finishes\n"
    content += " -  6 : joystick two enabled, task two starts\n"
    content += " -  7 : joystick one enabled, task one ignored, task two continues\n"
    content += " -  8 : task two finishes\n"
    content += "\n"
    s = content
    return s

def pre_tick_handler(behaviour_tree):
    print("\n--------- Run %s ---------\n" % behaviour_tree.count)


def post_tick_handler(snapshot_visitor, behaviour_tree):
    print(
        "\n" + pybt.display.unicode_tree(
            root=behaviour_tree.root,
            visited=snapshot_visitor.visited,
            previously_visited=snapshot_visitor.previously_visited
        )
    )
    print(pybt.display.unicode_blackboard())


def create_root():
    trigger_one = FailureIsRunning(
        name="FisR",
        child= SuccessEveryN(
            name="Joystick 1",
            n=4
        )
    )
    trigger_two = FailureIsRunning(
        name="FisR",
        child= SuccessEveryN(
            name="Joystick 2",
            n=7
        )
    )
    enable_joystick_one = SetBlackboardVariable(
        name="Joy1 - Enabled",
        variable_name="joystick_one",
        variable_value="enabled")
    enable_joystick_two = SetBlackboardVariable(
        name="Joy2 - Enabled",
        variable_name="joystick_two",
        variable_value="enabled")
    reset_joystick_one = SetBlackboardVariable(
        name="Joy1 - Disabled",
        variable_name="joystick_one",
        variable_value="disabled")
    reset_joystick_two = SetBlackboardVariable(
        name="Joy2 - Disabled",
        variable_name="joystick_two",
        variable_value="disabled")
    task_one = TickCounter(
        name="Task 1",
        duration=2,
        completion_status= Status.SUCCESS
    )
    task_two = TickCounter(
        name="Task 2",
        duration=2,
        completion_status= Status.SUCCESS
    )
    idle = Running(name="Idle")
    either_or = pybt.idioms.either_or(
        name="Either Or",
        conditions=[
            ComparisonExpression("joystick_one", "enabled", operator.eq),
            ComparisonExpression("joystick_two", "enabled", operator.eq),
        ],
        subtrees=[task_one, task_two],
        namespace="either_or",
    )
    root = Parallel(
        name="Root",
        policy= ParallelPolicy.SuccessOnAll(synchronise=False)
    )
    reset = Sequence(name="Reset")
    reset.add_children([reset_joystick_one, reset_joystick_two])
    joystick_one_events = Sequence(name="Joy1 Events")
    joystick_one_events.add_children([trigger_one, enable_joystick_one])
    joystick_two_events = Sequence(name="Joy2 Events")
    joystick_two_events.add_children([trigger_two, enable_joystick_two])
    tasks = Selector(name="Tasks")
    tasks.add_children([either_or, idle])
    root.add_children([reset, joystick_one_events, joystick_two_events, tasks])
    return root


##############################################################################
# Main
##############################################################################


def main():
    """
    Entry point for the demo script.
    """
    pybt.logging.level = pybt.logging.Level.DEBUG
    root = create_root()
    print(description(root))

    ####################
    # Tree Stewardship
    ####################
    behaviour_tree = BehaviourTree(root)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(DebugVisitor())
    snapshot_visitor = SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(functools.partial(post_tick_handler, snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)

    ####################
    # Tick Tock
    ####################
    for unused_i in range(1, 11):
        try:
            behaviour_tree.tick()
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")
