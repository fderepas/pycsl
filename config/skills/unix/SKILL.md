---
name: unix
description: "Describes Unix kernel internals and the system call interface — covers dual-mode execution, system calls, block I/O, buffer cache, file system layout, inodes, file descriptors, process model, fork-exec-wait, signals, CPU scheduling, virtual memory, device drivers, IPC (pipes, System V messages/shared memory/semaphores, sockets), and multiprocessor synchronisation. Use when the user asks about Unix or Linux kernel architecture, how system calls work, how fork/exec/wait works, how the buffer cache works, file descriptor tables, process states, virtual memory paging, pipe and socket internals, or any low-level OS concept. Sources: POSIX specifications, Linux man pages, kernel documentation."
---

# Unix Kernel Internals

## 1. Dual-Mode Execution and System Calls
### 1.1 Hardware Protection Rings
Unix relies on CPU-enforced privilege separation: user mode cannot execute privileged instructions, control devices directly, change page tables, or access kernel memory, and violations raise exceptions; controlled entry uses instructions such as `syscall`, `int $0x80`, and `svc #0` (`syscall(2)`).
### 1.2 System Call Mechanism
A system call is the standard user-to-kernel entry path (`intro(2)`), usually via C library wrappers that place the syscall number and arguments in ABI-defined locations, trap to the kernel, and translate negative kernel errors into `errno`.

```c
ssize_t n = write(fd, buf, len);
if (n == -1) perror("write");
```
The kernel dispatches through a syscall table indexed by number, returns syscall-specific results on success, and yields `ENOSYS` for unimplemented calls (`syscall(2)`).
### 1.3 Interrupts and Exceptions
Interrupts come from external events such as timers and device completion, while exceptions arise from the current instruction stream, such as page faults, divide-by-zero, invalid opcodes, and protection faults; many synchronous faults are reported to user space as signals such as `SIGSEGV`, `SIGBUS`, `SIGFPE`, `SIGILL`, and `SIGTRAP` (`signal(7)`).
### 1.4 Context Switching
A context switch saves enough CPU and, when needed, address-space state to resume one thread later and restore another; it occurs on blocking, yielding, or preemption and is costly because it disrupts caches, TLB state, branch prediction, and pipeline locality.
### 1.5 Kernel Re-entrancy
Traditional Unix kernels were largely non-preemptive in kernel mode, but modern kernels are more preemptible, so correctness depends on locks, atomic operations, memory ordering, and careful separation of interrupt, soft-interrupt, and process contexts; before returning to user mode, the kernel also checks pending unblocked signals and may arrange delivery via `sigreturn(2)` (`signal(7)`).

## 2. Block I/O and the Buffer Cache
### 2.1 Purpose of the Buffer Cache
The buffer cache keeps block-device data in memory between the filesystem layer and the device so repeated reads can be served from RAM and writes can be coalesced, delayed, and ordered more efficiently.
### 2.2 Cache Structure
A classic design keys buffers by `(device, block_number)` in a hash table and keeps reusable entries on a free list; each buffer tracks the device, block number, data pointer, and state such as `busy`, `valid`, `delayed_write`, and `async`.
### 2.3 Buffer Lookup and Allocation
Lookup first checks the hash table, sleeps if a matching buffer is busy, reuses a free buffer on a miss, and flushes dirty victims before retagging them; wakeups are advisory, so the caller must retry until the state is revalidated.

```c
for (;;) {
    if ((bp = hash_lookup(dev, blk)) && !bp->busy) return mark_busy(bp);
    if (bp && bp->busy) sleep(bp);
    vp = take_free_buffer();
    if (!vp) sleep(free_list);
    if (vp && vp->delayed_write) flush(vp);
    else if (vp) return retag(vp, dev, blk);
}
```
### 2.4 Read and Write Paths
`bread()` follows "lookup first, I/O on miss"; synchronous writes wait for completion, delayed writes mark buffers dirty for later flush, asynchronous writes let the caller continue, and read-ahead fetches likely future blocks early.
### 2.5 Cache Coherency and Sync
`fsync(2)` flushes file data and required metadata, `fdatasync(2)` may omit unrelated metadata, and directory durability can require `fsync()` on the directory itself; `sync(2)` and `syncfs(2)` push broader state, and write ordering still matters because metadata reaching disk before data can expose stale contents unless journaling or similar recovery rules are used.
### 2.6 Advantages and Limitations
The cache gives a uniform block abstraction, exploits locality, and improves throughput, but finite memory causes churn, dirty write-back creates crash windows, and concurrency around locks, wait queues, and wakeups adds complexity.

## 3. On-Disk File System Layout
### 3.1 Disk Abstraction
A filesystem treats persistent storage as an array of logical blocks within a partition, disk, or logical volume, and once mounted the VFS presents a common interface while preserving filesystem-specific layout rules; `statfs(2)` reports high-level properties such as block counts and inode counts.
### 3.2 Superblock
The superblock is the master record for the volume format, carrying block size, inode and free-space counts, feature flags, state, and identifiers, and ext-family filesystems replicate backups selectively as described in `ext4(5)`.
### 3.3 Inode Structure
An inode stores per-file metadata such as type, mode bits, ownership, size, timestamps, link count, and block mapping (`inode(7)`, `stat(2)`); in the classic scheme, if block size is `B` and pointer size is `P`, then `N = B / P` and the maximum data-block count is `12 + N + N^2 + N^3`.
### 3.4 Directory Structure
A directory is a file mapping names to inode numbers, conventionally including `.` and `..`, and ext2/ext4 store variable-length directory entries with optional file-type information (`ext4(5)`).
### 3.5 Free Space Management
Filesystems track free blocks and inodes with structures such as bitmaps, and ext2/ext4 keep block and inode bitmaps per block group so allocation can favor locality (`ext4(5)`).
### 3.6 Path Resolution
`path_resolution(7)` describes a component-by-component walk starting at `/`, the current working directory, or an *at() directory fd; missing search permission yields `EACCES`, a missing component yields `ENOENT`, an intermediate nondirectory yields `ENOTDIR`, symlink expansion is loop-limited, and a trailing `/` forces directory resolution.

## 4. File Naming, Metadata, and Permissions
### 4.1 Inodes and Names
A pathname is a sequence of directory lookups rather than the file object itself, because directories map names to inodes and the inode holds metadata; hard links created by `link(2)` are just additional names for the same inode, `rename(2)` changes directory entries atomically, and `unlink(2)` removes a name but the file persists until both the link count and open references reach zero.
### 4.2 The stat Family
`stat()`, `lstat()`, and `fstat()` return file metadata, with `stat()` following symlinks and `lstat()` reporting on the link object itself.
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
`(st_dev, st_ino)` commonly identifies a file, `st_mode` encodes type and permissions, `st_blocks` counts allocated 512-byte blocks, `st_ctime` is status-change time rather than creation time, and `stat(2)` warns that fields are not guaranteed to be one perfectly simultaneous snapshot.
### 4.3 Permission Model
Unix selects owner, group, or other permission bits based on effective credentials and supplementary groups, with directory execute meaning search permission (`path_resolution(7)`); `access(2)` instead checks the real IDs, capabilities such as `CAP_DAC_OVERRIDE` can bypass many checks, and special bits `S_ISUID`, `S_ISGID`, and `S_ISVTX` modify normal behavior (`chmod(2)`, `unlink(2)`).
### 4.4 Changing Metadata
`chmod()` and `fchmod()` change permission bits, `chown()` variants change ownership subject to privilege rules, and timestamp updates use `utime(2)` or `utimensat(2)`/`futimens()`; changing ownership can clear privileged bits, and setting arbitrary timestamps generally requires ownership or privilege.
### 4.5 Symbolic Links
A symbolic link is a separate inode whose data payload is a pathname string, so `lstat()` reports on the link while `stat()` usually follows it; nonfinal symlinks are resolved during traversal, `O_NOFOLLOW` makes `open()` fail on a trailing symlink with `ELOOP`, loop limits apply (`path_resolution(7)`), and removing or renaming the symlink affects only the link object, not the target.

## 5. File I/O System Calls
### 5.1 File Descriptor Table
Each process has a file descriptor table mapping small integers to kernel references, and those entries point at open file descriptions that hold shared state such as the current offset and file status flags (`open(2)`); `fork()` copies descriptor-table entries that still refer to the same open file descriptions, and `execve()` preserves descriptors unless `FD_CLOEXEC` is set.
### 5.2 Opening and Creating Files
`open(path, flags, mode)` chooses one access mode plus creation or status flags such as `O_CREAT`, `O_TRUNC`, `O_APPEND`, and `O_EXCL`, applies normal pathname and permission checks, filters creation mode through the umask, and historically overlaps with `creat()` and `mknod(2)` for special files.
### 5.3 Reading and Writing
`read()` and `write()` are byte-stream interfaces that may complete with short counts, so callers must handle partial transfers; successful operations normally advance the shared file offset, `O_APPEND` makes the end-of-file reposition plus write atomic (`open(2)`), and `pipe(7)` guarantees atomic writes only up to `PIPE_BUF`.
### 5.4 File Offset and Seeking
`lseek(fd, offset, whence)` updates the offset in the open file description, supports `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, and on Linux may also support `SEEK_DATA` and `SEEK_HOLE`; seeking past end creates holes only once data is later written, and pipes, FIFOs, and sockets fail with `ESPIPE` (`lseek(2)`).
### 5.5 Duplicating Descriptors
`dup()` and `dup2()` create new descriptor-table entries for the same open file description, so offsets and status flags remain shared; `dup2()` atomically closes and rebinds `newfd`, which is why shells use it for redirection (`dup(2)`).
```c
int fd = open("out.txt", O_WRONLY|O_CREAT|O_TRUNC, 0666);
dup2(fd, STDOUT_FILENO);
close(fd);
```
### 5.6 File Control
`fcntl(2)` manipulates descriptor flags such as `FD_CLOEXEC`, open-file-description status flags such as `O_APPEND` and `O_NONBLOCK`, and advisory record locks via `F_SETLK`, `F_SETLKW`, and `F_GETLK`; POSIX byte-range locks are advisory, process-associated, and released on exit.
### 5.7 Pipes
`pipe()` creates a unidirectional byte stream whose empty reads and full writes normally block unless `O_NONBLOCK` is set; EOF appears when all writers close, writers get `SIGPIPE` or `EPIPE` when all readers close, writes up to `PIPE_BUF` are atomic, and FIFOs expose the same model through the filesystem namespace (`pipe(7)`, `fifo(7)`).
### 5.8 File System Operations
`mount(2)` attaches a filesystem instance at a mount point, `umount(2)` or `umount2(2)` detaches it and may fail with `EBUSY`, `sync(2)` requests broader persistence, `chdir()` and `fchdir()` change the current working directory, and `chroot(2)` changes the root for absolute path resolution but is explicitly not a complete security mechanism.

## 6. Process Representation and States
### 6.1 Process Control Block
A process is represented by kernel-maintained state often described as a PCB, holding identifiers, credentials, saved CPU state, scheduling state, signal dispositions, timers, resource accounting, memory-map references, and open-file context; `/proc/<pid>/status` exposes a user-visible summary (`proc_pid_status(5)`).
### 6.2 The Process Table
The classic process-table model still applies conceptually: the kernel maintains a global PID-keyed set of live process entries, with PID allocation subject to limits such as `/proc/sys/kernel/pid_max`, process 0 reserved for the idle/swapper role, and process 1 acting as the init or subreaper anchor (`fork(2)`, `proc(5)`).
### 6.3 Process States
Processes move among running, runnable, sleeping, stopped, and zombie states, with Linux exposing refinements such as `R`, `S`, `D`, `T`, `t`, and `Z` through `/proc`.
```text
new/forked -> runnable -> running -> exited -> zombie -> reaped
                    ^         |
                    |         v
               event ready <- sleeping/blocked
                              |
                              v
                           stopped
```
A zombie has no running thread or normal memory image but keeps enough state for a parent to reap it with `wait()`.
### 6.4 Credentials
Unix separates real, effective, and saved IDs, and `execve()` of a setuid or setgid program may change effective IDs unless `no_new_privs`, `nosuid`, or tracing suppresses the transition (`execve(2)`); supplementary groups affect group permission checks, and Linux further decomposes privilege into capabilities such as `CAP_DAC_OVERRIDE`, `CAP_CHOWN`, and `CAP_SYS_CHROOT`.
### 6.5 Process Relationships
`fork(2)` creates parent-child edges, `setpgid(2)` groups related processes for job control and terminal signal delivery, and `setsid(2)` creates a new session with its own process-group leader and optional controlling terminal; if an orphaned process group contains stopped members, the kernel sends `SIGHUP` followed by `SIGCONT` (`setpgid(2)`).

## 7. Process Lifecycle

Process control is the core Unix pattern: create a process, replace its image,
run it, observe state changes, and reap it.

### 7.1 Process Creation — `fork()`
`fork()` duplicates the calling process, returning 0 in the child and the child's PID in the parent; the child gets a separate virtual address space via copy-on-write, inherits file descriptors that share the same open file descriptions, and inherits signal dispositions; `vfork()` is a constrained variant that shares the parent's address space and suspends the parent until the child execs or exits.

### 7.2 Program Execution — `execve()`
`execve(pathname, argv, envp)` replaces the process image without changing the PID; the kernel verifies the executable (ELF or `#!` script), discards the old address space, loads the new image, builds a stack with argv/envp, closes `FD_CLOEXEC` descriptors, resets caught signal handlers to defaults, and applies setuid/setgid transitions unless suppressed by `no_new_privs`, `nosuid`, or tracing (`execve(2)`).

### 7.3 Process Termination — `_exit()`
`_exit(status)` terminates the process without running `atexit()` handlers or flushing stdio buffers; the kernel releases resources, closes file descriptors, delivers `SIGCHLD` to the parent, retains the exit status in a zombie entry until reaped, and reparents surviving children to init or a designated subreaper.

### 7.4 Waiting for Children — `wait()`, `waitpid()`, `wait4()`
The wait family blocks until a child changes state, returns the child's PID and status decodable with `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, and `WTERMSIG`; `WNOHANG` makes the check nonblocking, `WUNTRACED` reports stopped children, `wait4()` adds `struct rusage`, and reaping is what finally removes a zombie from the system.

### 7.5 Signals
Signals are asynchronous notifications with dispositions of default action, ignore, or catch; `sigaction()` is preferred over `signal()`, `sigprocmask()` controls the per-thread mask, `SIGKILL` and `SIGSTOP` cannot be caught or blocked, and signal dispositions are inherited across `fork()` but caught handlers reset on `execve()`.

### 7.6 The Shell as Fork-Exec-Wait
The shell demonstrates lifecycle control: `fork()` creates a child, the child sets up redirections with `dup2()` and calls `execve()`, the parent waits with `waitpid()`; pipelines chain multiple children with `pipe()`, and background jobs defer reaping via `SIGCHLD` handling or `waitpid(..., WNOHANG)`.

## 8. CPU Scheduling and Timekeeping

Scheduling decides which runnable thread gets CPU time next, and timekeeping
provides the clocks and accounting used to measure that execution.

### 8.1 Scheduling Goals
Schedulers balance fairness, interactive responsiveness, batch throughput, priority differentiation, and real-time predictability; these goals often conflict, and scheduling policy is the art of choosing acceptable trade-offs.

### 8.2 Traditional Unix Scheduling
Traditional Unix schedulers combined a base priority with a CPU-usage decay penalty, boosted I/O-bound processes on wake, and adjusted via `nice(2)` and `setpriority(2)` with a range of -20 to +19 where higher nice means lower priority.

### 8.3 Scheduling Classes (POSIX/Linux)
POSIX defines `SCHED_OTHER` (time-sharing), `SCHED_FIFO` (real-time run-to-block), and `SCHED_RR` (real-time round-robin); Linux real-time priorities 1–99 always preempt normal tasks, and CFS implements normal scheduling by tracking virtual runtime in a red-black tree.

### 8.4 Timekeeping
A hardware timer drives clock-tick interrupts for scheduler accounting and time-slice expiry; `clock_gettime()` reads `CLOCK_REALTIME` (wall clock, may jump) and `CLOCK_MONOTONIC` (never goes backward), and `times(2)` reports per-process user/system time in `_SC_CLK_TCK` ticks.

### 8.5 Alarms and Timers
`alarm(seconds)` delivers `SIGALRM` after a delay (replacing any pending alarm), `setitimer()` adds interval capability, POSIX `timer_create()` supports per-clock timers, and `sleep()`/`nanosleep()` block until a timer event or signal interruption.

### 8.6 Context Switch Mechanics
A context switch saves registers, selects the next runnable thread by policy, switches address-space state if needed, and restores the chosen thread's state; switches are costly due to TLB flushes, cache disruption, and pipeline stalls, so good scheduling balances latency against preemption cost.

## 9. Virtual Memory Management

Virtual memory lets each process see a large, private address space while the
kernel maps that space onto physical memory and backing storage page by page.

### 9.1 Address Space Layout
A process address space is divided into text (code, read-only, shareable), data (initialized globals), BSS (zero-filled), heap (`brk()`/`sbrk()` growth), memory-mapped regions (shared libraries, `mmap()`), and a downward-growing stack; layout varies by architecture and ASLR.

### 9.2 Paging
Virtual pages map to physical frames via multi-level page tables (4–5 levels on x86-64), with page-table entries recording presence, permissions, dirty, and accessed bits; hardware caches translations in the TLB, and permission violations cause `SIGSEGV` via `mprotect()`.

### 9.3 Demand Paging
Pages are loaded only on first access: a fault traps to the kernel, which checks the faulting address against valid regions, allocates a frame, fills it from the executable, mapped file, swap, or zeros, and restarts the instruction; invalid addresses yield `SIGSEGV`.

### 9.4 Page Replacement
When free memory runs low the kernel evicts pages using LRU approximations (clock/second-chance with accessed bits); clean file-backed pages are cheap to discard, dirty pages must be written back first, and Linux uses `kswapd` for background reclaim.

### 9.5 Copy-on-Write
`fork()` marks parent and child pages read-only; a write fault triggers a private copy for the faulting process, so read-only and exec-discarded pages avoid copying entirely; `MAP_PRIVATE` file mappings use the same mechanism.

### 9.6 Memory-Mapped Files — `mmap()`
`mmap(addr, length, prot, flags, fd, offset)` maps file or anonymous memory: `MAP_SHARED` writes are visible to other mappers and to the file, `MAP_PRIVATE` gives copy-on-write isolation, `MAP_ANONYMOUS` provides zero-filled non-file-backed memory, and `munmap()`/`msync()`/`madvise()` manage lifecycle and hints.

### 9.7 Swapping and Thrashing
Anonymous pages evicted from memory go to swap; thrashing occurs when the working set exceeds RAM, collapsing throughput as the CPU waits on page-fault I/O; Linux uses the OOM killer as a last resort when reclaim and swap cannot satisfy demand.


## 10. Device Driver Architecture
### 10.1 Device Classification
Unix represents many devices as special files under `/dev`, with character and block nodes carrying major and minor numbers from `mknod(2)`; block devices support cached random-access block I/O, while character devices expose byte-stream or device-specific sequential interfaces such as terminals, serial ports, and `/dev/null` (`null(4)`, `zero(4)`).
### 10.2 Driver Interface
Drivers export operations such as `open`, `close`, `read`, `write`, and `ioctl`, and modern kernels often add `poll`, `mmap`, and async support; pathname resolution identifies a device inode, the kernel locates the registered implementation from the device number, and block drivers serve queued block requests while character drivers implement direct stream-style operations.
### 10.3 Terminal Drivers and Line Disciplines
Terminals are character devices with a line discipline layered between the low-level driver and user-visible I/O, and `termios` is the portable control interface (`tty(4)`); canonical mode line-buffers input and interprets editing and signal characters, while noncanonical mode uses `VMIN` and `VTIME` for raw or cbreak-like behavior.
### 10.4 The `ioctl` Interface
`ioctl(fd, request, ...)` is the generic control path for operations that do not fit `read` and `write`, including terminal settings, geometry queries, interface configuration, and mode changes; its strength is flexibility and its weakness is weak type checking at the syscall boundary.
### 10.5 STREAMS (System V)
STREAMS modeled I/O as a stream head, a driver, and zero or more pushable modules that exchanged messages, making protocol layering and terminal processing explicit; Linux did not adopt STREAMS as its mainline architecture, but the design remains historically important.
### 10.6 Modern: Linux Device Model
Linux keeps the `/dev` plus major/minor model but adds a unified device model exported through sysfs under `/sys`; hotplug events and user-space tools such as `udev` then create device nodes, set permissions, and choose stable names based on runtime hardware identity.

## 11. Inter-Process Communication
### 11.1 IPC Overview
Unix IPC ranges from signals and exit status to pipes, FIFOs, System V objects, shared memory, sockets, and `ptrace()`, and each mechanism trades off locality, message boundaries, copying cost, synchronization needs, and ease of composition.
### 11.2 Pipes and FIFOs
Pipes and FIFOs are byte streams rather than message queues, so reads on empty channels and writes on full channels block unless `O_NONBLOCK` is used; EOF appears when all writers close, `SIGPIPE` or `EPIPE` appears when all readers close, writes up to `PIPE_BUF` are atomic, and neither object supports `lseek(2)` (`pipe(7)`, `fifo(7)`).
### 11.3 System V IPC - Overview
System V IPC groups message queues, shared memory, and semaphore sets behind the common pattern of `xxxget()` to create or open, `xxxctl()` to inspect or remove, and mechanism-specific operations to transfer data or synchronize; objects are keyed by `key_t` or created privately with `IPC_PRIVATE`, carry `ipc_perm` metadata, and persist until explicitly removed with operations such as `IPC_RMID`.
### 11.4 Message Queues
`msgget()` creates or opens a queue, `msgsnd()` appends typed messages, `msgrcv()` removes messages selected by type rules, and `msgctl()` manages status and removal; the kernel preserves message boundaries and type-based selection, so applications can use one queue for multiple logical channels or priorities.
### 11.5 Shared Memory
`shmget()` creates or opens a segment, `shmat()` maps it, and `shmdt()` detaches it, after which processes communicate by ordinary loads and stores without per-access syscalls; the segment outlives any one process until `IPC_RMID` and last-detach, so synchronization must be provided separately.
### 11.6 Semaphores
`semget()` creates or opens a semaphore set, `semop()` applies one or more operations atomically, and `semctl()` handles administration; negative operations wait for resources, zero waits for a zero value, `IPC_NOWAIT` avoids sleeping, and `SEM_UNDO` asks the kernel to reverse tracked adjustments if the process exits.
### 11.7 Process Tracing - `ptrace()`
`ptrace()` lets a tracer observe and control a tracee for debuggers and low-level tracing tools: a child may request tracing with `PTRACE_TRACEME`, a debugger may attach with `PTRACE_ATTACH`, `waitpid()` observes stops, and requests such as `PTRACE_PEEKDATA`, `PTRACE_GETREGS`, `PTRACE_CONT`, and `PTRACE_SINGLESTEP` inspect or resume execution.
### 11.8 Sockets
`socket(domain, type, protocol)` creates an endpoint for local or network communication, with stream, datagram, and other semantics determined by the socket type; the common server path is `socket() -> bind() -> listen() -> accept()`, the client path is `socket() -> connect()`, data uses `send`/`recv` or `read`/`write`, and readiness can be multiplexed with `select()`, `poll()`, or `epoll`.

## 12. Multiprocessor Synchronisation
### 12.1 The Problem
SMP and kernel preemption let multiple CPUs or kernel paths touch shared state concurrently, so mutual exclusion and memory-ordering rules are correctness requirements rather than optional performance features.
### 12.2 Hardware Atomics
Locks depend on atomic read-modify-write primitives such as test-and-set, compare-and-swap, and LL/SC, and they must be paired with compiler and CPU memory barriers so loads and stores become visible in the required order.
### 12.3 Spinlocks
Spinlocks busy-wait until a short critical section becomes free, so they are appropriate for interrupt, softirq, and tiny scheduler paths, but code holding a spinlock must not sleep; Linux provides variants such as `spin_lock_irqsave()` to combine locking with local interrupt disabling.
### 12.4 Mutexes and Sleeping Locks
Mutexes let waiters sleep instead of burning CPU time, so they fit longer process-context critical sections that may block, but they cannot be used in interrupt context or other atomic contexts where sleeping is forbidden.
### 12.5 Semaphores (Kernel)
Kernel semaphores generalize exclusive locks into counters, with `down()` decrementing or sleeping and `up()` incrementing and waking waiters; they suit bounded-resource coordination but are sleeping locks and therefore unsuitable in interrupt context.
### 12.6 Read-Write Locks
Read-write locks allow many readers or one writer, with Linux offering spin-based and sleeping forms; they help on read-heavy paths but increase bookkeeping and fairness complexity compared with a plain mutex.
### 12.7 Lock Ordering and Deadlock
Deadlock arises when locks are acquired in inconsistent orders, so kernels impose lock hierarchies and use tools such as lockdep to detect cycles; `trylock` may help in special cases, but disciplined lock ordering is the real invariant.
### 12.8 Per-CPU Data and RCU
Per-CPU data avoids contention by giving each CPU its own copy of hot state, and RCU lets readers traverse read-mostly structures while writers publish replacements and defer reclamation until a grace period has passed.
### 12.9 The Big Kernel Lock and Fine-Grained Locking
Early Linux SMP used the Big Kernel Lock to serialize large regions of kernel execution, but it scaled poorly, so modern kernels replaced it with finer-grained locks, atomic operations, per-CPU structures, and RCU at the cost of more design complexity.

## Appendix: Design Principles
1. **Everything is a file.** Devices, pipes, sockets, and many pseudo-files expose file descriptors, so user space can
   reuse the same small set of I/O calls across very different kernel objects.
   Uniform handles make composition easier.

2. **Mechanisms, not policies.** The kernel provides scheduling classes, permission bits, namespaces, IPC primitives,
   and memory mappings; user space decides how to combine them into higher-level behavior.
   Policy stays mostly outside the core kernel.

3. **Separation of naming from content.** Directory entries map names to inodes or equivalent objects, while the inode
   stores metadata and data references. Multiple names can therefore refer to the same underlying object.
   This keeps path handling and storage layout decoupled.

4. **Layered I/O abstraction.** Applications see file descriptors; the VFS translates to filesystem or device methods;
   filesystems and drivers talk to the block layer, character layer, or protocol stack beneath them.
   Each layer hides lower-level detail behind a narrow interface.

5. **Process isolation with controlled sharing.** Each process starts with its own virtual address space, and sharing is
   explicit through `fork()`, inherited descriptors, shared mappings, sockets, or System V objects.
   Isolation is the default, not an add-on.

6. **Asynchronous notification via signals.** Child exit, alarms, terminal events, and hangups arrive as signals,
   letting the kernel report important events without forcing continuous polling.
   Signals are sparse but deeply integrated into Unix control flow.

7. **Composition through fork-exec-pipe.** The shell creates complex behavior by combining simple programs with
   `fork()`, descriptor redirection, and pipes, rather than by demanding one huge monolithic program.
   Small tools stay useful because the kernel makes composition cheap.

8. **Cache aggressively, sync lazily.** Buffer caches, page cache, and dentry caches exploit locality and defer work;
   explicit calls such as `fsync()` exist for the cases where durability matters more than throughput.
   Performance comes from avoiding needless immediate I/O.

9. **Fail explicitly.** System calls report errors with return codes and specific `errno` values such as `ENOENT`,
   `EPERM`, `EPIPE`, and `EAGAIN`, enabling precise recovery and composition.
   Failure is visible and therefore programmable.

10. **Least privilege.** UIDs, GIDs, capabilities, namespaces, seccomp, and related mechanisms aim to give each process
    only the authority it actually needs.
    Security improves when ambient authority is minimized.

## Reference Files

- **`references/kernel-fundamentals.md`** — Full detail on dual-mode execution, buffer cache internals, and filesystem disk layout. Consult when explaining hardware/kernel mode transitions, cache algorithms, or inode/block addressing.
- **`references/files-and-naming.md`** — Full detail on file naming, metadata, permissions, and all file I/O system calls. Consult when explaining inodes, stat, permissions, file descriptors, pipes, or mount operations.
- **`references/processes.md`** — Full detail on process representation, states, credentials, and relationships. Consult when explaining the process table, state transitions, or credential model.
- **`references/process-lifecycle-vm.md`** — Full detail on fork, execve, _exit, wait, signals, scheduling classes, timekeeping, and virtual memory. Consult when explaining process lifecycle, signal handling, CPU scheduling, or memory management in depth.
- **`references/devices-ipc-sync.md`** — Full detail on device drivers, terminal line disciplines, IPC mechanisms (pipes, SysV, sockets), and multiprocessor synchronisation. Consult when explaining ioctl, STREAMS, message queues, shared memory, semaphores, sockets, or locking primitives.
- **`references/algorithms.md`** — Pseudocode for core kernel algorithms (buffer cache, filesystem traversal, process lifecycle, memory management, synchronisation). Consult when you need the step-by-step logic of a kernel operation.
- **`references/data-structures.md`** — C struct definitions and field descriptions for kernel data structures (stat, termios, ipc_perm, sockaddr, page table entries, etc.). Consult when you need exact struct layouts or field semantics.
- **`references/syscall-reference.md`** — Quick-reference card for 112 system calls organised by category, with prototypes, one-line descriptions, and key error codes. Consult when you need a syscall's signature or common errors at a glance.
- **`references/syscall.md`** — Auto-generated index of every system call mention across the skill, with file and line references. Consult to find where a specific syscall is discussed.
