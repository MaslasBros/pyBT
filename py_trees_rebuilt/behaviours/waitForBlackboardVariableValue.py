import typing

from .. import common
from . import checkBlackboardVariableValue as c

class WaitForBlackboardVariableValue(c.CheckBlackboardVariableValue):
    """
    Inspect a blackboard variable and if it exists, check that it
    meets the specified criteria (given by operation type and expected value).
    This is blocking, so it will always tick with
    :data:`~py_trees.common.Status.SUCCESS` or
    :data:`~py_trees.common.Status.RUNNING`.

    .. seealso::

       :class:`~py_trees.behaviours.CheckBlackboardVariableValue` for
       the non-blocking counterpart to this behaviour.

    .. note::
        If the variable does not yet exist on the blackboard, the behaviour will
        return with status :data:`~py_trees.common.Status.RUNNING`.

    Args:
        check: a comparison expression to check against
        name: name of the behaviour
    """
    def __init__(
            self,
            check: common.ComparisonExpression,
            name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED
    ):
        super().__init__(
            check=check,
            name=name
        )

    def update(self):
        """
        Check for existence, or the appropriate match on the expected value.

        Returns:
             :class:`~py_trees.common.Status`: :data:`~py_trees.common.Status.FAILURE` if not matched, :data:`~py_trees.common.Status.SUCCESS` otherwise.
        """
        new_status = super().update()
        if new_status == common.Status.FAILURE:
            return common.Status.RUNNING
        else:
            return new_status