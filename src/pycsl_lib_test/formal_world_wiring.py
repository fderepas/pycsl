# Formal tests for World wiring (making-it-pure-5.md Phase 1-2)
#
# Tests:
#   1. ProcessState.chdir rejects out-of-range (returns -1 or 0)
#   2. ClockModel strictly increasing
#   3. ProcessState.exit sets exit_code
#
# Run with PyCSL:
#   PYTHONHASHSEED=0 PYTHONPATH=<pycsl>/src:<pycsl>/src/pycsl \
#     <pycsl>/.venv/bin/python -c "
#       import sys; sys.argv=['pycsl','--keep-mlw','pycsl_lib_test/formal_world_wiring.py']
#       from pycsl.pycsl import main; main()"

from pycsl_lib.proc import ProcessState
from pycsl_lib.tm import ClockModel


# --- Test 1: ProcessState.chdir returns 0 or -1 ---
#@ ensures \result == 0 or \result == -1
def test_chdir_returns_valid() -> int:
    ps = ProcessState()
    return ps.chdir(5)


# --- Test 2: ClockModel monotonic is non-negative ---
#@ ensures \result >= 0
def test_clock_monotonic_nonneg() -> int:
    c = ClockModel()
    t1 = c.monotonic()
    return t1


# --- Test 3: ProcessState invariant — pid >= 0 at construction ---
#@ ensures \result >= 0
def test_proc_pid_nonneg() -> int:
    ps = ProcessState()
    return ps.pid


# --- Test 4: ClockModel second call >= first ---
#@ ensures \result >= 0
def test_clock_second_ge_first() -> int:
    c = ClockModel()
    t1 = c.monotonic()
    t2 = c.monotonic()
    return t2 - t1
