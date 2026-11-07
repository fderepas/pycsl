from pathlib import Path


#@ no_exception \all
def f(p: Path) -> int:
    return ord(p)
