r"""Test 6613 -- route #438 (expected FAIL): NEW latent (#430 channel): a `no_exception \all` caller of an UN-CLAIMED same-file callee hashing `t: tuple`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R430-CALLEE-UNDERIVABLE-HASH).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
def h(t: tuple) -> int:
    s = {t}
    return 1


#@ no_exception \all
#@ ensures \result == 1
def caller(t: tuple) -> int:
    return h(t)


if __name__ == "__main__":
    try:
        r = caller(([1],))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
