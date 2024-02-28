#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Decorators are behaviours that manage a single child and provide common
modifications to their underlying child behaviour (e.g. inverting the result).
That is, they provide a means for behaviours to wear different 'hats' and
this combinatorially expands the capabilities of your behaviour library.

.. image:: images/many-hats.png
   :width: 40px
   :align: center

An example:

.. graphviz:: dot/decorators.dot
   :align: center

.. literalinclude:: examples/decorators.py
   :language: python
   :linenos:


**Decorators (Hats)**

Decorators with very specific functionality:

* :class:`py_trees.decorators.Condition`
* :class:`py_trees.decorators.EternalGuard`
* :class:`py_trees.decorators.Inverter`
* :class:`py_trees.decorators.OneShot`
* :class:`py_trees.decorators.StatusToBlackboard`
* :class:`py_trees.decorators.Timeout`

And the X is Y family:

* :class:`py_trees.decorators.FailureIsRunning`
* :class:`py_trees.decorators.FailureIsSuccess`
* :class:`py_trees.decorators.RunningIsFailure`
* :class:`py_trees.decorators.RunningIsSuccess`
* :class:`py_trees.decorators.SuccessIsFailure`
* :class:`py_trees.decorators.SuccessIsRunning`

**Decorators for Blocking Behaviours**

It is worth making a note of the effect of decorators on
behaviours that return :data:`~py_trees.common.Status.RUNNING` for
some time before finally returning  :data:`~py_trees.common.Status.SUCCESS`
or  :data:`~py_trees.common.Status.FAILURE` (blocking behaviours) since
the results are often at first, surprising.

A decorator, such as :func:`py_trees.decorators.RunningIsSuccess` on
a blocking behaviour will immediately terminate the underlying child and
re-intialise on it's next tick. This is necessary to ensure the underlying
child isn't left in a dangling state (i.e.
:data:`~py_trees.common.Status.RUNNING`), but is often not what is being
sought.

The typical use case being attempted is to convert the blocking
behaviour into a non-blocking behaviour. If the underlying child has no
state being modified in either the :meth:`~py_trees.behaviour.Behaviour.initialise`
or :meth:`~py_trees.behaviour.Behaviour.terminate` methods (e.g. machinery is
entirely launched at init or setup time), then conversion to a non-blocking
representative of the original succeeds. Otherwise, another approach is
needed. Usually this entails writing a non-blocking counterpart, or
combination of behaviours to affect the non-blocking characteristics.
"""

##############################################################################
# Imports
##############################################################################

import functools

from typing import Callable, Union
from inspect import signature

from .. import behaviour
from ..bb import blackboard
from .. import common

##############################################################################
# Classes
##############################################################################

ConditionType = Union[
    Callable[[], bool],
    Callable[[], common.Status],
    Callable[[blackboard.Blackboard], bool],
    Callable[[blackboard.Blackboard], common.Status]
]

class Decorator(behaviour.Behaviour):
    """
    A decorator is responsible for handling the lifecycle of a single
    child beneath

    Args:
        child: the child to be decorated
        name: the decorator name

    Raises:
        TypeError: if the child is not an instance of :class:`~py_trees.behaviour.Behaviour`
    """
    def __init__(
            self,
            child: behaviour.Behaviour = None,
            name=common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name)
        
        # Checks
        if child is not None:
            if not isinstance(child, behaviour.Behaviour):
                raise TypeError("A decorator's child must be an instance of py_trees.behaviours.Behaviour")
            # Initialise
            self.children.append(child)
            # Give a convenient alias
            self.decorated = self.children[0]
            self.decorated.parent = self
        else:
            self.decorated = None

    def add_decorated(self, decoratedNode):
        if self.decorated is not None:
            raise ValueError("Decorator {0} already contains a child node.")

        self.children.append(decoratedNode)
        # Give a convenient alias
        self.decorated = self.children[0]
        self.decorated.parent = self

    def tick(self):
        """
        A decorator's tick is exactly the same as a normal proceedings for
        a Behaviour's tick except that it also ticks the decorated child node.

        Yields:
            :class:`~py_trees.behaviour.Behaviour`: a reference to itself or one of its children
        """
        self.logger.debug("%s.tick()" % self.__class__.__name__)
        # initialise just like other behaviours/composites
        if self.status != common.Status.RUNNING:
            self.initialise()
        # interrupt proceedings and process the child node
        # (including any children it may have as well)
        for node in self.decorated.tick():
            yield node
        # resume normal proceedings for a Behaviour's tick
        new_status = self.update()
        if new_status not in list(common.Status):
            self.logger.error("A behaviour returned an invalid status, setting to INVALID [%s][%s]" % (new_status, self.name))
            new_status = common.Status.INVALID
        if new_status != common.Status.RUNNING:
            self.stop(new_status)
        self.status = new_status
        yield self

    def stop(self, new_status):
        """
        As with other composites, it checks if the child is running
        and stops it if that is the case.

        Args:
            new_status (:class:`~py_trees.common.Status`): the behaviour is transitioning to this new status
        """
        self.logger.debug("%s.stop(%s)" % (self.__class__.__name__, new_status))
        self.terminate(new_status)
        # priority interrupt handling
        if new_status == common.Status.INVALID:
            self.decorated.stop(new_status)
        # if the decorator returns SUCCESS/FAILURE and should stop the child
        if self.decorated.status == common.Status.RUNNING:
            self.decorated.stop(common.Status.INVALID)
        self.status = new_status

    def tip(self):
        """
        Get the *tip* of this behaviour's subtree (if it has one) after it's last
        tick. This corresponds to the the deepest node that was running before the
        subtree traversal reversed direction and headed back to this node.

        Returns:
            :class:`~py_trees.behaviour.Behaviour` or :obj:`None`: child behaviour, itself or :obj:`None` if its status is :data:`~py_trees.common.Status.INVALID`
        """
        if self.decorated.status != common.Status.INVALID:
            return self.decorated.tip()
        else:
            return super().tip()

    def update(self):
        """
        :data:`~py_trees.common.Status.SUCCESS` if the decorated child has returned
        the specified status, otherwise :data:`~py_trees.common.Status.RUNNING`.
        This decorator will never return :data:`~py_trees.common.Status.FAILURE`

        Returns:
            :class:`~py_trees.common.Status`: the behaviour's new status :class:`~py_trees.common.Status`
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        self.feedback_message = "'{0}' has status {1}, waiting for {2}".format(self.decorated.name, self.decorated.status, self.succeed_status)
        if self.decorated.status == self.succeed_status:
            return common.Status.SUCCESS
        return common.Status.RUNNING
