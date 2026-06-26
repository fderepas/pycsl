# Module-level function alias `kill = _kill` loses contract

**Category:** Candidate pycsl bug (emitter)
**Filed by:** test-supervise-sl (os module fleet)
**Date:** 2026-06-22
**Status:** CONFIRMED

## Reproduction

In `src/pycsl_lib/os/__init__.py`:

```python
#@ requires pid >= 0
#@ requires sig >= 0
#@ assigns \nothing
#@ ensures \result == 0
def _kill(pid, sig):
    """Send signal to a process. Stub: no-op, returns 0."""
    return 0

kill = _kill
```

When a formal test imports `kill`:

```python
from pycsl_lib.os import kill
r = kill(pid, sig)  # operate
```

## Observed behavior

PyCSL emits `kill` as an **abstract operation with no contract**:

```whyml
(* Abstract operations for unsupported Python patterns *)
val kill_2 (x0: int) (x1: int) : int
```

The `#@ ensures \result == 0` contract on `_kill` is **not propagated** through
the `kill = _kill` alias. The importer cannot prove `r == 0`.

## Expected behavior

The alias `kill = _kill` should propagate `_kill`'s contract. In Python,
`kill` IS `_kill` (same function object); the contract should be identical.

## Workaround

Import `_kill` directly (it carries the contract). This violates the
CALL-THE-API convention (underscore prefix) but is the only way to prove the
consequence. See `formal_os_kill.py`.

## Impact

Any module-level function alias (`name = other_name`) loses the original
function's contract. This affects any library that uses the common Python
pattern of defining a private function and re-exporting it under a public name.
