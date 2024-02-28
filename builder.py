from . import *

class BehaviourTreeBuilder():
    def __init__(self, showDebugs = False):
        self.showDebugs = showDebugs

        self.root = None # type: behaviour.Behaviour
        self.currentNode = None # type: behaviour.Behaviour
        self.parent = None # type: behaviour.Behaviour
        self.currentDecorator = None # type: nodes.decorator.Decorator
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
            self._handle_decorator_case(newNode)
            self.currentNode = newNode

    def _handle_decorator_case(self, newNode):
        if isinstance(self.currentNode, nodes.composite.Composite):
            self.currentNode.add_child(newNode)
        elif isinstance(self.currentNode, nodes.decorator.Decorator):
            self.currentNode.add_decorated(newNode)

    def _internalNodeHandler(self, nodeType):
        self._printNode(nodeType)
        self._handle_current_node(nodeType)
        self._handle_root()

    def _printNode(self, node  : object):
        if not self.showDebugs:
            return

        print("Added {0} named {1} -> {2}".format(node.__class__.__name__, node.name, self.currentNode.name if self.currentNode is not None else "None"))

#region ACCESS
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
#endregion

#region COMPOSITES
    def Sequence(self, name):
        self._internalNodeHandler(nodes.sequence.Sequence(name = name, memory = True))
        return self

    def Selector(self, name):
        self._internalNodeHandler(nodes.selector.Selector(name = name, memory = True))
        return self

    def Parallel(self, name, policy = common.ParallelPolicy.SuccessOnAll()):
        self._internalNodeHandler(nodes.parallel.Parallel(name = name, policy = policy))
        return self
#endregion

#region DECORATORS
    def EternalGuard(self, name, conditionCheckMethod):
        self._internalNodeHandler(nodes.eternalGuard.EternalGuard(name = name, condition = conditionCheckMethod))
        return self
    
    def FailureIsRunning(self, name):
        self._internalNodeHandler(nodes.failureIsRunning.FailureIsRunning(name = name))
        return self
    
    def FailureIsSuccess(self, name):
        self._internalNodeHandler(nodes.failureIsSuccess.FailureIsSuccess(name = name))
        return self
    
    def RunningIsFailure(self, name):
        self._internalNodeHandler(nodes.runningIsFailure.RunningIsFailure(name = name))
        return self
    
    def RunningIsSuccess(self, name):
        self._internalNodeHandler(nodes.runningIsSuccess.RunningIsSuccess(name = name))
        return self
    
    def SuccessIsFailure(self, name):
        self._internalNodeHandler(nodes.successIsFailure.SuccessIsFailure(name = name))
        return self 
    
    def SuccessIsRunning(self, name):
        self._internalNodeHandler(nodes.successIsRunning.SuccessIsRunning(name = name))
        return self 

    def Inverter(self, name):
        self._internalNodeHandler(nodes.inverter.Inverter(name = name))
        return self
    
    def Oneshot(self, name, policy = common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION):
        self._internalNodeHandler(nodes.oneshot.OneShot(name = name, policy = policy))
        return self
        
    def StatusToBlackboard(self, name, variableName):
        self._internalNodeHandler(nodes.statusToBlackboard.StatusToBlackboard(name = name, variable_name = variableName))
        return self
    
    def Timeout(self, name, duration):
        self._internalNodeHandler(nodes.timeout.Timeout(name = name, duration = duration))
        return self 
    
#endregion

    def Action(self, actionClass):
        if self.root is None:
            raise SyntaxError("An action can't be the root node to a Behaviour tree.")

        self._handle_decorator_case(actionClass)

        self._printNode(actionClass)
        return self