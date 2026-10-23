r"""Concurrent: unprotected write to a protected shared variable."""
import threading
_ = 0  # anchor
#@ shared counter protected_by lock

lock = threading.Lock()
counter = 0


#@ ensures \result == 0
def bump() -> int:
    global counter
    counter = counter + 1
    return 0


if __name__ == "__main__":
    print("CPython:", bump())
