from . import decorator as dec
from .. import common

class Condition(dec.Decorator):
    """
    Encapsulates a behaviour and wait for it's status to flip to the
    desired state. This behaviour will tick with
    :data:`~py_trees.common.Status.RUNNING` while waiting and
    :data:`~py_trees.common.Status.SUCCESS` when the flip occurs.
    """
    def __init__(self,
                 child,
                 name=common.Name.AUTO_GENERATED,
                 status=common.Status.SUCCESS):
        """
        Initialise with child and optional name, status variables.

        Args:
            child (:class:`~py_trees.behaviour.Behaviour`): the child to be decorated
            name (:obj:`str`): the decorator name (can be None)
            status (:class:`~py_trees.common.Status`): the desired status to watch for
        """
        super(Condition, self).__init__(child, name)
        self.succeed_status = status