# Advice probe (route #458): witness 6866's `base / name` rewritten `os.path.join(base, name)`.
import os


#@ no_exception \all
def f(base: str, name: str) -> int:
    full = os.path.join(base, name)
    return len(base)
