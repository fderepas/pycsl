"""PyCSL mock for Python's gc module — Interface to the cycle-detecting garbage collector."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def enable() -> int:
    """Mock: Enable automatic garbage collection."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def disable() -> int:
    """Mock: Disable automatic garbage collection."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isenabled() -> int:
    """Mock: Return ``True`` if automatic collection is enabled."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def collect(generation: int) -> int:
    """Mock: With no arguments, run a full collection.  The optional argument *generation* may be an integer specifying which generat..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_debug(flags: int) -> int:
    """Mock: Set the garbage collection debugging flags. Debugging information will be written to ``sys.stderr``.  See below for a li..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_debug() -> int:
    """Mock: Return the debugging flags currently set."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_objects(generation: int) -> int:
    """Mock: Returns a list of all objects tracked by the collector, excluding the list returned. If *generation* is not ``None``, re..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_stats() -> int:
    """Mock: Return a list of three per-generation dictionaries containing collection statistics since interpreter start.  The number..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_threshold(threshold0: int, threshold1: int, threshold2: int) -> int:
    """Mock: Set the garbage collection thresholds (the collection frequency). Setting *threshold0* to zero disables collection. The ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_count() -> int:
    """Mock: Return the current collection  counts as a tuple of ``(count0, count1, count2)``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_threshold() -> int:
    """Mock: Return the current collection thresholds as a tuple of ``(threshold0, threshold1, threshold2)``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_referrers() -> int:
    """Mock: Return the list of objects that directly refer to any of objs. This function will only locate those containers which sup..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_referents() -> int:
    """Mock: Return a list of objects directly referred to by any of the arguments. The referents returned are those objects visited ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_tracked(obj: int) -> int:
    """Mock: Returns ``True`` if the object is currently tracked by the garbage collector, ``False`` otherwise.  As a general rule, i..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_finalized(obj: int) -> int:
    """Mock: Returns ``True`` if the given object has been finalized by the garbage collector, ``False`` otherwise. :: >>> x = None >..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def freeze() -> int:
    """Mock: Freeze all the objects tracked by the garbage collector; move them to a permanent generation and ignore them in all the ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unfreeze() -> int:
    """Mock: Unfreeze the objects in the permanent generation, put them back into the oldest generation. .. versionadded:: 3.7"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_freeze_count() -> int:
    """Mock: Return the number of objects in the permanent generation. .. versionadded:: 3.7"""
    return 0
