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
   :module: py_trees.demos.context_switching
   :func: command_line_argument_parser
   :prog: py-trees-demo-context-switching

.. graphviz:: dot/demo-context_switching.dot

.. image:: images/context_switching.gif
"""

##############################################################################
# Imports
##############################################################################

import py_trees_rebuilt
import time

from py_trees_rebuilt.nodes.parallel import Parallel
from py_trees_rebuilt.nodes.sequence import Sequence
from py_trees_rebuilt.behaviours.count import Count

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates context switching with parallels and sequences.\n"
    content += "\n"
    content += "A context switching behaviour is run in parallel with a work sequence.\n"
    content += "Switching the context occurs in the initialise() and terminate() methods\n"
    content += "of the context switching behaviour. Note that whether the sequence results\n"
    content += "in failure or success, the context switch behaviour will always call the\n"
    content += "terminate() method to restore the context. It will also call terminate()\n"
    content += "to restore the context in the event of a higher priority parent cancelling\n"
    content += "this parallel subtree.\n"
    s = content
    return s

class ContextSwitch(py_trees_rebuilt.behaviour.Behaviour):
    """
    An example of a context switching class that sets (in ``initialise()``)
    and restores a context (in ``terminate()``). Use in parallel with a
    sequence/subtree that does the work while in this context.

    .. attention:: Simply setting a pair of behaviours (set and reset context) on
        either end of a sequence will not suffice for context switching. In the case
        that one of the work behaviours in the sequence fails, the final reset context
        switch will never trigger.

    """
    def __init__(self, name="ContextSwitch"):
        super(ContextSwitch, self).__init__(name)
        self.feedback_message = "no context"

    def initialise(self):
        """
        Backup and set a new context.
        """
        self.logger.debug("%s.initialise()[switch context]" % (self.__class__.__name__))
        # Some actions that:
        #   1. retrieve the current context from somewhere
        #   2. cache the context internally
        #   3. apply a new context
        self.feedback_message = "new context"

    def update(self):
        """
        Just returns RUNNING while it waits for other activities to finish.
        """
        self.logger.debug("%s.update()[RUNNING][%s]" % (self.__class__.__name__, self.feedback_message))
        return py_trees_rebuilt.common.Status.RUNNING

    def terminate(self, new_status):
        """
        Restore the context with the previously backed up context.
        """
        self.logger.debug("%s.terminate()[%s->%s][restore context]" % (self.__class__.__name__, self.status, new_status))
        # Some actions that:
        #   1. restore the cached context
        self.feedback_message = "restored context"


def create_root():
    root = Parallel(name="Parallel", policy=py_trees_rebuilt.common.ParallelPolicy.SuccessOnOne())
    context_switch = ContextSwitch(name="Context")
    sequence = Sequence(name="Sequence")
    for job in ["Action 1", "Action 2"]:
        success_after_two = Count(name=job,
                                fail_until=0,
                                running_until=2,
                                success_until=10)
        sequence.add_child(success_after_two)
    root.add_child(context_switch)
    root.add_child(sequence)
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
            print("\n")
            print("{}".format(py_trees_rebuilt.display.unicode_tree(root, show_status=True)))
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
    print("\n")
