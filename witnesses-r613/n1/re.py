# Benign stand-in for the stdlib `re` (route #613 probe): defines only what `json` touches at
# import time, and marks itself so the loaded file is identifiable.
MARKER = "local"
print("LOCAL re.py loaded:", __file__)
VERBOSE = 64
MULTILINE = 8
DOTALL = 16


class _Pattern:
    def __init__(self, pattern, flags=0):
        self.pattern = pattern
        self.flags = flags

    def match(self, *args, **kwargs):
        return None

    def search(self, *args, **kwargs):
        return None

    def sub(self, repl, string, *args, **kwargs):
        return string


def compile(pattern, flags=0):
    return _Pattern(pattern, flags)
