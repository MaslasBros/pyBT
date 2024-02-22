import uuid
import typing

class ActivityItem(object):
    """
    Recorded data pertaining to activity on the blackboard.

    Args:
        key: name of the variable on the blackboard
        client_name: convenient name of the client performing the operation
        client_id: unique id of the client performing the operation
        activity_type: type of activity
        previous_value: of the given key (None if this field is not relevant)
        current_value: current value for the given key (None if this field is not relevant)
    """
    def __init__(
            self,
            key,
            client_name: str,
            client_id: uuid.UUID,
            activity_type: str,
            previous_value: typing.Any=None,
            current_value: typing.Any=None):
        # TODO validity checks for values passed/not passed on the
        # respective activity types. Note: consider using an enum
        # for 'no value here' since None is a perfectly acceptable
        # value for a key
        self.key = key
        self.client_name = client_name
        self.client_id = client_id
        self.activity_type = activity_type
        self.previous_value = previous_value
        self.current_value = current_value