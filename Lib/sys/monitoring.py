"""PyCSL mock for Python's sys.monitoring module — Access and control event monitoring."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def use_tool_id(tool_id: int, name: int, ______None: int) -> int:
    """Mock: Must be called before *tool_id* can be used. *tool_id* must be in the range 0 to 5 inclusive. Raises a :exc:`ValueError`..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clear_tool_id(tool_id: int, ______None: int) -> int:
    """Mock: Unregister all events and callback functions associated with *tool_id*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def free_tool_id(tool_id: int, ______None: int) -> int:
    """Mock: Should be called once a tool no longer requires *tool_id*. Will call :func:`clear_tool_id` before releasing *tool_id*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_tool(tool_id: int, ______str___None: int) -> int:
    """Mock: Returns the name of the tool if *tool_id* is in use, otherwise it returns ``None``. *tool_id* must be in the range 0 to ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_events(tool_id: int, ______int: int) -> int:
    """Mock: Returns the ``int`` representing all the active events."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_events(tool_id: int, event_set: int, ______None: int) -> int:
    """Mock: Activates all events which are set in *event_set*. Raises a :exc:`ValueError` if *tool_id* is not in use."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_local_events(tool_id: int, code: int, ______int: int) -> int:
    """Mock: Returns all the :ref:`local events <monitoring-event-local>` for *code*"""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_local_events(tool_id: int, code: int, event_set: int, ______None: int) -> int:
    """Mock: Activates all the :ref:`local events <monitoring-event-local>` for *code* which are set in *event_set*. Raises a :exc:`V..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def restart_events(_____None: int) -> int:
    """Mock: Enable all the events that were disabled by :data:`sys.monitoring.DISABLE` for all tools."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_callback(tool_id: int, event: int, func: int, ______Callable___None: int) -> int:
    """Mock: Registers the callable *func* for the *event* with the given *tool_id* If another callback was registered for the given ..."""
    return 0
