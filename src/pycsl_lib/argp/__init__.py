# pycsl_lib/argp — pure-Python argparse module model
# Named 'argp' to avoid stdlib name clash.
#
# Contracts derived from library_reference/argparse.rst.
# RST: "Create a new ArgumentParser object."
# RST: "Define how a single command-line argument should be parsed."
# RST: "Run the parser and return an object holding attributes."
#
# Model: ArgumentParser tracks action count; parse_args returns
# number of successfully parsed arguments.


""  # pycsl
#@ class invariant self._action_count >= 0
class ArgumentParser:
    """RST: 'The ArgumentParser object will hold all the information
    necessary to parse the command line into Python data types.'"""

    def __init__(self):
        self._action_count = 0

    #@ ensures self._action_count == \old(self._action_count) + 1
    #@ assigns self._action_count
    def add_argument(self) -> None:
        """RST: 'Define how a single command-line argument should be parsed.'
        Adds one action to the parser."""
        self._action_count = self._action_count + 1

    #@ requires argc >= 0
    #@ ensures \result >= 0
    #@ ensures \result <= argc
    #@ assigns \nothing
    def parse_args(self, argc: int) -> int:
        """RST: 'Run the parser and return a Namespace.'
        Returns count of successfully parsed arguments (<= argc)."""
        return argc

    #@ requires argc >= 0
    #@ ensures \result >= 0
    #@ ensures \result <= argc
    #@ assigns \nothing
    def parse_known_args(self, argc: int) -> int:
        """RST: 'Like parse_args but does not produce an error for
        unrecognized arguments.' Returns parsed count."""
        return argc

    #@ ensures \result >= 0
    #@ assigns \nothing
    def format_help(self) -> int:
        """RST: 'Return a string containing a help message.'
        Returns help text length (non-negative)."""
        return self._action_count

    #@ ensures \result >= 0
    #@ assigns \nothing
    def format_usage(self) -> int:
        """RST: 'Return a string containing a brief usage message.'
        Returns usage text length."""
        return self._action_count

    #@ ensures \result == self._action_count
    #@ assigns \nothing
    def get_action_count(self) -> int:
        """Number of registered arguments."""
        return self._action_count
