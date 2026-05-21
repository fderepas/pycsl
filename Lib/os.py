"""PyCSL mock for Python's os module — Miscellaneous operating system interfaces."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def ctermid() -> int:
    """Mock: Return the filename corresponding to the controlling terminal of the process. .. availability:: Unix, not WASI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reload_environ() -> int:
    """Mock: The :data:`os.environ` and :data:`os.environb` mappings are a cache of environment variables at the time that Python sta..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fsencode(filename: int) -> int:
    """Mock: Encode :term:`path-like <path-like object>` *filename* to the :term:`filesystem encoding and error handler`; return :cla..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fsdecode(filename: int) -> int:
    """Mock: Decode the :term:`path-like <path-like object>` *filename* from the :term:`filesystem encoding and error handler`; retur..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fspath(path: int) -> int:
    """Mock: Return the file system representation of the path. If :class:`str` or :class:`bytes` is passed in, it is returned unchan..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getenv(key: int, default: int) -> int:
    """Mock: Return the value of the environment variable *key* as a string if it exists, or *default* if it doesn't. *key* is a stri..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getenvb(key: int, default: int) -> int:
    """Mock: Return the value of the environment variable *key* as bytes if it exists, or *default* if it doesn't. *key* must be byte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_exec_path(env: int) -> int:
    """Mock: Returns the list of directories that will be searched for a named executable, similar to a shell, when launching a proce..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getegid() -> int:
    """Mock: Return the effective group id of the current process.  This corresponds to the 'set id' bit on the file being executed i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def geteuid() -> int:
    """Mock: .. index:: single: user; effective id Return the current process's effective user id. .. availability:: Unix, not WASI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getgid() -> int:
    """Mock: .. index:: single: process; group Return the real group id of the current process. .. availability:: Unix. The function ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getgrouplist(user: int, group: int) -> int:
    """Mock: Return list of group ids that *user* belongs to. If *group* is not in the list, it is included; typically, *group* is sp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getgroups() -> int:
    """Mock: Return list of supplemental group ids associated with the current process. .. availability:: Unix, not WASI. .. note:: O..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getlogin() -> int:
    """Mock: Return the name of the user logged in on the controlling terminal of the process.  For most purposes, it is more useful ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpgid(pid: int) -> int:
    """Mock: Return the process group id of the process with process id *pid*. If *pid* is 0, the process group id of the current pro..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpgrp() -> int:
    """Mock: .. index:: single: process; group Return the id of the current process group. .. availability:: Unix, not WASI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpid() -> int:
    """Mock: .. index:: single: process; id Return the current process id. The function is a stub on WASI, see :ref:`wasm-availabilit..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getppid() -> int:
    """Mock: .. index:: single: process; id of parent Return the parent's process id.  When the parent process has exited, on Unix th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpriority(which: int, who: int) -> int:
    """Mock: .. index:: single: process; scheduling priority Get program scheduling priority.  The value *which* is one of :const:`PR..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getresuid() -> int:
    """Mock: Return a tuple (ruid, euid, suid) denoting the current process's real, effective, and saved user ids. .. availability:: ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getresgid() -> int:
    """Mock: Return a tuple (rgid, egid, sgid) denoting the current process's real, effective, and saved group ids. .. availability::..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getuid() -> int:
    """Mock: .. index:: single: user; id Return the current process's real user id. .. availability:: Unix. The function is a stub on..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def initgroups(username: int, gid: int) -> int:
    """Mock: Call the system ``initgroups()`` to initialize the group access list with all of the groups of which the specified usern..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def putenv(key: int, value: int) -> int:
    """Mock: .. index:: single: environment variables; setting Set the environment variable named *key* to the string *value*.  Such ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setegid(egid: int) -> int:
    """Mock: Set the current process's effective group id. .. availability:: Unix, not WASI, not Android."""
    return 0

#@ \trusted
#@ ensures \result == 0
def seteuid(euid: int) -> int:
    """Mock: Set the current process's effective user id. .. availability:: Unix, not WASI, not Android."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setgid(gid: int) -> int:
    """Mock: Set the current process' group id. .. availability:: Unix, not WASI, not Android."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setgroups(groups: int) -> int:
    """Mock: Set the list of supplemental group ids associated with the current process to *groups*. *groups* must be a sequence, and..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setns(fd: int, nstype: int) -> int:
    """Mock: Reassociate the current thread with a Linux namespace. See the :manpage:`setns(2)` and :manpage:`namespaces(7)` man page..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setpgrp() -> int:
    """Mock: Call the system call :c:func:`!setpgrp` or ``setpgrp(0, 0)`` depending on which version is implemented (if any).  See th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setpgid(pid: int, pgrp: int) -> int:
    """Mock: Call the system call :c:func:`!setpgid` to set the process group id of the process with id *pid* to the process group wi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setpriority(which: int, who: int, priority: int) -> int:
    """Mock: .. index:: single: process; scheduling priority Set program scheduling priority. The value *which* is one of :const:`PRI..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setregid(rgid: int, egid: int) -> int:
    """Mock: Set the current process's real and effective group ids. .. availability:: Unix, not WASI, not Android."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setresgid(rgid: int, egid: int, sgid: int) -> int:
    """Mock: Set the current process's real, effective, and saved group ids. .. availability:: Unix, not WASI, not Android. .. versio..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setresuid(ruid: int, euid: int, suid: int) -> int:
    """Mock: Set the current process's real, effective, and saved user ids. .. availability:: Unix, not WASI, not Android. .. version..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setreuid(ruid: int, euid: int) -> int:
    """Mock: Set the current process's real and effective user ids. .. availability:: Unix, not WASI, not Android."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsid(pid: int) -> int:
    """Mock: Call the system call :c:func:`!getsid`.  See the Unix manual for the semantics. .. availability:: Unix, not WASI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setsid() -> int:
    """Mock: Call the system call :c:func:`!setsid`.  See the Unix manual for the semantics. .. availability:: Unix, not WASI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setuid(uid: int) -> int:
    """Mock: .. index:: single: user; id, setting Set the current process's user id. .. availability:: Unix, not WASI, not Android."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strerror(code: int) -> int:
    """Mock: Return the error message corresponding to the error code in *code*. On platforms where :c:func:`!strerror` returns ``NUL..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def umask(mask: int) -> int:
    """Mock: Set the current numeric umask and return the previous umask. The function is a stub on WASI, see :ref:`wasm-availability..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uname() -> int:
    """Mock: .. index:: single: gethostname() (in module socket) single: gethostbyaddr() (in module socket) Returns information ident..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unsetenv(key: int) -> int:
    """Mock: .. index:: single: environment variables; deleting Unset (delete) the environment variable named *key*. Such changes to ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unshare(flags: int) -> int:
    """Mock: Disassociate parts of the process execution context, and move them into a newly created namespace. See the :manpage:`uns..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fdopen(fd: int) -> int:
    """Mock: Return an open file object connected to the file descriptor *fd*.  This is an alias of the :func:`open` built-in functio..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def close(fd: int) -> int:
    """Mock: Close file descriptor *fd*. .. note:: This function is intended for low-level I/O and must be applied to a file descript..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def closerange(fd_low: int, fd_high: int) -> int:
    """Mock: Close all file descriptors from *fd_low* (inclusive) to *fd_high* (exclusive), ignoring errors. Equivalent to (but much ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy_file_range(src: int, dst: int, count: int, offset_src: int, offset_dst: int) -> int:
    """Mock: Copy *count* bytes from file descriptor *src*, starting from offset *offset_src*, to file descriptor *dst*, starting fro..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def device_encoding(fd: int) -> int:
    """Mock: Return a string describing the encoding of the device associated with *fd* if it is connected to a terminal; else return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dup(fd: int) -> int:
    """Mock: Return a duplicate of file descriptor *fd*. The new file descriptor is :ref:`non-inheritable <fd_inheritance>`. On Windo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dup2(fd: int, fd2: int, inheritable: int) -> int:
    """Mock: Duplicate file descriptor *fd* to *fd2*, closing the latter first if necessary. Return *fd2*. The new file descriptor is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fchmod(fd: int, mode: int) -> int:
    """Mock: Change the mode of the file given by *fd* to the numeric *mode*.  See the docs for :func:`chmod` for possible values of ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fchown(fd: int, uid: int, gid: int) -> int:
    """Mock: Change the owner and group id of the file given by *fd* to the numeric *uid* and *gid*.  To leave one of the ids unchang..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fdatasync(fd: int) -> int:
    """Mock: Force write of file with filedescriptor *fd* to disk. Does not force update of metadata. .. availability:: Unix. .. note..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fpathconf(fd: int, name: int) -> int:
    """Mock: Return system configuration information relevant to an open file. *name* specifies the configuration value to retrieve; ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fstat(fd: int) -> int:
    """Mock: Get the status of the file descriptor *fd*. Return a :class:`stat_result` object. As of Python 3.3, this is equivalent t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fstatvfs(fd: int) -> int:
    """Mock: Return information about the filesystem containing the file associated with file descriptor *fd*, like :func:`statvfs`. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fsync(fd: int) -> int:
    """Mock: Force write of file with filedescriptor *fd* to disk.  On Unix, this calls the native :c:func:`!fsync` function; on Wind..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ftruncate(fd: int, length: int) -> int:
    """Mock: Truncate the file corresponding to file descriptor *fd*, so that it is at most *length* bytes in size.  As of Python 3.3..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_blocking(fd: int) -> int:
    """Mock: Get the blocking mode of the file descriptor: ``False`` if the :data:`O_NONBLOCK` flag is set, ``True`` if the flag is c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def grantpt(fd: int) -> int:
    """Mock: Grant access to the slave pseudo-terminal device associated with the master pseudo-terminal device to which the file des..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isatty(fd: int) -> int:
    """Mock: Return ``True`` if the file descriptor *fd* is open and connected to a tty(-like) device, else ``False``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lockf(fd: int, cmd: int, len: int) -> int:
    """Mock: Apply, test or remove a POSIX lock on an open file descriptor. *fd* is an open file descriptor. *cmd* specifies the comm..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def login_tty(fd: int) -> int:
    """Mock: Prepare the tty of which fd is a file descriptor for a new login session. Make the calling process a session leader; mak..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lseek(fd: int, pos: int, whence: int) -> int:
    """Mock: Set the current position of file descriptor *fd* to position *pos*, modified by *whence*, and return the new position in..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open(path: int, flags: int, mode: int, dir_fd: int) -> int:
    """Mock: Open the file *path* and set various flags according to *flags* and possibly its mode according to *mode*.  When computi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def openpty() -> int:
    """Mock: .. index:: pair: module; pty Open a new pseudo-terminal pair. Return a pair of file descriptors ``(master, slave)`` for ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pipe() -> int:
    """Mock: Create a pipe.  Return a pair of file descriptors ``(r, w)`` usable for reading and writing, respectively. The new file ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pipe2(flags: int) -> int:
    """Mock: Create a pipe with *flags* set atomically. *flags* can be constructed by ORing together one or more of these values: :da..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def posix_fallocate(fd: int, offset: int, len: int) -> int:
    """Mock: Ensures that enough disk space is allocated for the file specified by *fd* starting from *offset* and continuing for *le..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def posix_fadvise(fd: int, offset: int, len: int, advice: int) -> int:
    """Mock: Announces an intention to access data in a specific pattern thus allowing the kernel to make optimizations. The advice a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pread(fd: int, n: int, offset: int) -> int:
    """Mock: Read at most *n* bytes from file descriptor *fd* at a position of *offset*, leaving the file offset unchanged. Return a ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def posix_openpt(oflag: int) -> int:
    """Mock: Open and return a file descriptor for a master pseudo-terminal device. Calls the C standard library function :c:func:`po..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def preadv(fd: int, buffers: int, offset: int, flags: int) -> int:
    """Mock: Read from a file descriptor *fd* at a position of *offset* into mutable :term:`bytes-like objects <bytes-like object>` *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ptsname(fd: int) -> int:
    """Mock: Return the name of the slave pseudo-terminal device associated with the master pseudo-terminal device to which the file ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pwrite(fd: int, str: int, offset: int) -> int:
    """Mock: Write the bytestring in *str* to file descriptor *fd* at position of *offset*, leaving the file offset unchanged. Return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pwritev(fd: int, buffers: int, offset: int, flags: int) -> int:
    """Mock: Write the *buffers* contents to file descriptor *fd* at an offset *offset*, leaving the file offset unchanged.  *buffers..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read(fd: int, n: int) -> int:
    """Mock: Read at most *n* bytes from file descriptor *fd*. Return a bytestring containing the bytes read. If the end of the file ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def readinto(fd: int, buffer: int) -> int:
    """Mock: Read from a file descriptor *fd* into a mutable :ref:`buffer object <bufferobjects>` *buffer*. The *buffer* should be mu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sendfile(out_fd: int, in_fd: int, offset: int, count: int) -> int:
    """Mock: Copy *count* bytes from file descriptor *in_fd* to file descriptor *out_fd* starting at *offset*. Return the number of b..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_blocking(fd: int, blocking: int) -> int:
    """Mock: Set the blocking mode of the specified file descriptor. Set the :data:`O_NONBLOCK` flag if blocking is ``False``, clear ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def splice(src: int, dst: int, count: int, offset_src: int, offset_dst: int, flags: int) -> int:
    """Mock: Transfer *count* bytes from file descriptor *src*, starting from offset *offset_src*, to file descriptor *dst*, starting..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def readv(fd: int, buffers: int) -> int:
    """Mock: Read from a file descriptor *fd* into a number of mutable :term:`bytes-like objects <bytes-like object>` *buffers*. Tran..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcgetpgrp(fd: int) -> int:
    """Mock: Return the process group associated with the terminal given by *fd* (an open file descriptor as returned by :func:`os.op..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tcsetpgrp(fd: int, pg: int) -> int:
    """Mock: Set the process group associated with the terminal given by *fd* (an open file descriptor as returned by :func:`os.open`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ttyname(fd: int) -> int:
    """Mock: Return a string which specifies the terminal device associated with file descriptor *fd*.  If *fd* is not associated wit..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unlockpt(fd: int) -> int:
    """Mock: Unlock the slave pseudo-terminal device associated with the master pseudo-terminal device to which the file descriptor *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def write(fd: int, str: int) -> int:
    """Mock: Write the bytestring in *str* to file descriptor *fd*. Return the number of bytes actually written. .. note:: This funct..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def writev(fd: int, buffers: int) -> int:
    """Mock: Write the contents of *buffers* to file descriptor *fd*. *buffers* must be a sequence of :term:`bytes-like objects <byte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_terminal_size(fd: int) -> int:
    """Mock: Return the size of the terminal window as ``(columns, lines)``, tuple of type :class:`terminal_size`. The optional argum..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_inheritable(fd: int) -> int:
    """Mock: Get the 'inheritable' flag of the specified file descriptor (a boolean)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_inheritable(fd: int, inheritable: int) -> int:
    """Mock: Set the 'inheritable' flag of the specified file descriptor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_handle_inheritable(handle: int) -> int:
    """Mock: Get the 'inheritable' flag of the specified handle (a boolean). .. availability:: Windows."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_handle_inheritable(handle: int, inheritable: int) -> int:
    """Mock: Set the 'inheritable' flag of the specified handle. .. availability:: Windows."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def access(path: int, mode: int, dir_fd: int, effective_ids: int, follow_symlinks: int) -> int:
    """Mock: Use the real uid/gid to test for access to *path*.  Note that most operations will use the effective uid/gid, therefore ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chdir(path: int) -> int:
    """Mock: .. index:: single: directory; changing Change the current working directory to *path*. This function can support :ref:`s..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chflags(path: int, flags: int, follow_symlinks: int) -> int:
    """Mock: Set the flags of *path* to the numeric *flags*. *flags* may take a combination (bitwise OR) of the following values (as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chmod(path: int, mode: int, dir_fd: int, follow_symlinks: int) -> int:
    """Mock: Change the mode of *path* to the numeric *mode*. *mode* may take one of the following values (as defined in the :mod:`st..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chown(path: int, uid: int, gid: int, dir_fd: int, follow_symlinks: int) -> int:
    """Mock: Change the owner and group id of *path* to the numeric *uid* and *gid*.  To leave one of the ids unchanged, set it to -1..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def chroot(path: int) -> int:
    """Mock: Change the root directory of the current process to *path*. .. availability:: Unix, not WASI, not Android. .. versioncha..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fchdir(fd: int) -> int:
    """Mock: Change the current working directory to the directory represented by the file descriptor *fd*.  The descriptor must refe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getcwd() -> int:
    """Mock: Return a string representing the current working directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getcwdb() -> int:
    """Mock: Return a bytestring representing the current working directory. .. versionchanged:: 3.8 The function now uses the UTF-8 ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def lchflags(path: int, flags: int) -> int:
    """Mock: Set the flags of *path* to the numeric *flags*, like :func:`chflags`, but do not follow symbolic links.  As of Python 3...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lchmod(path: int, mode: int) -> int:
    """Mock: Change the mode of *path* to the numeric *mode*. If path is a symlink, this affects the symlink rather than the target. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lchown(path: int, uid: int, gid: int) -> int:
    """Mock: Change the owner and group id of *path* to the numeric *uid* and *gid*.  This function will not follow symbolic links.  ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def link(src: int, dst: int, src_dir_fd: int, dst_dir_fd: int, follow_symlinks: int) -> int:
    """Mock: Create a hard link pointing to *src* named *dst*. This function can support specifying *src_dir_fd* and/or *dst_dir_fd* ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listdir(path: int) -> int:
    """Mock: Return a list containing the names of the entries in the directory given by *path*.  The list is in arbitrary order, and..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listdrives() -> int:
    """Mock: Return a list containing the names of drives on a Windows system. A drive name typically looks like ``'C:\\'``. Not ever..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listmounts(volume: int) -> int:
    """Mock: Return a list containing the mount points for a volume on a Windows system. *volume* must be represented as a GUID path,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listvolumes() -> int:
    """Mock: Return a list containing the volumes in the system. Volumes are typically represented as a GUID path that looks like ``\..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lstat(path: int, dir_fd: int) -> int:
    """Mock: Perform the equivalent of an :c:func:`!lstat` system call on the given path. Similar to :func:`~os.stat`, but does not f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def mkdir(path: int, mode: int, dir_fd: int) -> int:
    """Mock: Create a directory named *path* with numeric mode *mode*. If the directory already exists, :exc:`FileExistsError` is rai..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def makedirs(name: int, mode: int, exist_ok: int) -> int:
    """Mock: .. index:: single: directory; creating single: UNC paths; and os.makedirs() Recursive directory creation function.  Like..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mkfifo(path: int, mode: int, dir_fd: int) -> int:
    """Mock: Create a FIFO (a named pipe) named *path* with numeric mode *mode*. The current umask value is first masked out from the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mknod(path: int, mode: int, device: int, dir_fd: int) -> int:
    """Mock: Create a filesystem node (file, device special file or named pipe) named *path*. *mode* specifies both the permissions t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def major(device: int) -> int:
    """Mock: Extract the device major number from a raw device number (usually the :attr:`~stat_result.st_dev` or :attr:`~stat_result..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def minor(device: int) -> int:
    """Mock: Extract the device minor number from a raw device number (usually the :attr:`~stat_result.st_dev` or :attr:`~stat_result..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def makedev(major: int, minor: int) -> int:
    """Mock: Compose a raw device number from the major and minor device numbers."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pathconf(path: int, name: int) -> int:
    """Mock: Return system configuration information relevant to a named file. *name* specifies the configuration value to retrieve; ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def readlink(path: int, dir_fd: int) -> int:
    """Mock: Return a string representing the path to which the symbolic link points.  The result may be either an absolute or relati..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def remove(path: int, dir_fd: int) -> int:
    """Mock: Remove (delete) the file *path*.  If *path* is a directory, an :exc:`OSError` is raised.  Use :func:`rmdir` to remove di..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def removedirs(name: int) -> int:
    """Mock: .. index:: single: directory; deleting Remove directories recursively.  Works like :func:`rmdir` except that, if the lea..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def rename(src: int, dst: int, src_dir_fd: int, dst_dir_fd: int) -> int:
    """Mock: Rename the file or directory *src* to *dst*. If *dst* exists, the operation will fail with an :exc:`OSError` subclass in..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def renames(old_: int, new: int) -> int:
    """Mock: Recursive directory or file renaming function. Works like :func:`rename`, except creation of any intermediate directorie..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def replace(src: int, dst: int, src_dir_fd: int, dst_dir_fd: int) -> int:
    """Mock: Rename the file or directory *src* to *dst*.  If *dst* is a non-empty directory, :exc:`OSError` will be raised.  If *dst..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def rmdir(path: int, dir_fd: int) -> int:
    """Mock: Remove (delete) the directory *path*.  If the directory does not exist or is not empty, a :exc:`FileNotFoundError` or an..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def scandir(path: int) -> int:
    """Mock: Return an iterator of :class:`os.DirEntry` objects corresponding to the entries in the directory given by *path*. The en..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stat(path: int, dir_fd: int, follow_symlinks: int) -> int:
    """Mock: Get the status of a file or a file descriptor. Perform the equivalent of a :c:func:`stat` system call on the given path...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def statx(path: int, mask: int, flags: int, dir_fd: int, follow_symlinks: int) -> int:
    """Mock: Get the status of a file or file descriptor by performing a :c:func:`!statx` system call on the given path. *path* is a ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def statvfs(path: int) -> int:
    """Mock: Perform a :c:func:`!statvfs` system call on the given path.  The return value is an object whose attributes describe the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def symlink(src: int, dst: int, target_is_directory: int, dir_fd: int) -> int:
    """Mock: Create a symbolic link pointing to *src* named *dst*. The *src* parameter refers to the target of the link (the file or ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sync() -> int:
    """Mock: Force write of everything to disk. .. availability:: Unix. .. versionadded:: 3.3"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def truncate(path: int, length: int) -> int:
    """Mock: Truncate the file corresponding to *path*, so that it is at most *length* bytes in size. This function can support :ref:..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unlink(path: int, dir_fd: int) -> int:
    """Mock: Remove (delete) the file *path*.  This function is semantically identical to :func:`remove`; the ``unlink`` name is its ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def utime(path: int, times: int, ns: int, dir_fd: int, follow_symlinks: int) -> int:
    """Mock: Set the access and modified times of the file specified by *path*. :func:`utime` takes two optional parameters, *times* ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def walk(top: int, topdown: int, onerror: int, followlinks: int) -> int:
    """Mock: .. index:: single: directory; walking single: directory; traversal Generate the file names in a directory tree by walkin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fwalk(top: int, topdown: int, onerror: int, follow_symlinks: int, dir_fd: int) -> int:
    """Mock: .. index:: single: directory; walking single: directory; traversal This behaves exactly like :func:`walk`, except that i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def memfd_create(name: int, flags: int) -> int:
    """Mock: Create an anonymous file and return a file descriptor that refers to it. *flags* must be one of the ``os.MFD_*`` constan..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def eventfd(initval: int, flags: int) -> int:
    """Mock: Create and return an event file descriptor. The file descriptors supports raw :func:`read` and :func:`write` with a buff..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def eventfd_read(fd: int) -> int:
    """Mock: Read value from an :func:`eventfd` file descriptor and return a 64 bit unsigned int. The function does not verify that *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def eventfd_write(fd: int, value: int) -> int:
    """Mock: Add value to an :func:`eventfd` file descriptor. *value* must be a 64 bit unsigned int. The function does not verify tha..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_create(clockid: int, flags: int) -> int:
    """Mock: Create and return a timer file descriptor (*timerfd*). The file descriptor returned by :func:`timerfd_create` supports: ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_settime(fd: int, flags: int, initial: int, interval: int) -> int:
    """Mock: Alter a timer file descriptor's internal timer. This function operates the same interval timer as :func:`timerfd_settime..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_settime_ns(fd: int, flags: int, initial: int, interval: int) -> int:
    """Mock: Similar to :func:`timerfd_settime`, but use time as nanoseconds. This function operates the same interval timer as :func..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_gettime(fd: int) -> int:
    """Mock: Return a two-item tuple of floats (``next_expiration``, ``interval``). ``next_expiration`` denotes the relative time unt..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_gettime_ns(fd: int) -> int:
    """Mock: Similar to :func:`timerfd_gettime`, but return time as nanoseconds. .. availability:: Linux >= 2.6.27 with glibc >= 2.8 ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getxattr(path: int, attribute: int, follow_symlinks: int) -> int:
    """Mock: Return the value of the extended filesystem attribute *attribute* for *path*. *attribute* can be bytes or str (directly ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listxattr(path: int, follow_symlinks: int) -> int:
    """Mock: Return a list of the extended filesystem attributes on *path*.  The attributes in the list are represented as strings de..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def removexattr(path: int, attribute: int, follow_symlinks: int) -> int:
    """Mock: Removes the extended filesystem attribute *attribute* from *path*. *attribute* should be bytes or str (directly or indir..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setxattr(path: int, attribute: int, value: int, flags: int, follow_symlinks: int) -> int:
    """Mock: Set the extended filesystem attribute *attribute* on *path* to *value*. *attribute* must be a bytes or str with no embed..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def abort() -> int:
    """Mock: Generate a :const:`~signal.SIGABRT` signal to the current process.  On Unix, the default behavior is to produce a core d..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def add_dll_directory(path: int) -> int:
    """Mock: Add a path to the DLL search path. This search path is used when resolving dependencies for imported extension modules (..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def execl(path: int, arg0: int, arg1: int, ___: int) -> int:
    """Mock: These functions all execute a new program, replacing the current process; they do not return.  On Unix, the new executab..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _exit(n: int) -> int:
    """Mock: Exit the process with status *n*, without calling cleanup handlers, flushing stdio buffers, etc. .. note:: The standard ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fork() -> int:
    """Mock: Fork a child process.  Return ``0`` in the child and the child's process id in the parent.  If an error occurs :exc:`OSE..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def forkpty() -> int:
    """Mock: Fork a child process, using a new pseudo-terminal as the child's controlling terminal. Return a pair of ``(pid, fd)``, w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def kill(pid: int, sig: int) -> int:
    """Mock: .. index:: single: process; killing single: process; signalling Send signal *sig* to the process *pid*.  Constants for t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def killpg(pgid: int, sig: int) -> int:
    """Mock: .. index:: single: process; killing single: process; signalling Send the signal *sig* to the process group *pgid*. .. au..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nice(increment: int) -> int:
    """Mock: Add *increment* to the process's 'niceness'.  Return the new niceness. .. availability:: Unix, not WASI."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pidfd_open(pid: int, flags: int) -> int:
    """Mock: Return a file descriptor referring to the process *pid* with *flags* set. This descriptor can be used to perform process..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def plock(op: int) -> int:
    """Mock: Lock program segments into memory.  The value of *op* (defined in ``<sys/lock.h>``) determines which segments are locked..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def popen(cmd: int, mode: int, buffering: int) -> int:
    """Mock: Open a pipe to or from command *cmd*. The return value is an open file object connected to the pipe, which can be read o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def posix_spawn(path: int, argv: int, env: int, file_actions: int, __setpgroup: int, resetids: int, setsid: int) -> int:
    """Mock: Wraps the :c:func:`!posix_spawn` C library API for use from Python. Most users should use :func:`subprocess.run` instead..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def posix_spawnp(path: int, argv: int, env: int, file_actions: int, __setpgroup: int, resetids: int, setsid: int) -> int:
    """Mock: Wraps the :c:func:`!posix_spawnp` C library API for use from Python. Similar to :func:`posix_spawn` except that the syst..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_at_fork(before: int, after_in_parent: int, __after_in_child: int) -> int:
    """Mock: Register callables to be executed when a new child process is forked using :func:`os.fork` or similar process cloning AP..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnl(mode: int, path: int, ___: int) -> int:
    """Mock: Execute the program *path* in a new process. (Note that the :mod:`subprocess` module provides more powerful facilities f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def startfile(path: int, operation: int, arguments: int, cwd: int, show_cmd: int) -> int:
    """Mock: Start a file with its associated application. When *operation* is not specified, this acts like double-clicking the file..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def system(command: int) -> int:
    """Mock: Execute the command (a string) in a subshell.  This is implemented by calling the Standard C function :c:func:`system`, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def times() -> int:
    """Mock: Returns the current global process times. The return value is an object with five attributes: * :attr:`!user` - user tim..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait() -> int:
    """Mock: Wait for completion of a child process, and return a tuple containing its pid and exit status indication: a 16-bit numbe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def waitid(idtype: int, id: int, options: int) -> int:
    """Mock: Wait for the completion of a child process. *idtype* can be :data:`P_PID`, :data:`P_PGID`, :data:`P_ALL`, or (on Linux) ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def waitpid(pid: int, options: int) -> int:
    """Mock: The details of this function differ on Unix and Windows. On Unix: Wait for completion of a child process given by proces..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait3(options: int) -> int:
    """Mock: Similar to :func:`waitpid`, except no process id argument is given and a 3-element tuple containing the child's process ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait4(pid: int, options: int) -> int:
    """Mock: Similar to :func:`waitpid`, except a 3-element tuple, containing the child's process id, exit status indication, and res..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def waitstatus_to_exitcode(status: int) -> int:
    """Mock: Convert a wait status to an exit code. On Unix: * If the process exited normally (if ``WIFEXITED(status)`` is true), ret..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def WCOREDUMP(status: int) -> int:
    """Mock: Return ``True`` if a core dump was generated for the process, otherwise return ``False``. This function should be employ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def WIFCONTINUED(status: int) -> int:
    """Mock: Return ``True`` if a stopped child has been resumed by delivery of :const:`~signal.SIGCONT` (if the process has been con..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def WIFSTOPPED(status: int) -> int:
    """Mock: Return ``True`` if the process was stopped by delivery of a signal, otherwise return ``False``. :func:`WIFSTOPPED` only ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def WIFSIGNALED(status: int) -> int:
    """Mock: Return ``True`` if the process was terminated by a signal, otherwise return ``False``. .. availability:: Unix, not WASI,..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def WIFEXITED(status: int) -> int:
    """Mock: Return ``True`` if the process exited terminated normally, that is, by calling ``exit()`` or ``_exit()``, or by returnin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WEXITSTATUS(status: int) -> int:
    """Mock: Return the process exit status. This function should be employed only if :func:`WIFEXITED` is true. .. availability:: Un..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WSTOPSIG(status: int) -> int:
    """Mock: Return the signal which caused the process to stop. This function should be employed only if :func:`WIFSTOPPED` is true...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WTERMSIG(status: int) -> int:
    """Mock: Return the number of the signal that caused the process to terminate. This function should be employed only if :func:`WI..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_get_priority_min(policy: int) -> int:
    """Mock: Get the minimum priority value for *policy*. *policy* is one of the scheduling policy constants above."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_get_priority_max(policy: int) -> int:
    """Mock: Get the maximum priority value for *policy*. *policy* is one of the scheduling policy constants above."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_setscheduler(pid: int, policy: int, param: int) -> int:
    """Mock: Set the scheduling policy for the process with PID *pid*. A *pid* of 0 means the calling process. *policy* is one of the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_getscheduler(pid: int) -> int:
    """Mock: Return the scheduling policy for the process with PID *pid*. A *pid* of 0 means the calling process. The result is one o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_setparam(pid: int, param: int) -> int:
    """Mock: Set the scheduling parameters for the process with PID *pid*. A *pid* of 0 means the calling process. *param* is a :clas..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_getparam(pid: int) -> int:
    """Mock: Return the scheduling parameters as a :class:`sched_param` instance for the process with PID *pid*. A *pid* of 0 means t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_rr_get_interval(pid: int) -> int:
    """Mock: Return the round-robin quantum in seconds for the process with PID *pid*. A *pid* of 0 means the calling process."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_yield() -> int:
    """Mock: Voluntarily relinquish the CPU. See :manpage:`sched_yield(2)` for details."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_setaffinity(pid: int, mask: int) -> int:
    """Mock: Restrict the process with PID *pid* (or the current process if zero) to a set of CPUs.  *mask* is an iterable of integer..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_getaffinity(pid: int) -> int:
    """Mock: Return the set of CPUs the process with PID *pid* is restricted to. If *pid* is zero, return the set of CPUs the calling..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def confstr(name: int) -> int:
    """Mock: Return string-valued system configuration values. *name* specifies the configuration value to retrieve; it may be a stri..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cpu_count() -> int:
    """Mock: Return the number of logical CPUs in the **system**. Returns ``None`` if undetermined. The :func:`process_cpu_count` fun..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getloadavg() -> int:
    """Mock: Return the number of processes in the system run queue averaged over the last 1, 5, and 15 minutes or raises :exc:`OSErr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def process_cpu_count() -> int:
    """Mock: Get the number of logical CPUs usable by the calling thread of the **current process**. Returns ``None`` if undetermined..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sysconf(name: int) -> int:
    """Mock: Return integer-valued system configuration values. If the configuration value specified by *name* isn't defined, ``-1`` ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrandom(size: int, flags: int) -> int:
    """Mock: Get up to *size* random bytes. The function can return less bytes than requested. These bytes can be used to seed user-s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urandom(size: int) -> int:
    """Mock: Return a bytestring of *size* random bytes suitable for cryptographic use. This function returns random bytes from an OS..."""
    return 0
