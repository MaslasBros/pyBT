import itertools

from . import composite as co
from .. import common

class Selector(co.Composite):
    """
    Selectors are the decision makers.

    .. graphviz:: dot/selector.dot

    A selector executes each of its child behaviours in turn until one of them
    succeeds (at which point it itself returns :data:`~py_trees.common.Status.RUNNING` or :data:`~py_trees.common.Status.SUCCESS`,
    or it runs out of children at which point it itself returns :data:`~py_trees.common.Status.FAILURE`.
    We usually refer to selecting children as a means of *choosing between priorities*.
    Each child and its subtree represent a decreasingly lower priority path.

    .. note::

       Switching from a low -> high priority branch causes a `stop(INVALID)` signal to be sent to the previously
       executing low priority branch. This signal will percolate down that child's own subtree. Behaviours
       should make sure that they catch this and *destruct* appropriately.

    .. seealso:: The :ref:`py-trees-demo-selector-program` program demos higher priority switching under a selector.

    Args:
        name (:obj:`str`): the composite behaviour name
        memory (:obj:`bool`): if :data:`~py_trees.common.Status.RUNNING` on the previous tick, resume with the :data:`~py_trees.common.Status.RUNNING` child
        children ([:class:`~py_trees.behaviour.Behaviour`]): list of children to add
    """

    def __init__(self, name = "Selector", memory = False, children = None):
        super(Selector, self).__init__(name, children)
        self.memory = memory

    def tick(self):
        """
        Run the tick behaviour for this selector. Note that the status
        of the tick is always determined by its children, not
        by the user customised update function.

        Yields:
            :class:`~py_trees.behaviour.Behaviour`: a reference to itself or one of its children
        """
        self.logger.debug("%s.tick()" % self.__class__.__name__)
        # initialise
        if self.status != common.Status.RUNNING:
            # selector specific initialisation - leave initialise() free for users to
            # re-implement without having to make calls to super()
            self.logger.debug("%s.tick() [!RUNNING->reset current_child]" % self.__class__.__name__)
            self.current_child = self.children[0] if self.children else None

            # reset the children - don't need to worry since they will be handled
            # a) prior to a remembered starting point, or
            # b) invalidated by a higher level priority

            # user specific initialisation
            self.initialise()

        # customised work
        self.update()

        # nothing to do
        if not self.children:
            self.current_child = None
            self.stop(common.Status.FAILURE)
            yield self
            return

        # starting point
        if self.memory:
            index = self.children.index(self.current_child)
            # clear out preceding status' - not actually necessary but helps
            # visualise the case of memory vs no memory
            for child in itertools.islice(self.children, None, index):
                child.stop(common.Status.INVALID)
        else:
            index = 0

        # actual work
        previous = self.current_child
        for child in itertools.islice(self.children, index, None):
            for node in child.tick():
                yield node
                if node is child:
                    if node.status == common.Status.RUNNING or node.status == common.Status.SUCCESS:
                        self.current_child = child
                        self.status = node.status
                        if previous is None or previous != self.current_child:
                            # we interrupted, invalidate everything at a lower priority
                            passed = False
                            for child in self.children:
                                if passed:
                                    if child.status != common.Status.INVALID:
                                        child.stop(common.Status.INVALID)
                                passed = True if child == self.current_child else passed
                        yield self
                        return
        # all children failed, set failure ourselves and current child to the last bugger who failed us
        self.status = common.Status.FAILURE
        try:
            self.current_child = self.children[-1]
        except IndexError:
            self.current_child = None
        yield self

    def stop(self, new_status=common.Status.INVALID):
        """
        Stopping a selector requires setting the current child to none. Note that it
        is important to implement this here instead of terminate, so users are free
        to subclass this easily with their own terminate and not have to remember
        that they need to call this function manually.

        Args:
            new_status (:class:`~py_trees.common.Status`): the composite is transitioning to this new status
        """
        # retain information about the last running child if the new status is
        # SUCCESS or FAILURE
        if new_status == common.Status.INVALID:
            self.current_child = None
        co.Composite.stop(self, new_status)