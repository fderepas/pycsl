# Advice probe (route #457): witness 6864 naming a real class (`dict`) instead of the function `loads`.
from json import loads


#@ no_exception \all
def f(x: int) -> int:
    if isinstance(x, dict):
        return 1
    return 0
