import typing
import operator

from .. import common
from .. import behaviour

class CheckBlackboardVariableValue(behaviour.Behaviour):
    """
    Inspect a blackboard variable and if it exists, check that it
    meets the specified criteria (given by operation type and expected value).
    This is non-blocking, so it will always tick with
    :data:`~py_trees.common.Status.SUCCESS` or
    :data:`~py_trees.common.Status.FAILURE`.

    Args:
        check: a comparison expression to check against
        name: name of the behaviour

    .. note::
        If the variable does not yet exist on the blackboard, the behaviour will
        return with status :data:`~py_trees.common.Status.FAILURE`.

    .. tip::
        The python `operator module`_ includes many useful comparison operations.
    """
    def __init__(
            self,
            check: common.ComparisonExpression,
            name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name)
        self.check = check
        name_components = self.check.variable.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.READ)

    def update(self):
        """
        Check for existence, or the appropriate match on the expected value.

        Returns:
             :class:`~py_trees.common.Status`: :data:`~py_trees.common.Status.FAILURE` if not matched, :data:`~py_trees.common.Status.SUCCESS` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        try:
            value = self.blackboard.get(self.key)
            if self.key_attributes:
                try:
                    value = operator.attrgetter(self.key_attributes)(value)
                except AttributeError:
                    self.feedback_message = 'blackboard key-value pair exists, but the value does not have the requested nested attributes [{}]'.format(self.variable_name)
                    return common.Status.FAILURE
        except KeyError:
            self.feedback_message = "key '{}' does not yet exist on the blackboard".format(self.check.variable)
            return common.Status.FAILURE

        success = self.check.operator(value, self.check.value)

        if success:
            self.feedback_message = "'%s' comparison succeeded [v: %s][e: %s]" % (self.check.variable, value, self.check.value)
            return common.Status.SUCCESS
        else:
            self.feedback_message = "'%s' comparison failed [v: %s][e: %s]" % (self.check.variable, value, self.check.value)
            return common.Status.FAILURE