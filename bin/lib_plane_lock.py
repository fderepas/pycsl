"""Shared guard: REFUSE to emit while the soundness battery is running.

WHY THIS EXISTS (#49, gen #30). Several planes emit `.mlw` BESIDE the mirror or corpus
sources and then move them out (`check-trusted-frame-honesty`, `check-yield-erasure`,
`check-computed-rhs-erasure`, `check-bespoke-model-drift`), while others READ those files
in place (`check-emitted-vacuity`). `bin/run-soundness-planes.sh` runs its planes
SEQUENTIALLY precisely so the two never overlap — and a plane started BY HAND from another
shell defeats that ordering completely.

It happened THREE TIMES IN ONE NIGHT to the same driver, each time while confirming a fix:
once it produced a `FileNotFoundError` traceback in `check-emitted-vacuity` (a `.mlw` the
walk had just listed, moved out from under it) and twice it was harmless only by luck.
Lesson (r3) says a gate whose inputs can be deleted underneath it must REFUSE; this is the
other half — **a rule that a careful driver breaks three times in one night is a rule that
needs a mechanism, not a reminder.**

THE DESIGN IS DELIBERATELY FAIL-OPEN FOR THE BATTERY AND FAIL-CLOSED FOR THE HAND-RUN:

  * the battery writes `<root>/.soundness-planes.lock` containing its PID and exports
    `PYCSL_PLANES_RUNNING`; it removes the lock on exit via a trap;
  * a plane calling `refuse_if_battery_running()` refuses ONLY when the lock exists, its
    PID is still alive, and `PYCSL_PLANES_RUNNING` is NOT set — so the battery's own
    children never trip it, and neither does a stale lock from a killed run.

`PYCSL_PLANES_IGNORE_LOCK=1` overrides, for the case where you really do mean it.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(_ROOT, ".soundness-planes.lock")


def _alive(pid):
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    except PermissionError:
        return True
    return True


def battery_running():
    """(running, pid) — is a soundness battery holding the lock from ANOTHER shell?"""
    if os.environ.get("PYCSL_PLANES_RUNNING") or os.environ.get("PYCSL_PLANES_IGNORE_LOCK"):
        return False, None
    try:
        with open(LOCK, encoding="utf-8") as fh:
            pid = int(fh.read().split()[0])
    except (OSError, ValueError, IndexError):
        return False, None
    if not _alive(pid):
        return False, pid          # a stale lock is not a lock
    return True, pid


def refuse_if_battery_running(plane):
    """Print the refusal and exit 2 if a battery is running in another shell."""
    running, pid = battery_running()
    if not running:
        return
    print("[!] %s: REFUSING — bin/run-soundness-planes.sh is RUNNING (pid %s) and this "
          "plane EMITS `.mlw` beside the mirror or corpus sources. The battery's loop is "
          "sequential exactly so an emitting plane and a reading plane never overlap; a "
          "hand-run from another shell defeats that, and has already produced one "
          "traceback in check-emitted-vacuity from a file that vanished mid-walk. Wait "
          "for the battery, or re-run with PYCSL_PLANES_IGNORE_LOCK=1 if you mean it. "
          "THIS IS A REFUSAL, NOT A PASS." % (plane, pid))
    sys.exit(2)
