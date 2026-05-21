"""Test 0263 — Concurrent: acquires with mutex invariant, two thread_entry functions"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared score protected_by lock_score
#@ mutex_invariant lock_score: score >= 0
_ = 0  # anchor

import threading
lock_score = threading.Lock()
score = 0

#@ thread_entry
#@ \diverges
def add_score() -> int:
    #@ acquires lock_score
    with lock_score:
        score += 10
    return 0

#@ thread_entry
#@ \diverges
def reset_score() -> int:
    #@ acquires lock_score
    with lock_score:
        score = 0
    return 0

if __name__ == "__main__":
    print("PASS")
