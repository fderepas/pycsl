r"""Test 8794 -- route #556 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; u25 probe beyond red team 53's family): `import builtins` then `return 1 if k in builtins.len else 0`; CPython TypeError: argument of type 'builtin_function_or_method' is not a container or iterable
"""
# pycsl-expected: FAIL
import builtins


#@ no_exception \all
def f(k: int) -> int:
    return 1 if k in builtins.len else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
