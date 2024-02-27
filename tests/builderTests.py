import time
import pybt.logging as logger
import pybt.builder.pybtbuilder as pb

from pybt.common import Status
from pybt.behaviour import Behaviour

class Action(Behaviour):
    def __init__(self, name):
        super(Action, self).__init__(name)
        pass

    def setup(self):
        self.logger.debug("%s[Action::setup()]" % self.name)

    def initialise(self):
        self.logger.debug("%s[Action::initialise()]" % self.name)

    def update(self):
        time.sleep(1)
        return Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug("%s[Action::terminate().terminate()][%s->%s]" % (self.name, self.status, new_status))

if __name__ == "__main__":
    #invalid_bt = pb.BehaviourTreeBuilder().Action(MyAction("My invalid action")).Build()

    bt = pb.BehaviourTreeBuilder().Sequence("Entry").\
                                    Sequence("Sequence1").\
                                        Action(Action("Action1.1")).\
                                        Action(Action("Action1.2")).\
                                        Selector("Selector1").\
                                            Action(Action("SelAction1")).\
                                            Action(Action("SelAction2")).\
                                            Action(Action("SelAction3")).\
                                    Parent().Action(Action("Action1.3")).\
                                Root().Sequence("Sequence2").\
                                    Action(Action("Action2.1")).\
                                    Action(Action("Action2.2")).\
                                Build()
    
    bt.setup()

    logger.level = logger.Level.DEBUG
    for i in range(1):
        print("\nTick {0}".format(i+1))
        bt.tick()