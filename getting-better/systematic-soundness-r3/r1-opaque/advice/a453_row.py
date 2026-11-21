# Advice probe (route #453, module function): a function with a (module, function) row, `os.path.join` over `str`.
import os


#@ no_exception \all
def f(path: str) -> int:
    p = os.path.join(path, "x.bak")
    return len(path)
