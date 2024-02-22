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
   :module: py_trees.demos.blackboard_remappings
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard-remappings

.. figure:: images/blackboard_remappings.png
   :align: center

   Console Screenshot
"""

##############################################################################
# Imports
##############################################################################

import argparse
import py_trees_rebuilt
import typing

import py_trees_rebuilt.console as console

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates usage of blackbord remappings.\n"
    content += "\n"
    content += "Demonstration is via an exemplar behaviour making use of remappings..\n"
    s = content
    return s

class Remap(py_trees_rebuilt.behaviour.Behaviour):
    """
    Custom writer that submits a more complicated variable to the blackboard.
    """
    def __init__(self, name: str, remap_to: typing.Dict[str, str]):
        super().__init__(name=name)
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(
            key="/foo/bar/wow",
            access=py_trees_rebuilt.common.Access.WRITE,
            remap_to=remap_to["/foo/bar/wow"]
        )

    def update(self):
        """
        Write a dictionary to the blackboard and return :data:`~py_trees.common.Status.SUCCESS`.
        """
        self.logger.debug("%s.update()" % (self.__class__.__name__))
        self.blackboard.foo.bar.wow = "colander"

        return py_trees_rebuilt.common.Status.SUCCESS

##############################################################################
# Main
##############################################################################


def main():
    """
    Entry point for the demo script.
    """
    print(description())
    py_trees_rebuilt.logging.level = py_trees_rebuilt.logging.Level.DEBUG
    py_trees_rebuilt.bb.blackboard.Blackboard.enable_activity_stream(maximum_size=100)
    root = Remap(name="Remap", remap_to={"/foo/bar/wow": "/parameters/wow"})

    ####################
    # Execute
    ####################
    root.tick_once()
    print(root.blackboard)
    print(py_trees_rebuilt.display.unicode_blackboard())
