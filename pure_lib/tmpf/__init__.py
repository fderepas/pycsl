# pure_lib/tmpf — pure-Python tempfile module
# Over fs. mkstemp: Modelled. Name sequence: Specified (counter, not random).
# TCB: collision-freedom/unpredictability not modelled.

_name_counter = 0
_tempdir = 0


#@ ensures \result >= 0
def _next_name() -> int:
    global _name_counter
    _name_counter = _name_counter + 1
    return _name_counter


#@ ensures \result >= 0
def gettempdir() -> int:
    return _tempdir


#@ ensures \result[0] >= 0
#@ ensures \result[1] >= 0
def mkstemp(suffix, prefix, dir_path) -> tuple:
    name = _next_name()
    fd = 0
    return (fd, name)


class NamedTemporaryFile:
    def __init__(self, suffix, prefix, dir_path, delete):
        self._delete = delete
        r = mkstemp(suffix, prefix, dir_path)
        self._fd = r[0]
        self._name = r[1]

    #@ ensures \result >= 0
    def name(self) -> int:
        return self._name

    def __enter__(self):
        return self

    #@ ensures \result == 0
    def __exit__(self, exc_type, exc_val, exc_tb) -> int:
        return 0

    def close(self):
        pass
