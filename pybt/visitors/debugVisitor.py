from .visitorBase import VisitorBase

class DebugVisitor(VisitorBase):
    """
    Picks up and logs feedback messages and the behaviour's status. Logging is done with
    the behaviour's logger.
    """
    def __init__(self):
        super(DebugVisitor, self).__init__(full=False)

    def run(self, behaviour):
        if behaviour.feedback_message:
            behaviour.logger.debug("%s.run() [%s][%s]" % (self.__class__.__name__, behaviour.feedback_message, behaviour.status))
        else:
            behaviour.logger.debug("%s.run() [%s]" % (self.__class__.__name__, behaviour.status))