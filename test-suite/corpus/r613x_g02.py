# run #8 u55 witness 10220 (review rt66 g02): the module CPython loads for `import r613x_g02` under
# `cd test-suite/corpus && python -m pycsl-reference.10220_...` -- sys.path[0] is this directory (benign marker).
print("ROOT r613x_g02.py loaded:", __file__)


def one() -> int:
    return 2
