"""Concrete tests for World wiring (making-it-pure-5.md §1-§8)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pure_lib.world import World
from pure_lib.tm import ClockModel
from pure_lib.proc import ProcessState
from pure_lib.os.UnixInodeFileSystem import UnixInodeFileSystem
from pure_lib.iomod import FileIO, set_world as iomod_set_world, open_file
from pure_lib.sysmod import set_world as sysmod_set_world
import pure_lib.sysmod as sysmod
from pure_lib.tmpf import set_world as tmpf_set_world
import pure_lib.tmpf as tmpf
from pure_lib.shutl import set_world as shutl_set_world
import pure_lib.shutl as shutl
from pure_lib.subproc import set_world as subproc_set_world

passed = 0
failed = 0

def check(name, cond):
    global passed, failed
    if cond:
        print(f"PASS: {name}")
        passed += 1
    else:
        print(f"FAIL: {name}")
        failed += 1


# --- World construction ---
w = World()
check("world clock exists", w.clock is not None)
check("world fs exists", w.fs is not None)
check("world proc exists", w.proc is not None)

# --- Clock ↔ Filesystem wiring ---
t1 = w.clock.monotonic()
fd = w.fs.sys_creat("test.txt", 0o644)
check("creat via world.fs", fd >= 3)
inode_num = w.fs._dir_lookup(5, "test.txt")
inode = w.fs._read_inode(inode_num)
check("mtime set from shared clock", inode[7] > t1)

w.fs.sys_write(fd, b"hello world")
inode2 = w.fs._read_inode(inode_num)
check("mtime updated on write", inode2[7] > inode[7])

t2 = w.clock.monotonic()
check("clock > mtime after write", t2 > inode2[7])

# --- ProcessState ---
check("proc pid", w.proc.pid == 1)
check("proc getenv HOME", w.proc.getenv("HOME") == "/")
w.proc.setenv("TMPDIR", "/tmp")
check("proc setenv/getenv", w.proc.getenv("TMPDIR") == "/tmp")
w.proc.unsetenv("TMPDIR")
check("proc unsetenv", w.proc.getenv("TMPDIR") == "")
check("proc umask", w.proc.umask_set(0o077) == 18)  # old umask was 0o022=18
check("proc umask new", w.proc.umask == 63)  # 0o077=63

# cwd
w.fs.sys_mkdir("testdir", 0o755)
dir_inode = w.fs._dir_lookup(5, "testdir")
check("chdir to dir", w.proc.chdir(dir_inode) == 0)
check("getcwd after chdir", w.proc.getcwd_inode() == dir_inode)
check("chdir to invalid", w.proc.chdir(99) == -1)

# argv
w.proc.set_argv(["prog", "--flag", "arg1"])
check("argc", w.proc.argc() == 3)
check("argv 0", w.proc.argv(0) == "prog")
check("argv 2", w.proc.argv(2) == "arg1")
check("argv out of range", w.proc.argv(10) == "")

# --- sysmod wiring ---
sysmod_set_world(w)
w.proc.set_argv(["myapp", "run"])
check("sysmod get_argv wired", sysmod.get_argv() == ["myapp", "run"])
w.proc.set_path(["/usr/bin", "/bin"])
check("sysmod get_path wired", sysmod.get_path() == ["/usr/bin", "/bin"])

# --- iomod FileIO flush-through ---
iomod_set_world(w)
fd_io = w.fs.sys_creat("iotest.txt", 0o644)
fio = FileIO(fd_io, w.fs)
n = fio.write(b"abcdef")
check("fileio write returns len", n == 6)
check("fileio tell", fio.tell() == 6)
fio.seek(0)
n_read = fio.read(6)
check("fileio read after seek", n_read == 6)
fio.close()

# open_file via module
fd_f = w.fs.sys_creat("opentest.txt", 0o644)
w.fs.sys_write(fd_f, b"xyz")
w.fs.sys_close(fd_f)
stream = open_file("opentest.txt", "r")
check("open_file returns FileIO", isinstance(stream, FileIO))
rd = stream.read(3)
check("open_file read", rd == 3)
stream.close()

# --- tmpf wiring ---
tmpf_set_world(w)
w.proc.setenv("TMPDIR", "/var/tmp")
check("gettempdir from env", tmpf.gettempdir() == "/var/tmp")
result = tmpf.mkstemp("", "tmp", "")
check("mkstemp fd > 0 wired", result[0] >= 3)
check("mkstemp name > 0", result[1] >= 1)

# --- shutl wiring ---
shutl_set_world(w)
# Create source file, copyfile
fd_src = w.fs.sys_creat("src.txt", 0o644)
w.fs.sys_write(fd_src, b"copy me")
w.fs.sys_close(fd_src)
copied = shutl.copyfile("src.txt", "dst.txt")
check("copyfile returns > 0", copied > 0)
# Verify dst has same content
fd_dst = w.fs.sys_open("dst.txt", 0)
check("dst.txt exists", fd_dst >= 3)
if fd_dst >= 3:
    # sys_read returns byte count, verify via inode size instead
    dst_ino = w.fs._dir_lookup(5, "dst.txt")
    dst_inode = w.fs._read_inode(dst_ino)
    check("copyfile size matches", dst_inode[0] == 7)  # len("copy me") == 7
    w.fs.sys_close(fd_dst)

# rmtree
rmresult = shutl.rmtree("dst.txt")
check("rmtree removes file", rmresult == 1)
check("rmtree file gone", w.fs._dir_lookup(5, "dst.txt") < 0)

# --- Cross-subsystem coherence (informal coarse probe) ---
# After a proc operation, verify fs state is untouched
inode_before = w.fs._read_inode(w.fs._dir_lookup(5, "test.txt"))
w.proc.setenv("FOO", "bar")
w.proc.set_argv(["new", "args"])
t3 = w.clock.monotonic()
inode_after = w.fs._read_inode(w.fs._dir_lookup(5, "test.txt"))
check("fs preserved across proc ops", inode_before[0] == inode_after[0])
check("fs mtime preserved across proc ops", inode_before[7] == inode_after[7])

print(f"\n{passed} passed, {failed} failed out of {passed + failed}")
if failed > 0:
    exit(1)
