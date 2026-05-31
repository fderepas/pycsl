"""PyCSL mock for Python's argparse module.

Provides trusted stubs for command-line argument parsing.
ArgumentParser modelled as a class with argument count invariant.
"""
_ = 0  # anchor

# ── ArgumentParserObj class ─────────────────────────────────────────

""  # pycsl
#@ class invariant self._arg_count >= 0
class ArgumentParserObj:
    def __init__(self):
        self._arg_count = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._arg_count == \old(self._arg_count) + 1
    #@ assigns self._arg_count
    def add_argument(self, name_or_flags: int, action: int, nargs: int, const_val: int, default: int, arg_type: int, choices: int, required: int, help_text: int, metavar: int, dest: int, deprecated: int) -> int:
        self._arg_count += 1
        return self._arg_count

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/argparse.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def add_argument_group(self, title: int, description: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/argparse.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def add_mutually_exclusive_group(self, required: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers
#@ requires True
#@ ensures True
#@ assigns \nothing
    def add_subparsers(self, title: int, description: int, prog: int, dest: int, required: int, help_text: int, metavar: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args
#@ requires True
#@ ensures True
#@ assigns \nothing
    def parse_args(self, args: int, namespace: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/argparse.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def parse_known_args(self, args: int, namespace: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.set_defaults
#@ requires True
#@ ensures True
#@ assigns \nothing
    def set_defaults(self, kwargs: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.get_default
#@ requires True
#@ ensures True
#@ assigns \nothing
    def get_default(self, dest: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.print_usage
#@ requires True
#@ ensures True
#@ assigns \nothing
    def print_usage(self, file: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/argparse.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def print_help(self, file: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.format_usage
#@ requires True
#@ ensures True
#@ assigns \nothing
    def format_usage(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.format_help
#@ requires True
#@ ensures True
#@ assigns \nothing
    def format_help(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/argparse.py
#@ requires True
#@ ensures True
    def error_exit(self, message: int) -> int:
        return 0

# ── NamespaceObj class ──────────────────────────────────────────────

#@ class invariant self._attrs >= 0
class NamespaceObj:
    def __init__(self):
        self._attrs = 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.Namespace
#@ requires True
#@ ensures True
#@ assigns \nothing
    def get_attr(self, name: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._attrs == \old(self._attrs) + 1
    #@ assigns self._attrs
    def set_attr(self, name: int, attr_val: int) -> int:
        self._attrs += 1
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.FileType
#@ requires bufsize >= -1
#@ ensures \result >= 0
def FileType(mode: int, bufsize: int, encoding: int, errors: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.HelpFormatter
#@ ensures True
def HelpFormatter(prog: int, indent_increment: int, max_help_position: int, width: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.RawDescriptionHelpFormatter
#@ ensures True
def RawDescriptionHelpFormatter(prog: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.RawTextHelpFormatter
#@ ensures True
def RawTextHelpFormatter(prog: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentDefaultsHelpFormatter
#@ ensures True
def ArgumentDefaultsHelpFormatter(prog: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentError
#@ ensures True
def ArgumentError(argument: int, message: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.ArgumentTypeError
#@ ensures True
def ArgumentTypeError(message: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/argparse.html#argparse.BooleanOptionalAction
#@ requires True
#@ ensures True
def BooleanOptionalAction(option_strings: int, dest: int) -> int:
    return 0

SUPPRESS = 0
OPTIONAL = 0
ZERO_OR_MORE = 0
ONE_OR_MORE = 0
REMAINDER = 0
