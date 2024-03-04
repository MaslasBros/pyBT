from . import decorator as dec
from .. import common

class RunningIsFailure(dec.Decorator):
    """
    Got to be snappy! We want results...yesterday!
    """
    def update(self):
        """
        Return the decorated child's status unless it is
        :data:`~py_trees.common.Status.RUNNING` in which case, return
        :data:`~py_trees.common.Status.FAILURE`.

        Returns:
            :class:`~py_trees.common.Status`: the behaviour's new status :class:`~py_trees.common.Status`
        """
        if self.decorated.status == common.Status.RUNNING:
            self.feedback_message = "running is failure" + (" [%s]" % self.decorated.feedback_message if self.decorated.feedback_message else "")
            return common.Status.FAILURE
        else:
            self.feedback_message = self.decorated.feedback_message
            return self.decorated.status