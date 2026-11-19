# run #8 u55 witness 10224 (review rt66 g10): a benign NON-identical stand-in for the stdlib json,
# in an --import-path root (CPython: PYTHONPATH). cwd's admitted ./json/ copy no longer hides it.
print("LOCAL g10/json.py loaded:", __file__)


def dumps(obj):
    return "local"
