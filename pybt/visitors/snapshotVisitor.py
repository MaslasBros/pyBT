from .visitorBase import VisitorBase

class SnapshotVisitor(VisitorBase):
    """
    Visits the ticked part of a tree, checking off the status against the set of status
    results recorded in the previous tick. If there has been a change, it flags it.
    This is useful for determining when to trigger, e.g. logging.

    Attributes:
        changed (Bool): flagged if there is a difference in the visited path or :class:`~py_trees.common.Status` of any behaviour on the path
        visited (dict): dictionary of behaviour id (uuid.UUID) and status (:class:`~py_trees.common.Status`) pairs from the current tick
        previously_visited (dict): dictionary of behaviour id (uuid.UUID) and status (:class:`~py_trees.common.Status`) pairs from the previous tick
        running_nodes([uuid.UUID]): list of id's for behaviours which were traversed in the current tick
        previously_running_nodes([uuid.UUID]): list of id's for behaviours which were traversed in the last tick
        visited_blackboard_ids(typing.Set[uuid.UUID]): blackboard client id's on the visited path
        visited_blackboard_keys(typing.Set[str]): blackboard variable keys on the visited path

    .. seealso:: The :ref:`py-trees-demo-logging-program` program demonstrates use of this visitor to trigger logging of a tree serialisation.
    """
    def __init__(self):
        super().__init__(full=False)
        self.changed = False
        self.visited = {}
        self.previously_visited = {}
        self.visited_blackboard_keys = set()
        self.visited_blackboard_client_ids = set()

    def initialise(self):
        """
        Switch running to previously running and then reset all other variables. This should
        get called before a tree ticks.
        """
        self.changed = False
        self.previously_visited = self.visited
        self.visited = {}
        self.visited_blackboard_keys = set()
        self.visited_blackboard_client_ids = set()

    def run(self, behaviour):
        """
        This method gets run as each behaviour is ticked. Catch the id and status and store it.
        Additionally add it to the running list if it is :data:`~py_trees.common.Status.RUNNING`.

        Args:
            behaviour (:class:`~py_trees.behaviour.Behaviour`): behaviour that is ticking
        """
        # behaviour status
        self.visited[behaviour.id] = behaviour.status
        try:
            if self.visited[behaviour.id] != self.previously_visited[behaviour.id]:
                self.changed = True
        except KeyError:
            self.changed = True
        # blackboards
        for blackboard in behaviour.blackboards:
            self.visited_blackboard_client_ids.add(blackboard.id())
            self.visited_blackboard_keys = self.visited_blackboard_keys | blackboard.read | blackboard.write | blackboard.exclusive