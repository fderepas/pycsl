# pycsl_lib/plib — pure-Python pathlib module
# Path parsing: Specified (string-heavy). Filesystem ops: delegate to os model.


class PurePath:
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
