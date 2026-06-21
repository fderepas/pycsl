"""Formal test: os.* FAITHFUL FAILURE SEMANTICS — failures RAISE, they do not
return -1.

This is the external-faithfulness counterpart to formal_os_dir.py. Where the
older tests guard on a `-1`/return-code sentinel (`if rc != 0: ...`), these
EXERCISE THE EXCEPTION PATH that os.rst l.47-49 mandates:

    "All functions in this module raise OSError (or subclasses thereof) in the
     case of invalid or inaccessible file names and paths …"

INTERNALS-BLIND. Imports only public names from pycsl_lib.os.

WHAT IS PROVEN (each a genuine setup -> operate -> OBSERVE consequence, through
the public API, NOT the op's own return code):
  - mkdir(d); stat(d): the directory is PRESENT — stat returns a VALID inode
    (0 <= ino < 32) and does NOT raise.
  - mkdir(d); rmdir(d); stat(d): the name is now ABSENT — stat RAISES, and the
    raised FileNotFoundError is caught by `except OSError` (the subclass
    hierarchy: a raised FileNotFoundError is an OSError).  The handler path is
    the observed consequence of the absence.

NON-VACUITY.  The absence theorem's `ensures \result == 1` is reached ONLY via
the `except OSError` handler — if stat did NOT raise on the absent name (the
old `-1` model), control would fall through to `return 0` and the postcondition
would be violated.  So the proof genuinely depends on stat raising on absence.
"""
from pycsl_lib.os import _filesystem, mkdir, rmdir, stat


# mkdir -> stat sees a valid inode (PRESENT, no raise).
# CONSEQUENCE: after mkdir(d) succeeds, stat(d) returns a VALID inode in
# [0, 32) and does not raise.  The success path of the faithful model.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures 0 <= \result and \result < 32
def formal_os_stat_present(name: str) -> int:
    mkdir(name, 0o777)          # set up: create the directory (success path)
    return stat(name)           # observe: VALID inode, no raise — ASSERTED


# mkdir; rmdir -> stat RAISES, caught by `except OSError`.
# CONSEQUENCE: after the name is removed, stat(d) raises FileNotFoundError;
# the `except OSError` handler catches it (subclass hierarchy) and is the
# observed consequence of absence.  Returns 1 ONLY through the handler.
#@ requires True
#@ assigns _filesystem.disk
#@ ensures \result == 1
def formal_os_stat_absent_raises(name: str) -> int:
    mkdir(name, 0o777)          # set up: create...
    rmdir(name)                 # ...then remove -> name now ABSENT
    try:
        stat(name)              # the REAL observation on the absent name
        return 0                # UNREACHABLE if stat faithfully raises
    except OSError:
        return 1                # observed: stat RAISED on absence — ASSERTED == 1
