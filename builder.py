from .. import *

class BehaviourTreeBuilder():
    def __init__(self):
        self.root = None # type: behaviour.Behaviour
        self.currentNode = None # type: behaviour.Behaviour
        self.parent = None # type: behaviour.Behaviour
        pass

    def _handle_root(self):
        if self.root is None:
            self.root = self.currentNode

        pass

    def _handle_current_node(self, newNode):
        if self.currentNode is None:
            self.currentNode = newNode
        else:
            self.parent = self.currentNode
            self.currentNode.add_child(newNode)
            self.currentNode = newNode

        pass

    def Root(self):
        print("Root -> {0}".format(self.root.name))
        self.currentNode = self.root
        return self

    def Parent(self):
        print("Parent -> {0}".format(self.parent.name))
        self.currentNode = self.parent
        return self

    def Build(self):
        return trees.BehaviourTree(self.root)

    def Sequence(self, name):
        print("Added sequence {0} -> {1}".format(name, self.currentNode.name if self.currentNode is not None else "None"))
        self._handle_current_node(nodes.sequence.Sequence(name = name, memory = True))
        self._handle_root()

        return self

    def Selector(self, name):
        print("Added selector {0} -> {1}".format(name, self.currentNode.name if self.currentNode is not None else "None"))
        self._handle_current_node(nodes.selector.Selector(name = name, memory = True))
        self._handle_root()

        return self

    def Parallel(self, name, policy):
        print("Added parallel {0} with policy {1} -> {2}".format(name, policy, self.currentNode.name if self.currentNode is not None else "None"))
        self._handle_current_node(nodes.parallel.Parallel(name = name, policy = policy))
        self._handle_root()

        return self

    def Action(self, actionClass):
        if self.root is None:
            raise SyntaxError("An action can't be the root node to a Behaviour tree.")

        self.currentNode.add_child(actionClass)

        print("Added action {0} -> {1}".format(actionClass.name, self.currentNode.name if self.currentNode is not None else "None"))
        return self