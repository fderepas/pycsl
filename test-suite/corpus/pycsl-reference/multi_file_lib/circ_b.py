"""multi_file_lib.circ_b — circular-import fixture (circ_a <-> circ_b)."""
_ = 0  # anchor
# (#49) gen #31 — the cycle via a MODULE import, not a FROM import. The `from … import func_a`
# form asks the partially-initialised `circ_a` for a name it has not bound yet, so CPython
# refused the whole fixture — `cannot import name 'func_a' from partially initialized
# module` — and 0065, 0186 and 0187 were three `# pycsl-expected: PASS` drivers that could
# not be imported at all. `import multi_file_lib.circ_a` establishes exactly the same cycle
# and is the circular import PYTHON SUPPORTS, which is also the one a real program writes.
# Measured: all three drivers now load and print their own PASS, and all three emissions are
# BYTE-IDENTICAL.
import multi_file_lib.circ_a  # noqa: F401 — establishes the cycle


#@ ensures \result == x + 1
def func_b(x: int) -> int:
    return x + 1
