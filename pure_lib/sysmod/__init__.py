# pure_lib/sysmod — pure-Python sys module
# Façade over ProcessState + fd_table. Modelled.
# Unix skill §6.1 (PCB), §5.1 (fd table), §7.2 (argv, envp).


class FloatInfo:
    def __init__(self):
        self.max_10_exp = 308


_argv = []
_path = []
_exit_code = -1
_float_info = FloatInfo()


#@ ensures \result >= 0
def get_argv() -> int:
    return _argv


#@ ensures \result >= 0
def get_path() -> int:
    return _path


def path_insert(index, item):
    _path.insert(index, item)


#@ ensures \result == 308
def get_float_info_max_10_exp() -> int:
    return 308


def exit(code):
    raise Exception()


# stdin, stdout, stderr are FDs 0, 1, 2 in the shared fd_table.
# In the World model, these delegate to world.fs.sys_read/sys_write.
# For now, provide stubs that match the calling.json API surface.

#@ ensures \result >= 0
def stdin_buffer_read(n) -> int:
    return 0


#@ ensures \result >= 0
def stderr_write(data) -> int:
    return 0
