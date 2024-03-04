from . import decorator as dec
from .. import behaviour
from .. import common

class OneShot(dec.Decorator):
    """
    A decorator that implements the oneshot pattern.

    This decorator ensures that the underlying child is ticked through
    to completion just once and while doing so, will return
    with the same status as it's child. Thereafter it will return
    with the final status of the underlying child.

    Completion status is determined by the policy given on construction.

    * With policy :data:`~py_trees.common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION`, the oneshot will activate only when the underlying child returns :data:`~py_trees.common.Status.SUCCESS` (i.e. it permits retries).
    * With policy :data:`~py_trees.common.OneShotPolicy.ON_COMPLETION`, the oneshot will activate when the child returns :data:`~py_trees.common.Status.SUCCESS` || :data:`~py_trees.common.Status.FAILURE`.

    .. seealso:: :meth:`py_trees.idioms.oneshot`
    """
    def __init__(self, child = None,
                 name=common.Name.AUTO_GENERATED,
                 policy=common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION):
        """
        Init with the decorated child.

        Args:
            name (:obj:`str`): the decorator name
            child (:class:`~py_trees.behaviour.Behaviour`): behaviour to time
            policy (:class:`~py_trees.common.OneShotPolicy`): policy determining when the oneshot should activate
        """
        super(OneShot, self).__init__(name=name, child=child)
        self.final_status = None
        self.policy = policy

    def update(self):
        """
        Bounce if the child has already successfully completed.
        """
        if self.final_status:
            self.logger.debug("{}.update()[bouncing]".format(self.__class__.__name__))
            return self.final_status
        return self.decorated.status

    def tick(self):
        """
        Select between decorator (single child) and behaviour (no children) style
        ticks depending on whether or not the underlying child has been ticked
        successfully to completion previously.
        """
        if self.final_status:
            # ignore the child
            for node in behaviour.Behaviour.tick(self):
                yield node
        else:
            # tick the child
            for node in dec.Decorator.tick(self):
                yield node

    def terminate(self, new_status):
        """
        If returning :data:`~py_trees.common.Status.SUCCESS` for the first time,
        flag it so future ticks will block entry to the child.
        """
        if not self.final_status and new_status in self.policy.value:
            self.logger.debug("{}.terminate({})[oneshot completed]".format(self.__class__.__name__, new_status))
            self.feedback_message = "oneshot completed"
            self.final_status = new_status
        else:
            self.logger.debug("{}.terminate({})".format(self.__class__.__name__, new_status))