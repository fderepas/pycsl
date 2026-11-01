r"""Test 8117 -- route #510 (expected FAIL: REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe o8064_class_type; refused PYCSL-R325-OPAQUE-INT-FALLBACK at base): a `type K = int` directly in a class body rebinds the class attribute `K = 5`, so the attribute read `C.K` is a TypeAliasType; CPython f(10) raises TypeError
"""
# pycsl-expected: FAIL


class C:
    K = 5
    type K = int


#@ no_exception \all
def f(n: int) -> int:
    return n // C.K


if __name__ == "__main__":
    try:
        print("result", f(10))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
