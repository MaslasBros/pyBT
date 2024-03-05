class KeyMetaData(object):
    """
    Stores the aggregated metadata for a key on the blackboard.
    """
    def __init__(self):
        self.read = set()
        self.write = set()
        self.exclusive = set()