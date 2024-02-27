import typing
import copy

from .. import common
from .. import behaviour

class StatusSequence(behaviour.Behaviour):
    """
    Cycle through the specified sequence of states.

    Args:
        name: name of the behaviour
        sequence: list of status values to cycle through
        eventually: status to use eventually, None to re-cycle the sequence
    """
    def __init__(
            self,
            name: str,
            sequence: typing.List[common.Status],
            eventually: typing.Optional[common.Status]
    ):
        super(StatusSequence, self).__init__(name)
        self.sequence = sequence
        self.eventually = eventually
        self.current_sequence = copy.copy(sequence)

    def update(self):
        if self.current_sequence:
            status = self.current_sequence.pop(0)
        elif self.eventually is not None:
            status = self.eventually
        else:
            self.current_sequence = copy.copy(self.sequence)
            status = self.current_sequence.pop(0)
        return status