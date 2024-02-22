from typing import List, Set # noqa

from . import decorator as dec
from .. import behaviour
from .. import common

class EternalGuard(dec.Decorator):
    """
    A decorator that continually guards the execution of a subtree.
    If at any time the guard's condition check fails, then the child
    behaviour/subtree is invalidated.

    .. note:: This decorator's behaviour is stronger than the
       :term:`guard` typical of a conditional check at the beginning of a
       sequence of tasks as it continues to check on every tick whilst the
       task (or sequence of tasks) runs.

    Args:
        child: the child behaviour or subtree
        condition: a functional check that determines execution or not of the subtree
        blackboard_keys: provide read access for the conditional function to these keys
        name: the decorator name

    Examples:

    Simple conditional function returning True/False:

    .. code-block:: python

        def check():
             return True

        foo = py_trees.behaviours.Foo()
        eternal_guard = py_trees.decorators.EternalGuard(
            name="Eternal Guard",
            condition=check,
            child=foo
        )

    Simple conditional function returning SUCCESS/FAILURE:

    .. code-block:: python

        def check():
             return py_trees.common.Status.SUCCESS

        foo = py_trees.behaviours.Foo()
        eternal_guard = py_trees.decorators.EternalGuard(
            name="Eternal Guard",
            condition=check,
            child=foo
        )

    Conditional function that makes checks against data on the blackboard (the
    blackboard client with pre-configured access is provided by the EternalGuard
    instance):

    .. code-block:: python

        def check(blackboard):
             return blackboard.velocity > 3.0

        foo = py_trees.behaviours.Foo()
        eternal_guard = py_trees.decorators.EternalGuard(
            name="Eternal Guard",
            condition=check,
            blackboard_keys={"velocity"},
            child=foo
        )

    .. seealso:: :meth:`py_trees.idioms.eternal_guard`
    """
    def __init__(
            self,
            *,
            child: behaviour.Behaviour,
            # Condition is one of 4 callable types illustrated in the docstring, partials complicate
            # it as well. When typing_extensions are available (very recent) more generally, can use
            # Protocols to handle it. Probably also a sign that it's not a very clean api though...
            condition,
            blackboard_keys: dec.Union[List[str], Set[str]]=[],
            name: dec.Union[str, common.Name]=common.Name.AUTO_GENERATED,
    ):
        super().__init__(name=name, child=child)
        self.blackboard = self.attach_blackboard_client(self.name)
        for key in blackboard_keys:
            self.blackboard.register_key(key=key, access=common.Access.READ)
        condition_signature = dec.inspect.signature(condition)
        if "blackboard" in [p.name for p in condition_signature.parameters.values()]:
            self.condition = dec.functools.partial(condition, self.blackboard)
        else:
            self.condition = condition

    def tick(self):
        """
        A decorator's tick is exactly the same as a normal proceedings for
        a Behaviour's tick except that it also ticks the decorated child node.

        Yields:
            :class:`~py_trees.behaviour.Behaviour`: a reference to itself or one of its children
        """
        self.logger.debug("%s.tick()" % self.__class__.__name__)

        # condition check
        result = self.condition()
        if type(result) == common.Status:
            result = False if result == common.Status.FAILURE else True
        elif type(result) != bool:
            error_message = "conditional check must return 'bool' or 'common.Status' [{}]".format(type(result))
            self.logger.error("The {}".format(error_message))
            raise RuntimeError(error_message)

        if not result:
            # abort, abort, the FSM is losing his noodles!!!
            self.stop(common.Status.FAILURE)
            yield self
        else:
            # normal behaviour
            for node in super().tick():
                yield node

    def update(self):
        """
        The update method is only ever triggered in the child's post-tick, which implies
        that the condition has already been checked and passed (refer to the :meth:`tick` method).
        """
        return self.decorated.status