r"""Test 6786 -- route #443 (expected PASS): CONTROL -- a parameter annotated by a concrete standard-library class imported by name (`from pathlib import Path`) is a KNOWN class, not underivable: its attribute `p.name` is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from pathlib import Path


#@ no_exception \all
def f(p: Path) -> int:
    return 1 if p.name == "a" else 0


if __name__ == "__main__":
    print("result", f(Path("/x/a")), f(Path("b")))
