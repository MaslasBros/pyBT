import typing

from .. import common
from .. import behaviour

class CheckBlackboardVariableExists(behaviour.Behaviour):
    """
    Check the blackboard to verify if a specific variable (key-value pair)
    exists. This is non-blocking, so will always tick with
    status :data:`~py_trees.common.Status.FAILURE`
    :data:`~py_trees.common.Status.SUCCESS`.

    .. seealso::

       :class:`~py_trees.behaviours.WaitForBlackboardVariable` for
       the blocking counterpart to this behaviour.

    Args:
        variable_name: name of the variable look for, may be nested, e.g. battery.percentage
        name: name of the behaviour
    """
    def __init__(
            self,
            variable_name: str,
            name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name)
        self.variable_name = variable_name
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.READ)

    def update(self) -> common.Status:
        """
        Check for existence.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS` if key found, :data:`~py_trees.common.Status.FAILURE` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        try:
            unused_value = self.blackboard.get(self.variable_name)
            self.feedback_message = "variable '{}' found".format(self.variable_name)
            return common.Status.SUCCESS
        except KeyError:
            self.feedback_message = "variable '{}' not found".format(self.variable_name)
            return common.Status.FAILURE