# advice of PYCSL-R434-ORD-PATH followed for witness 6579: drop \all
from pathlib import Path


#@ requires len(str(p)) == 1
#@ no_exception IndexError
def f(p: Path) -> int:
    return ord(p)
