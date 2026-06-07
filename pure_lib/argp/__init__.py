# pure_lib/argp — pure-Python argparse module
# State (action lists): Modelled. parse_args: Specified (string-heavy).


class Namespace:
    def __init__(self):
        self._attrs = []
        self._vals = []
        self._size = 0

    def __setattr__(self, name, value):
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        self._attrs.append(name)
        self._vals.append(value)
        self._size = self._size + 1


class ArgumentError(Exception):
    pass


class ArgumentParser:
    def __init__(self):
        self._actions = []
        self._defaults = {}
        self._action_count = 0

    def add_argument(self, name, default=0, action=0, nargs=0, help_text=0):
        self._actions.append(name)
        self._action_count = self._action_count + 1
        if default != 0:
            self._defaults[name] = default

    #@ ensures \result >= 0
    def parse_args(self, args) -> int:
        return 0

    #@ ensures \result >= 0
    def parse_known_args(self, args) -> int:
        return 0

    #@ ensures \result >= 0
    def format_help(self) -> int:
        return 0

    #@ ensures \result >= 0
    def format_usage(self) -> int:
        return 0

    def error(self, message):
        raise ArgumentError()

    def exit(self, status, message):
        raise Exception()
