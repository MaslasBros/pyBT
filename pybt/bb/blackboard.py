#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Blackboards are not a necessary component of behaviour tree implementations,
but are nonetheless, a fairly common mechanism for sharing data between
behaviours in the tree. See, for example, the `design notes`_
for blackboards in Unreal Engine.

.. image:: images/blackboard.jpg
   :width: 300px
   :align: center

Implementations vary widely depending on the needs of
the framework using them. The simplest implementations take the
form of a key-value store with global access, while more
rigorous implementations scope access or form a secondary
graph overlaying the tree connecting data ports between behaviours.

The *'Zen of PyTrees'* is to enable rapid development, yet be rich
enough so that *all* of the magic is exposed for debugging purposes.
The first implementation of a blackboard was merely a global key-value
store with an api that lent itself to ease of use, but did not
expose the data sharing between behaviours which meant any tooling
used to introspect or visualise the tree, only told half the story.

The current implementation adopts a strategy similar to that of a
filesystem. Each client (subsequently behaviour) registers itself
for read/write access to keys on the blackboard. This is less to
do with permissions and more to do with tracking users of keys
on the blackboard - extremely helpful with debugging.

The alternative approach of layering a secondary data graph
with parameter and input-output ports on each behaviour was
discarded as being too heavy for the zen requirements of py_trees.
This is in part due to the wiring costs, but also due to
complexity arising from a tree's partial graph execution
(a feature which makes trees different from most computational
graph frameworks) and not to regress on py_trees' capability to
dynamically insert and prune subtrees on the fly.

A high-level list of existing / planned features:

* [+] Centralised key-value store
* [+] Client connections with namespaced read/write access to the store
* [+] Integration with behaviours for key-behaviour associations (debugging)
* [+] Activity stream that logs read/write operations by clients
* [+] Exclusive locks for writing
* [+] Framework for key remappings

.. include:: weblinks.rst
"""

##############################################################################
# Imports
##############################################################################

import operator
import re
import typing
import uuid

from ._internal.activityStream import ActivityStream
from ._internal.keyMetaData import KeyMetaData

##############################################################################
# Classes
##############################################################################
class Blackboard(object):
    """
    Centralised key-value store for sharing data between behaviours.
    This class is a coat-hanger for the centralised data store, metadata
    for it's administration and static methods for interacting with it.

    This api is intended for authors of debugging and introspection
    tools on the blackboard. Users should make use of the :class:`Client`.

    Attributes:
        Blackboard.clients (typing.Dict[uuid.UUID, str]): client uuid-name registry
        Blackboard.storage (typing.Dict[str, typing.Any]): key-value data store
        Blackboard.metadata (typing.Dict[str, KeyMetaData]): key associated metadata
        Blackboard.activity_stream (ActivityStream): logged activity
        Blackboard.separator (char): namespace separator character
    """
    storage = {}  # key-value storage
    metadata = {}  # key-metadata information
    clients = {}   # client id-name pairs
    activity_stream = None
    separator = "/"

    @staticmethod
    def keys() -> typing.Set[str]:
        """
        Get the set of blackboard keys.

        Returns:
            the complete set of keys registered by clients
        """
        # return registered keys, those on the blackboard are not
        # necessarily written to yet
        return set(Blackboard.metadata.keys())

    @staticmethod
    def get(variable_name: str) -> typing.Any:
        """
        Extract the value associated with the given a variable name,
        can be nested, e.g. battery.percentage. This differs from the
        client get method in that it doesn't pass through the client access
        checks. To be used for utility tooling (e.g. display methods) and not by
        users directly.

        Args:
            variable_name: of the variable to get, can be nested, e.g. battery.percentage

        Raises:
            KeyError: if the variable or it's nested attributes do not yet exist on the blackboard

        Return:
            The stored value for the given variable
        """
        variable_name = Blackboard.absolute_name(Blackboard.separator, variable_name)
        name_components = variable_name.split('.')
        key = name_components[0]
        key_attributes = '.'.join(name_components[1:])
        # can raise KeyError
        value = Blackboard.storage[key]
        if key_attributes:
            try:
                value = operator.attrgetter(key_attributes)(value)
            except AttributeError:
                raise KeyError("Key exists, but does not have the specified nested attributes [{}]".format(variable_name))
        return value

    @staticmethod
    def set(variable_name: str, value: typing.Any):
        """
        Set the value associated with the given a variable name,
        can be nested, e.g. battery.percentage. This differs from the
        client get method in that it doesn't pass through the client access
        checks. To be used for utility tooling (e.g. display methods) and not by
        users directly.

        Args:
            variable_name: of the variable to set, can be nested, e.g. battery.percentage

        Raises:
            AttributeError: if it is attempting to set a nested attribute tha does not exist.
        """
        variable_name = Blackboard.absolute_name(Blackboard.separator, variable_name)
        name_components = variable_name.split('.')
        key = name_components[0]
        key_attributes = '.'.join(name_components[1:])
        if not key_attributes:
            Blackboard.storage[key] = value
        else:
            setattr(Blackboard.storage[key], key_attributes, value)
        Blackboard.metadata.setdefault(key, KeyMetaData())

    @staticmethod
    def unset(key: str):
        """
        For when you need to completely remove a blackboard variable (key-value pair),
        this provides a convenient helper method.

        Args:
            key: name of the variable to remove

        Returns:
            True if the variable was removed, False if it was already absent
        """
        try:
            key = Blackboard.absolute_name(Blackboard.separator, key)
            del Blackboard.storage[key]
            return True
        except KeyError:
            return False

    @staticmethod
    def exists(name: str) -> bool:
        """
        Check if the specified variable exists on the blackboard.

        Args:
            name: name of the variable, can be nested, e.g. battery.percentage

        Raises:
            AttributeError: if the client does not have read access to the variable
        """
        try:
            name = Blackboard.absolute_name(Blackboard.separator, name)
            unused_value = Blackboard.get(name)
            return True
        except KeyError:
            return False

    @staticmethod
    def keys_filtered_by_regex(regex: str) -> typing.Set[str]:
        """
        Get the set of blackboard keys filtered by regex.

        Args:
            regex: a python regex string

        Returns:
            subset of keys that have been registered and match the pattern
        """
        pattern = re.compile(regex)
        return {key for key in Blackboard.metadata.keys() if pattern.search(key) is not None}

    @staticmethod
    def keys_filtered_by_clients(
        client_ids: typing.Union[typing.Set[uuid.UUID], typing.List[uuid.UUID]]
    ) -> typing.Set[str]:
        """
        Get the set of blackboard keys filtered by client unique identifiers.

        Args:
            client_ids: set of client uuid's.

        Returns:
            subset of keys that have been registered by the specified clients
        """
        # forgive users if they sent a list instead of a set
        if isinstance(client_ids, list):
            client_ids = set(client_ids)
        keys = set()
        for key in Blackboard.metadata.keys():
            # for sets, | is union, & is intersection
            key_clients = (
                set(Blackboard.metadata[key].read) |
                set(Blackboard.metadata[key].write) |
                set(Blackboard.metadata[key].exclusive)
            )
            if key_clients & client_ids:
                keys.add(key)
        return keys

    @staticmethod
    def enable_activity_stream(maximum_size: int=500):
        """
        Enable logging of activities on the blackboard.

        Args:
            maximum_size: pop items from the stream if this size is exceeded

        Raises:
            RuntimeError if the activity stream is already enabled
        """
        if Blackboard.activity_stream is None:
            Blackboard.activity_stream = ActivityStream(maximum_size)
        else:
            RuntimeError("activity stream is already enabled for this blackboard")

    @staticmethod
    def disable_activity_stream():
        """
        Disable logging of activities on the blackboard
        """
        Blackboard.activity_stream = None

    @staticmethod
    def clear():
        """
        Completely clear all key, value and client information from the blackboard.
        Also deletes the activity stream.
        """
        Blackboard.storage.clear()
        Blackboard.metadata.clear()
        Blackboard.clients.clear()
        Blackboard.activity_stream = None

    @staticmethod
    def absolute_name(namespace: str, key: str) -> str:
        """
        Generate the fully qualified key name from namespace and name arguments.

        **Examples**

        .. code-block:: python

            '/' + 'foo'  = '/foo'
            '/' + '/foo' = '/foo'
            '/foo' + 'bar' = '/foo/bar'
            '/foo/' + 'bar' = '/foo/bar'
            '/foo' + '/foo/bar' = '/foo/bar'
            '/foo' + '/bar' = '/bar'
            '/foo' + 'foo/bar' = '/foo/foo/bar'

        Args:
            namespace: namespace the key should be embedded in
            key: key name (relative or absolute)

        Returns:
            the absolute name

        .. warning::

            To expedite the method call (it's used with high frequency
            in blackboard key lookups), no checks are made to ensure
            the namespace argument leads with a "/". Nor does it check
            that a name in absolute form is actually embedded in the
            specified namespace, it just returns the given (absolute)
            name directly.
        """
        # it's already absolute
        if key.startswith(Blackboard.separator):
            return key
        # remove leading and trailing separators
        namespace = namespace if namespace.endswith(Blackboard.separator) else namespace + Blackboard.separator
        key = key.strip(Blackboard.separator)
        return "{}{}".format(namespace, key)

    @staticmethod
    def relative_name(namespace: str, key: str) -> str:
        """
        **Examples**

        .. code-block:: python

            '/' + 'foo'  = '/foo'
            '/' + '/foo' = '/foo'
            '/foo' + 'bar' = '/foo/bar'
            '/foo/' + 'bar' = '/foo/bar'
            '/foo' + '/bar' => KeyError('/bar' is not in 'foo')
            '/foo' + 'foo/bar' = '/foo/foo/bar'

        Args:
            namespace: namespace the key should be embedded in
            key: key name (relative or absolute)

        Returns:
            the absolute name

        Raises:
            KeyError if the key is not in the specified namespace

        .. warning::

            To expedite the method call (it's used with high frequency
            in blackboard key lookups), no checks are made to ensure
            the namespace argument leads with a "/"
        """
        # it's already relative
        if not key.startswith(Blackboard.separator):
            return key
        # remove leading and trailing separators
        namespace = namespace if namespace.endswith(Blackboard.separator) else namespace + Blackboard.separator
        if key.startswith(namespace):
            return key.lstrip(namespace)
        else:
            raise KeyError("key '{}' is not in namespace '{}'".format(
                key, namespace)
            )

    @staticmethod
    def key(variable_name: str) -> str:
        """
        Extract the key for an arbitrary blackboard variable, keeping in mind that blackboard variable
        names can be pointing to a nested attribute within a key.

        Example: '/foo/bar.woohoo -> /foo/bar'.

        Args:
            variable_name: blackboard variable name - can be nested, e.g. battery.percentage

        Returns:
            name of the underlying key
        """
        name_components = variable_name.split('.')
        key = name_components[0]
        return key

    @staticmethod
    def key_with_attributes(variable_name: str) -> typing.Tuple[str, str]:
        """
        Extract the key for an arbitrary blackboard variable, keeping in mind that blackboard variable
        names can be pointing to a nested attribute within a key,

        Example: '/foo/bar.woohoo -> (/foo/bar'. 'woohoo')

        Args:
            variable_name: blackboard variable name - can be nested, e.g. battery.percentage

        Returns:
            a tuple consisting of the key and it's attributes (in string form)
        """
        name_components = variable_name.split('.')
        key = name_components[0]
        key_attributes = '.'.join(name_components[1:])
        return (key, key_attributes)