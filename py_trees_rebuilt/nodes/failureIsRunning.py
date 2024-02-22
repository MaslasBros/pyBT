from . import decorator as dec
from .. import common

class FailureIsRunning(dec.Decorator):
    """
    Dont stop running.
    """
    def update(self):
        """
        Return the decorated child's status unless it is
        :data:`~py_trees.common.Status.FAILURE` in which case, return
        :data:`~py_trees.common.Status.RUNNING`.

        Returns:
            :class:`~py_trees.common.Status`: the behaviour's new status :class:`~py_trees.common.Status`
        """
        if self.decorated.status == common.Status.FAILURE:
            self.feedback_message = "failure is running" + (" [%s]" % self.decorated.feedback_message if self.decorated.feedback_message else "")
            return common.Status.RUNNING
        self.feedback_message = self.decorated.feedback_message
        return self.decorated.status