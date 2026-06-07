# Formal tests for pure_lib/insp — inspect module
from pure_lib.insp import unwrap, signature


#@ requires func >= 0
#@ ensures \result >= 0
def test_unwrap_nonneg(func: int) -> int:
    """unwrap returns non-negative."""
    return unwrap(func)


#@ requires func >= 0
#@ ensures \result >= 0
def test_signature_nonneg(func: int) -> int:
    """signature returns non-negative."""
    return signature(func)
