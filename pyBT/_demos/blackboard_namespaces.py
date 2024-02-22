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
   :module: py_trees.demos.blackboard_namespaces
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard-namespaces

.. figure:: images/blackboard_namespaces.png
   :align: center

   Console Screenshot
"""

##############################################################################
# Imports
##############################################################################

import py_trees_rebuilt

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates usage of blackboard namespaces.\n"
    content += "\n"
    s = content
    return s

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
    blackboard = py_trees_rebuilt.bb.client.Client(name="Blackboard")
    blackboard.register_key(key="dude", access=py_trees_rebuilt.common.Access.WRITE)
    blackboard.register_key(key="/dudette", access=py_trees_rebuilt.common.Access.WRITE)
    blackboard.register_key(key="/foo/bar/wow", access=py_trees_rebuilt.common.Access.WRITE)
    print(blackboard)
    print("-------------------------------------------------------------------------------")
    print("$ blackboard.dude = 'Bob'")
    print("$ blackboard.dudette = 'Jade'")
    print("-------------------------------------------------------------------------------")
    blackboard.dude = "Bob"
    blackboard.dudette = "Jade"
    print(py_trees_rebuilt.display.unicode_blackboard())
    print("-------------------------------------------------------------------------------")
    print("$ blackboard.foo.bar.wow = 'foobar'")
    print("-------------------------------------------------------------------------------")
    blackboard.foo.bar.wow = "foobar"
    print(py_trees_rebuilt.display.unicode_blackboard())
    print("-------------------------------------------------------------------------------")
    print("$ py_trees.blackboard.Client(name='Foo', namespace='foo')")
    print("$ foo.register_key(key='awesome', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/brilliant', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/foo/clever', access=py_trees.common.Access.WRITE)")
    print("-------------------------------------------------------------------------------")
    foo = py_trees_rebuilt.bb.client.Client(name="Foo", namespace="foo")
    foo.register_key(key="awesome", access=py_trees_rebuilt.common.Access.WRITE)
    # TODO: should /brilliant be namespaced or go directly to root?
    foo.register_key(key="/brilliant", access=py_trees_rebuilt.common.Access.WRITE)
    # absolute names are ok, so long as they include the namespace
    foo.register_key(key="/foo/clever", access=py_trees_rebuilt.common.Access.WRITE)
    print(foo)
    print("-------------------------------------------------------------------------------")
    print("$ foo.awesome = True")
    print("$ foo.set('/brilliant', False)")
    print("$ foo.clever = True")
    print("-------------------------------------------------------------------------------")
    foo.awesome = True
    # Only accessable via set since it's not in the namespace
    foo.set("/brilliant", False)
    # This will fail since it looks for the namespaced /foo/brilliant key
    # foo.brilliant = False
    foo.clever = True
    print(py_trees_rebuilt.display.unicode_blackboard())
