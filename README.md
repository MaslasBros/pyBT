# Py Trees

----

## About

PyTrees is a python implementation of behaviour trees designed to facilitate the rapid development of medium sized decision making engines for use in fields like robotics. Brief feature list:

* Sequence, Selector, Parallel composites
* Blackboards for data sharing
* Python generators for smarter ticking over the tree graph
* Python decorators for enabling meta behaviours
* Render trees to dot graphs or visualise with ascii graphs on stdout

## Tree Builder

The MaslasBros fork has its own Tree Builder which is essentially a wrapper class on top of the already-existing PyTrees API.

The role of the PyTreeBuilder is to provide the developer with a simple-to-use API that will construct for him a BehaviourTree instance.

> Indendation does not matter on the actual tree building sequence, it's just for tree clarity and easier debugging. 

The PyTreeBuilder can be used as follows:

```python
import pybt.logging as logger
import pybt.builder as pb

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
```

### Glossary

Tree Node Control:

- BehaviourTreeBuilder(printDebugs): creates a BehaviourTreeBuilder, pass True as an argument if you want to print debug logs. 
- Root(): adds the next node to the root of the tree.
- Parent(): adds the next node to the parent of the current node.
- Build(): builds and returns the behaviour tree instance.

Composites:

- Sequence
- Selector
- Parallel

Decorators:

- EternalGuard
- FailureIsRunning
- FailureIsSuccess
- RunningIsFailure
- RunningIsSuccess
- SuccessIsFailure
- SuccessIsRunning
- Inverter
- Oneshot
- StatusToBlackboard
- Timeout

Actions (Leaf Nodes):

- Action(): pass as an argument your custom Behaviour class 

```python
class MyAction(Behaviour):
    def __init__(self, name):
        super(MyAction, self).__init__(name)
        pass

    def setup(self):
        self.logger.debug("%s[MyAction::setup()]" % self.name)

    def initialise(self):
        self.logger.debug("%s[MyAction::initialise()]" % self.name)

    def update(self):
        return Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug("%s[MyAction::terminate().terminate()][%s->%s]" % (self.name, self.status, new_status))
```

## Docs and Demos

Core API documentation (also includes some explanation concerning the demo scripts):
If you're really looking for something more edifying than hello world examples, walk through the [ros tutorials](https://py-trees-ros-tutorials.readthedocs.io/en/release-2.0.x/index.html) which incrementally step through the process of building a scenario handling layer for a robot.

There are also runtime visualisation tools - refer to the [py_trees_ros_viewer/README](https://github.com/splintered-reality/py_trees_ros_viewer/blob/devel/README.md) as an example implementation of the underlying [py_trees_js](https://github.com/splintered-reality/py_trees_js) library.

## Compatibility

This module is compatible with any version equall or greater than [IronPython 3.4.1](https://ironpython.net/) and its Python equivalent which is Python 3.4.

*__Note__: IronPython3.4.1 support some Python 3.6 features which are listed in its website and [repository](https://github.com/IronLanguages/ironpython3).*

## Dependencies

* IronPython dependencies 
  * [IronPython 3.4.1 site](https://ironpython.net/)
  * [IronPython 3.4.1 repository](https://github.com/IronLanguages/ironpython3)
* [PyTrees 2.1.6 repository](https://github.com/splintered-reality/py_trees/tree/release/2.1.x)
