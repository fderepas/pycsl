r"""Test 4390 -- gen #37 route #332 (expected PASS): CONTROL: an assert WITHOUT any `no_exception` keeps the documented erasure (annotations §7.1, partial correctness, `python -O`): PROVES unchanged.
"""
# pycsl-expected: PASS
#@ ensures \result == 7
#@ assigns \nothing
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
