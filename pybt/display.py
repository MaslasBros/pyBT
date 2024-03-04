#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Behaviour trees are significantly easier to design, monitor and debug
with visualisations. Py Trees does provide minimal assistance to render
trees to various simple output formats. Currently this includes dot graphs,
strings or stdout.
"""

##############################################################################
# Imports
##############################################################################

import typing
import uuid

from . import behaviour
from . import common
from . import utilities

#Blackboard imports
from .bb.blackboard import Blackboard
from .bb._internal.activityItem import ActivityItem
from .bb._internal.activityType import ActivityType

#Composites imports
from .nodes.selector import Selector
from .nodes.sequence import Sequence
from .nodes.parallel import Parallel

#Decorator imports
from .nodes.decorator import Decorator

##############################################################################
# Symbols
##############################################################################

Symbols = typing.Dict[typing.Any, str]

unicode_symbols = {
    'space': ' ',
    'left_arrow': '->',
    'right_arrow': '<-',
    'left_right_arrow': '<->',
    'sequence_with_memory': u'{-}',
    'selector_with_memory': u'{o}',
    'bold': '',
    Sequence: u'[-]',
    Selector: u'[o]',
    Parallel: u'/_/',
    Decorator: u'-^-',
    behaviour.Behaviour: u'-->',
    common.Status.SUCCESS: 'Status.SUCCESS',
    common.Status.FAILURE: 'Status.FAILURE',
    common.Status.INVALID: 'Status.INVALID',
    common.Status.RUNNING: 'Status.RUNNING'
}
"""Symbols for a unicode, escape sequence capable console."""

##############################################################################
# Trees
##############################################################################

def _generate_text_tree(
        root,
        show_only_visited=False,
        show_status=False,
        visited={},
        previously_visited={},
        indent=0,
        symbols=None):
    """
    Generate a text tree utilising the specified symbol formatter.

    Args:
        root (:class:`~py_trees.behaviour.Behaviour`): the root of the tree, or subtree you want to show
        show_only_visited (:obj:`bool`): show only visited behaviours
        show_status (:obj:`bool`): always show status and feedback message (i.e. for every element,
            not just those visited)
        visited (dict): dictionary of (uuid.UUID) and status (:class:`~py_trees.common.Status`) pairs
            for behaviours visited on the current tick
        previously_visited (dict): dictionary of behaviour id/status pairs from the previous tree tick
        indent (:obj:`int`): the number of characters to indent the tree
        symbols (dict, optional): dictates formatting style
            (one of :data:`py_trees.display.unicode_symbols` || :data:`py_trees.display.ascii_symbols` || :data:`py_trees.display.xhtml_symbols`),
            defaults to unicode if stdout supports it, ascii otherwise

    Returns:
        :obj:`str`: a text-based representation of the behaviour tree

    .. seealso:: :meth:`py_trees.display.ascii_tree`, :meth:`py_trees.display.unicode_tree`, :meth:`py_trees.display.xhtml_tree`
    """
    # default to unicode if stdout supports it, ascii otherwise
    if symbols is None:
        symbols = unicode_symbols
    tip_id = root.tip().id if root.tip() else None

    def get_behaviour_type(b):
        if isinstance(b, Parallel):
            return Parallel
        if isinstance(b, Decorator):
            return Decorator
        if isinstance(b, Sequence):
            return "sequence_with_memory" if b.memory else Sequence
        if isinstance(b, Selector):
            return "selector_with_memory" if b.memory else Selector
        return behaviour.Behaviour

    def style(s, font_weight=False):
        """
        Because the way the shell escape sequences reset everything, this needs to get used on any
        single block of formatted text.
        """
        return s

    def generate_lines(root, internal_indent):

        def assemble_single_line(b):
            font_weight = True if b.id == tip_id else False
            s = ""
            s += symbols['space'] * 4 * internal_indent
            s += style(symbols[get_behaviour_type(b)], font_weight)
            s += " "

            if show_status or b.id in visited.keys():
                s += style("{} [".format(b.name.replace('\n', ' ')), font_weight)
                s += style("{}".format(symbols[b.status]), font_weight)
                message = "" if not b.feedback_message else " -- " + b.feedback_message
                s += style("]" + message, font_weight)
            elif (b.id in previously_visited.keys() and
                  b.id not in visited.keys() and
                  previously_visited[b.id] == common.Status.RUNNING):
                s += style("{} [".format(b.name.replace('\n', ' ')), font_weight)
                s += style("{}".format(symbols[b.status]), font_weight)
                s += style("]", font_weight)
            else:
                s += style("{}".format(b.name.replace('\n', ' ')), font_weight)
            return s

        if internal_indent == indent:
            # Root
            yield assemble_single_line(root)
            internal_indent += 1
        for child in root.children:
            yield assemble_single_line(child)
            if child.children != []:
                if not show_only_visited or child.id in visited.keys():
                    for line in generate_lines(child, internal_indent + 1):
                        yield line
                else:
                    yield "{}...".format(symbols['space'] * 4 * (internal_indent + 1))
    s = ""
    for line in generate_lines(root, indent):
        if line:
            s += "%s\n" % line
    return s

def unicode_tree(
        root,
        show_only_visited=False,
        show_status=False,
        visited={},
        previously_visited={},
        indent=0):
    """
    Graffiti your console with unicode art for your trees.

    Args:
        root (:class:`~py_trees.behaviour.Behaviour`): the root of the tree, or subtree you want to show
        show_only_visited (:obj:`bool`) : show only visited behaviours
        show_status (:obj:`bool`): always show status and feedback message (i.e. for every element, not just those visited)
        visited (dict): dictionary of (uuid.UUID) and status (:class:`~py_trees.common.Status`) pairs for behaviours visited on the current tick
        previously_visited (dict): dictionary of behaviour id/status pairs from the previous tree tick
        indent (:obj:`int`): the number of characters to indent the tree

    Returns:
        :obj:`str`: a unicode tree (i.e. in string form)

    .. seealso:: :meth:`py_trees.display.ascii_tree`, :meth:`py_trees.display.xhtml_tree`

    """
    lines = _generate_text_tree(
        root,
        show_only_visited,
        show_status,
        visited,
        previously_visited,
        indent,
        symbols=unicode_symbols
    )
    return lines

##############################################################################
# Blackboards
##############################################################################

def _generate_text_blackboard(
        key_filter: typing.Union[typing.Set[str], typing.List[str]]=None,
        regex_filter: str=None,
        client_filter: typing.Union[typing.Set[uuid.UUID], typing.List[uuid.UUID]]=None,
        keys_to_highlight: typing.List[str]=[],
        display_only_key_metadata: bool=False,
        indent: int=0,
        symbols: typing.Optional[Symbols]=None) -> str:
    """
    Generate a text blackboard.

    Args:
        key_filter: filter on a set/list of blackboard keys
        regex_filter: filter on a python regex str
        client_filter: filter on a set/list of client uuids
        keys_to_highlight: list of keys to highlight
        display_only_key_metadata: (read/write access, ...) instead of values
        indent: the number of characters to indent the blackboard
        symbols: dictates formatting style
            (one of :data:`py_trees.display.unicode_symbols` || :data:`py_trees.display.ascii_symbols` || :data:`py_trees.display.xhtml_symbols`),
            defaults to unicode if stdout supports it, ascii otherwise

    Returns:
        a text-based representation of the behaviour tree

    .. seealso:: :meth:`py_trees.display.unicode_blackboard`
    """
    if symbols is None:
        symbols = unicode_symbols

    def style(s, font_weight=False):
        if font_weight:
            return symbols['bold'] + s + symbols['bold_reset']
        else:
            return s

    def generate_lines(storage, metadata, indent):
        def assemble_value_line(key, value, apply_highlight, indent, key_width):
            s = ""
            lines = ('{0}'.format(value)).split('\n')
            if len(lines) > 1:
                s += indent + '{0: <{1}}'.format(key, key_width) + ":\n"
                for line in lines:
                    s += indent + "  {0}\n".format(line)
            else:
                s += indent + '{0: <{1}}'.format(key, key_width) + ": " + '{0}\n'.format(value)
            return style(s, apply_highlight)

        def assemble_metadata_line(key, metadata, apply_highlight, indent, key_width):
            s = ""
            s += indent + '{0: <{1}}'.format(key, key_width + 1) + ": "
            client_uuids = list(set(metadata.read) | set(metadata.write) | set(metadata.exclusive))
            prefix = ''
            metastrings = []
            for client_uuid in client_uuids:
                metastring = prefix + '{0}'.format(
                    utilities.truncate(
                        Blackboard.clients[client_uuid], 11
                    )
                )
                metastring += ' ('
                if client_uuid in metadata.read:
                    metastring += 'r'
                if client_uuid in metadata.write:
                    metastring += 'w'
                if client_uuid in metadata.exclusive:
                    metastring += 'x'
                metastring += ')'
                metastrings.append(metastring)
            s += "{}\n".format(', '.join(metastrings))
            return style(s, apply_highlight)

        text_indent = symbols['space'] * (4 + indent)
        key_width = 0
        for key in storage.keys():
            key_width = len(key) if len(key) > key_width else key_width
        for key in sorted(storage.keys()):
            if metadata is not None:
                yield assemble_metadata_line(
                    key=key,
                    metadata=metadata[key],
                    apply_highlight=key in keys_to_highlight,
                    indent=text_indent,
                    key_width=key_width)
            else:
                yield assemble_value_line(
                    key=key,
                    value=storage[key],
                    apply_highlight=key in keys_to_highlight,
                    indent=text_indent,
                    key_width=key_width)

    blackboard_metadata = Blackboard.metadata if display_only_key_metadata else None

    if key_filter:
        if isinstance(key_filter, list):
            key_filter = set(key_filter)
        all_keys = Blackboard.keys() & key_filter
    elif regex_filter:
        all_keys = Blackboard.keys_filtered_by_regex(regex_filter)
    elif client_filter:
        all_keys = Blackboard.keys_filtered_by_clients(client_filter)
    else:
        all_keys = Blackboard.keys()
    blackboard_storage = {}
    for key in all_keys:
        try:
            blackboard_storage[key] = Blackboard.storage[key]
        except KeyError:
            blackboard_storage[key] = "-"

    title = "Clients" if display_only_key_metadata else "Data"
    s = symbols['space'] * indent + "Blackboard {}\n".format(title)
    if key_filter:
        s += symbols['space'] * (indent + 2) + "Filter: '{}'\n".format(key_filter)
    elif regex_filter:
        s += symbols['space'] * (indent + 2) + "Filter: '{}'\n".format(regex_filter)
    elif client_filter:
        s += symbols['space'] * (indent + 2) + "Filter: {}\n".format(str(client_filter))
    for line in generate_lines(blackboard_storage, blackboard_metadata, indent):
        s += "{}".format(line)
    return s

def unicode_blackboard(
        key_filter: typing.Union[typing.Set[str], typing.List[str]]=None,
        regex_filter: str=None,
        client_filter: typing.Optional[typing.Union[typing.Set[uuid.UUID], typing.List[uuid.UUID]]]=None,
        keys_to_highlight: typing.List[str]=[],
        display_only_key_metadata: bool=False,
        indent: int=0) -> str:
    """
    Graffiti your console with unicode art for your blackboard.

    Args:
        key_filter: filter on a set/list of blackboard keys
        regex_filter: filter on a python regex str
        client_filter: filter on a set/list of client uuids
        keys_to_highlight: list of keys to highlight
        display_only_key_metadata: read/write access, ... instead of values
        indent: the number of characters to indent the blackboard

    Returns:
        a unicoded blackboard (i.e. in string form)

    .. seealso:: :meth:`py_trees.display.ascii_blackboard`

    .. note:: registered variables that have not yet been set are marked with a '-'
    """
    lines = _generate_text_blackboard(
        key_filter=key_filter,
        regex_filter=regex_filter,
        client_filter=client_filter,
        keys_to_highlight=keys_to_highlight,
        display_only_key_metadata=display_only_key_metadata,
        indent=indent,
        symbols=None  # defaults to unicode, falls back to ascii
    )
    return lines


def _generate_text_activity(
    activity_stream: typing.Optional[typing.List[ActivityItem]]=None,
    show_title: bool=True,
    indent: int=0,
    symbols: typing.Optional[Symbols]=None
) -> str:
    """
    Generator for the various formatted outputs (ascii, unicode, xhtml).

    Args:
        activity_stream: the log of activity, if None, get the entire activity stream
        indent: the number of characters to indent the blackboard
        show_title: include the title in the output
    """
    if symbols is None:
        symbols = unicode_symbols
    space = symbols['space']
    if activity_stream is None and Blackboard.activity_stream is not None:
        activity_stream = Blackboard.activity_stream.data
    s = ""
    if show_title:
        s += space * indent + "Blackboard Activity Stream" + "\n"
    if activity_stream is not None:
        key_width = 0
        client_width = 0
        for item in activity_stream:
            key_width = len(item.key) if len(item.key) > key_width else key_width
            client_width = len(item.client_name) if len(item.client_name) > client_width else client_width
        client_width = min(client_width, 20)
        type_width = len("ACCESS_DENIED")
        value_width = 80 - key_width - 3 - type_width - 3 - client_width - 3
        for item in activity_stream:
            s += space * (4 + indent)
            s += "{0: <{1}}:".format(item.key, key_width + 1) + space
            s += "{0: <{1}}".format(item.activity_type, type_width) + space
            s += "|" + space
            s += "{0: <{1}}".format(
                utilities.truncate(
                    item.client_name.replace('\n', '_'),
                    client_width),
                client_width) + space
            s += "|" + space
            if item.activity_type == ActivityType.READ.value:
                s += symbols["left_arrow"] + space + "{}\n".format(
                    utilities.truncate(str(item.current_value), value_width)
                )
            elif item.activity_type == ActivityType.WRITE.value:
                s += symbols["right_arrow"] + space
                s += "{}\n".format(
                    utilities.truncate(str(item.current_value), value_width)
                )
            elif item.activity_type == ActivityType.ACCESSED.value:
                s += symbols["left_right_arrow"] + space
                s += "{}\n".format(
                    utilities.truncate(str(item.current_value), value_width)
                )
            elif item.activity_type == ActivityType.ACCESS_DENIED.value:
                s += u'\u2715' + space
                s += "client has no read/write access\n"
            elif item.activity_type == ActivityType.NO_KEY.value:
                s += space
                s += "key does not yet exist\n"
            elif item.activity_type == ActivityType.NO_OVERWRITE.value:
                s += space
                s += "{}\n".format(
                    utilities.truncate(str(item.current_value), value_width)
                )
            elif item.activity_type == ActivityType.UNSET.value:
                s += "\n"
            elif item.activity_type == ActivityType.INITIALISED.value:
                s += symbols["right_arrow"] + space
                s += "{}\n".format(
                    utilities.truncate(str(item.current_value), value_width)
                )
            else:
                s += "unknown operation\n"
        s = s.rstrip("\n")
    return s


def unicode_blackboard_activity_stream(
    activity_stream: typing.List[ActivityItem]=None,
    indent: int=0,
    show_title: bool=True
):
    """
    Pretty print the blackboard stream to console.

    Args:
        activity_stream: the log of activity, if None, get the entire activity stream
        indent: the number of characters to indent the blackboard
        show_title: include the title in the output
    """
    return _generate_text_activity(
        activity_stream=activity_stream,
        show_title=show_title,
        indent=indent,
        symbols=unicode_symbols
    )