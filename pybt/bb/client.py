import typing
import uuid
import operator
import itertools

from .. import common
from .. import utilities

from .blackboard import Blackboard
from ._internal.activityType import ActivityType
from ._internal.activityItem import ActivityItem
from ._internal.keyMetaData import KeyMetaData
from ._internal.IntermediateVariableFetcher import IntermediateVariableFetcher

class Client(object):
    """
    Client to the key-value store for sharing data between behaviours.

    **Examples**

    Blackboard clients will accept a user-friendly name or create one
    for you if none is provided. Regardless of what name is chosen, clients
    are always uniquely identified via a uuid generated on construction.

    .. code-block:: python

        provided = py_trees.blackboard.Client(name="Provided")
        print(provided)
        generated = py_trees.blackboard.Client()
        print(generated)

    .. figure:: images/blackboard_client_instantiation.png
       :align: center

       Client Instantiation

    Register read/write access for keys on the blackboard. Note, registration is
    not initialisation.

    .. code-block:: python

        blackboard = py_trees.blackboard.Client(name="Client")
        blackboard.register_key(key="foo", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="bar", access=py_trees.common.Access.READ)
        blackboard.foo = "foo"
        print(blackboard)

    .. figure:: images/blackboard_read_write.png
       :align: center

       Variable Read/Write Registration

    Keys and clients can make use of namespaces, designed by the '/' char. Most
    methods permit a flexible expression of either relative or absolute names.

    .. code-block:: python

        blackboard = py_trees.blackboard.Client(name="Global")
        parameters = py_trees.blackboard.Client(name="Parameters", namespace="parameters")

        blackboard.register_key(key="foo", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="/bar", access=py_trees.common.Access.WRITE)
        blackboard.register_key(key="/parameters/default_speed", access=py_trees.common.Access.WRITE)
        parameters.register_key(key="aggressive_speed", access=py_trees.common.Access.WRITE)

        blackboard.foo = "foo"
        blackboard.bar = "bar"
        blackboard.parameters.default_speed = 20.0
        parameters.aggressive_speed = 60.0

        miss_daisy = blackboard.parameters.default_speed
        van_diesel = parameters.aggressive_speed

        print(blackboard)
        print(parameters)

    .. figure:: images/blackboard_namespaces.png
       :align: center

       Namespaces and Namespaced Clients


    Disconnected instances will discover the centralised
    key-value store.

    .. code-block:: python

        def check_foo():
            blackboard = py_trees.blackboard.Client(name="Reader")
            blackboard.register_key(key="foo", access=py_trees.common.Access.READ)
            print("Foo: {}".format(blackboard.foo))


        blackboard = py_trees.blackboard.Client(name="Writer")
        blackboard.register_key(key="foo", access=py_trees.common.Access.WRITE)
        blackboard.foo = "bar"
        check_foo()

    To respect an already initialised key on the blackboard:

    .. code-block:: python

        blackboard = Client(name="Writer")
        blackboard.register_key(key="foo", access=py_trees.common.Access.READ)
        result = blackboard.set("foo", "bar", overwrite=False)

    Store complex objects on the blackboard:

    .. code-block:: python

        class Nested(object):
            def __init__(self):
                self.foo = None
                self.bar = None

            def __str__(self):
                return str(self.__dict__)


        writer = py_trees.blackboard.Client(name="Writer")
        writer.register_key(key="nested", access=py_trees.common.Access.WRITE)
        reader = py_trees.blackboard.Client(name="Reader")
        reader.register_key(key="nested", access=py_trees.common.Access.READ)

        writer.nested = Nested()
        writer.nested.foo = "I am foo"
        writer.nested.bar = "I am bar"

        foo = reader.nested.foo
        print(writer)
        print(reader)

    .. figure:: images/blackboard_nested.png
       :align: center

    Log and display the activity stream:

    .. code-block:: python

        py_trees.blackboard.Blackboard.enable_activity_stream(maximum_size=100)
        reader = py_trees.blackboard.Client(name="Reader")
        reader.register_key(key="foo", access=py_trees.common.Access.READ)
        writer = py_trees.blackboard.Client(name="Writer")
        writer.register_key(key="foo", access=py_trees.common.Access.WRITE)
        writer.foo = "bar"
        writer.foo = "foobar"
        unused_result = reader.foo
        print(py_trees.display.unicode_blackboard_activity_stream())
        py_trees.blackboard.Blackboard.activity_stream.clear()

    .. figure:: images/blackboard_activity_stream.png
       :align: center

    Display the blackboard on the console, or part thereof:

    .. code-block:: python

        writer = py_trees.blackboard.Client(name="Writer")
        for key in {"foo", "bar", "dude", "dudette"}:
            writer.register_key(key=key, access=py_trees.common.Access.WRITE)

        reader = py_trees.blackboard.Client(name="Reader")
        for key in {"foo", "bar"}:
            reader.register_key(key="key", access=py_trees.common.Access.READ)

        writer.foo = "foo"
        writer.bar = "bar"
        writer.dude = "bob"

        # all key-value pairs
        print(py_trees.display.unicode_blackboard())
        # various filtered views
        print(py_trees.display.unicode_blackboard(key_filter={"foo"}))
        print(py_trees.display.unicode_blackboard(regex_filter="dud*"))
        print(py_trees.display.unicode_blackboard(client_filter={reader.unique_identifier}))
        # list the clients associated with each key
        print(py_trees.display.unicode_blackboard(display_only_key_metadata=True))

    .. figure:: images/blackboard_display.png
       :align: center

    Behaviours are not automagically connected to the blackboard but you may
    manually attach one or more clients so that associations between behaviours
    and variables can be tracked - this is very useful for introspection and
    debugging.

    Creating a custom behaviour with blackboard variables:

    .. code-block:: python

        class Foo(py_trees.behaviour.Behaviour):

            def __init__(self, name):
                super().__init__(name=name)
                self.blackboard = self.attach_blackboard_client(name="Foo Global")
                self.parameters = self.attach_blackboard_client(name="Foo Params", namespace="foo_parameters_")
                self.state = self.attach_blackboard_client(name="Foo State", namespace="foo_state_")

                # create a key 'foo_parameters_init' on the blackboard
                self.parameters.register_key("init", access=py_trees.common.Access.READ)
                # create a key 'foo_state_number_of_noodles' on the blackboard
                self.state.register_key("number_of_noodles", access=py_trees.common.Access.WRITE)

            def initialise(self):
                self.state.number_of_noodles = self.parameters.init

            def update(self):
                self.state.number_of_noodles += 1
                self.feedback_message = self.state.number_of_noodles
                if self.state.number_of_noodles > 5:
                    return py_trees.common.Status.SUCCESS
                else:
                    return py_trees.common.Status.RUNNING


        # could equivalently do directly via the Blackboard static methods if
        # not interested in tracking / visualising the application configuration
        configuration = py_trees.blackboard.Client(name="App Config")
        configuration.register_key("foo_parameters_init", access=py_trees.common.Access.WRITE)
        configuration.foo_parameters_init = 3

        foo = Foo(name="The Foo")
        for i in range(1, 8):
            foo.tick_once()
            print("Number of Noodles: {}".format(foo.feedback_message))

    Rendering a dot graph for a behaviour tree, complete with blackboard variables:

    .. code-block:: python

        # in code
        py_trees.display.render_dot_tree(py_trees.demos.blackboard.create_root())
        # command line tools
        py-trees-render --with-blackboard-variables py_trees.demos.blackboard.create_root

    .. graphviz:: dot/demo-blackboard.dot
       :align: center
       :caption: Tree with Blackboard Variables

    And to demonstrate that it doesn't become a tangled nightmare at scale, an example of
    a more complex tree:

    .. graphviz:: dot/blackboard-with-variables.dot
       :align: center
       :caption: A more complex tree

    Debug deeper with judicious application of the tree, blackboard and activity stream
    display methods around the tree tick (refer to
    :class:`py_trees.visitors.DisplaySnapshotVisitor` for examplar code):

    .. figure:: images/blackboard_trees.png
       :align: center

       Tree level debugging

    .. seealso::

       * :ref:`py-trees-demo-blackboard <py-trees-demo-blackboard-program>`
       * :ref:`py-trees-demo-namespaces <py-trees-demo-blackboard-namespaces-program>`
       * :ref:`py-trees-demo-remappings <py-trees-demo-blackboard-remappings-program>`
       * :class:`py_trees.visitors.DisplaySnapshotVisitor`
       * :class:`py_trees.behaviours.SetBlackboardVariable`
       * :class:`py_trees.behaviours.UnsetBlackboardVariable`
       * :class:`py_trees.behaviours.CheckBlackboardVariableExists`
       * :class:`py_trees.behaviours.WaitForBlackboardVariable`
       * :class:`py_trees.behaviours.CheckBlackboardVariableValue`
       * :class:`py_trees.behaviours.WaitForBlackboardVariableValue`

    Attributes:
        name (str): client's convenient, but not necessarily unique identifier
        namespace (str): apply this as a prefix to any key/variable name operations
        unique_identifier (uuid.UUID): client's unique identifier
        read (typing.Set[str]): set of absolute key names with read access
        write (typing.Set[str]): set of absolute key names with write access
        exclusive (typing.Set[str]): set of absolute key names with exclusive write access
        required (typing.Set[str]): set of absolute key names required to have data present
        remappings (typing.Dict[str, str]: client key names with blackboard remappings
        namespaces (typing.Set[str]: a cached list of namespaces this client accesses
    """
    def __init__(
            self, *,
            name: str=None,
            namespace: str=None):
        """
        Args:
            name: client's convenient identifier (stringifies the uuid if None)
            namespace: prefix to apply to key/variable name operations
            read: list of keys for which this client has read access
            write: list of keys for which this client has write access
            exclusive: list of keys for which this client has exclusive write access

        Raises:
            TypeError: if the provided name is not of type str
            ValueError: if the unique identifier has already been registered
        """

        # unique identifier
        super().__setattr__("unique_identifier", uuid.uuid4())
        if super().__getattribute__("unique_identifier") in Blackboard.clients.keys():
            raise ValueError("this unique identifier has already been registered")

        # name
        if name is None or not name:
            name = utilities.truncate(
                original=str(super().__getattribute__("unique_identifier")).replace('-', '_'),
                length=7
            )
            super().__setattr__("name", name)
        else:
            if not isinstance(name, str):
                raise TypeError("provided name is not of type str [{}]".format(type(name)))
            super().__setattr__("name", name)

        # namespaces
        namespace = "" if namespace is None else namespace
        if not namespace.startswith(Blackboard.separator):
            namespace = Blackboard.separator + namespace
        super().__setattr__("namespace", namespace)
        super().__setattr__("namespaces", set())

        super().__setattr__("read", set())
        super().__setattr__("write", set())
        super().__setattr__("exclusive", set())
        super().__setattr__("required", set())
        super().__setattr__("remappings", {})
        Blackboard.clients[
            super().__getattribute__("unique_identifier")
        ] = self.name

    def id(self) -> uuid.UUID:
        """
        The unique identifier for this client.

        Returns:
            The uuid.UUID object
        """
        return super().__getattribute__("unique_identifier")

    def __setattr__(self, name: str, value: typing.Any):
        """
        Convenience attribute style referencing with checking against
        permissions.

        Raises:
            AttributeError: if the client does not have write access to the variable
        """
        # print("__setattr__ [{}][{}]".format(name, value))
        name = Blackboard.absolute_name(super().__getattribute__("namespace"), name)
        if (
            (name not in super().__getattribute__("write")) and
            (name not in super().__getattribute__("exclusive"))
        ):
            if Blackboard.activity_stream is not None:
                Blackboard.activity_stream.push(
                    self._generate_activity_item(name, ActivityType.ACCESS_DENIED)
                )
            raise AttributeError("client '{}' does not have write access to '{}'".format(self.name, name))
        remapped_name = super().__getattribute__("remappings")[name]
        if Blackboard.activity_stream is not None:
            if remapped_name in Blackboard.storage.keys():
                Blackboard.activity_stream.push(
                    self._generate_activity_item(
                        key=remapped_name,
                        activity_type=ActivityType.WRITE,
                        previous_value=Blackboard.storage[remapped_name],
                        current_value=value
                    )
                )
            else:
                Blackboard.activity_stream.push(
                    self._generate_activity_item(
                        key=remapped_name,
                        activity_type=ActivityType.INITIALISED,
                        current_value=value
                    )
                )
        Blackboard.storage[remapped_name] = value

    def __getattr__(self, name: str):
        """
        Convenience attribute style referencing with checking against
        permissions.

        Raises:
            AttributeError: if the client does not have read access to the variable
            KeyError: if the variable does not yet exist on the blackboard
        """
        # print("__getattr__ [{}]".format(name))
        name = Blackboard.absolute_name(super().__getattribute__("namespace"), name)
        read_key = False
        write_key = False
        if name in super().__getattribute__("read"):
            read_key = True
        elif name in super().__getattribute__("write"):
            write_key = True
        elif name in super().__getattribute__("exclusive"):
            write_key = True
        else:
            if name in super().__getattribute__("namespaces"):
                return IntermediateVariableFetcher(blackboard=self, namespace=name)
            if Blackboard.activity_stream is not None:
                Blackboard.activity_stream.push(
                    self._generate_activity_item(name, ActivityType.ACCESS_DENIED)
                )
            raise AttributeError("client '{}' does not have read/write access to '{}'".format(self.name, name))
        remapped_name = super().__getattribute__("remappings")[name]
        try:
            if write_key:
                if Blackboard.activity_stream is not None:
                    if utilities.is_primitive(Blackboard.storage[remapped_name]):
                        activity_type = ActivityType.READ
                    else:  # could be a nested class object being accessed to write an attribute
                        activity_type = ActivityType.ACCESSED
                    Blackboard.activity_stream.push(
                        self._generate_activity_item(
                            key=remapped_name,
                            activity_type=activity_type,
                            current_value=Blackboard.storage[remapped_name],
                        )
                    )
                return Blackboard.storage[remapped_name]
            if read_key:
                if Blackboard.activity_stream is not None:
                    Blackboard.activity_stream.push(
                        self._generate_activity_item(
                            key=remapped_name,
                            activity_type=ActivityType.READ,
                            current_value=Blackboard.storage[remapped_name],
                        )
                    )
                return Blackboard.storage[remapped_name]
        except KeyError as e:
            if Blackboard.activity_stream is not None:
                Blackboard.activity_stream.push(
                    self._generate_activity_item(remapped_name, ActivityType.NO_KEY)
                )
            raise KeyError("client '{}' tried to access '{}' but it does not yet exist on the blackboard".format(self.name, remapped_name)) from e

    def set(self, name: str, value: typing.Any, overwrite: bool=True) -> bool:
        """
        Set, conditionally depending on whether the variable already exists or otherwise.

        This is most useful when initialising variables and multiple elements
        seek to do so. A good policy to adopt for your applications in these situations is
        a first come, first served policy. Ensure global configuration has the first
        opportunity followed by higher priority behaviours in the tree and so forth.
        Lower priority behaviours would use this to respect the pre-configured
        setting and at most, just validate that it is acceptable to the functionality
        of it's own behaviour.

        Args:
            name: name of the variable to set
            value: value of the variable to set
            overwrite: do not set if the variable already exists on the blackboard

        Returns:
            success or failure (overwrite is False and variable already set)

        Raises:
            AttributeError: if the client does not have write access to the variable
            KeyError: if the variable does not yet exist on the blackboard
        """
        name = Blackboard.absolute_name(super().__getattribute__("namespace"), name)
        name_components = name.split('.')
        key = name_components[0]
        key_attributes = '.'.join(name_components[1:])
        if (
            (key not in super().__getattribute__("write")) and
            (key not in super().__getattribute__("exclusive"))
        ):
            if Blackboard.activity_stream is not None:
                Blackboard.activity_stream.push(
                    self._generate_activity_item(key, ActivityType.ACCESS_DENIED)
                )
            raise AttributeError("client '{}' does not have write access to '{}'".format(self.name, name))
        remapped_key = super().__getattribute__("remappings")[key]
        if not overwrite:
            if remapped_key in Blackboard.storage:
                if Blackboard.activity_stream is not None:
                    Blackboard.activity_stream.push(
                        self._generate_activity_item(
                            key=remapped_key,
                            activity_type=ActivityType.NO_OVERWRITE,
                            current_value=Blackboard.storage[remapped_key])
                    )
                return False
        if not key_attributes:
            setattr(self, key, value)
            return True
        else:
            blackboard_object = getattr(self, key)
            try:
                setattr(blackboard_object, key_attributes, value)
                return True
            except AttributeError:  # when the object doesn't have the attributes
                return False

    def exists(self, name: str) -> bool:
        """
        Check if the specified variable exists on the blackboard.

        Args:
            name: name of the variable to get, can be nested, e.g. battery.percentage

        Raises:
            AttributeError: if the client does not have read access to the variable
        """
        try:
            unused_value = self.get(name)
            return True
        except KeyError:
            return False

    def absolute_name(self, key: str) -> str:
        """
        Generate the fully qualified key name for this key.

        .. code-block:: python

            blackboard = Client(name="FooBar", namespace="foo")
            blackboard.register_key(key="bar", access=py_trees.common.Access.READ)
            print("{}".format(blackboard.absolute_name("bar")))  # "/foo/bar"

        Args:
            key: name of the key

        Returns:
            the absolute name

        Raises:
            KeyError: if the key is not registered with this client
        """
        if not self.is_registered(key=key):
            raise KeyError("key '{}' is not in namespace '{}'".format(
                key, super().__getattribute__("namespace"))
            )
        return Blackboard.absolute_name(
            super().__getattribute__("namespace"),
            key
        )

    def get(self, name: str) -> typing.Any:
        """
        Method based accessor to the blackboard variables (as opposed to simply using
        '.<name>').

        Args:
            name: name of the variable to get, can be nested, e.g. battery.percentage

        Raises:
            AttributeError: if the client does not have read access to the variable
            KeyError: if the variable or it's nested attributes do not yet exist on the blackboard
        """
        # key attributes is an empty string if not a nested variable name
        name_components = name.split('.')
        key = name_components[0]
        key_attributes = '.'.join(name_components[1:])
        value = getattr(self, key)  # will run through client access checks in __getattr__
        if key_attributes:
            try:
                value = operator.attrgetter(key_attributes)(value)
            except AttributeError:
                raise KeyError("Key exists, but does not have the specified nested attributes [{}]".format(name))
        return value

    def unset(self, key: str):
        """
        For when you need to completely remove a blackboard variable (key-value pair),
        this provides a convenient helper method.

        Args:
            key: name of the variable to remove

        Returns:
            True if the variable was removed, False if it was already absent
        """
        key = Blackboard.absolute_name(super().__getattribute__("namespace"), key)
        remapped_key = super().__getattribute__("remappings")[key]
        if Blackboard.activity_stream is not None:
            Blackboard.activity_stream.push(
                self._generate_activity_item(remapped_key, ActivityType.UNSET)
            )
        # Three means of handling a non-existent key - 1) raising a KeyError, 2) catching
        # the KeyError and passing, 3) catch the KeyError and return True/False.
        # Option 1) is inconvenient - requires a redundant try/catch 99% of cases
        # Option 2) hides information - bad
        # Option 3) no extra code necessary and information is there if desired
        try:
            del Blackboard.storage[remapped_key]
            return True
        except KeyError:
            return False

    def _generate_activity_item(self, key, activity_type, previous_value=None, current_value=None):
        return ActivityItem(
            key=key,
            client_name=super().__getattribute__("name"),
            client_id=super().__getattribute__("unique_identifier"),
            # use strings here, so displaying the streams is agnostic of the enum
            activity_type=activity_type.value,
            previous_value=previous_value,
            current_value=current_value
        )

    def _update_namespaces(self, added_key=None):
        """
        Update the namespace cache.

        Args:
            added_key: hint on the most recent operation to enable an smart check/rebuild
        """
        if added_key is not None:
            namespace = added_key.rsplit("/", 1)[0]
            while namespace:
                super().__getattribute__("namespaces").add(namespace)
                namespace = namespace.rsplit("/", 1)[0]
        else:
            # completely rebuild
            super().__getattribute__("namespaces").clear()
            for key in itertools.chain(
                super().__getattribute__("read"),
                super().__getattribute__("write"),
                super().__getattribute__("exclusive")
            ):
                namespace = key.rsplit("/", 1)[0]
                while namespace:
                    super().__getattribute__("namespaces").add(namespace)
                    namespace = namespace.rsplit("/", 1)[0]

    def __str__(self):
        indent = "  "
        s = "Blackboard Client" + "\n"
        s += indent + "Client Data" + "\n"
        keys = ["name", "namespace", "unique_identifier", "read", "write", "exclusive"]
        s += self._stringify_key_value_pairs(keys, self.__dict__, 2 * indent)
        keys = {k for k, v in self.remappings.items() if k != v}
        if keys:
            s +=  indent + "Remappings"  + "\n"
            s += self._stringify_key_value_pairs(
                keys=keys,
                key_value_dict=self.remappings,
                indent=2 * indent
            )
        s += indent + "Variables" + "\n"
        keys = self.remappings.values()
        s += self._stringify_key_value_pairs(keys, Blackboard.storage, 2 * indent)
        return s

    def _stringify_key_value_pairs(self, keys, key_value_dict, indent, separator=":"):
        s = ""
        max_length = 0
        for key in keys:
            max_length = len(key) if len(key) > max_length else max_length
        for key in keys:
            try:
                value = key_value_dict[key]
                lines = ('{0}'.format(value)).split('\n')
                if len(lines) > 1:
                    s += indent + '{0: <{1}}'.format(key, max_length + 1) + separator + "\n"
                    for line in lines:
                        s += indent + "  {0}\n".format(line)
                else:
                    s += indent + '{0: <{1}}'.format(key, max_length + 1) + separator + " " + '{0}\n'.format(value)
            except KeyError:
                s += indent + '{0: <{1}}'.format(key, max_length + 1) + separator + " " + "-\n"
        return s

    def unregister(self, clear: bool=True):
        """
        Unregister this blackboard client and if requested, clear key-value pairs if this
        client is the last user of those variables.

        Args:
            clear: remove key-values pairs from the blackboard
        """
        self.unregister_all_keys(clear)
        del Blackboard.clients[super().__getattribute__("unique_identifier")]

    def unregister_all_keys(self, clear: bool=True):
        """
        Unregister all keys currently registered by this blackboard client and if requested,
        clear key-value pairs if this client is the last user of those variables.

        Args:
            clear: remove key-values pairs from the blackboard
        """
        for key in itertools.chain(set(self.read), set(self.write), set(self.exclusive)):
            self.unregister_key(key=key, clear=clear, update_namespace_cache=False)
        self._update_namespaces()

    def verify_required_keys_exist(self):
        """
        En-masse check of existence on the blackboard for all keys that were hitherto
        registered as 'required'.

        Raises: KeyError if any of the required keys do not exist on the blackboard
        """
        absent = set()
        for key in super().__getattribute__("required"):
            if not self.exists(key):
                absent.add(key)
        if absent:
            raise KeyError("keys required, but not yet on the blackboard [{}]".format(absent))

    def is_registered(
        self,
        key: str,
        access: typing.Union[None, common.Access]=None
    ) -> bool:
        """
        Check to see if the specified key is registered.

        Args:
           key: in either relative or absolute form
           access: access property, if None, just checks for registration, regardless of property

        Returns:
           if registered, True otherwise False
        """
        absolute_name = Blackboard.absolute_name(
            super().__getattribute__("namespace"),
            key
        )
        if access == common.Access.READ:
            return absolute_name in self.read
        elif access == common.Access.WRITE:
            return absolute_name in self.write
        elif access == common.Access.EXCLUSIVE_WRITE:
            return absolute_name in self.exclusive
        else:
            return absolute_name in self.read | self.write | self.exclusive

    def register_key(
            self,
            key: str,
            access: common.Access,
            required: bool=False,
            remap_to: str=None,
    ):
        """
        Register a key on the blackboard to associate with this client.

        Args:
            key: key to register
            access: access level (read, write, exclusive write)
            required: if true, check key exists when calling
                :meth:`~verify_required_keys_exist`
            remap_to: remap the key to this location on the blackboard

        Note the remap simply changes the storage location. From the perspective of
        the client, access via the specified 'key' remains the same.

        Raises:
            AttributeError if exclusive write access is requested, but write access has already been given to another client
            TypeError if the access argument is of incorrect type
        """
        key = Blackboard.absolute_name(super().__getattribute__("namespace"), key)
        super().__getattribute__("remappings")[key] = key if remap_to is None else remap_to
        remapped_key = super().__getattribute__("remappings")[key]
        if access == common.Access.READ:
            super().__getattribute__("read").add(key)
            Blackboard.metadata.setdefault(remapped_key, KeyMetaData())
            Blackboard.metadata[remapped_key].read.add(super().__getattribute__("unique_identifier"))
        elif access == common.Access.WRITE:
            conflicts = set()
            try:
                for unique_identifier in Blackboard.metadata[remapped_key].exclusive:
                    conflicts.add(Blackboard.clients[unique_identifier])
                    if conflicts:
                        raise AttributeError("'{}' requested write on key '{}', but this key already associated with an exclusive writer[{}]".format(
                            super().__getattribute__("name"),
                            remapped_key,
                            conflicts)
                        )
            except KeyError:
                pass  # no readers or writers on the key yet
            super().__getattribute__("write").add(key)
            Blackboard.metadata.setdefault(remapped_key, KeyMetaData())
            Blackboard.metadata[remapped_key].write.add(super().__getattribute__("unique_identifier"))
        elif access == common.Access.EXCLUSIVE_WRITE:
            try:
                key_metadata = Blackboard.metadata[remapped_key]
                conflicts = set()
                for unique_identifier in (key_metadata.write | key_metadata.exclusive):
                    conflicts.add(Blackboard.clients[unique_identifier])
                if conflicts:
                    raise AttributeError("'{}' requested exclusive write on key '{}', but this key is already associated [{}]".format(
                        super().__getattribute__("name"),
                        remapped_key,
                        conflicts)
                    )
            except KeyError:
                pass  # no readers or writers on the key yet
            super().__getattribute__("exclusive").add(key)
            Blackboard.metadata.setdefault(remapped_key, KeyMetaData())
            Blackboard.metadata[remapped_key].exclusive.add(super().__getattribute__("unique_identifier"))
        else:
            raise TypeError("access argument is of incorrect type [{}]".format(type(access)))
        if required:
            super().__getattribute__("required").add(key)
        self._update_namespaces(added_key=key)

    def unregister_key(
            self,
            key: str,
            clear: bool=True,
            update_namespace_cache: bool=True):
        """
        Unegister a key associated with this client.

        Args:
            key: key to unregister
            clear: remove key-values pairs from the blackboard
            update_namespace_cache: disable if you are batching

        A method that batches calls to this method is :meth:`unregister_all_keys()`.

        Raises:
            KeyError if the key has not been previously registered
        """
        key = Blackboard.absolute_name(super().__getattribute__("namespace"), key)
        remapped_key = super().__getattribute__("remappings")[key]
        super().__getattribute__("read").discard(key)  # doesn't throw exceptions if it not present
        super().__getattribute__("write").discard(key)
        super().__getattribute__("exclusive").discard(key)
        Blackboard.metadata[remapped_key].read.discard(super().__getattribute__("unique_identifier"))
        Blackboard.metadata[remapped_key].write.discard(super().__getattribute__("unique_identifier"))
        Blackboard.metadata[remapped_key].exclusive.discard(super().__getattribute__("unique_identifier"))
        if (
            (not Blackboard.metadata[remapped_key].read) and
            (not Blackboard.metadata[remapped_key].write) and
            (not Blackboard.metadata[remapped_key].exclusive)
        ):
            del Blackboard.metadata[remapped_key]
            if clear:
                try:
                    del Blackboard.storage[remapped_key]
                except KeyError:
                    pass  # perfectly legitimate for a registered key to not exist on the blackboard
        del super().__getattribute__("remappings")[key]
        if update_namespace_cache:
            self._update_namespaces()