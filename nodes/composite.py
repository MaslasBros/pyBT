#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Composites are responsible for directing the path traced through
the tree on a given tick (execution). They are the **factories**
(Sequences and Parallels) and **decision makers** (Selectors) of a behaviour
tree.

.. graphviz:: dot/composites.dot
   :align: center
   :caption: PyTree Composites

Composite behaviours typically manage children and apply some logic to the way
they execute and return a result, but generally don't do anything themselves.
Perform the checks or actions you need to do in the non-composite behaviours.

Most any desired functionality can be authored with a combination of these
three composites. In fact, it is precisely this feature that makes behaviour
trees attractive - it breaks down complex decision making logic to just three
primitive elements. It is possible and often desirable to extend this set with
custom composites of your own, but think carefully before you do - in almost
every case, a combination of the existing composites will serve and as a
result, you will merely compound the complexity inherent in your tree logic.
This this makes it confoundingly difficult to design, introspect and debug. As
an example, design sessions often revolve around a sketched graph on a
whiteboard. When these graphs are composed of just five elements (Selectors,
Sequences, Parallels, Decorators and Behaviours), it is very easy to understand
the logic at a glance. Double the number of fundamental elements and you may as
well be back at the terminal parsing code.

.. tip:: You should never need to subclass or create new composites.

The basic operational modes of the three composites in this library are as follows:

* :class:`~py_trees.composites.Selector`: select a child to execute based on cascading priorities
* :class:`~py_trees.composites.Sequence`: execute children sequentially
* :class:`~py_trees.composites.Parallel`: execute children concurrently

This library does provide some flexibility in *how* each composite is implemented without
breaking the fundamental nature of each (as described above). Selectors and Sequences can
be configured with or without memory (resumes or resets if children are RUNNING) and
the results of a parallel can be configured to wait upon all children completing, succeed
on one, all or a subset thereof.

.. tip:: Follow the links in each composite's documentation to the relevant demo programs.

"""

##############################################################################
# Imports
##############################################################################

import typing

from .. import behaviour
from .. import common

##############################################################################
# Composites
##############################################################################


class Composite(behaviour.Behaviour):
    """
    The parent class to all composite behaviours, i.e. those that
    have children.

    Args:
        name (:obj:`str`): the composite behaviour name
        children ([:class:`~py_trees.behaviour.Behaviour`]): list of children to add
    """
    def __init__(self,
                 name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED,
                 children: typing.List[behaviour.Behaviour]=None
                 ):
        super(Composite, self).__init__(name)
        if children is not None:
            for child in children:
                self.add_child(child)
        else:
            self.children = []
        self.current_child = None
        pass

    ############################################
    # Worker Overrides
    ############################################

    def stop(self, new_status=common.Status.INVALID):
        """
        There is generally two use cases that must be supported here.

        1) Whenever the composite has gone to a recognised state (i.e. :data:`~py_trees.common.Status.FAILURE` or SUCCESS),
        or 2) when a higher level parent calls on it to truly stop (INVALID).

        In only the latter case will children need to be forcibly stopped as well. In the first case, they will
        have stopped themselves appropriately already.

        Args:
            new_status (:class:`~py_trees.common.Status`): behaviour will transition to this new status
        """
        self.logger.debug("%s.stop()[%s]" % (self.__class__.__name__, "%s->%s" % (self.status, new_status) if self.status != new_status else "%s" % new_status))
        # priority interrupted
        if new_status == common.Status.INVALID:
            self.current_child = None
            for child in self.children:
                child.stop(new_status)
        # This part just replicates the Behaviour.stop function. We replicate it here so that
        # the Behaviour logging doesn't duplicate the composite logging here, just a bit cleaner this way.
        self.terminate(new_status)
        self.status = new_status
        self.iterator = self.tick()

    def tip(self):
        """
        Recursive function to extract the last running node of the tree.

        Returns:
            :class::`~py_trees.behaviour.Behaviour`: the tip function of the current child of this composite or None
        """
        if self.current_child is not None:
            return self.current_child.tip()
        else:
            return super().tip()

    ############################################
    # Children
    ############################################

    def add_child(self, child):
        """
        Adds a child.

        Args:
            child (:class:`~py_trees.behaviour.Behaviour`): child to add

        Raises:
            TypeError: if the child is not an instance of :class:`~py_trees.behaviour.Behaviour`
            RuntimeError: if the child already has a parent

        Returns:
            uuid.UUID: unique id of the child
        """
        if not isinstance(child, behaviour.Behaviour):
            raise TypeError("children must be behaviours, but you passed in {}".format(type(child)))
        self.children.append(child)
        if child.parent is not None:
            raise RuntimeError("behaviour '{}' already has parent '{}'".format(child.name, child.parent.name))
        child.parent = self
        return child.id

    def add_children(self, children):
        """
        Append a list of children to the current list.

        Args:
            children ([:class:`~py_trees.behaviour.Behaviour`]): list of children to add
        """
        for child in children:
            self.add_child(child)
        return self

    def remove_child(self, child):
        """
        Remove the child behaviour from this composite.

        Args:
            child (:class:`~py_trees.behaviour.Behaviour`): child to delete

        Returns:
            :obj:`int`: index of the child that was removed

        .. todo:: Error handling for when child is not in this list
        """
        if self.current_child is not None and (self.current_child.id == child.id):
            self.current_child = None
        if child.status == common.Status.RUNNING:
            child.stop(common.Status.INVALID)
        child_index = self.children.index(child)
        self.children.remove(child)
        child.parent = None
        return child_index

    def remove_all_children(self):
        """
        Remove all children. Makes sure to stop each child if necessary.
        """
        self.current_child = None
        for child in self.children:
            if child.status == common.Status.RUNNING:
                child.stop(common.Status.INVALID)
            child.parent = None
        # makes sure to delete it for this class and all references to it
        #   http://stackoverflow.com/questions/850795/clearing-python-lists
        del self.children[:]

    def replace_child(self, child, replacement):
        """
        Replace the child behaviour with another.

        Args:
            child (:class:`~py_trees.behaviour.Behaviour`): child to delete
            replacement (:class:`~py_trees.behaviour.Behaviour`): child to insert
        """
        self.logger.debug("%s.replace_child()[%s->%s]" % (self.__class__.__name__, child.name, replacement.name))
        child_index = self.children.index(child)
        self.remove_child(child)
        self.insert_child(replacement, child_index)
        child.parent = None

    def remove_child_by_id(self, child_id):
        """
        Remove the child with the specified id.

        Args:
            child_id (uuid.UUID): unique id of the child

        Raises:
            IndexError: if the child was not found
        """
        child = next((c for c in self.children if c.id == child_id), None)
        if child is not None:
            self.remove_child(child)
        else:
            raise IndexError('child was not found with the specified id [%s]' % child_id)

    def prepend_child(self, child):
        """
        Prepend the child before all other children.

        Args:
            child (:class:`~py_trees.behaviour.Behaviour`): child to insert

        Returns:
            uuid.UUID: unique id of the child
        """
        self.children.insert(0, child)
        child.parent = self
        return child.id

    def insert_child(self, child, index):
        """
        Insert child at the specified index. This simply directly calls
        the python list's :obj:`insert` method using the child and index arguments.

        Args:
            child (:class:`~py_trees.behaviour.Behaviour`): child to insert
            index (:obj:`int`): index to insert it at

        Returns:
            uuid.UUID: unique id of the child
        """
        self.children.insert(index, child)
        child.parent = self
        return child.id