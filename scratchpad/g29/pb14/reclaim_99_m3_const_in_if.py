_ = 0  # anchor

K: int = 3
if K > 0:
    K = 9


#@ ensures \result == 99
def probe() -> int:
    return K
