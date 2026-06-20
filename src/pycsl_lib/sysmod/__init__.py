# pycsl_lib/sysmod — pure-Python sys module
# Façade over ProcessState + fd_table. Modelled.
# Unix skill §6.1 (PCB), §5.1 (fd table), §7.2 (argv, envp).
#
# When wired to World: delegates to world.proc for argv/path/exit,
# and to world.fs for stdin/stdout/stderr (FDs 0,1,2).
# Without World: uses module-level state (backward-compatible).


class FloatInfo:
    def __init__(self):
        self.max_10_exp = 308


# Module-level state — used when no World is wired
_argv = []
_path = []
_exit_code = -1
_float_info = FloatInfo()
_world = None


def set_world(world) -> None:
    """Wire this module to a World instance. After this call, argv/path/exit
    delegate to world.proc, and stdin/stderr to world.fs."""
    global _world
    _world = world


#@ ensures \result >= 0
def get_argv() -> int:
    if _world is not None:
        return _world.proc._argv_keys
    return _argv


#@ ensures \result >= 0
def get_path() -> int:
    if _world is not None:
        return _world.proc._path
    return _path


def path_insert(index, item):
    if _world is not None:
        _world.proc._path.insert(index, item)
    else:
        _path.insert(index, item)


#@ ensures \result == 308
def get_float_info_max_10_exp() -> int:
    return 308


def exit(code):
    if _world is not None:
        _world.proc.exit(code)
    raise Exception()


# stdin, stdout, stderr are FDs 0, 1, 2 in the shared fd_table.
# In the World model, these delegate to world.fs.sys_read/sys_write.

#@ ensures \result >= 0
def stdin_buffer_read(n) -> int:
    if _world is not None:
        return _world.fs.sys_read(0, n)
    return 0


#@ ensures \result >= 0
def stderr_write(data) -> int:
    if _world is not None:
        return _world.fs.sys_write(2, data)
    return 0
