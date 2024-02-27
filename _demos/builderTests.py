import time
import pybt.logging as logger
import pybt.builder as pb

from pybt.common import Status
from pybt.behaviour import Behaviour

class MyAction(Behaviour):
    def __init__(self, name):
        super(MyAction, self).__init__(name)
        pass

    def setup(self):
        self.logger.debug("%s[MyAction::setup()]" % self.name)

    def initialise(self):
        self.logger.debug("%s[MyAction::initialise()]" % self.name)

    def update(self):
        time.sleep(1)
        return Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug("%s[MyAction::terminate().terminate()][%s->%s]" % (self.name, self.status, new_status))

if __name__ == "__main__":
    #invalid_bt = pb.BehaviourTreeBuilder().Action(MyAction("My invalid action")).Build()

    bt = pb.BehaviourTreeBuilder().Sequence("Entry").\
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
    
    bt.setup()

    logger.level = logger.Level.DEBUG
    for i in range(1):
        print("\nTick {0}".format(i+1))
        bt.tick()