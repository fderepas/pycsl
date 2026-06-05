# Devices, IPC, and Multiprocessor Synchronisation

Full detail on device drivers, inter-process communication, and multiprocessor synchronisation.

## 10. Device Driver Architecture
### 10.1 Device Classification
Unix represents many devices as special files, usually under `/dev`. These files do not hold ordinary data;
they name driver entry points inside the kernel. For character and block special files, `mknod(2)` records a
**major** and **minor** number. The major number selects a driver or driver family; the minor number selects a
particular unit, subdevice, or mode.

The traditional split is between **block devices** and **character devices**. Block devices transfer fixed-size
blocks, support random access, and sit behind the block layer plus the page or buffer cache. Disks are the
canonical example, and filesystems normally sit on top of them.

Character devices instead expose a byte stream or device-specific sequential interface. Terminals, serial ports,
pseudoterminals, and many control devices fall into this class. The kernel does not treat them like cached,
random-access block stores, even if a driver maintains small internal queues or buffers.

Simple devices make the distinction concrete. `man 4 null` and `man 4 zero` describe `/dev/null` as a sink that
discards writes and returns end-of-file on read, while `/dev/zero` discards writes and returns zero bytes on read.
These are character-device behaviors even though no physical hardware is involved.

The classification matters because it shapes the rest of the kernel path. Block devices are optimized for queued,
cache-backed storage I/O; character devices are optimized for direct stream handling, terminal semantics, and
control-oriented operations.

### 10.2 Driver Interface
A driver exports a set of operations the kernel can call. The classic conceptual set is `open`, `close`, `read`,
`write`, and `ioctl`. Modern kernels often add `poll`, `mmap`, and async support, but the core Unix idea is that
user space reaches very different devices through the same file-descriptor interface.

When a process opens a device node, the VFS resolves the pathname to an inode and sees that the inode represents a
device. From the embedded device number, the kernel finds the registered implementation. Older Unix descriptions
speak of character- and block-device switch tables; Linux expresses the same idea through registered operation
vectors and the block layer.

For character devices, reads and writes usually move bytes between the driver and user buffers, with whatever
validation, waiting, copying, and queue handling the device requires. For block devices, the kernel typically turns
user operations into cached block I/O requests, and the driver handles scheduled requests rather than raw stream
bytes from user space.

Traditional Unix descriptions give block drivers an extra strategy or request routine for servicing block I/O.
Linux uses request queues and bio structures instead of the old names, but the architectural role is the same:
block drivers serve block-oriented requests assembled by upper layers, while character drivers implement direct
stream-style operations.

### 10.3 Terminal Drivers and Line Disciplines
Terminals are character devices with additional semantics. A terminal path usually includes a low-level driver and a
**line discipline** that sits between the driver and user-visible reads and writes. The line discipline can echo
input, edit lines, translate characters, and generate signals.

`man 4 tty` describes `/dev/tty` as the controlling terminal of a process, with major 5 and minor 0 on Linux.
Portable applications configure terminal behavior through `termios`, not through ad hoc device-specific commands.
`struct termios` contains `c_iflag`, `c_oflag`, `c_cflag`, `c_lflag`, and the `c_cc[]` special-character array.

In **canonical mode** (`ICANON` set), input is line-buffered. A read completes when a line delimiter arrives; line
editing is active; and special characters such as `VERASE` and `VKILL` are interpreted by the line discipline.
When `ISIG` is enabled, `VINTR` produces `SIGINT`, `VQUIT` produces `SIGQUIT`, and job-control characters like
`VSUSP` can stop the foreground job.

In **noncanonical mode** (`ICANON` clear), input is available without waiting for a full line, line editing is
disabled, and read completion is controlled by `VMIN` and `VTIME`. This is the basis of raw or cbreak-like modes
used by screen programs, serial protocols, password entry, and terminal emulators.

`tcgetattr()` reads the current settings, and `tcsetattr()` applies new ones immediately, after drain, or after
flush depending on the requested action. Baud rates are handled through helpers such as `cfgetispeed()` and
`cfsetospeed()`. The line discipline therefore acts as a policy layer over a character driver that merely moves
bytes to and from hardware or a pseudo-terminal peer.

### 10.4 The `ioctl` Interface
`ioctl(fd, request, ...)` is the generic control path for operations that do not fit `read` and `write`. The file
descriptor identifies the target object, and the request code identifies a device-specific operation plus whatever
argument format that operation expects.

Terminal settings are the classic example. Historically, requests such as `TCGETS` and `TCSETS` were used directly;
portable code now prefers `tcgetattr()` and `tcsetattr()`, which wrap the underlying terminal ioctls. Other devices
use ioctl requests for tasks such as geometry queries, interface configuration, mode changes, and queue tuning.

The strength of `ioctl` is flexibility. Its weakness is that it is a catch-all with weak type checking at the
system-call boundary. Even so, Unix kernels keep it because real devices almost always expose a control plane that
cannot be expressed as ordinary byte-stream I/O.

### 10.5 STREAMS (System V)
System V STREAMS was a modular I/O framework built around a chain of processing stages. At the top sat the **stream
head**, which handled user-visible system calls. At the bottom sat a driver that talked to hardware or a lower-level
service. Between them sat zero or more **modules**.

Modules could transform, buffer, classify, or annotate data, and they communicated by passing messages rather than
by sharing one implicit byte stream inside the kernel. A configuration could often be changed dynamically by
pushing or popping modules, which made protocol layering and terminal processing more explicit.

Linux did not adopt STREAMS as its mainline device and networking architecture, but STREAMS remains historically
important. It showed a clear modular decomposition of I/O paths and strongly influenced later thinking about
protocol stacks, filter chains, and dynamically configurable communication layers.

### 10.6 Modern: Linux Device Model
Linux still honors the classic `/dev` plus major/minor model, but it adds a unified **device model** on top.
Kernel objects for devices, drivers, buses, and classes are exported through **sysfs**, normally mounted at `/sys`.
`/sys/devices` shows the device tree, `/sys/bus` groups by bus type, and `/sys/class` groups by function such as
`tty`, `block`, or `net`.

The practical effect is that device discovery and naming are no longer mostly static. The kernel emits hotplug
uevents, and user-space tools such as `udev` react by creating or removing device nodes, setting permissions,
choosing stable symlinks, and applying policy based on hardware identity. The old device-file abstraction remains,
but modern Linux couples it to a richer runtime model for discovery, binding, and hotplug.

## 11. Inter-Process Communication
### 11.1 IPC Overview
Unix IPC ranges from tiny notifications to rich bidirectional communication channels. At the lightweight end are
exit status and signals. At the richer end are pipes, FIFOs, System V objects, shared memory, sockets, and tracing
interfaces such as `ptrace()`.

Each mechanism makes a different trade-off. Some preserve message boundaries and some do not. Some are local to one
machine; sockets can also cross networks. Some copy data through kernel buffers, while shared memory avoids
per-access system calls after setup. Some are easy to compose in the shell, while others target high performance or
more specialized coordination patterns.

Unix therefore treats IPC as a toolbox rather than a single framework. The right choice depends on scope, data
volume, synchronization needs, and whether the program values simplicity, structure, or raw speed.

### 11.2 Pipes and FIFOs
A **pipe** is a unidirectional kernel buffer with a read end and a write end. `pipe(2)` creates one and returns two
file descriptors. Pipes are commonly used between related processes created by `fork()`, which is why they are the
natural building block for shell pipelines.

A **FIFO** or named pipe provides the same data-transfer semantics once opened, but it has a pathname in the
filesystem and is typically created with `mkfifo(3)`. That pathname lets unrelated processes rendezvous through the
filesystem namespace while still exchanging bytes through a kernel pipe buffer rather than through ordinary file
storage.

`man 7 pipe` emphasizes that pipes and FIFOs are byte streams: they do **not** preserve message boundaries. If a
process reads from an empty pipe, `read(2)` blocks until data arrives; if it writes to a full pipe, `write(2)`
blocks until enough space becomes available. With `O_NONBLOCK`, the same operations fail with `EAGAIN` instead of
sleeping.

End-of-stream rules matter. If all write descriptors are closed, readers see end-of-file and `read()` returns 0.
If all read descriptors are closed, a writer gets `SIGPIPE`; if that signal is ignored or blocked, the write fails
with `EPIPE`. Correctly closing unused duplicate descriptors after `fork()` is therefore part of correct pipe use.

POSIX defines `PIPE_BUF` so that writes of at most that size are atomic. Linux documents `PIPE_BUF` as 4096 bytes.
Writes larger than `PIPE_BUF` may be interleaved with data from other writers. Pipes also do not support `lseek(2)`,
which underlines their role as sequential communication channels rather than random-access objects.

### 11.3 System V IPC - Overview
System V IPC groups three facilities: message queues, shared memory, and semaphore sets. The APIs look different in
detail, but they share a recognizable pattern. `xxxget()` creates or opens an object, `xxxctl()` inspects or
removes it, and one or more mechanism-specific calls then perform data transfer or synchronization.

Objects are keyed by a `key_t`, often generated with `ftok(3)`, and the kernel returns an internal identifier such
as `msqid`, `shmid`, or `semid`. The special key `IPC_PRIVATE` requests creation of a fresh private object rather
than lookup by a shared key.

Creation flags mirror file-open conventions. `IPC_CREAT` means create the object if it does not already exist;
`IPC_EXCL` combined with `IPC_CREAT` makes creation fail if an object for that key already exists. Each object also
carries permission metadata in an `ipc_perm` structure, including owner IDs, creator IDs, and Unix-style mode bits.

A key difference from file descriptors is lifetime. System V IPC objects can outlive the creating process and remain
in kernel tables until explicitly removed, typically with `IPC_RMID`. Tools such as `ipcs` and `ipcrm` exist because
administrators must sometimes inspect and clean up these persistent kernel objects.

### 11.4 Message Queues
A System V message queue stores discrete records in the kernel. `msgget(key, flags)` creates or opens a queue and
returns an `msqid`. Each message begins with a positive `long` type field, traditionally named `mtype`, followed by
application data.

`msgsnd(msqid, msgp, msgsz, flags)` appends a message. If the queue lacks space, the sender blocks unless
`IPC_NOWAIT` is specified. `msgrcv(msqid, msgp, msgsz, msgtyp, flags)` removes a message selected by type.

The type-selection rules are a distinctive part of the API. If `msgtyp == 0`, the first message in the queue is
received. If `msgtyp > 0`, the first message of exactly that type is received. If `msgtyp < 0`, the queue returns
the message with the lowest type value less than or equal to `|msgtyp|`. This allows one queue to support simple
priorities or multiple logical channels.

If no matching message is available, the receiver blocks unless `IPC_NOWAIT` is supplied. `msgctl()` handles status
and lifecycle management: `IPC_STAT` reads queue metadata, `IPC_SET` updates selected fields, and `IPC_RMID`
removes the queue. Message queues are therefore useful when an application wants kernel-managed message boundaries
and typed selection without inventing its own framing protocol.

### 11.5 Shared Memory
System V shared memory is the classic high-throughput local IPC mechanism. `shmget(key, size, flags)` creates or
opens a segment and returns a `shmid`. `shmat(shmid, addr, flags)` attaches that segment into the caller's address
space and returns the mapped address.

After attachment, the process performs ordinary loads and stores. There is no per-access system call and no copying
through a pipe or socket buffer. This is why shared memory is often the fastest local IPC method for large data
structures or high traffic.

`shmdt(addr)` detaches a mapping from one process. The segment itself remains until `shmctl(..., IPC_RMID, ...)`
marks it for removal, and actual destruction waits until the last attachment disappears. Shared memory therefore has
object lifetime separate from process lifetime.

The price of speed is that shared memory does not provide synchronization by itself. Processes must coordinate with
semaphores, mutexes placed in shared mappings, lock-free protocols, or some other external scheme. Shared memory is
best understood as a data-sharing mechanism, not a complete communication protocol.

### 11.6 Semaphores
System V semaphores provide kernel-managed synchronization state. `semget(key, nsems, flags)` creates or opens a set
containing `nsems` semaphores and returns a `semid`. The interface is built around arrays from the start rather than
single semaphore objects.

`semop(semid, sops, nsops)` applies an array of operations atomically. For each `struct sembuf`, a positive
`sem_op` increments the semaphore, a negative `sem_op` decrements it if possible or blocks otherwise, and a zero
`sem_op` waits until the semaphore value becomes zero. `IPC_NOWAIT` converts blocking cases into immediate failure.

`SEM_UNDO` asks the kernel to remember an adjustment that should be undone automatically if the process exits. This
helps keep crash cleanup from leaving semaphore counts permanently wrong, though it does not replace careful protocol
design.

`semctl()` provides administrative operations such as `GETVAL`, `SETVAL`, and `IPC_RMID`. System V semaphores are
verbose compared with newer APIs, but they are expressive: they can count resources, serialize access, and perform
multi-semaphore transactions in one atomic `semop()` call.

### 11.7 Process Tracing - `ptrace()`
`ptrace(request, pid, addr, data)` lets one process observe and control another. The controlling process is the
**tracer** and the controlled process is the **tracee**. This interface is the foundation of debuggers and low-level
process tracing tools.

A child can request tracing with `PTRACE_TRACEME` before `exec`, or a debugger can attach to an existing process
with `PTRACE_ATTACH`. Once tracing is active, the tracee stops at significant events such as signal delivery and
`exec`, and the tracer usually uses `waitpid()` to observe those stops.

Requests such as `PTRACE_PEEKDATA` and `PTRACE_POKEDATA` read and write the tracee's memory. `PTRACE_GETREGS` and
`PTRACE_SETREGS` access registers on architectures that support them. `PTRACE_CONT` resumes execution, while
`PTRACE_SINGLESTEP` runs one instruction and stops again. `gdb` and `strace` are the best-known user-space clients
of this mechanism.

### 11.8 Sockets
Sockets generalize IPC beyond the parent-child model. `socket(domain, type, protocol)` creates an endpoint and
returns a file descriptor. Common domains are `AF_UNIX` for local communication, `AF_INET` for IPv4, and `AF_INET6`
for IPv6.

The socket type determines semantics. `SOCK_STREAM` provides a sequenced, reliable, connection-based byte stream;
TCP is the standard Internet example. `SOCK_DGRAM` provides connectionless datagrams; for Internet sockets this is
usually UDP. `man 7 unix` notes that Unix-domain datagram sockets preserve message boundaries and are reliable on
Linux, unlike UDP.

The normal connection-oriented server flow is `socket() -> bind() -> listen() -> accept()`. `bind()` assigns a local
address, `listen()` marks the socket as passive, and `accept()` returns a **new** descriptor for one established
connection while leaving the listening socket available for more. The client side is usually `socket() -> connect()`.

Data transfer then uses `send()` and `recv()` or, on stream sockets, plain `read()` and `write()`. Datagram programs
often use `sendto()` and `recvfrom()` so that each packet carries explicit source or destination addressing.
`shutdown(fd, how)` disables reading, writing, or both with `SHUT_RD`, `SHUT_WR`, or `SHUT_RDWR`.

For multiplexing, classic Unix provides `select()`, which monitors descriptor sets for read, write, or exception
readiness. Modern code may prefer `poll()` or Linux `epoll`, but the architectural idea is the same: one process
can coordinate many communication endpoints without dedicating a thread to each one.

## 12. Multiprocessor Synchronisation
### 12.1 The Problem
Early Unix kernels on uniprocessors often relied on a simple execution model: once in kernel mode, a thread ran
until it blocked or returned to user mode. Interrupts still introduced concurrency, but the space of interleavings
was much smaller than on an SMP machine.

SMP breaks that assumption. Two CPUs can execute kernel code at the same time and touch the same shared data. Without
synchronization, updates to lists, counters, queues, and object state race with one another. Kernel preemption adds a
related problem even on one CPU, because one kernel path can be interrupted and another scheduled.

The result is that modern kernels need explicit mutual exclusion, memory-ordering rules, and context-aware locking.
Synchronization is not just a performance feature; it is a correctness requirement.

### 12.2 Hardware Atomics
Higher-level locks depend on hardware instructions that make a read-modify-write sequence indivisible. Typical
examples are **test-and-set**, **compare-and-swap** (CAS), and **load-linked/store-conditional** (LL/SC).
Without such primitives, even a simple shared counter increment could lose updates under contention.

Atomics must be paired with **memory barriers**, because compilers and CPUs may reorder loads and stores for
performance. Compiler barriers constrain optimization; CPU barriers constrain visibility and ordering across cores.
Acquire, release, and full barriers are the building blocks that make higher-level synchronization trustworthy.

### 12.3 Spinlocks
A **spinlock** is the standard short-duration lock in kernel code. If the lock is unavailable, the caller busy-waits
until it becomes free. This is efficient only when the critical section is very short.

A thread holding a spinlock must not sleep. If it blocks while owning the lock, other CPUs may spin forever waiting
for a lock that cannot be released. Spinlocks are therefore the normal choice for data touched in interrupt context,
softirq context, or tiny scheduler paths.

Linux provides `spin_lock()` and `spin_unlock()`, plus variants such as `spin_lock_irqsave()` that also disable
local interrupts while the lock is held. On a uniprocessor build, the implementation may collapse to interrupt or
preemption control rather than literal spinning, but the abstraction stays the same.

### 12.4 Mutexes and Sleeping Locks
When the protected region may take longer, spinning wastes CPU time. A **mutex** lets the waiter sleep and gives the
processor to some other runnable task. This makes mutexes appropriate for process-context code that may block or run
for longer than a tiny critical section.

Linux exposes `mutex_lock()` and `mutex_unlock()` for this purpose. The holder may sleep, and a contending thread
sleeps instead of burning cycles. The cost is that mutexes cannot be used in interrupt context or other atomic
contexts where sleeping is forbidden.

### 12.5 Semaphores (Kernel)
Kernel counting semaphores generalize exclusive locks into a resource counter. `down()` decrements the count or
sleeps if the count is zero; `up()` increments it and wakes waiters. This fits bounded resource pools such as a
fixed number of buffers or channels.

Semaphores are sleeping locks, so they are unsuitable in interrupt context. Modern Linux often prefers mutexes or
specialized completions for one-owner cases, but semaphores remain an important conceptual tool for counting-style
synchronization.

### 12.6 Read-Write Locks
A **read-write lock** allows either multiple readers or one exclusive writer. It is useful when read traffic greatly
outnumbers writes and readers do not interfere with one another.

Linux offers a spin-based form (`rwlock_t`) for short atomic regions and a sleeping form (`rw_semaphore`) for longer
process-context regions. These locks can improve throughput on read-heavy paths, but they add bookkeeping and can
make fairness more complicated than with a plain mutex.

### 12.7 Lock Ordering and Deadlock
Locks prevent races, but bad locking order creates deadlocks. The classic case is two threads acquiring two locks in
opposite orders and then waiting forever.

The standard prevention rule is to define a global lock hierarchy and always acquire locks in that order. Linux also
includes **lockdep**, a runtime lock-dependency checker that tracks observed lock orderings and warns about cycles
that could deadlock. `trylock` can sometimes be useful as an escape hatch, but the real solution is disciplined lock
design, not endless retries.

### 12.8 Per-CPU Data and RCU
A common way to avoid contention is to avoid sharing. **Per-CPU data** gives each CPU its own copy of a hot variable
or structure, so updates proceed without global locking and are combined later when needed.

For read-mostly shared structures, Linux often uses **RCU**. Read-Copy-Update lets readers traverse data with very
low overhead while writers publish a new version and defer reclamation of the old one until a **grace period** has
passed. Readers thus see either the old version or the new version, not a partially updated structure.

Per-CPU storage and RCU are both examples of replacing generic locking with workload-specific synchronization
strategies that scale better on SMP systems.

### 12.9 The Big Kernel Lock and Fine-Grained Locking
Early Linux SMP support relied heavily on the **Big Kernel Lock** (BKL), a single coarse lock protecting large
regions of kernel execution. It simplified correctness because developers did not have to reason about each
subsystem independently.

Its scalability limits were severe: unrelated work still serialized behind one giant lock. Over time Linux replaced
the BKL with fine-grained subsystem locks, atomic operations, per-CPU structures, and RCU. The gain was much better
parallelism; the cost was greater complexity, more lock-ordering hazards, and a higher need for analysis tools and
discipline.

