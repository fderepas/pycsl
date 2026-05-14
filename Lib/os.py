"""PyCSL mock for Python's os module.

Provides trusted stubs for OS-level functions: process management,
file descriptors, file/directory operations, path utilities,
environment access, scheduler, extended attributes, and more.
Side-effect functions ensure result == 0; functions returning file
descriptors, PIDs, sizes, or handles ensure result >= 0; path/string
returns use str.
"""
_ = 0  # anchor

# ── Process management: exec family ─────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def execl(path: int, arg0: int) -> int:
    """Mock: execute program, replacing current process."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execle(path: int, arg0: int, env: int) -> int:
    """Mock: execute program with environment."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execlp(file: int, arg0: int) -> int:
    """Mock: execute program, searching PATH."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execlpe(file: int, arg0: int, env: int) -> int:
    """Mock: execute program, searching PATH, with environment."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execv(path: int, args: int) -> int:
    """Mock: execute program with argument list."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execve(path: int, args: int, env: int) -> int:
    """Mock: execute program with argument list and environment."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execvp(file: int, args: int) -> int:
    """Mock: execute program, searching PATH, with argument list."""
    return 0

#@ \trusted
#@ ensures \result == 0
def execvpe(file: int, args: int, env: int) -> int:
    """Mock: execute program, searching PATH, with args and environment."""
    return 0

# ── Process management: fork / exit / kill ───────────────────────────

#@ \trusted
#@ ensures \result == 0
def _exit(n: int) -> int:
    """Mock: exit process immediately."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fork() -> int:
    """Mock: fork a child process, returns PID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def forkpty() -> int:
    """Mock: fork with pseudo-terminal, returns PID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def kill(pid: int, sig: int) -> int:
    """Mock: send signal to process."""
    return 0

#@ \trusted
#@ ensures \result == 0
def killpg(pgid: int, sig: int) -> int:
    """Mock: send signal to process group."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nice(increment: int) -> int:
    """Mock: add increment to process niceness, returns new niceness."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pidfd_open(pid: int, flags: int) -> int:
    """Mock: obtain file descriptor referring to a process."""
    return 0

#@ \trusted
#@ ensures \result == 0
def plock(op: int) -> int:
    """Mock: lock program segments into memory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def popen(cmd: int, mode: int) -> int:
    """Mock: open pipe to/from a command, returns file object handle."""
    return 0

# ── Process management: spawn family ────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def spawnl(mode: int, path: int, arg0: int) -> int:
    """Mock: spawn new process."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnle(mode: int, path: int, arg0: int, env: int) -> int:
    """Mock: spawn new process with environment."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnlp(mode: int, file: int, arg0: int) -> int:
    """Mock: spawn new process, searching PATH."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnlpe(mode: int, file: int, arg0: int, env: int) -> int:
    """Mock: spawn new process, searching PATH, with environment."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnv(mode: int, path: int, args: int) -> int:
    """Mock: spawn new process with argument list."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnve(mode: int, path: int, args: int, env: int) -> int:
    """Mock: spawn new process with argument list and environment."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnvp(mode: int, file: int, args: int) -> int:
    """Mock: spawn new process, searching PATH, with argument list."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawnvpe(mode: int, file: int, args: int, env: int) -> int:
    """Mock: spawn new process, searching PATH, with args and environment."""
    return 0

#@ \trusted
#@ ensures \result == 0
def startfile(path: int) -> int:
    """Mock: start a file with its associated application (Windows)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def system(command: int) -> int:
    """Mock: execute command in a subshell, returns exit status."""
    return 0

# ── Process management: wait family ─────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def times() -> int:
    """Mock: returns process times as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait() -> int:
    """Mock: wait for child process, returns PID and status."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def waitid(idtp: int, ident: int, options: int) -> int:
    """Mock: wait for child process by ID type."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def waitpid(pid: int, options: int) -> int:
    """Mock: wait for specific child process."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait3(options: int) -> int:
    """Mock: wait for child with resource usage info."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait4(pid: int, options: int) -> int:
    """Mock: wait for specific child with resource usage info."""
    return 0

#@ \trusted
#@ ensures \result == 0
def abort() -> int:
    """Mock: generate SIGABRT signal to current process."""
    return 0

# ── Process management: posix_spawn ─────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def posix_spawn(path: int, file_actions: int, attr: int, argv: int, env: int) -> int:
    """Mock: spawn a new process (posix_spawn), returns PID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def posix_spawnp(path: int, file_actions: int, attr: int, argv: int, env: int) -> int:
    """Mock: spawn a new process searching PATH, returns PID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def register_at_fork(before: int, after_in_parent: int, after_in_child: int) -> int:
    """Mock: register callables to be called around fork."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def waitstatus_to_exitcode(status: int) -> int:
    """Mock: convert wait status to exit code."""
    return 0

# ── Process IDs and session ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getpid() -> int:
    """Mock: returns current process ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getppid() -> int:
    """Mock: returns parent process ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpgrp() -> int:
    """Mock: returns current process group ID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setpgrp() -> int:
    """Mock: set process group ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getpgid(pid: int) -> int:
    """Mock: returns process group ID for given process."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setpgid(pid: int, pgrp: int) -> int:
    """Mock: set process group ID for given process."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsid(pid: int) -> int:
    """Mock: returns session ID for given process."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setsid() -> int:
    """Mock: create new session, returns session ID."""
    return 0

# ── Process UIDs / GIDs ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getuid() -> int:
    """Mock: returns real user ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getgid() -> int:
    """Mock: returns real group ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def geteuid() -> int:
    """Mock: returns effective user ID."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getegid() -> int:
    """Mock: returns effective group ID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setuid(uid: int) -> int:
    """Mock: set real user ID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setgid(gid: int) -> int:
    """Mock: set real group ID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def seteuid(euid: int) -> int:
    """Mock: set effective user ID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setegid(egid: int) -> int:
    """Mock: set effective group ID."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setreuid(ruid: int, euid: int) -> int:
    """Mock: set real and effective user IDs."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setregid(rgid: int, egid: int) -> int:
    """Mock: set real and effective group IDs."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getresuid() -> int:
    """Mock: returns real, effective, and saved user IDs."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getresgid() -> int:
    """Mock: returns real, effective, and saved group IDs."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setresuid(ruid: int, euid: int, suid: int) -> int:
    """Mock: set real, effective, and saved user IDs."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setresgid(rgid: int, egid: int, sgid: int) -> int:
    """Mock: set real, effective, and saved group IDs."""
    return 0

#@ \trusted
def getlogin() -> str:
    """Mock: returns name of user logged in on controlling terminal."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def getgroups() -> int:
    """Mock: returns supplementary group IDs as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setgroups(groups: int) -> int:
    """Mock: set supplementary group IDs."""
    return 0

#@ \trusted
#@ ensures \result == 0
def initgroups(username: int, gid: int) -> int:
    """Mock: initialize group access list."""
    return 0

# ── Process priority ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getpriority(which: int, who: int) -> int:
    """Mock: returns scheduling priority."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setpriority(which: int, who: int, priority: int) -> int:
    """Mock: set scheduling priority."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getloadavg() -> int:
    """Mock: returns system load averages as opaque handle."""
    return 0

# ── Process terminal ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def tcgetpgrp(fd: int) -> int:
    """Mock: returns foreground process group for terminal fd."""
    return 0

#@ \trusted
#@ ensures \result == 0
def tcsetpgrp(fd: int, pgrp: int) -> int:
    """Mock: set foreground process group for terminal fd."""
    return 0

#@ \trusted
def ctermid() -> str:
    """Mock: returns filename of controlling terminal."""
    return ""

# ── Wait status macros ───────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def WCOREDUMP(status: int) -> int:
    """Mock: returns nonzero if core dump was produced."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WEXITSTATUS(status: int) -> int:
    """Mock: returns exit status of child."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WIFCONTINUED(status: int) -> int:
    """Mock: returns nonzero if child was continued."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WIFEXITED(status: int) -> int:
    """Mock: returns nonzero if child exited normally."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WIFSIGNALED(status: int) -> int:
    """Mock: returns nonzero if child was terminated by signal."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WIFSTOPPED(status: int) -> int:
    """Mock: returns nonzero if child was stopped."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WSTOPSIG(status: int) -> int:
    """Mock: returns signal that stopped child."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WTERMSIG(status: int) -> int:
    """Mock: returns signal that terminated child."""
    return 0

# ── File descriptors ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def open(path: int, flags: int, mode: int) -> int:
    """Mock: open file, returns file descriptor."""
    return 0

#@ \trusted
#@ ensures \result == 0
def close(fd: int) -> int:
    """Mock: close file descriptor."""
    return 0

#@ \trusted
#@ ensures \result == 0
def closerange(fd_low: int, fd_high: int) -> int:
    """Mock: close range of file descriptors."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dup(fd: int) -> int:
    """Mock: duplicate file descriptor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dup2(fd: int, fd2: int) -> int:
    """Mock: duplicate file descriptor to given number."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fchmod(fd: int, mode: int) -> int:
    """Mock: change mode of file referred to by fd."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fchown(fd: int, uid: int, gid: int) -> int:
    """Mock: change owner of file referred to by fd."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fdatasync(fd: int) -> int:
    """Mock: force write of file data to disk."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fpathconf(fd: int, name: int) -> int:
    """Mock: returns configurable pathname variable for open file."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fstat(fd: int) -> int:
    """Mock: returns status of file descriptor as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fstatvfs(fd: int) -> int:
    """Mock: returns filesystem info for fd as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fsync(fd: int) -> int:
    """Mock: force write of file to disk."""
    return 0

#@ \trusted
#@ ensures \result == 0
def ftruncate(fd: int, length: int) -> int:
    """Mock: truncate file to specified length."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def isatty(fd: int) -> int:
    """Mock: returns nonzero if fd is connected to a terminal."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lseek(fd: int, pos: int, how: int) -> int:
    """Mock: set file position, returns new position."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read(fd: int, n: int) -> int:
    """Mock: read bytes from fd, returns bytes read count."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def write(fd: int, data: int) -> int:
    """Mock: write bytes to fd, returns bytes written count."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pread(fd: int, n: int, offset: int) -> int:
    """Mock: read from fd at offset without changing position."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pwrite(fd: int, data: int, offset: int) -> int:
    """Mock: write to fd at offset without changing position."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sendfile(out_fd: int, in_fd: int, offset: int, count: int) -> int:
    """Mock: copy data between file descriptors, returns bytes sent."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pipe() -> int:
    """Mock: create pipe, returns read/write fd pair as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pipe2(flags: int) -> int:
    """Mock: create pipe with flags, returns fd pair as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_inheritable(fd: int) -> int:
    """Mock: returns inheritable flag of fd."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_inheritable(fd: int, inheritable: int) -> int:
    """Mock: set inheritable flag of fd."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_blocking(fd: int) -> int:
    """Mock: returns blocking mode of fd."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_blocking(fd: int, blocking: int) -> int:
    """Mock: set blocking mode of fd."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_handle_inheritable(handle: int) -> int:
    """Mock: returns inheritable flag of handle (Windows)."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_handle_inheritable(handle: int, inheritable: int) -> int:
    """Mock: set inheritable flag of handle (Windows)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def openpty() -> int:
    """Mock: open pseudo-terminal pair, returns master/slave fds."""
    return 0

# ── File descriptor: vectored / positional I/O ───────────────────────

#@ \trusted
#@ ensures \result >= 0
def readv(fd: int, buffers: int) -> int:
    """Mock: read into multiple buffers, returns total bytes read."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def writev(fd: int, buffers: int) -> int:
    """Mock: write from multiple buffers, returns total bytes written."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def preadv(fd: int, buffers: int, offset: int) -> int:
    """Mock: read into multiple buffers at offset."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pwritev(fd: int, buffers: int, offset: int) -> int:
    """Mock: write from multiple buffers at offset."""
    return 0

# ── File descriptor: advisory / allocation ───────────────────────────

#@ \trusted
#@ ensures \result == 0
def posix_fadvise(fd: int, offset: int, length: int, advice: int) -> int:
    """Mock: announce intention for file access pattern."""
    return 0

#@ \trusted
#@ ensures \result == 0
def posix_fallocate(fd: int, offset: int, length: int) -> int:
    """Mock: ensure space is allocated for file."""
    return 0

#@ \trusted
#@ ensures \result == 0
def lockf(fd: int, cmd: int, length: int) -> int:
    """Mock: apply or test POSIX lock on open file."""
    return 0

# ── File / directory operations ──────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def access(path: int, mode: int) -> int:
    """Mock: check access permissions, returns nonzero if accessible."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chdir(path: int) -> int:
    """Mock: change current working directory."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chflags(path: int, flags: int) -> int:
    """Mock: set file flags."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chmod(path: int, mode: int) -> int:
    """Mock: change file mode bits."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chown(path: int, uid: int, gid: int) -> int:
    """Mock: change file owner and group."""
    return 0

#@ \trusted
#@ ensures \result == 0
def chroot(path: int) -> int:
    """Mock: change root directory."""
    return 0

#@ \trusted
def getcwd() -> str:
    """Mock: returns current working directory as string."""
    return ""

#@ \trusted
def getcwdb() -> str:
    """Mock: returns current working directory as bytes string."""
    return ""

#@ \trusted
#@ ensures \result == 0
def lchflags(path: int, flags: int) -> int:
    """Mock: set file flags, not following symlinks."""
    return 0

#@ \trusted
#@ ensures \result == 0
def lchmod(path: int, mode: int) -> int:
    """Mock: change file mode, not following symlinks."""
    return 0

#@ \trusted
#@ ensures \result == 0
def lchown(path: int, uid: int, gid: int) -> int:
    """Mock: change file owner, not following symlinks."""
    return 0

#@ \trusted
#@ ensures \result == 0
def link(src: int, dst: int) -> int:
    """Mock: create hard link."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listdir(path: int) -> int:
    """Mock: list directory contents, returns opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lstat(path: int) -> int:
    """Mock: stat without following symlinks, returns opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def mkdir(path: int, mode: int) -> int:
    """Mock: create directory."""
    return 0

#@ \trusted
#@ ensures \result == 0
def makedirs(name: int, mode: int) -> int:
    """Mock: create directory tree recursively."""
    return 0

#@ \trusted
#@ ensures \result == 0
def mkfifo(path: int, mode: int) -> int:
    """Mock: create FIFO (named pipe)."""
    return 0

#@ \trusted
#@ ensures \result == 0
def mknod(path: int, mode: int, device: int) -> int:
    """Mock: create filesystem node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pathconf(path: int, name: int) -> int:
    """Mock: returns configurable pathname variable."""
    return 0

#@ \trusted
def readlink(path: int) -> str:
    """Mock: returns target of symbolic link."""
    return ""

#@ \trusted
#@ ensures \result == 0
def remove(path: int) -> int:
    """Mock: remove file."""
    return 0

#@ \trusted
#@ ensures \result == 0
def removedirs(name: int) -> int:
    """Mock: remove directory tree (leaf to root)."""
    return 0

#@ \trusted
#@ ensures \result == 0
def rename(src: int, dst: int) -> int:
    """Mock: rename file or directory."""
    return 0

#@ \trusted
#@ ensures \result == 0
def renames(old: int, new: int) -> int:
    """Mock: rename with intermediate directory creation."""
    return 0

#@ \trusted
#@ ensures \result == 0
def replace(src: int, dst: int) -> int:
    """Mock: rename file, replacing destination if it exists."""
    return 0

#@ \trusted
#@ ensures \result == 0
def rmdir(path: int) -> int:
    """Mock: remove directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def scandir(path: int) -> int:
    """Mock: returns directory iterator as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stat(path: int) -> int:
    """Mock: returns file status as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def statvfs(path: int) -> int:
    """Mock: returns filesystem statistics as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def symlink(src: int, dst: int) -> int:
    """Mock: create symbolic link."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sync() -> int:
    """Mock: force write of everything to disk."""
    return 0

#@ \trusted
#@ ensures \result == 0
def truncate(path: int, length: int) -> int:
    """Mock: truncate file to specified length."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unlink(path: int) -> int:
    """Mock: remove file (same as remove)."""
    return 0

#@ \trusted
#@ ensures \result == 0
def utime(path: int, times: int) -> int:
    """Mock: set access and modification times."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def walk(top: int) -> int:
    """Mock: generate directory tree, returns opaque iterator handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fwalk(top: int) -> int:
    """Mock: like walk but with file descriptors, returns opaque handle."""
    return 0

# ── Extended attributes ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getxattr(path: int, attribute: int) -> int:
    """Mock: returns value of extended attribute."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setxattr(path: int, attribute: int, v: int, flags: int) -> int:
    """Mock: set extended attribute."""
    return 0

#@ \trusted
#@ ensures \result == 0
def removexattr(path: int, attribute: int) -> int:
    """Mock: remove extended attribute."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def listxattr(path: int) -> int:
    """Mock: list extended attributes, returns opaque handle."""
    return 0

# ── Path operations ──────────────────────────────────────────────────

#@ \trusted
def fspath(path: int) -> str:
    """Mock: returns file system representation of path."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def get_exec_path(env: int) -> int:
    """Mock: returns list of dirs to search for executables."""
    return 0

#@ \trusted
def fsdecode(filename: int) -> str:
    """Mock: decode filename from bytes, returns string."""
    return ""

#@ \trusted
def fsencode(filename: int) -> str:
    """Mock: encode filename to bytes, returns encoded string."""
    return ""

# ── Environment ──────────────────────────────────────────────────────

#@ \trusted
def getenv(key: int) -> str:
    """Mock: returns value of environment variable."""
    return ""

#@ \trusted
#@ ensures \result == 0
def putenv(key: int, v: int) -> int:
    """Mock: set environment variable."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unsetenv(key: int) -> int:
    """Mock: unset environment variable."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def supports_dir_fd() -> int:
    """Mock: returns set of functions supporting dir_fd as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def supports_effective_ids() -> int:
    """Mock: returns set of functions supporting effective_ids."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def supports_fd() -> int:
    """Mock: returns set of functions supporting fd parameter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def supports_follow_symlinks() -> int:
    """Mock: returns set of functions supporting follow_symlinks."""
    return 0

# ── System information ───────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def cpu_count() -> int:
    """Mock: returns number of CPUs in the system."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urandom(size: int) -> int:
    """Mock: returns random bytes as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrandom(size: int) -> int:
    """Mock: returns random bytes from OS, opaque handle."""
    return 0

#@ \trusted
def strerror(code: int) -> str:
    """Mock: returns error message for error code."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def umask(mask: int) -> int:
    """Mock: set file mode creation mask, returns previous mask."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uname() -> int:
    """Mock: returns system identification as opaque handle."""
    return 0

#@ \trusted
def confstr(name: int) -> str:
    """Mock: returns system configuration string."""
    return ""

#@ \trusted
#@ ensures \result >= 0
def sysconf(name: int) -> int:
    """Mock: returns system configuration integer value."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pathconf_names() -> int:
    """Mock: returns dict of pathconf variable names as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def confstr_names() -> int:
    """Mock: returns dict of confstr variable names as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sysconf_names() -> int:
    """Mock: returns dict of sysconf variable names as opaque handle."""
    return 0

#@ \trusted
def device_encoding(fd: int) -> str:
    """Mock: returns encoding of device associated with fd."""
    return ""

# ── Terminal ─────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def terminal_size(columns: int, lines: int) -> int:
    """Mock: create terminal_size named tuple."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_terminal_size(fd: int) -> int:
    """Mock: returns terminal size as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def login_tty(fd: int) -> int:
    """Mock: prepare terminal for new login session."""
    return 0

# ── Timer file descriptors ───────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def timerfd_create(clockid: int, flags: int) -> int:
    """Mock: create timer file descriptor."""
    return 0

#@ \trusted
#@ ensures \result == 0
def timerfd_settime(fd: int, flags: int, initial: int, interval: int) -> int:
    """Mock: arm/disarm timer file descriptor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_gettime(fd: int) -> int:
    """Mock: returns current timer setting as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def timerfd_settime_ns(fd: int, flags: int, initial: int, interval: int) -> int:
    """Mock: arm/disarm timer fd with nanosecond precision."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timerfd_gettime_ns(fd: int) -> int:
    """Mock: returns timer setting in nanoseconds as opaque handle."""
    return 0

# ── Event file descriptors ───────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def eventfd(initval: int, flags: int) -> int:
    """Mock: create event file descriptor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def eventfd_read(fd: int) -> int:
    """Mock: read event counter from eventfd."""
    return 0

#@ \trusted
#@ ensures \result == 0
def eventfd_write(fd: int, v: int) -> int:
    """Mock: write value to eventfd."""
    return 0

# ── Splice / copy / memfd ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def splice(src: int, dst: int, count: int, offset_src: int, offset_dst: int, flags: int) -> int:
    """Mock: move data between file descriptors, returns bytes moved."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def copy_file_range(src: int, dst: int, count: int, offset_src: int, offset_dst: int) -> int:
    """Mock: copy data between file descriptors, returns bytes copied."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def memfd_create(name: int, flags: int) -> int:
    """Mock: create anonymous file in memory, returns fd."""
    return 0

# ── Scheduler ────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def sched_getaffinity(pid: int) -> int:
    """Mock: returns CPU affinity mask as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sched_setaffinity(pid: int, mask: int) -> int:
    """Mock: set CPU affinity mask."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sched_yield() -> int:
    """Mock: voluntarily relinquish CPU."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_getscheduler(pid: int) -> int:
    """Mock: returns scheduling policy for process."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sched_setscheduler(pid: int, policy: int, param: int) -> int:
    """Mock: set scheduling policy and parameters."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_getparam(pid: int) -> int:
    """Mock: returns scheduling parameters as opaque handle."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sched_setparam(pid: int, param: int) -> int:
    """Mock: set scheduling parameters."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_get_priority_min(policy: int) -> int:
    """Mock: returns minimum priority for scheduling policy."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_get_priority_max(policy: int) -> int:
    """Mock: returns maximum priority for scheduling policy."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sched_rr_get_interval(pid: int) -> int:
    """Mock: returns round-robin time quantum for process."""
    return 0

# ── Device numbers ───────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def major(device: int) -> int:
    """Mock: extract major device number."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def minor(device: int) -> int:
    """Mock: extract minor device number."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def makedev(major_num: int, minor_num: int) -> int:
    """Mock: compose device number from major and minor."""
    return 0

# ── Windows DLL directory ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def add_dll_directory(path: int) -> int:
    """Mock: add DLL search directory (Windows), returns handle."""
    return 0
