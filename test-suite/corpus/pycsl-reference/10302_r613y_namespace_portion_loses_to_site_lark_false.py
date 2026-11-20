r"""Test 10302 -- run #8 u58, review rt69 G5 / n09 (FAIL, PRE-EXISTING). The --import-path root (CPython:
PYTHONPATH) holds a BARE `lark/` directory (no `__init__.py`: a namespace portion) with utils.py, whose
`is_id_start` claims `\result == False`. CPython's PathFinder takes the REGULAR site-packages `lark` package
(pycsl's own parser dependency) over the portion: lark.utils.is_id_start("a") is True. pycsl read the local
file and PROVED the false claim at int72. REFUSED: PYCSL-SEM-IMPORT-NAMESPACE-PORTION-SHADOWED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613y/g5
from lark.utils import is_id_start


#@ ensures \result == False
#@ assigns \nothing
def g() -> bool:
    return is_id_start("a")


if __name__ == "__main__":
    print("result", g())
