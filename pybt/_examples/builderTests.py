import time
import pybt.logging as logger
import pybt.builder as pb

from pybt._demos import *
from pybt.common import Status
from pybt.behaviour import Behaviour

class MyAction(Behaviour):
    def __init__(self, name):
        super(MyAction, self).__init__(name)
        pass

    def setup(self):
        self.logger.debug("%s[MyAction::setup()]" % self.name)
        self.blackboard = self.attach_blackboard_client("main", "Actions")
        self.blackboard.register_key(self.name, pb.common.Access.READ)

    def initialise(self):
        self.logger.debug("%s[MyAction::initialise()]" % self.name)

    def update(self):
        #time.sleep(1)
        self.blackboard.set("{0}".format(self.name), "Heloooooooooooo")
        return Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug("%s[MyAction::terminate().terminate()][%s->%s]" % (self.name, self.status, new_status))

#invalid_bt = pb.BehaviourTreeBuilder().Action(MyAction("My invalid action")).Build()

bt = pb.BehaviourTreeBuilder(True).Sequence("Entry").\
                                        Sequence("Sequence1").\
                                            Action(MyAction("Action1.1")).\
                                            Action(MyAction("Action1.2")).\
                                            Selector("Selector1").\
                                                Action(MyAction("SelAction1")).\
                                                Action(MyAction("SelAction2")).\
                                                Action(MyAction("SelAction3")).\
                                        Parent().Action(MyAction("Action1.3")).\
                                    Root().Sequence("Sequence2").\
                                        Action(MyAction("Action2.1")).\
                                        Action(MyAction("Action2.2")).\
                                    Build()

""" def returnTrue():
    return pb.common.Status.SUCCESS

bt = pb.BehaviourTreeBuilder(True).Sequence("Entry").\
                                Inverter("AC").\
                                Sequence("Sequencer").\
                                    Action(MyAction("Action1")).\
                                    Action(MyAction("Action2")).\
                                    Action(MyAction("Action3")).\
                            Build() """

print("\nSetup\n")
logger.level = logger.Level.DEBUG
bt.setup()

print("\n")
print(pb.display.unicode_blackboard())

for i in range(1):
    print("\nTick {0}".format(i+1))
    bt.tick()