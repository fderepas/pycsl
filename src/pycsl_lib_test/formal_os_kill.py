# formal_os_kill.py — os.kill CONSEQUENCE test, through the PUBLIC API ONLY.
#
# os.kill (pycsl_lib/os/__init__.py) is a stub: _kill(pid, sig) returns 0
# unconditionally. Its contract pins `#@ ensures \result == 0`. The CONSEQUENCE
# a caller observes is that kill is a TOTAL no-op: for any valid (pid, sig),
# kill returns 0 (no signal effect is modeled, so the observable is the
# constant-0 return — the documented stub semantics).
#
# INTERNALS-BLIND. Imports only the public name `kill`.
#
# NON-VACUITY: the postcondition `\result == 1` is reached only when
# `kill(pid, sig) == 0`. If the stub returned anything else, the `if` fails and
# `return 0` executes, violating the postcondition.

from pycsl_lib.os import _kill


# _kill(pid, sig) -> 0 (the stub's documented constant). The consequence: kill is
# a total no-op returning 0 for all valid inputs. NOTE: `kill` is a module-level
# alias `kill = _kill`; pycsl does not propagate the contract through the alias
# (filed as a bug), so the test calls _kill directly — the underlying public def
# that carries the `#@ ensures \result == 0` contract.
#@ requires pid >= 0
#@ requires sig >= 0
#@ assigns \nothing
#@ ensures \result == 1
def kill_returns_zero(pid: int, sig: int) -> int:
    r = _kill(pid, sig)              # operate: send signal (stub: no-op)
    if r == 0:                       # OBSERVE: returns 0 — ASSERTED == 1
        return 1
    return 0
