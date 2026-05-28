"""Test 0406 — UB-7.1 baseline: mutating a different container is fine.

The detector should not flag `for x in src: dst.append(x)` — only `src`
is iterated, only `dst` is mutated. We use `--no-proof` flags so the
test stays focused on the detector rather than tripping on the proof
that `for`-over-list converges (which would need full invariants).
"""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires \length(src) >= 0
#@ ensures True
#@ assigns dst[0..\length(dst)]
def copy_to_different(src: list, dst: list) -> None:
    for x in src:
        dst.append(x)


if __name__ == "__main__":
    pass
