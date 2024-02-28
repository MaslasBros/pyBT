import time

from . import decorator as dec
from .. import behaviour
from .. import common

class Timeout(dec.Decorator):
    """
    A decorator that applies a timeout pattern to an existing behaviour.
    If the timeout is reached, the encapsulated behaviour's
    :meth:`~py_trees.behaviour.Behaviour.stop` method is called with
    status :data:`~py_trees.common.Status.FAILURE` otherwise it will
    simply directly tick and return with the same status
    as that of it's encapsulated behaviour.
    """
    def __init__(self,
                 child: behaviour.Behaviour = None,
                 name: dec.Union[str, common.Name]=common.Name.AUTO_GENERATED,
                 duration: float=5.0):
        """
        Init with the decorated child and a timeout duration.

        Args:
            child: the child behaviour or subtree
            name: the decorator name
            duration: timeout length in seconds
        """
        super(Timeout, self).__init__(name=name, child=child)
        self.duration = duration
        self.finish_time = None

    def initialise(self):
        """
        Reset the feedback message and finish time on behaviour entry.
        """
        self.finish_time = time.monotonic() + self.duration
        self.feedback_message = ""

    def update(self):
        """
        Terminate the child and return :data:`~py_trees.common.Status.FAILURE`
        if the timeout is exceeded.
        """
        current_time = time.monotonic()
        if self.decorated.status == common.Status.RUNNING and current_time > self.finish_time:
            self.feedback_message = "timed out"
            self.logger.debug("{}.update() {}".format(self.__class__.__name__, self.feedback_message))
            # invalidate the decorated (i.e. cancel it), could also put this logic in a terminate() method
            self.decorated.stop(common.Status.INVALID)
            return common.Status.FAILURE
        if self.decorated.status == common.Status.RUNNING:
            self.feedback_message = "time still ticking ... [remaining: {}s]".format(
                self.finish_time - current_time
            )
        else:
            self.feedback_message = "child finished before timeout triggered"
        return self.decorated.status