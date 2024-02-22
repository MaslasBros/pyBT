from . import decorator as dec
from .. import behaviour
from .. import common

class StatusToBlackboard(dec.Decorator):
    """
    Reflect the status of the decorator's child to the blackboard.

    Args:
        child: the child behaviour or subtree
        variable_name: name of the blackboard variable, may be nested, e.g. foo.status
        name: the decorator name
    """
    def __init__(
            self,
            *,
            child: behaviour.Behaviour,
            variable_name: str,
            name: dec.Union[str, common.Name]=common.Name.AUTO_GENERATED,
    ):
        super().__init__(child=child, name=name)
        self.variable_name = variable_name
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client(self.name)
        self.blackboard.register_key(key=self.key, access=common.Access.WRITE)

    def update(self):
        """
        Reflect the decorated child's status to the blackboard and return

        Returns: the decorated child's status
        """
        self.blackboard.set(
            name=self.variable_name,
            value=self.decorated.status,
            overwrite=True
        )
        return self.decorated.status
