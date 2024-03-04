import typing

from .. import common
from . import checkBlackboardVariableExists as base

class WaitForBlackboardVariable(base.CheckBlackboardVariableExists):
    """
    Wait for the blackboard variable to become available on the blackboard.
    This is blocking, so it will tick with
    status :data:`~py_trees.common.Status.SUCCESS` if the variable is found,
    and :data:`~py_trees.common.Status.RUNNING` otherwise.

    .. seealso::

       :class:`~py_trees.behaviours.CheckBlackboardVariableExists` for
       the non-blocking counterpart to this behaviour.

    Args:
        variable_name: name of the variable to wait for, may be nested, e.g. battery.percentage
        name: name of the behaviour
    """
    def __init__(
            self,
            variable_name: str,
            name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name, variable_name=variable_name)

    def update(self) -> common.Status:
        """
        Check for existence, wait otherwise.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS` if key found, :data:`~py_trees.common.Status.RUNNING` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        new_status = super().update()
        # CheckBlackboardExists only returns SUCCESS || FAILURE
        if new_status == common.Status.SUCCESS:
            self.feedback_message = "'{}' found".format(self.key)
            return common.Status.SUCCESS
        else:  # new_status == common.Status.FAILURE
            self.feedback_message = "waiting for key '{}'...".format(self.key)
            return common.Status.RUNNING