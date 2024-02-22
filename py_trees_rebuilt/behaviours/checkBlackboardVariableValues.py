import typing
import functools

from .. import common
from .. import behaviour
from .. import blackboard

class CheckBlackboardVariableValues(behaviour.Behaviour):
    """
    Apply a logical operation across a set of blackboard variable checks.
    This is non-blocking, so will always tick with status
    :data:`~py_trees.common.Status.FAILURE` or
    :data:`~py_trees.common.Status.SUCCESS`.

    Args:
        checks: a list of comparison checks to apply to blackboard variables
        logical_operator: a logical check to apply across the results of the blackboard variable checks
        name: name of the behaviour
        namespace: optionally store results of the checks (boolean) under this namespace

    .. tip::
        The python `operator module`_ includes many useful logical operators, e.g. operator.xor.

    Raises:
        ValueError if less than two variable checks are specified (insufficient for logical operations)
    """
    def __init__(
        self,
        checks: typing.List[common.ComparisonExpression],
        operator: typing.Callable[[bool, bool], bool],
        name: typing.Union[str, common.Name]=common.Name.AUTO_GENERATED,
        namespace: typing.Optional[str]=None,
    ):
        super().__init__(name=name)
        self.checks = checks
        self.operator = operator
        self.blackboard = self.attach_blackboard_client()
        if len(checks) < 2:
            raise ValueError("Must be at least two variables to operate on [only {} provided]".format(len(checks)))
        for check in self.checks:
            self.blackboard.register_key(
                key=blackboard.Blackboard.key(check.variable),
                access=common.Access.READ
            )
        self.blackboard_results = None
        if namespace is not None:
            self.blackboard_results = self.attach_blackboard_client(namespace=namespace)
            for counter in range(1, len(self.checks) + 1):
                self.blackboard_results.register_key(
                    key=str(counter),
                    access=common.Access.WRITE
                )

    def update(self) -> common.Status:
        """
        Applies comparison checks on each variable and a logical check across the
        complete set of variables.

        Returns:
             :data:`~py_trees.common.Status.FAILURE` if key retrieval or logical checks failed, :data:`~py_trees.common.Status.SUCCESS` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        results = []
        for check in self.checks:
            try:
                value = self.blackboard.get(check.variable)
            except KeyError:
                self.feedback_message = "variable '{}' does not yet exist on the blackboard".format(check.variable)
                return common.Status.FAILURE
            results.append(check.operator(value, check.value))
        if self.blackboard_results is not None:
            for counter in range(1, len(results) + 1):
                self.blackboard_results.set(str(counter), results[counter - 1])
        logical_result = functools.reduce(self.operator, results)
        if logical_result:
            self.feedback_message = "[{}]".format(
                "|".join(["T" if result else "F" for result in results])
            )
            return common.Status.SUCCESS
        else:
            self.feedback_message = "[{}]".format(
                "|".join(["T" if result else "F" for result in results])
            )
            return common.Status.FAILURE