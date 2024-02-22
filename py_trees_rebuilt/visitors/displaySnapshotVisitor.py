from .snapshotVisitor import SnapshotVisitor
from ..bb import blackboard
from .. import display

class DisplaySnapshotVisitor(SnapshotVisitor):
    """
    Visit the tree, capturing the visited path, it's changes since the last
    tick and additionally print the snapshot to console.

    Args:
        display_blackboard: print to the console the relevant part of the blackboard associated with behaviours on the visited path
        display_activity_stream: print to the console a log of the activity on the blackboard over the last tick
    """
    def __init__(
            self,
            display_only_visited_behaviours=False,
            display_blackboard: bool=False,
            display_activity_stream: bool=False
    ):
        super().__init__()
        self.display_only_visited_behaviours = display_only_visited_behaviours
        self.display_blackboard = display_blackboard
        self.display_activity_stream = display_activity_stream
        if self.display_activity_stream:
            blackboard.Blackboard.enable_activity_stream()

    def initialise(self):
        self.root = None
        super().initialise()
        if self.display_activity_stream:
            blackboard.Blackboard.activity_stream.clear()

    def run(self, behaviour):
        self.root = behaviour  # last behaviour visited will always be the root
        super().run(behaviour)

    def finalise(self):
        #@TODO: Fix display
        pass
        print(
            "\n" +
            display.unicode_tree(
                root=self.root,
                show_only_visited=self.display_only_visited_behaviours,
                show_status=False,
                visited=self.visited,
                previously_visited=self.previously_visited
            )
        )
        if self.display_blackboard:
            print(display.unicode_blackboard(key_filter=self.visited_blackboard_keys))
        if self.display_activity_stream:
            print(display.unicode_blackboard_activity_stream())