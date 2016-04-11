#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/yujinrobot/gopher_crazy_hospital/license/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
.. module:: battery
   :platform: Unix
   :synopsis: Battery behaviours

Behaviours related to checking and reacting to battery notifications.
"""

##############################################################################
# Imports
##############################################################################

import gopher_configuration
import gopher_std_msgs.srv as gopher_std_srvs
import py_trees
import rospy
import somanet_msgs.msg as somanet_msgs

from . import interactions

##############################################################################
# Battery
##############################################################################


class CheckChargeState(py_trees.Behaviour):

    def __init__(self, name, expected_state):
        """
        :param int expected_state: return success if the battery enters this charging state
        """
        super(CheckChargeState, self).__init__(name)
        self.expected_state = expected_state
        self.charge_state = None
        self._battery_subscriber = rospy.Subscriber("~battery", somanet_msgs.SmartBatteryStatus, self.battery_callback)

    def battery_callback(self, msg):
        self.charge_state = msg.charge_state

    def update(self):
        if self.charge_state is None:
            self.feedback_message = "waiting for battery update"
            return py_trees.Status.RUNNING
        elif self.charge_state == self.expected_state:
            self.feedback_message = "got expected charge state"
            return py_trees.Status.SUCCESS
        else:
            self.feedback_message = "charge state differed from expected"
            return py_trees.Status.FAILURE


def create_is_docked(name="Is Docked?"):
    """
    Hooks up a subscriber and checks that the charging source is the dock.

    :param str name: behaviour name
    :returns: the behaviour
    :rtype: subscribers.CheckSubscriberVariable
    """
    gopher = gopher_configuration.Configuration(fallback_to_defaults=True)

    check_docked = py_trees.CheckSubscriberVariable(
        name=name,
        topic_name=gopher.topics.battery,
        topic_type=somanet_msgs.SmartBatteryStatus,
        variable_name="charging_source",
        expected_value=somanet_msgs.SmartBatteryStatus.CHARGING_SOURCE_DOCK,
        fail_if_no_data=False,
        fail_if_bad_comparison=True,
        clearing_policy=py_trees.common.ClearingPolicy.NEVER
    )
    return check_docked


def create_is_discharging(name="Is Discharging?"):
    """
    Hooks up a subscriber and checks that there is no current charging source.
    This will 'block', i.e. return RUNNING until it detects that it is discharging.

    :param str name: behaviour name
    :rtype: subscribers.CheckSubscriberVariable
    """
    gopher = gopher_configuration.Configuration(fallback_to_defaults=True)
    is_discharging = py_trees.CheckSubscriberVariable(
        name=name,
        topic_name=gopher.topics.battery,
        topic_type=somanet_msgs.SmartBatteryStatus,
        variable_name="charging_source",
        expected_value=somanet_msgs.SmartBatteryStatus.CHARGING_SOURCE_NONE,
        fail_if_no_data=False,
        fail_if_bad_comparison=True,
        clearing_policy=py_trees.common.ClearingPolicy.NEVER
    )
    return is_discharging


def create_wait_to_be_unplugged(name="Unplug Me"):
    """
    Hooks up a subscriber and checks that there is no current charging source.
    This will 'block', i.e. return RUNNING until it detects that it is discharging.

    :param str name: subtree root name
    :returns: the subtree
    """
    gopher = gopher_configuration.Configuration(fallback_to_defaults=True)

    wait_to_be_unplugged = py_trees.composites.Parallel(
        name="Wait to be Unplugged",
        policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE
    )
    wait_to_be_unplugged.blackbox_level = py_trees.common.BlackBoxLevel.DETAIL
    flash_notification = interactions.Notification(
        name='Flash for Help',
        message='waiting for button press to continue',
        led_pattern=gopher.led_patterns.humans_i_need_help,
        duration=gopher_std_srvs.NotifyRequest.INDEFINITE
    )
    check_if_discharging = py_trees.CheckSubscriberVariable(
        name="Check if Discharging",
        topic_name=gopher.topics.battery,
        topic_type=somanet_msgs.SmartBatteryStatus,
        variable_name="charging_source",
        expected_value=somanet_msgs.SmartBatteryStatus.CHARGING_SOURCE_NONE,
        fail_if_no_data=False,
        fail_if_bad_comparison=False,
        clearing_policy=py_trees.common.ClearingPolicy.NEVER
    )
    wait_to_be_unplugged.add_child(flash_notification)
    wait_to_be_unplugged.add_child(check_if_discharging)
    return wait_to_be_unplugged


class CheckBatteryLevel(py_trees.Behaviour):
    """
    Subscribes to the battery message and continually checks on the battery level, returning
    a FAILURE when it is low, SUCCESS otherwise
    """
    def __init__(self, name):
        # setup
        super(CheckBatteryLevel, self).__init__(name)
        self.successes = 0
        self.battery_percentage = 100
        self.gopher = None
        self.subscriber = None

    def setup(self, unused_timeout):
        self.logger.debug("  %s [CheckBatteryLevel.setup()]" % self.name)
        self.gopher = gopher_configuration.Configuration(fallback_to_defaults=True)
        self.subscriber = rospy.Subscriber(self.gopher.topics.battery, somanet_msgs.SmartBatteryStatus, self.battery_callback)
        return True

    def update(self):
        self.logger.debug("  %s [CheckBatteryLevel.update()]" % self.name)
        if self.subscriber is None:
            # safe to setup the subscriber in here...no blocking involved
            self.setup(None)
        # Note : battery % in the feedback message causes spam in behaviour
        # tree rqt viewer, we are merely interested in the transitions, so do not send this
        # self.feedback_message = "battery %s%% [low: %s%%]" % (self.battery_percentage, self.gopher.battery.low)
        if self.battery_percentage < self.gopher.battery.low:
            if self.successes % 10 == 0:  # throttling
                rospy.logwarn("Behaviours [%s]: battery level is low!" % self.name)
            self.successes += 1
            self.feedback_message = "Battery level is low."
            return py_trees.Status.SUCCESS
        else:
            self.feedback_message = "Battery level is ok."
            return py_trees.Status.FAILURE

    def battery_callback(self, msg):
        self.battery_percentage = msg.percentage
