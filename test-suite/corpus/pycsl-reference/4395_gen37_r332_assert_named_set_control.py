r"""Test 4395 -- gen #37 route #332 (expected PASS): CONTROL: a failing assert under the named set `no_exception IndexError` keeps the erasure: AssertionError is outside the claimed set, so the claim is true (CPython raises AssertionError, never IndexError). PROVES.
"""
# pycsl-expected: PASS
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception IndexError
def g() -> int:
    x = 1
    assert x == 2
    return 7

if __name__ == "__main__":
    # CPython ground truth, run in a child so that no handler can catch AssertionError
    # here (route 16 refuses that shape): g() RAISES AssertionError.
    import subprocess, sys
    r = subprocess.run([sys.executable, "-c", "import runpy; ns = runpy.run_path(%r); ns['g']()" % __file__],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "AssertionError" in r.stderr, r.stderr
