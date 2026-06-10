"""Test 0691 — Concurrent: mutex_invariant referencing a non-shared variable is rejected.

The core (core_ir_semantic._check_mutex_invariants, migrated from Module 4's
_validate_mutex_invariant_scope) rejects a `#@ mutex_invariant` whose expression
references a variable that is not a shared variable protected by that mutex."""
# pycsl-flags: --no-proof --memory-model concurrent
# pycsl-expected: FAIL
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: bogus_unshared_variable >= 0
_ = 0  # anchor

import threading
lock_counter = threading.Lock()
counter = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter += 1
    return 0

if __name__ == "__main__":
    print("PASS")
