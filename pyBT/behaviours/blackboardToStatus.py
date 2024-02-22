import typing

from .. import common
from .. import behaviour

class BlackboardToStatus(behaviour.Behaviour):
    """
    This behaviour reverse engineers the :class:`~py_trees.decorators.StatusToBlackboard`
    decorator. Used in conjuction with that decorator, this behaviour can be used to
    reflect the status of a decision elsewhere in the tree.

    .. note::

       A word of caution. The consequences of a behaviour's status should be discernable
       upon inspection of the tree graph. If using StatusToBlackboard
       and BlackboardToStatus to reflect a behaviour's status across a tree,
       this is no longer true. The graph of the tree communicates the local consequences,
       but not the reflected consequences at the point BlackboardToStatus is used. A
       recommendation, use this class only where other options are infeasible or impractical.

    Args:
        variable_name: name of the variable look for, may be nested, e.g. battery.percentage
        name: name of the behaviour

    Raises:
        KeyError: if the variable doesn't exist
        TypeError: if the variable isn't of type :py:data:`~py_trees.common.Status`
    """
    def __init__(
        self,
        variable_name: str,
        name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name)
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.variable_name = variable_name
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.READ)

    def update(self) -> common.Status:
        """
        Check for existence.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS` if key found, :data:`~py_trees.common.Status.FAILURE` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        # raises a KeyError if the variable doesn't exist
        status = self.blackboard.get(self.variable_name)
        if type(status) != common.Status:
            raise TypeError("{0} is not of type py_trees.common.Status".format(self.variable_name))
        self.feedback_message = "{0}: {1}".format(self.variable_name, status)
        return status