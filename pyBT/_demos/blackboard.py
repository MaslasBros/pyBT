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
   :module: py_trees.demos.blackboard
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard

.. graphviz:: dot/demo-blackboard.dot
   :align: center
   :caption: Dot Graph

.. figure:: images/blackboard_demo.png
   :align: center

   Console Screenshot
"""

##############################################################################
# Imports
##############################################################################

import operator
import pybt

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates usage of the blackboard and related behaviours.\n"
    content += "\n"
    content += "A sequence is populated with a few behaviours that exercise\n"
    content += "reading and writing on the Blackboard in interesting ways.\n"
    s = content
    return s

class Nested(object):
    """
    A more complex object to interact with on the blackboard.
    """
    def __init__(self):
        self.foo = "bar"

    def __str__(self):
        return str({"foo": self.foo})


class BlackboardWriter(pybt.behaviour.Behaviour):
    """
    Custom writer that submits a more complicated variable to the blackboard.
    """
    def __init__(self, name="Writer"):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="dude", access=pybt.common.Access.READ)
        self.blackboard.register_key(key="spaghetti", access=pybt.common.Access.WRITE)

        self.logger.debug("%s.__init__()" % (self.__class__.__name__))

    def update(self):
        """
        Write a dictionary to the blackboard and return :data:`~py_trees.common.Status.SUCCESS`.
        """
        self.logger.debug("%s.update()" % (self.__class__.__name__))
        try:
            unused = self.blackboard.dude
        except KeyError:
            pass
        try:
            unused = self.blackboard.dudette
        except AttributeError:
            pass
        try:
            self.blackboard.dudette = "Jane"
        except AttributeError:
            pass
        self.blackboard.spaghetti = {"type": "Carbonara", "quantity": 1}
        self.blackboard.spaghetti = {"type": "Gnocchi", "quantity": 2}
        try:
            self.blackboard.set("spaghetti", {"type": "Bolognese", "quantity": 3}, overwrite=False)
        except AttributeError:
            pass
        return pybt.common.Status.SUCCESS


class ParamsAndState(pybt.behaviour.Behaviour):
    """
    A more esotoric use of multiple blackboards in a behaviour to represent
    storage of parameters and state.
    """
    def __init__(self, name="ParamsAndState"):
        super().__init__(name=name)
        # namespaces can include the separator or may leave it out
        # they can also be nested, e.g. /agent/state, /agent/parameters
        self.parameters = self.attach_blackboard_client("Params", "parameters")
        self.state = self.attach_blackboard_client("State", "state")
        self.parameters.register_key(
            key="default_speed",
            access=pybt.common.Access.READ
        )
        self.state.register_key(
            key="current_speed",
            access=pybt.common.Access.WRITE
        )

    def initialise(self):
        try:
            self.state.current_speed = self.parameters.default_speed
        except KeyError as e:
            raise RuntimeError("parameter 'default_speed' not found [{}]".format(str(e)))

    def update(self):
        if self.state.current_speed > 40.0:
            return pybt.common.Status.SUCCESS
        else:
            self.state.current_speed += 1.0
            return pybt.common.Status.RUNNING


def create_root():
    root = pybt.nodes.sequence.Sequence("Blackboard Demo")
    set_blackboard_variable = pybt.behaviours.setBlackboardVariable.SetBlackboardVariable(
        name="Set Nested", variable_name="nested", variable_value=Nested()
    )
    write_blackboard_variable = BlackboardWriter(name="Writer")
    check_blackboard_variable = pybt.behaviours.checkBlackboardVariableValue.CheckBlackboardVariableValue(
        name="Check Nested Foo",
        check=pybt.common.ComparisonExpression(
            variable="nested.foo",
            value="bar",
            operator=operator.eq
        )
    )
    params_and_state = ParamsAndState()
    root.add_children([
        set_blackboard_variable,
        write_blackboard_variable,
        check_blackboard_variable,
        params_and_state
    ])
    return root

##############################################################################
# Main
##############################################################################


def main():
    """
    Entry point for the demo script.
    """
    print(description())
    pybt.logging.level = pybt.logging.Level.DEBUG
    pybt.bb.blackboard.Blackboard.enable_activity_stream(maximum_size=100)
    blackboard = pybt.bb.client.Client(name="Configuration")
    blackboard.register_key(key="dude", access=pybt.common.Access.WRITE)
    blackboard.register_key(key="/parameters/default_speed", access=pybt.common.Access.WRITE)
    blackboard.dude = "Bob"
    blackboard.parameters.default_speed = 30.0

    root = create_root()

    ####################
    # Execute
    ####################
    root.setup_with_descendants()
    unset_blackboard = blackboard = pybt.bb.client.Client(name="Unsetter")
    unset_blackboard.register_key(key="foo", access=pybt.common.Access.WRITE)
    print("\n--------- Tick 0 ---------\n")
    root.tick_once()
    print("\n")
    print(pybt.display.unicode_tree(root))
    print("--------------------------\n")
    print(pybt.display.unicode_blackboard())
    print("--------------------------\n")
    print(pybt.display.unicode_blackboard(display_only_key_metadata=True))
    print("--------------------------\n")
    unset_blackboard.unset("foo")
    print(pybt.display.unicode_blackboard())
