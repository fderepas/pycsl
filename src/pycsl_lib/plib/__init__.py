# pycsl_lib/plib — pure-Python pathlib module
# Path parsing: Specified (string-heavy). Filesystem ops: delegate to os model.


#@ class invariant self._path >= 0
class PurePath:
    # (#49) gen #31 — THE CLASS INVARIANT AND THE `requires` ARE NEW, AND THEY ARE THE
    # ASSUMPTION `__str__`'s POSTCONDITION WAS ALREADY MAKING. Dunders used to be dropped
    # before any IR was built, so `__str__`'s `#@ ensures \result >= 0` over `return
    # self._path` was never checked against anything: the field is an opaque model handle
    # and nothing said it was non-negative. The clause was a claim with no basis in the
    # model, and it went unnoticed for as long as the method was invisible.
    # Now that the body is emitted the goal is real and does not discharge, so the
    # assumption moves INTO THE CONTRACT where a reader can see it — which is the same
    # repair the stdlib-identity-stub audit applied to `context_var_get` in gen #30 ("an
    # assumption in a comment is not a contract").
    #@ requires path >= 0
    def __init__(self, path):
        self._path = path

    #@ ensures \result >= 0
    def __str__(self) -> int:
        return self._path

    #@ ensures \result == 0 or \result == 1
    def is_absolute(self) -> int:
        return 0


class Path(PurePath):
    def __init__(self, path):
        PurePath.__init__(self, path)

    #@ ensures \result >= 0
    def stat(self) -> int:
        return 0

    #@ ensures \result == 0 or \result == 1
    def exists(self) -> int:
        return 0

    #@ ensures \result == 0 or \result == 1
    def is_file(self) -> int:
        return 0

    #@ ensures \result == 0 or \result == 1
    def is_dir(self) -> int:
        return 0

    #@ ensures \result >= 0
    def mkdir(self, mode, parents, exist_ok) -> int:
        return 0

    #@ ensures \result >= 0
    def open(self, mode) -> int:
        return 0

    #@ ensures \result >= 0
    def read_text(self) -> int:
        return 0

    #@ ensures \result >= 0
    def write_text(self, data) -> int:
        return 0

    def unlink(self):
        pass

    #@ ensures \result >= 0
    def joinpath(self, other) -> int:
        return 0

    #@ ensures \result >= 0
    def parent(self) -> int:
        return 0

    #@ ensures \result >= 0
    def name(self) -> int:
        return 0
