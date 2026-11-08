r"""Test 3118 — route #281 (expected FAIL): `repr(x)`, `f"{x!r}"` and `f"{x:d}"` under `no_exception ValueError` PROVED. CPython 3.11+ raises `ValueError` (Exceeds the
limit (4300 digits) for integer string conversion) for `x = 10**5000`; the conversion now owes
`|x| < 10**4300` under `no_exception`, which nothing establishes.
NOTE (route #284): until route #284 the `f"{x:d}"` line carried NO obligation (the literal-spec
test read the operand's WhyML type instead of the presentation type), so this file FAILED only
through its `repr(x)` / `f"{x!r}"` lines and over-claimed coverage of `:d`. The per-spec witnesses
are 3260-3265 (`:d`, `v={x:d}`, `:5`, `:05d`, `:n`/`:,`, `:>10`).
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception ValueError
def f(x: int) -> int:
    a = repr(x)
    b = f"{x!r}"
    c = f"{x:d}"
    return 1


if __name__ == "__main__":
    try:
        f(10**5000)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
