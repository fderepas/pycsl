"""Test 0417 — UB-7.3: protected shared variable passes strict mode."""
# pycsl-flags: --memory-model concurrent --strict-concurrent-checks --no-proof
_ = 0  # anchor
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
import threading
lock_counter = threading.Lock()
counter = 0


#@ thread_entry
#@ \diverges
#@ requires True
#@ ensures True
#@ assigns \nothing
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        return 0


if __name__ == "__main__":
    pass
