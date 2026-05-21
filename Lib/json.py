"""PyCSL mock for Python's json module — Encode and decode the JSON format."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def dump(obj: int, fp: int, skipkeys: int, ensure_ascii: int, __check_circular: int, allow_nan: int, cls: int) -> int:
    """Mock: Serialize *obj* as a JSON formatted stream to *fp* (a ``.write()``-supporting :term:`file-like object`) using this :ref:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dumps(obj: int, skipkeys: int, ensure_ascii: int, __check_circular: int, allow_nan: int, cls: int, __indent: int) -> int:
    """Mock: Serialize *obj* to a JSON formatted :class:`str` using this :ref:`conversion table <py-to-json-table>`.  The arguments h..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def load(fp: int, cls: int, object_hook: int, parse_float: int, __parse_int: int, parse_constant: int, __object_pairs_hook: int) -> int:
    """Mock: Deserialize *fp* to a Python object using the :ref:`JSON-to-Python conversion table <json-to-py-table>`. :param fp: A ``..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def loads(s: int, cls: int, object_hook: int, parse_float: int, parse_int: int, parse_constant: int, object_pairs_hook: int) -> int:
    """Mock: Identical to :func:`load`, but instead of a file-like object, deserialize *s* (a :class:`str`, :class:`bytes` or :class:..."""
    return 0
