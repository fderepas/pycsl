# Formal tests for pure_lib/argp — argparse module
from pure_lib.argp import ArgumentParser


#@ ensures \result >= 0
#@ ensures \result <= argc
def test_parse_args_bounded(argc: int) -> int:
    """parse_args returns at most argc parsed arguments."""
    #@ requires argc >= 0
    p = ArgumentParser()
    return p.parse_args(argc)
