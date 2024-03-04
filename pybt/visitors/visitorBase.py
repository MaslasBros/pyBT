#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Visitors are entities that can be passed to a tree implementation
(e.g. :class:`~py_trees.trees.BehaviourTree`) and used to either visit
each and every behaviour in the tree, or visit behaviours as the tree is
traversed in an executing tick. At each behaviour, the visitor
runs its own method on the behaviour to do as it wishes - logging, introspecting, etc.

.. warning:: Visitors should not modify the behaviours they visit.
"""

class VisitorBase(object):
    """
    Parent template for visitor types.

    Visitors are primarily designed to work with :class:`~py_trees.trees.BehaviourTree`
    but they can be used in the same way for other tree custodian implementations.

    Args:
        full (:obj:`bool`): flag to indicate whether it should be used to visit only traversed nodes or the entire tree

    Attributes:
        full (:obj:`bool`): flag to indicate whether it should be used to visit only traversed nodes or the entire tree
    """
    def __init__(self, full=False):
        self.full = full

    def initialise(self):
        """
        Override this method if any resetting of variables needs to be
        performed between ticks (i.e. visitations).
        """
        pass

    def finalise(self):
        """
        Override this method if any work needs to be
        performed after ticks (i.e. showing data).
        """
        pass

    def run(self, behaviour):
        """
        This method gets run as each behaviour is ticked. Override it to
        perform some activity - e.g. introspect the behaviour
        to store/process logging data for visualisations.

        Args:
            behaviour (:class:`~py_trees.behaviour.Behaviour`): behaviour that is ticking
        """
        pass