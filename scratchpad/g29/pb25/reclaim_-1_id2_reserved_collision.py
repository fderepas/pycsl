_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    any: int = 1
    py_any: int = 2
    return any + py_any
