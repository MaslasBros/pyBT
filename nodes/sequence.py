import itertools
import typing

from . import composite as co
from .. import behaviour
from .. import common

class Sequence(co.Composite):
    """
    Sequences are the factory lines of Behaviour Trees

    .. graphviz:: dot/sequence.dot

    A sequence will progressively tick over each of its children so long as
    each child returns :data:`~py_trees.common.Status.SUCCESS`. If any child returns
    :data:`~py_trees.common.Status.FAILURE` or :data:`~py_trees.common.Status.RUNNING` the sequence will halt and the parent will adopt
    the result of this child. If it reaches the last child, it returns with
    that result regardless.

    .. note::

       The sequence halts once it sees a child is RUNNING and then returns
       the result. *It does not get stuck in the running behaviour*.

    .. seealso:: The :ref:`py-trees-demo-sequence-program` program demos a simple sequence in action.

    Args:
        name: the composite behaviour name
        memory: if :data:`~py_trees.common.Status.RUNNING` on the previous tick, resume with the :data:`~py_trees.common.Status.RUNNING` child
        children: list of children to add

    """
    def __init__(
        self,
        name: str="Sequence",
        memory: bool=True,
        children: typing.List[behaviour.Behaviour]=None
    ):
        super(Sequence, self).__init__(name, children)
        self.memory = memory

    def tick(self):
        """
        Tick over the children.

        Yields:
            :class:`~py_trees.behaviour.Behaviour`: a reference to itself or one of its children
        """
        self.logger.debug("%s.tick()" % self.__class__.__name__)

        # initialise
        index = 0
        if self.status != common.Status.RUNNING or not self.memory:
            self.current_child = self.children[0] if self.children else None
            for child in self.children:
                if child.status != common.Status.INVALID:
                    child.stop(common.Status.INVALID)
            # user specific initialisation
            self.initialise()
        else:  # self.memory is True and status is RUNNING
            index = self.children.index(self.current_child)

        # customised work
        self.update()

        # nothing to do
        if not self.children:
            self.current_child = None
            self.stop(common.Status.SUCCESS)
            yield self
            return

        # actual work
        for child in itertools.islice(self.children, index, None):
            for node in child.tick():
                yield node
                if node is child and node.status != common.Status.SUCCESS:
                    self.status = node.status
                    yield self
                    return
            try:
                # advance if there is 'next' sibling
                self.current_child = self.children[index + 1]
                index += 1
            except IndexError:
                pass

        self.stop(common.Status.SUCCESS)
        yield self