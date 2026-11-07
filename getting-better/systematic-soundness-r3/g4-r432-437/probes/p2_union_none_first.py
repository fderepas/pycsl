from typing import Union
#@ no_exception \all
def f(x: Union[None, str]) -> int:
    return len(x.strip())
