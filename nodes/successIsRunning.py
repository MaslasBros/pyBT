from . import decorator as dec
from .. import common

class SuccessIsRunning(dec.Decorator):
    """
    It never ends...
    """
    def update(self):
        """
        Return the decorated child's status unless it is
        :data:`~py_trees.common.Status.SUCCESS` in which case, return
        :data:`~py_trees.common.Status.RUNNING`.

        Returns:
            :class:`~py_trees.common.Status`: the behaviour's new status :class:`~py_trees.common.Status`
        """
        if self.decorated.status == common.Status.SUCCESS:
            self.feedback_message = "success is running [%s]" % self.decorated.feedback_message
            return common.Status.RUNNING
        self.feedback_message = self.decorated.feedback_message
        return self.decorated.status