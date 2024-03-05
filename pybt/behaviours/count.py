from .. import common
from .. import behaviour

class Count(behaviour.Behaviour):
    """
    A counting behaviour that updates its status at each tick depending on
    the value of the counter. The status will move through the states in order -
    :data:`~py_trees.common.Status.FAILURE`, :data:`~py_trees.common.Status.RUNNING`,
    :data:`~py_trees.common.Status.SUCCESS`.

    This behaviour is useful for simple testing and demo scenarios.

    Args:
        name (:obj:`str`): name of the behaviour
        fail_until (:obj:`int`): set status to :data:`~py_trees.common.Status.FAILURE` until the counter reaches this value
        running_until (:obj:`int`): set status to :data:`~py_trees.common.Status.RUNNING` until the counter reaches this value
        success_until (:obj:`int`): set status to :data:`~py_trees.common.Status.SUCCESS` until the counter reaches this value
        reset (:obj:`bool`): whenever invalidated (usually by a sequence reinitialising, or higher priority interrupting)

    Attributes:
        count (:obj:`int`): a simple counter which increments every tick
    """
    def __init__(self, name="Count", fail_until=3, running_until=5, success_until=6, reset=True):
        super(Count, self).__init__(name)
        self.count = 0
        self.fail_until = fail_until
        self.running_until = running_until
        self.success_until = success_until
        self.number_count_resets = 0
        self.number_updated = 0
        self.reset = reset

    def terminate(self, new_status):
        self.logger.debug("%s.terminate(%s->%s)" % (self.__class__.__name__, self.status, new_status))
        # reset only if udpate got us into an invalid state
        if new_status == common.Status.INVALID and self.reset:
            self.count = 0
            self.number_count_resets += 1
        self.feedback_message = ""

    def update(self):
        self.number_updated += 1
        self.count += 1
        if self.count <= self.fail_until:
            self.logger.debug("%s.update()[%s: failure]" % (self.__class__.__name__, self.count))
            self.feedback_message = "failing"
            return common.Status.FAILURE
        elif self.count <= self.running_until:
            self.logger.debug("%s.update()[%s: running]" % (self.__class__.__name__, self.count))
            self.feedback_message = "running"
            return common.Status.RUNNING
        elif self.count <= self.success_until:
            self.logger.debug("%s.update()[%s: success]" % (self.__class__.__name__, self.count))
            self.feedback_message = "success"
            return common.Status.SUCCESS
        else:
            self.logger.debug("%s.update()[%s: failure]" % (self.__class__.__name__, self.count))
            self.feedback_message = "failing forever more"
            return common.Status.FAILURE

    def __repr__(self):
        """
        Simple string representation of the object.

        Returns:
            :obj:`str`: string representation
        """
        s = "%s\n" % self.name
        s += "  Status : %s\n" % self.status
        s += "  Count  : %s\n" % self.count
        s += "  Resets : %s\n" % self.number_count_resets
        s += "  Updates: %s\n" % self.number_updated
        return s