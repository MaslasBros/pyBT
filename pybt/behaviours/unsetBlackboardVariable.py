import typing

from .. import common
from .. import behaviour

class UnsetBlackboardVariable(behaviour.Behaviour):
    """
    Unset the specified variable (key-value pair) from the blackboard.

    This always returns
    :data:`~py_trees.common.Status.SUCCESS` regardless of whether
    the variable was already present or not.

    Args:
        key: unset this key-value pair
        name: name of the behaviour
    """
    def __init__(self,
                 key: str,
                 name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED,
                 ):
        super().__init__(name=name)
        self.key = key
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.WRITE)

    def update(self) -> common.Status:
        """
        Unset and always return success.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS`
        """
        if self.blackboard.unset(self.key):
            self.feedback_message = "'{}' found and removed".format(self.key)
        else:
            self.feedback_message = "'{}' not found, nothing to remove"
        return common.Status.SUCCESS