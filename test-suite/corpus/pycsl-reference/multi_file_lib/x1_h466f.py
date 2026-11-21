"""Helper for corpus 7265 (route #466): one half of a circular import (`g` is bound
AFTER the import of the other half, which imports `g` from this partially initialised module)."""
from multi_file_lib.x1_h466g import k


def g(x: int) -> int:
    return x
