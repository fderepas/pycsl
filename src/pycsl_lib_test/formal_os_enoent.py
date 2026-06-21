# formal_os_enoent.py — os ENOENT consequence, through the PUBLIC API ONLY.
#
# MIGRATED to the FAITHFUL exception model (os.rst l.47-49: "All functions in
# this module raise OSError (or subclasses thereof) in the case of invalid or
# inaccessible file names and paths …").  Previously this test asserted the
# `-1` sentinel (`if fd == -1: return 1`); now open(absent) RAISES
# FileNotFoundError, and the consequence is observed through `except OSError`.
#
# We ESTABLISH absence via the API first: mkdir(d) then rmdir(d).  rmdir's
# contract pins `dir_lookup(disk,5,d) < 0` (the ABSENCE view) on its non-raising
# return, and open's `raises FileNotFoundError when dir_lookup(...) < 0` then
# FIRES — so open(d, O_RDONLY) raises, caught by `except OSError` (the Fix-1
# subclass hierarchy: a raised FileNotFoundError IS-A OSError).
#
# INTERNALS-BLIND. Imports only public names; no _filesystem, disk, sys_*,
# _dir_lookup, UnixInodeFileSystem in code or contracts.
#
# NON-VACUITY: `ensures \result == 1` is reached ONLY through the `except OSError`
# handler.  If open did NOT raise on the absent name (the old `-1` model), control
# would fall through to `return 0` and the postcondition would be violated.

from pycsl_lib.os import (
    mkdir, rmdir, open, O_RDONLY,
)


# ---------------------------------------------------------------------------
# open(absent, O_RDONLY) -> RAISES FileNotFoundError, with absence ESTABLISHED
# via the API.  Setup: mkdir(d) (d present), then rmdir(d) (d absent).
# Operate: open(d, RDONLY).  OBSERVE: open RAISES, caught by `except OSError`.
#@ requires True
#@ ensures \result == 1
def open_removed_yields_enoent(d: str) -> int:
    mkdir(d, 0o777)                 # set up: d present
    rmdir(d)                        # establish ABSENCE: dir_lookup(d) < 0
    try:
        open(d, O_RDONLY, 0o777)    # operate: open the now-absent name
        return 0                    # UNREACHABLE if open faithfully raises
    except OSError:
        return 1                    # OBSERVE: open RAISED ENOENT — ASSERTED == 1
