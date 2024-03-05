from .. import common
from .. import behaviour

class TickCounter(behaviour.Behaviour):
    """
    A useful utility behaviour for demos and tests. Simply
    ticks with :data:`~py_trees.common.Status.RUNNING` for
    the specified number of ticks before returning the
    requested completion status (:data:`~py_trees.common.Status.SUCCESS`
    or :data:`~py_trees.common.Status.FAILURE`).

    This behaviour will reset the tick counter when initialising.

    Args:
        name: name of the behaviour
        duration: number of ticks to run
        completion_status: status to switch to once the counter has expired
    """
    def __init__(
        self,
        duration: int,
        name=common.Name.AUTO_GENERATED,
        completion_status: common.Status=common.Status.SUCCESS
    ):
        super().__init__(name=name)
        self.completion_status = completion_status
        self.duration = duration
        self.counter = 0

    def initialise(self):
        """
        Reset the tick counter.
        """
        self.counter = 0

    def update(self):
        """
        Increment the tick counter and return the appropriate status for this behaviour
        based on the tick count.

        Returns
            :data:`~py_trees.common.Status.RUNNING` while not expired, the given completion status otherwise
        """
        self.counter += 1
        if self.counter <= self.duration:
            return common.Status.RUNNING
        else:
            return self.completion_status