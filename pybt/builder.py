from . import *

class BehaviourTreeBuilder():
    def __init__(self, showDebugs = False):
        self.showDebugs = showDebugs # type: bool
        """Whether to print debug logs in the console"""

        self._root = None # type: behaviour.Behaviour
        """The root of the tree"""

        self._currentNode = None # type: behaviour.Behaviour
        """Current behaviour tree building node"""
        
        self._parent = None # type: behaviour.Behaviour
        """The parent of the currentNode"""
        self._currentDecorator = None # type: nodes.decorator.Decorator
        """The current decorator of the currentNode"""
        pass

    def _internalNodeHandler(self, newNode):
        """
        Prints the newly added node in the console.
        Adds the passed node as a child of the previous Composite or Decorator.
        Sets the self.root to the passed node if the root is None.

        Args:
            newNode (:class:`~pybt.behaviour.Behaviour`): The new node to add in the tree
        """
        self._printNode(newNode)

        if self._currentNode is None:
            self._currentNode = newNode
        else:
            self._parent = self._currentNode
            if isinstance(self._currentNode, nodes.composite.Composite):
                self._currentNode.add_child(newNode)
            elif isinstance(self._currentNode, nodes.decorator.Decorator):
                self._currentNode.add_decorated(newNode)
            
            self._currentNode = newNode

        if self._root is None:
            self._root = self._currentNode
    
    def _printNode(self, node  : object):
        """
        Prints the passed node in a pretty format in the console if self.showDebugs is True.

        Args:
            node (:class:`~pybt.behaviour.Behaviour`): The node to print
        """
        
        if not self.showDebugs:
            return

        print("Added {0} named {1} -> {2}".format(node.__class__.__name__, node.name, self._currentNode.name if self._currentNode is not None else "None"))

#region ACCESS
    def Root(self):
        """
        Returns the root node of the tree.
        """
        
        self._currentNode = self._root
        return self

    def Parent(self):
        """
        Returns the parent of the current node.
        """

        self._currentNode = self._parent
        return self

    def Build(self):
        """
        Builds and returns a Behaviour Tree instance. 
        """
        
        return trees.BehaviourTree(self._root)
#endregion

#region COMPOSITES
    def Sequence(self, name):
        """
        Adds a sequence Composite to the tree.

        Args:
            name (:class:`str`): The node name.
        """

        self._internalNodeHandler(nodes.sequence.Sequence(name = name, memory = True))
        return self

    def Selector(self, name):
        """
        Adds a selector Composite to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """

        self._internalNodeHandler(nodes.selector.Selector(name = name, memory = True))
        return self

    def Parallel(self, name, policy = common.ParallelPolicy.SuccessOnAll()):
        """
        Adds a parallel Composite to the tree. 
        
        Args:
            name (:class:`str`): The node name.
            policy (:class:`pybt.common.ParallelPolicy`): The parallel policy of this node
        """

        self._internalNodeHandler(nodes.parallel.Parallel(name = name, policy = policy))
        return self
#endregion

#region DECORATORS
    def EternalGuard(self, name, conditionCheckMethod):
        """
        Adds a eternal guard Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
            conditionCheckMethod (:class:`function`): A functional check that determines execution or not of the subtree
        """
        
        self._internalNodeHandler(nodes.eternalGuard.EternalGuard(name = name, condition = conditionCheckMethod))
        return self
    
    def FailureIsRunning(self, name):
        """
        Adds a failure is running Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """

        self._internalNodeHandler(nodes.failureIsRunning.FailureIsRunning(name = name))
        return self
    
    def FailureIsSuccess(self, name):
        """
        Adds a failure is success Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.failureIsSuccess.FailureIsSuccess(name = name))
        return self
    
    def RunningIsFailure(self, name):
        """
        Adds a running is failure Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.runningIsFailure.RunningIsFailure(name = name))
        return self
    
    def RunningIsSuccess(self, name):
        """
        Adds a running is success Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.runningIsSuccess.RunningIsSuccess(name = name))
        return self
    
    def SuccessIsFailure(self, name):
        """
        Adds a success is failure Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.successIsFailure.SuccessIsFailure(name = name))
        return self 
    
    def SuccessIsRunning(self, name):
        """
        Adds a success is running Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.successIsRunning.SuccessIsRunning(name = name))
        return self 

    def Inverter(self, name):
        """
        Adds an inverter Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.inverter.Inverter(name = name))
        return self
    
    def Oneshot(self, name, policy = common.OneShotPolicy.ON_SUCCESSFUL_COMPLETION):
        """
        Adds an oneshot Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.oneshot.OneShot(name = name, policy = policy))
        return self
        
    def StatusToBlackboard(self, name, variableName):
        """
        Adds a status to blackboard Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.statusToBlackboard.StatusToBlackboard(name = name, variable_name = variableName))
        return self
    
    def Timeout(self, name, duration):
        """
        Adds a timeout Decorator to the tree. 
        
        Args:
            name (:class:`str`): The node name.
        """
        
        self._internalNodeHandler(nodes.timeout.Timeout(name = name, duration = duration))
        return self  
#endregion

    def Action(self, actionClass):
        """
        Adds an Action (leaf) to the tree. 
        
        Args:
            name (:class:`str`): The node name.

        Raises:
            SyntaxError (:class:`SyntaxError`): If an Action node is the root of the behaviour.
        """
        
        if self._root is None:
            raise SyntaxError("An action node can't be the root node to a Behaviour tree.")

        if isinstance(self._currentNode, nodes.composite.Composite):
                self._currentNode.add_child(actionClass)
        elif isinstance(self._currentNode, nodes.decorator.Decorator):
            self._currentNode.add_decorated(actionClass)

        self._printNode(actionClass)
        return self