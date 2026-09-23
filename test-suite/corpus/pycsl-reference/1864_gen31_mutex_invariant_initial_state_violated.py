r"""Test 1864 — gen #31 NEGATIVE TWIN of 1863 (expected FAIL): the initial state violates it.

Byte-identical to 1863 except that the invariant is `counter >= 1` while the module binds
`counter = 0`. It FAILS, on the initial-state goal

    goal _check_initial_lock_counter : lock_counter_inv 1

and that is the entire content of the repair: before gen #31 this file and 1863 were
INDISTINGUISHABLE — both unprovable with the prover on, both silently unchecked under
`--no-proof`, which is the mode all 19 existing `#@ mutex_invariant` drivers use. A
directive that cannot be discharged in any program and is not checked in the mode everyone
runs is a directive with no configuration in which it means anything.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model concurrent --strict-concurrent-checks
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 1
import threading
lock_counter = threading.Lock()
counter = 0
_ = 0  # anchor


#@ thread_entry
#@ \diverges
#@ requires True
#@ ensures True
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter = 0
    return 0
