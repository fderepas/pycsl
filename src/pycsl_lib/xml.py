"""PyCSL mock for Python's xml module — Package containing XML processing modules."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_valid_name(name: int) -> int:
    """Mock: Return ``True`` if the string is a valid element or attribute name, ``False`` otherwise. Almost all characters are permi..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_valid_text(data: int) -> int:
    """Mock: Return ``True`` if the string is a sequence of legal XML 1.0 characters, ``False`` otherwise. Almost all characters are ..."""
    return 0
