r"""Test 7288 -- route #472 CONTROL (expected PASS: PROVED at base and candidate): `import packaging`, an INSTALLED package (site-packages; pip's own dependency, present in the venv and the system interpreter alike), imports in CPython too.
"""
# pycsl-expected: PASS
import packaging


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
