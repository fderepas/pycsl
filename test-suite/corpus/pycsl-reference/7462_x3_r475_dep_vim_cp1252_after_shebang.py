r"""Test 7462 -- route #475 (expected FAIL): red-team 39 witnesses `g38_q711_vim_cookie_latin1` / `g38_q713_shebang_then_cookie` -- a vim-style `cp1252` cookie on line 2 after a shebang; PROVED at base 8aaa864ca; CPython returns 2. Now REFUSED (PYCSL-R475-DEPENDENCY-ENCODING).
"""
# pycsl-expected: FAIL
from multi_file_lib.x3_h475c import S


#@ ensures \result == 1
def f(n: int) -> int:
    return len(S)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
