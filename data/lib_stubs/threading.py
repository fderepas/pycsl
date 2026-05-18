"""PyCSL mock for Python's threading module.

Thread, Lock, Semaphore, Event, and Barrier modelled as classes with invariants.
"""
_ = 0  # anchor

# ── ThreadObj class ─────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._alive >= 0 and self._alive <= 1
class ThreadObj:
    def __init__(self):
        self._alive = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._alive == 1
    #@ assigns self._alive
    def start(self) -> int:
        self._alive = 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._alive == 0
    #@ assigns self._alive
    def join(self, timeout: int) -> int:
        self._alive = 0
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._alive
    #@ assigns \nothing
    def is_alive(self) -> int:
        return self._alive

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def get_name(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def ident(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def native_id(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def daemon(self) -> int:
        return 0

# ── LockObj class ───────────────────────────────────────────────────

#@ class invariant self._locked >= 0 and self._locked <= 1
class LockObj:
    def __init__(self):
        self._locked = 0

    #@ \trusted
    #@ requires self._locked == 0
    #@ ensures self._locked == 1
    #@ assigns self._locked
    def acquire(self, blocking: int, timeout: int) -> int:
        self._locked = 1
        return 1

    #@ \trusted
    #@ requires self._locked == 1
    #@ ensures self._locked == 0
    #@ assigns self._locked
    def release(self) -> int:
        self._locked = 0
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._locked
    #@ assigns \nothing
    def locked(self) -> int:
        return self._locked

# ── SemaphoreObj class ──────────────────────────────────────────────

#@ class invariant self._value >= 0
class SemaphoreObj:
    def __init__(self):
        self._value = 1

    #@ \trusted
    #@ requires self._value >= 1
    #@ ensures self._value == \old(self._value) - 1
    #@ assigns self._value
    def acquire(self, blocking: int, timeout: int) -> int:
        self._value -= 1
        return 1

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._value == \old(self._value) + 1
    #@ assigns self._value
    def release(self, n: int) -> int:
        self._value += 1
        return 0

# ── EventObj class ──────────────────────────────────────────────────

#@ class invariant self._flag >= 0 and self._flag <= 1
class EventObj:
    def __init__(self):
        self._flag = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._flag == 1
    #@ assigns self._flag
    def set(self) -> int:
        self._flag = 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._flag == 0
    #@ assigns self._flag
    def clear(self) -> int:
        self._flag = 0
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._flag
    #@ assigns \nothing
    def is_set(self) -> int:
        return self._flag

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def wait(self, timeout: int) -> int:
        return self._flag

# ── BarrierObj class ────────────────────────────────────────────────

#@ class invariant self._parties >= 1
#@ class invariant self._n_waiting >= 0 and self._n_waiting <= self._parties
class BarrierObj:
    def __init__(self):
        self._parties = 1
        self._n_waiting = 0

    #@ \trusted
    #@ requires self._n_waiting <= self._parties - 1
    #@ ensures self._n_waiting == \old(self._n_waiting) + 1
    #@ assigns self._n_waiting
    def wait(self, timeout: int) -> int:
        self._n_waiting += 1
        return self._n_waiting

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._n_waiting == 0
    #@ assigns self._n_waiting
    def reset(self) -> int:
        self._n_waiting = 0
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._n_waiting == 0
    #@ assigns self._n_waiting
    def abort(self) -> int:
        self._n_waiting = 0
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._parties
    #@ assigns \nothing
    def parties(self) -> int:
        return self._parties

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._n_waiting
    #@ assigns \nothing
    def n_waiting(self) -> int:
        return self._n_waiting

# ── Module-level functions ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def active_count() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def current_thread() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_ident() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_native_id() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def main_thread() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def stack_size(size: int) -> int:
    return 0
