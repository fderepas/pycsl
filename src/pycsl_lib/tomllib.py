"""PyCSL mock for Python's tomllib module — Parse TOML files."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def load(fp: int, parse_float: int) -> int:
    """Mock: Read a TOML file. The first argument should be a readable and binary file object. Return a :class:`dict`. Convert TOML t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def loads(s: int, parse_float: int) -> int:
    """Mock: Load TOML from a :class:`str` object. Return a :class:`dict`. Convert TOML types to Python using this :ref:`conversion t..."""
    return 0
