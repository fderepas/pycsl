r"""Test 3271 — route #284 controls (PASS): a BOUNDED int renders through every valid
decimal spec (`:d`, `v={x:d}`, `:5`, `:05d`, `:n`, `:,`, `:>10`, `!r:>5`) under `no_exception \all`;
an UNBOUNDED int renders in hex (`:x`, `:#06x`, binary `:b`) with no obligation; a str renders through
the specs valid for a str (`:>5`, `:s`, `:.2`, `:^7`); a valid `%` format (`"%5d|%s|%%" % (x, x)`)
discharges.
"""
# pycsl-expected: PASS


#@ requires 0 <= x and x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    a = f"{x:d}"
    b = f"v={x:d}"
    c = f"{x:5}"
    d = f"{x:05d}"
    e = f"{x:n}"
    g = f"{x:,}"
    h = f"{x:>10}"
    i = f"{x!r:>5}"
    return 1


#@ requires 0 <= x and x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def pct(x: int) -> int:
    print("%5d|%s|%%" % (x, x))
    return 1


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def hx(x: int) -> int:
    a = f"{x:x}"
    b = f"{x:#06x}"
    c = f"{x:b}"
    return 1


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def st(s: str) -> int:
    a = f"{s:>5}"
    b = f"{s:s}"
    c = f"{s:.2}"
    d = f"{s:^7}"
    return 1


if __name__ == "__main__":
    assert f(5) == 1 and f(1000) == 1
    assert hx(10**5000) == 1 and pct(7) == 1
    assert st("abcdef") == 1
    print("ok")
