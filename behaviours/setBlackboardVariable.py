import typing

from .. import common
from .. import behaviour

class SetBlackboardVariable(behaviour.Behaviour):
    """
    Set the specified variable on the blackboard.

    Args:
        variable_name: name of the variable to set, may be nested, e.g. battery.percentage
        variable_value: value of the variable to set
        overwrite: when False, do not set the variable if it already exists
        name: name of the behaviour
    """
    def __init__(
            self,
            variable_name: str,
            variable_value: typing.Union[typing.Any, typing.Callable[[], typing.Any]],
            overwrite: bool = True,
            name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED,
    ):
        super().__init__(name=name)
        self.variable_name = variable_name
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.WRITE)
        self.variable_value_generator = variable_value if callable(variable_value) else lambda: variable_value
        self.overwrite = overwrite

    def update(self) -> common.Status:
        """
        Always return success.

        Returns:
             :data:`~py_trees.common.Status.FAILURE` if no overwrite requested and the variable exists,  :data:`~py_trees.common.Status.SUCCESS` otherwise
        """
        if self.blackboard.set(
            self.variable_name,
            self.variable_value_generator(),
            overwrite=self.overwrite
        ):
            return common.Status.SUCCESS
        else:
            return common.Status.FAILURE