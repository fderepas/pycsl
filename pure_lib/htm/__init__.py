# Pure model for html — HTML escaping utilities
# Models escape/unescape as length-preserving-or-growing transforms.


#@ requires length >= 0
#@ ensures \result >= length
def escape(length: int) -> int:
    """Escape HTML special chars. Output length >= input length."""
    return length


#@ requires length >= 0
#@ ensures \result >= 0
#@ ensures \result <= length
def unescape(length: int) -> int:
    """Unescape HTML entities. Output length <= input length."""
    return length
