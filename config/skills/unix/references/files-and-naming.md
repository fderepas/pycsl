# Files and Naming

Full detail on file naming, metadata, permissions, and file I/O system calls.

## 4. File Naming, Metadata, and Permissions
### 4.1 Inodes and Names
A pathname is a sequence of directory lookups, not the file object itself. The kernel resolves each component during traversal, starting
from either `/` or the process's current working directory; see `path_resolution(7)`. The result of a successful lookup is usually an
inode-like filesystem object plus the permissions needed for the requested operation. The important UNIX idea is that a name and the file's
metadata are separate. A directory entry maps a name to an inode number. The inode holds the file's type, ownership, mode bits, timestamps,
size, block mapping, and link count. Because of that split, changing a name does not usually change the underlying file object. A hard link
is simply another directory entry naming the same inode. `link(2)` creates such another name. After a successful hard link, both names refer
to the same file object. There is no distinguished "original" name; `link(2)` explicitly notes that both names are equally valid. Because
the inode is shared, the names also share metadata. Permissions, ownership, size, timestamps, and data blocks are common to all hard links.
A write through one pathname is visible through the others. The `st_nlink` field records how many directory entries point at that inode.
`rename(2)` changes directory entries, not file contents. If the rename succeeds, the replacement of `newpath` is atomic from the viewpoint
of pathname lookup. Open file descriptors continue to refer to the same open file description and inode. Other hard links to the inode are
unaffected. `unlink(2)` removes a name from the filesystem. It does not immediately destroy file contents just because one pathname
disappeared. If the removed name was not the last hard link, the inode remains reachable through its other names. If it was the last link,
the file is deleted only when no process still has it open; see `unlink(2)` and `close(2)`. This explains the classic UNIX behavior where a
process can keep reading or writing a file after another process has unlinked its pathname. Directories are special here. In normal POSIX
usage, hard links to directories are restricted to preserve an acyclic namespace. The `.` and `..` entries are handled specially by pathname
resolution; see `path_resolution(7)`.
### 4.2 The stat Family
The `stat` family retrieves file metadata from the kernel. `stat(path, &sb)` follows symbolic links and reports on the final target.
`lstat(path, &sb)` instead reports on the symbolic link itself. `fstat(fd, &sb)` reports on the file referred to by an open file descriptor;
see `stat(2)`. A simplified `struct stat` looks like this:
```c
struct stat {
    dev_t     st_dev;
    ino_t     st_ino;
    mode_t    st_mode;
    nlink_t   st_nlink;
    uid_t     st_uid;
    gid_t     st_gid;
    off_t     st_size;
    blksize_t st_blksize;
    blkcnt_t  st_blocks;
    time_t    st_atime;
    time_t    st_mtime;
    time_t    st_ctime;
};
```
`st_dev` identifies the device containing the file. `st_ino` is the inode number on that device. Together, `(st_dev, st_ino)` commonly
identify a file within the system. `st_mode` encodes both file type and permission bits. Masking with the file-type bits tells whether the
object is a regular file, directory, symbolic link, character device, block device, FIFO, or socket. The lower permission bits hold
owner/group/other access rights plus special bits such as setuid, setgid, and sticky. `st_nlink` is the hard-link count. `st_uid` and
`st_gid` identify the owning user and group. `st_size` is the size in bytes for a regular file, and for a symbolic link it is the length of
the stored target pathname; see `stat(3type)`. `st_blksize` is the preferred block size for efficient I/O. `st_blocks` is the number of
allocated 512-byte blocks, which may be smaller than `st_size / 512` for sparse files. The three classic timestamps are also fundamental.
`st_atime` is the last access time for file data. `st_mtime` is the last modification time for file data. `st_ctime` is the last
status-change time for the inode, not a creation time. POSIX and modern Linux also expose nanosecond forms via `st_atim`, `st_mtim`, and
`st_ctim`; see `stat(3type)`. A subtle point from `stat(2)` is that fields are not guaranteed to be a perfectly simultaneous snapshot. If
another process changes mode or ownership while `stat()` is running, different fields can reflect slightly different moments. That matters
when code assumes metadata was read atomically.
### 4.3 Permission Model
UNIX permissions are organized into owner, group, and other classes. Each class has read, write, and execute/search bits. For ordinary
files, execute controls program execution. For directories, the execute bit means search permission: the right to traverse the directory
during pathname lookup; see `path_resolution(7)`. The permission-selection algorithm is simple. If the caller's effective user ID matches
the file owner, the owner bits are used. Otherwise, if the file's group matches the effective group ID or one of the supplementary groups,
the group bits are used. Otherwise, the other bits are used. Linux actually uses fsuid/fsgid for filesystem checks, though they usually
equal the effective IDs; see `path_resolution(7)`. `access(2)` is worth reading carefully. It checks using the process's real UID and GID,
not the effective IDs used for the actual operation. That is why set-user-ID programs use `access()` to ask what the invoking user could do,
not what the privileged program itself could do. Privileged processes can bypass many DAC checks. Traditionally that means root. On Linux,
the relevant privilege is described in terms of capabilities such as `CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH`; see `path_resolution(7)`.
Even then, execute permission still requires at least one execute bit to be set for a regular file. The special mode bits modify normal
behavior. `S_ISUID` requests set-user-ID behavior on `execve(2)`. `S_ISGID` requests set-group-ID behavior on `execve(2)` and also has
directory-related effects. `S_ISVTX`, the sticky bit, restricts deletion in directories such as `/tmp`: typically only the file owner,
directory owner, or a privileged process may remove or rename entries there; see `chmod(2)` and `unlink(2)`.
### 4.4 Changing Metadata
`chmod(path, mode)` and `fchmod(fd, mode)` change permission bits. The caller must either own the file or hold appropriate privilege
(`CAP_FOWNER` on Linux); see `chmod(2)`. A common pattern is:
```c
if (fchmod(fd, 0644) == -1) {
    /* handle error */
}
```
`chown()`, `fchown()`, and `lchown()` change ownership. Only a privileged process may change the owning user ID. The file owner may change
the group to one of the groups of which that owner is a member. Linux documents this under `CAP_CHOWN`; see `chown(2)`. Changing ownership
of an executable file may clear setuid/setgid bits and associated file capabilities. Timestamp updates use `utime(2)` or the more modern
`utimensat(2)`/`futimens()`. `utime()` sets atime and mtime with second precision. `utimensat()` uses `struct timespec` and supports
nanosecond precision plus `UTIME_NOW` and `UTIME_OMIT`. In both interfaces, ctime is updated to the current time because inode status
changed. When setting timestamps to "now", permission can come from write access, ownership, or privilege, depending on the interface and
arguments. When setting arbitrary timestamps, ownership or privilege is generally required; see `utime(2)` and `utimensat(2)`.
### 4.5 Symbolic Links
A symbolic link is a separate filesystem object with its own inode. Its data payload is a pathname string naming another object. That is why
`lstat()` reports on the link itself, while `stat()` follows it to the target; see `stat(2)` and `path_resolution(7)`. During pathname
traversal, symlinks in nonfinal components are resolved as the kernel walks the path. The final component may or may not be followed
depending on the system call. `stat()` follows the final symlink. `lstat()` does not. `open()` usually follows it, but `O_NOFOLLOW` causes
`open()` to fail with `ELOOP` if the trailing component is a symbolic link; see `open(2)`. Because symbolic links can point to other
symbolic links, loops are possible. The kernel therefore enforces a limit on the number of symlink resolutions during one pathname lookup.
If that limit is exceeded, the call fails with `ELOOP`; see `path_resolution(7)`. A symlink's own metadata is distinct from the target's
metadata. Its size is the length of the stored pathname. Removing a symlink with `unlink(2)` removes only the link object, not the target.
Renaming a symlink renames that link object, again without changing the target; see `unlink(2)` and `rename(2)`. In short, UNIX naming is
deliberately indirect. Directories hold names. Inodes hold metadata. Hard links add more names to one inode. Symbolic links add a different
inode whose contents are another pathname. That indirection is what makes the namespace flexible while keeping the underlying file object
model simple.

## 5. File I/O System Calls
### 5.1 File Descriptor Table
User code does I/O through file descriptors, which are small integers. Each process has a descriptor table indexed by those integers.
`open(2)` returns the lowest-numbered unused entry in that table. Conceptually, UNIX I/O is a three-level structure. First, the process's
file descriptor table maps integers like 0, 1, and 2 to kernel objects. Second, those entries point to open file descriptions in a
system-wide open-file table. Third, each open file description refers to a file object such as an inode or vnode plus filesystem-specific
state. The man pages make the middle layer explicit. `open(2)` says that opening a file creates a new open file description, and that the
open file description stores the current file offset and file status flags. A file descriptor is just a reference to that shared open file
description. That distinction explains several important behaviors. If two descriptors refer to the same open file description, they share
the offset. A call to `lseek()` on one affects reads and writes done through the other. They also share file status flags such as `O_APPEND`
or `O_NONBLOCK`. They do not necessarily share descriptor flags such as `FD_CLOEXEC`, because those live in the descriptor table entry.
`fork(2)` copies the parent's descriptor table into the child. But the copied entries still refer to the same underlying open file
descriptions. So parent and child share offsets and status flags after `fork()`. This is exactly why a shell can open a file once before
`fork()`, then let the child inherit it. `execve(2)` does not create a new process; it replaces the program image in the current one. By
default, file descriptors remain open across `execve()`. Descriptors marked close-on-exec are closed during the transition; see `open(2)`,
`fcntl(2)`, and `execve(2)`. `close(fd)` removes one descriptor-table reference. If that was the last descriptor pointing at an open file
description, the kernel can free the open-file entry. If that was also the last reference to an inode whose final name was already removed
with `unlink()`, the file is finally deleted; see `close(2)`.
### 5.2 Opening and Creating Files
The general interface is:
```c
int fd = open(path, flags, mode);
```
`flags` must include exactly one access mode: `O_RDONLY`, `O_WRONLY`, or `O_RDWR`. Additional creation and status flags refine the
operation. `O_CREAT` creates the file if it does not exist. `O_TRUNC` truncates an existing regular file when opened for writing. `O_APPEND`
forces each write to go to end-of-file. `O_EXCL` combined with `O_CREAT` requests exclusive creation. The `mode` argument matters only when
a new file is created. Its effective value is filtered by the process umask. Ownership of a newly created file comes from the caller's
effective UID, and group assignment depends on normal UNIX rules plus the parent directory's setgid state; see `open(2)` and `chown(2)`. The
kernel path lookup for `open()` follows the normal pathname-resolution rules. It checks search permission on each directory component. It
applies permission checks on the final object according to the requested access mode. If `O_CREAT` is present and the file does not exist,
the kernel allocates a new inode and inserts a directory entry. `creat(path, mode)` is historical shorthand for opening a file write-only,
creating it if needed, and truncating it if it already exists. Modern code usually calls `open()` directly because it makes the flags
explicit. `mknod(2)` creates special filesystem nodes. With `S_IFIFO` it creates a named pipe. With `S_IFCHR` or `S_IFBLK` it creates device
special files carrying a major/minor device number. Regular applications more often use higher-level wrappers such as `mkfifo(3)`.
### 5.3 Reading and Writing
`read(fd, buf, count)` transfers up to `count` bytes from the current offset into user memory. `write(fd, buf, count)` transfers bytes from
user memory to the file object. Both are byte-stream interfaces: neither call has an inherent notion of records for regular files. On
success, `read()` returns the number of bytes actually read. That may be smaller than requested. A short read is not an error. It can mean
end-of-file is near, less data is immediately available on a pipe or terminal, or the call was interrupted after some progress; see
`read(2)`. A return of 0 from `read()` on a regular file means end-of-file. `write()` similarly returns the number of bytes actually
written. A short write is possible and must be handled by the caller. Causes include signal interruption, nonblocking I/O, quotas,
filesystem limits, or pipe capacity. Robust code loops until all required bytes are transferred or an error occurs. For seekable files,
successful reads and writes normally advance the shared file offset by the number of bytes transferred. Because the offset is stored in the
open file description, the advancement is shared by duplicated descriptors and by parent/child processes that inherited the same description
after `fork()`. `O_APPEND` changes the write rule. Before each `write(2)`, the kernel positions the offset at end-of-file and performs the
reposition-plus-write as one atomic step; see `open(2)`. That matters for log files and shell redirections like `>>`. Pipes and FIFOs are
special. POSIX requires writes of at most `PIPE_BUF` bytes to be atomic. `pipe(7)` states that writes smaller than `PIPE_BUF` appear as one
contiguous sequence; larger writes may be interleaved with data from other writers. On Linux, `PIPE_BUF` is 4096 bytes.
### 5.4 File Offset and Seeking
`lseek(fd, offset, whence)` changes the current file offset stored in the open file description. `SEEK_SET` makes the new offset exactly
`offset`. `SEEK_CUR` adds `offset` to the current position. `SEEK_END` adds `offset` to the current file size; see `lseek(2)`. Seeking past
the current end of file does not by itself enlarge the file. The size changes only when data is later written. If an application seeks far
forward and then writes, the unwritten gap behaves as a hole. Subsequent reads from that region return zero bytes. Such files are sparse
files. `st_blocks` can therefore be much smaller than `st_size / 512`. Linux also supports `SEEK_DATA` and `SEEK_HOLE` on filesystems that
implement them. These operations let backup tools and similar programs map sparse regions without reading the whole file; see `lseek(2)`.
Not every descriptor is seekable. Applying `lseek()` to a pipe, FIFO, or socket fails with `ESPIPE`. This follows directly from the
streaming nature of those objects.
### 5.5 Duplicating Descriptors
`dup(fd)` returns a new descriptor referring to the same open file description as `fd`. The new descriptor number is the lowest unused one.
Because the underlying open file description is shared, file offset and status flags are shared too; see `dup(2)`. `dup2(oldfd, newfd)` is
the targeted version. If `newfd` is already open, the kernel closes it and then makes it refer to `oldfd`'s open file description. The
close-and-rebind happens atomically. That atomicity matters because a user-space sequence like `close(newfd); dup(oldfd);` is racy in the
presence of signals or threads. Shell I/O redirection is the classic use case. A shell that wants standard output to go to a file typically
does something like:
```c
int fd = open("out.txt", O_WRONLY|O_CREAT|O_TRUNC, 0666);
dup2(fd, STDOUT_FILENO);
close(fd);
```
After the `dup2()`, writes to file descriptor 1 go to the open file description created by `open()`. The original descriptor returned by
`open()` can then be closed without losing the redirection. `fcntl(fd, F_DUPFD, min)` provides a more general duplication primitive. It
returns a duplicate using the lowest available descriptor number greater than or equal to `min`. Linux and POSIX also provide close-on-exec
variants such as `F_DUPFD_CLOEXEC`.
### 5.6 File Control
`fcntl(2)` is a multiplexer for per-descriptor and per-open-file-description operations. Two especially common commands are `F_GETFD` and
`F_SETFD`. These manipulate descriptor flags, most notably `FD_CLOEXEC`. That flag is stored in the descriptor entry, not in the shared open
file description. `F_GETFL` and `F_SETFL` operate on file status flags. Examples include `O_APPEND`, `O_NONBLOCK`, and `O_ASYNC`. Because
status flags live in the open file description, all descriptors that refer to that same description see the change. That is why setting
nonblocking mode on one duplicate affects the others. `fcntl()` also implements advisory record locking. `F_SETLK` tries to place or release
a byte-range lock and fails immediately if a conflicting lock exists. `F_SETLKW` waits until the conflicting lock is released. `F_GETLK`
asks the kernel whether a requested lock would conflict, and if so returns details of one blocker; see `fcntl_locking(2)`. These locks are
advisory, not mandatory by default. Processes cooperate by checking and honoring them. The `struct flock` range is described relative to
`SEEK_SET`, `SEEK_CUR`, or `SEEK_END`, which makes it possible to lock arbitrary regions in a file. Traditional POSIX record locks are
associated with the process, are released when the process exits, and are not inherited across `fork()`; see `fcntl_locking(2)`.
### 5.7 Pipes
`pipe(int fd[2])` creates a unidirectional byte stream. `fd[0]` is the read end. `fd[1]` is the write end. `pipe(7)` emphasizes that
ordinary pipe I/O has byte-stream semantics: there are no message boundaries. If a process reads from an empty pipe, `read()` blocks until
data becomes available. If a process writes to a full pipe, `write()` blocks until enough data has been drained. With `O_NONBLOCK`, the same
operations fail with `EAGAIN` instead of sleeping; see `pipe(7)`. End-of-stream behavior is defined by reference counts on the ends. When
all write ends are closed, a reader gets end-of-file and `read()` returns 0. When all read ends are closed, a writer gets `SIGPIPE`; if that
signal is ignored or blocked, `write()` fails with `EPIPE`. That is why programs using `pipe()` and `fork()` must close unused duplicate
ends promptly. Small writes matter. POSIX guarantees atomic writes up to `PIPE_BUF` bytes. Larger writes may be split or interleaved with
data from other writers. For protocol-like use over pipes, applications either keep messages at or below `PIPE_BUF` or add their own
framing. Named pipes, or FIFOs, export the same I/O model through the filesystem namespace. They can be created with `mkfifo(3)` or
`mknod(path, S_IFIFO|mode, 0)`. Once opened, FIFOs behave like pipes for `read()`, `write()`, blocking, EOF, and `SIGPIPE`; see `pipe(7)`,
`fifo(7)`, and `mknod(2)`.
### 5.8 File System Operations
`mount(2)` attaches a filesystem instance at a mount point in the process's mount namespace. After a successful mount, pathname resolution
crossing that directory reaches the root of the mounted filesystem; see `mount(2)` and `path_resolution(7)`. Linux extends this with bind
mounts, remounts, propagation control, and mount namespaces. `umount(2)` or `umount2(2)` detaches a mounted filesystem. A normal unmount
fails with `EBUSY` if the filesystem is still in use. Linux also supports lazy unmount via `MNT_DETACH`, which disconnects the mount from
the namespace immediately and completes the actual teardown when the mount is no longer busy. `sync()` asks the kernel to flush dirty
filesystem buffers. POSIX only guarantees scheduling of writes, but Linux documents that `sync()` waits for I/O completion, effectively
giving the same global guarantee as `fsync()` on every file; see `sync(2)`. It is therefore a system-wide persistence operation, not just a
per-file call. `chdir(path)` and `fchdir(fd)` change the process's current working directory. Relative pathnames are interpreted from there.
The working directory is inherited across `fork()` and preserved across `execve()`; see `chdir(2)`. `chroot(path)` changes the process's
root directory for absolute pathname resolution. It is inherited by children. But `chroot(2)` explicitly warns that this is not a complete
security mechanism: it does not close open file descriptors, does not change the current working directory, and can often be escaped if used
carelessly. That is why modern containment uses namespaces, capabilities, and other mechanisms in addition to or instead of plain
`chroot()`.
