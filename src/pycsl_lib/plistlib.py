"""PyCSL mock for Python's plistlib module — Generate and parse Apple plist files."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def load(fp: int, fmt: int, dict_type: int, aware_datetime: int) -> int:
    """Mock: Read a plist file. *fp* should be a readable and binary file object. Return the unpacked root object (which usually is a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def loads(data: int, fmt: int, dict_type: int, aware_datetime: int) -> int:
    """Mock: Load a plist from a bytes or string object. See :func:`load` for an explanation of the keyword arguments. .. versionadde..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def dump(value: int, fp: int, fmt: int, sort_keys: int, skipkeys: int, aware_datetime: int) -> int:
    """Mock: Write *value* to a plist file. *fp* should be a writable, binary file object. The *fmt* argument specifies the format of..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dumps(value: int, fmt: int, sort_keys: int, skipkeys: int, aware_datetime: int) -> int:
    """Mock: Return *value* as a plist-formatted bytes object. See the documentation for :func:`dump` for an explanation of the keywo..."""
    return 0
