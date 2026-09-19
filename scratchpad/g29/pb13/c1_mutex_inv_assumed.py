# pycsl-flags: --memory-model concurrent
#@ shared total protected_by lock_total
#@ mutex_invariant lock_total: total == 99
_ = 0  # anchor

import threading
lock_total = threading.Lock()
total = 0


#@ thread_entry
#@ ensures \result == 99
def producer() -> int:
    r: int = 0
    #@ critical lock_total
    with lock_total:
        r = total
    return r
