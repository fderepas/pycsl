_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    any: int = 1
    py_any: int = 2
    return any + py_any
