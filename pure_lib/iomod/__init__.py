# pure_lib/iomod — pure-Python io module
# StreamModel: flush-through (write routes to fs.sys_write).
# StringIO: in-memory buffer (no fd). TextIOWrapper: Specified.
#
# making-it-pure-5.md §8: flush-through model — every StreamModel.write
# immediately delegates to world.fs.sys_write(fd, data). No private
# buffer divergence. Sound with fs_ownership HAPPY (§2): iomod has
# no direct fs write site; the write lands in fs.sys_write.


#@ class invariant self._size >= 0
class StringIO:
    def __init__(self, initial_value):
        self._buf = []
        self._pos = 0
        self._size = 0
        if initial_value != 0:
            n = len(initial_value)
            i = 0
            #@ loop invariant 0 <= i
            #@ loop invariant i <= n
            #@ loop variant n - i
            while i < n:
                self._buf.append(initial_value[i])
                i = i + 1
            self._size = n

    #@ ensures \result >= 0
    def read(self, n) -> int:
        if n < 0:
            n = self._size - self._pos
        if n <= 0:
            return 0
        start = self._pos
        end = self._pos + n
        if end > self._size:
            end = self._size
        self._pos = end
        return end - start

    #@ ensures \result >= 0
    def write(self, data) -> int:
        n = len(data)
        i = 0
        #@ loop invariant 0 <= i
        #@ loop invariant i <= n
        #@ loop variant n - i
        while i < n:
            if self._pos < self._size:
                self._buf[self._pos] = data[i]
            else:
                self._buf.append(data[i])
                self._size = self._size + 1
            self._pos = self._pos + 1
            i = i + 1
        return n

    #@ ensures \result >= 0
    def tell(self) -> int:
        return self._pos

    def seek(self, pos):
        if pos < 0:
            pos = 0
        if pos > self._size:
            pos = self._size
        self._pos = pos

    #@ ensures \result >= 0
    def getvalue(self) -> int:
        return self._buf


class FileIO:
    """Flush-through file stream backed by world.fs FD.

    Every write immediately delegates to world.fs.sys_write(fd, data).
    Every read immediately delegates to world.fs.sys_read(fd, n).
    No private buffer — the fd_offset in the filesystem IS the position.
    """

    def __init__(self, fd, fs):
        self._fd = fd
        self._fs = fs

    #@ ensures \result >= -1
    def read(self, n) -> int:
        return self._fs.sys_read(self._fd, n)

    #@ ensures \result >= -1
    def write(self, data) -> int:
        return self._fs.sys_write(self._fd, data)

    #@ ensures \result >= -1
    def seek(self, pos, whence=0) -> int:
        return self._fs.sys_lseek(self._fd, pos, whence)

    #@ ensures \result >= 0
    def tell(self) -> int:
        if self._fd >= 0 and self._fd < 64:
            return self._fs.fd_offset[self._fd]
        return 0

    def close(self) -> int:
        return self._fs.sys_close(self._fd)

    def flush(self) -> None:
        pass  # flush-through: nothing to flush


_world = None


def set_world(world) -> None:
    """Wire this module to a World instance."""
    global _world
    _world = world


def open_file(name, mode) -> int:
    """Open a file via the World filesystem. Returns a FileIO stream."""
    if _world is None:
        return 0
    flags = 0
    if mode == "r":
        flags = 0  # O_RDONLY
    elif mode == "w":
        flags = 1 | 64  # O_WRONLY | O_CREAT
    elif mode == "rw":
        flags = 2  # O_RDWR
    fd = _world.fs.sys_open(name, flags)
    if fd < 0:
        return 0
    return FileIO(fd, _world.fs)


#@ ensures \result >= 0
def text_encoding(encoding) -> int:
    return encoding
