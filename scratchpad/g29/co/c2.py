r"""Concurrent: mutex invariant broken inside the critical section."""
import threading
_ = 0  # anchor
#@ shared counter protected_by lock
#@ mutex_invariant lock: counter >= 0

lock = threading.Lock()
counter = 0


#@ ensures \result == 0
def bump() -> int:
    global counter
    #@ critical lock
    with lock:
        counter = counter - 1
    return 0


if __name__ == "__main__":
    print("CPython:", bump())
