import typing

from .. import blackboard as bb

class IntermediateVariableFetcher(object):
    def __init__(self, blackboard, namespace):
        super().__setattr__("blackboard", blackboard)
        super().__setattr__("namespace", namespace)

    def __getattr__(self, name: str):
        # print("Fetcher:__getattr__ [{}]".format(name))
        name = bb.Blackboard.absolute_name(self.namespace, name)
        return self.blackboard.get(name)

    def __setattr__(self, name: str, value: typing.Any):
        # print("Fetcher:__setattr__ [{}][{}]".format(name, value))
        name = bb.Blackboard.absolute_name(self.namespace, name)
        return self.blackboard.set(name, value)