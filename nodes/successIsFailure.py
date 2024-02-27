from . import decorator as dec
from .. import common

class SuccessIsFailure(dec.Decorator):
    """
    Be depressed, always fail.
    """
    def update(self):
        """
        Return the decorated child's status unless it is
        :data:`~py_trees.common.Status.SUCCESS` in which case, return
        :data:`~py_trees.common.Status.FAILURE`.

        Returns:
            :class:`~py_trees.common.Status`: the behaviour's new status :class:`~py_trees.common.Status`
        """
        if self.decorated.status == common.Status.SUCCESS:
            self.feedback_message = "success is failure" + (" [%s]" % self.decorated.feedback_message if self.decorated.feedback_message else "")
            return common.Status.FAILURE
        self.feedback_message = self.decorated.feedback_message
        return self.decorated.status