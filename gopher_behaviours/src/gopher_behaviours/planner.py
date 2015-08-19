#!/usr/bin/env python

##############################################################################
# Imports
##############################################################################

import rospy
import delivery
import moveit

##############################################################################
# Implementation
##############################################################################

class Planner():

    def __init__(self, locations, auto_go):
        self.current_location = None
        self.auto_go = auto_go
        self.semantic_locations = {}
        
        for semantic_location in locations:
            self.semantic_locations[semantic_location.unique_name] = semantic_location
        
    def create_tree(self, locations, undock=True):
        """
        Find the semantic locations corresponding to the incoming string location identifier and
        create the appropriate behaviours.

        :param: string list of location unique names given to us by the delivery goal.

        .. todo::

           Clean up the key error handling
        """
        # if we are constructing a "complete" 
        children = [moveit.UnDock("UnDock")] if undock else []
        for ind, location in enumerate(locations):
            try:
                semantic_location = self.semantic_locations[location]  # this is the full gopher_std_msgs.Location structure
                children.append(moveit.MoveToGoal(name=semantic_location.name, pose=semantic_location.pose))
                # don't append a waiting action for the last location
                if ind < len(locations) - 1:
                    children.append(
                        delivery.Waiting(name="Waiting at " + semantic_location.name,
                                         location=semantic_location.unique_name,
                                         dont_wait_for_hoomans_flag=self.auto_go)
                    )
            except KeyError, ke:  # a location passed was unknown : ignore it
                rospy.logwarn("{0} is not in semantic_locations".format(location))
                continue

        return children

