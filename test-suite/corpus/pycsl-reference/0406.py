"""Test 0406 — UB-7.1 baseline: mutating a different container is fine.

The detector should not flag `for x in src: dst.append(x)` — only `src` is iterated, only
`dst` is mutated. `--no-proof` keeps the test focused on the DETECTOR rather than on the
proof that `for`-over-list converges (which would need full invariants).

RELAUNCH #48: `dst` is now a LOCAL rather than a second PARAMETER, and the reason is route
#49. An `append` to a list PARAMETER lowered to an append on a local SNAPSHOT with no
`writes` clause, so `copy_to_different(src, dst)` really did append INVISIBLY to its
caller's list — `g(a); len(a)` proved unchanged where Python had grown it (witnesses
1080/1081). That is now a designed refusal, so a driver whose subject is the UB-7.1
DETECTOR must not also be a live instance of route #49. The detector's subject is unchanged:
one container is iterated and a DIFFERENT one is mutated, which is exactly what must not be
flagged."""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires \length(src) >= 0
#@ ensures True
#@ assigns \nothing
def copy_to_different(src: list) -> None:
    dst = []
    for x in src:
        dst.append(x)


if __name__ == "__main__":
    pass
