# pycsl_lib/tmpf — pure-Python tempfile module
# Over fs. mkstemp: Modelled. Name sequence: Specified (counter, not random).
# TCB: collision-freedom/unpredictability not modelled.
#
# When wired to World: mkstemp creates a real file via world.fs.sys_creat,
# gettempdir reads from world.proc.environ["TMPDIR"].

_name_counter = 0
_tempdir = 0
_world = None


def set_world(world) -> None:
    """Wire this module to a World instance."""
    global _world
    _world = world


#@ ensures \result >= 0
def _next_name() -> int:
    global _name_counter
    _name_counter = _name_counter + 1
    return _name_counter


#@ ensures \result >= 0
def gettempdir() -> int:
    if _world is not None:
        d = _world.proc.getenv("TMPDIR", "")
        if d != "":
            return d
    return _tempdir


#@ ensures \result[0] >= 0
#@ ensures \result[1] >= 0
def mkstemp(suffix, prefix, dir_path) -> tuple:
    name = _next_name()
    fd = 0
    if _world is not None:
        fd = _world.fs.sys_creat("tmp_" + str(name), 0o600)
        if fd < 0:
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
        if self._delete != 0 and _world is not None and self._fd > 0:
            _world.fs.sys_close(self._fd)
        return 0

    def close(self):
        if _world is not None and self._fd > 0:
            _world.fs.sys_close(self._fd)
