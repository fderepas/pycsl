# formal_os_walk.py — os.walk CONSEQUENCE test — PUBLIC API ONLY.
#
# STATUS: PROVEN (gap-3 closed). os.walk was a generator (used `yield`);
# PyCSL's emitter cannot lower `yield`, so the import stub raised a WhyML
# type error. Rewritten as a NON-generator returning the bounded COUNT of
# subdirectory names at `top` (see os/__init__.py). The contract pins
# `0 <= \result <= 16`, so a caller's bounded-totality consequence is
# entailed on the non-raising path.
#
# CONSEQUENCE: walk(".") on the root directory (which always exists in this
# model — inode 0) returns a count in [0, 16] without raising. Non-vacuous:
# a walker returning a negative count, or > 16, would fail. The root "."
# resolves to inode 0 (listdir's special-case), so the non-raising path is
# taken and the bounded-return ensures fires.

from pycsl_lib.os import walk


# (1) walk — CONSEQUENCE: walk(".") returns a bounded count (0..16). The
# root "." always resolves (listdir special-cases it to inode 0), so the
# normal-return ensures `0 <= \result <= 16` is entailed.
#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def walk_root_bounded() -> int:
    r = walk(".")
    if r >= 0 and r <= 16:
        return 1
    return 0
