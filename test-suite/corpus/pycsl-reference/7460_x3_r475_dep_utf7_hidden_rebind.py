r"""Test 7460 -- route #475 (expected FAIL): red-team 39 witness `g38_q701_utf7_hidden_rebind` -- a `utf-7` dependency whose comment `# +AAo-K = 0` CPython decodes to a newline and `K = 0`; PROVED at base 8aaa864ca; CPython ZeroDivisionError. Now REFUSED (PYCSL-R475-DEPENDENCY-ENCODING).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h475a import K


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
