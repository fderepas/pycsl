r"""Test 6463 -- route #430 (expected PASS): CONTROL: a `no_exception \all` caller of an un-claimed callee that hashes a DERIVABLE value (`{k}`, `k: str`) is not refused. PROVED at base and candidate.
"""
# pycsl-expected: PASS


#@ ensures \result == n + 1
def h(k: str, n: int) -> int:
    s = {k}
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def caller(k: str, n: int) -> int:
    return h(k, n)


if __name__ == "__main__":
    print(caller("a", 0))
