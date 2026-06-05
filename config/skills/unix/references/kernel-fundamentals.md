# Kernel Fundamentals

Full detail on dual-mode execution, the buffer cache, and on-disk filesystem layout.

## 1. Dual-Mode Execution and System Calls
### 1.1 Hardware Protection Rings
Unix kernels depend on CPU-enforced privilege separation rather than mere convention.
Most processors expose several privilege levels, but Unix usually treats them as two
practical domains: user mode for applications and kernel mode for the operating system.
User mode forbids privileged instructions, direct device control, page-table changes, and
arbitrary access to kernel memory.
If user code attempts such operations, the CPU raises an exception instead of executing them.
A controlled transition uses a trap-like instruction that enters a privileged kernel entry
path.
`syscall(2)` lists examples such as `syscall` on x86-64, `int $0x80` on i386, and `svc #0`
on arm64.
### 1.2 System Call Mechanism
A system call is the standard entry point from user space into the kernel (see `intro(2)`).
Programs normally call C library wrappers like `read()`, `write()`, or `open()` rather than
issuing raw trap instructions themselves.
As `intro(2)` explains, the wrapper typically copies arguments and the syscall number into
registers, traps to kernel mode, and translates kernel error returns into `errno`.

```c
ssize_t n = write(fd, buf, len);
if (n == -1) perror("write");
```
The exact register convention is ABI-specific.
`syscall(2)` notes that x86-64 uses `eax` for the syscall number and `rax` for the return
value, while other architectures use different registers and, on some 32-bit ABIs, must
split 64-bit arguments across aligned register pairs.
Inside the kernel, the low-level entry stub validates the request and dispatches through a
syscall table indexed by the syscall number.
That table maps numbers such as `SYS_read` or `SYS_fsync` to kernel handler routines.
An unimplemented number yields `ENOSYS` (`syscall(2)`).
Kernel code often reports failure internally as a negative error code; the C library wrapper
converts that into `-1` for the caller and stores the positive error value in `errno`
(`intro(2)`).
A successful call may return zero, a byte count, a file descriptor, a PID, or another
syscall-specific result.
### 1.3 Interrupts and Exceptions
System calls are only one way to enter the kernel.
Hardware interrupts originate outside the running instruction stream: a timer expires, a disk
completes I/O, a NIC receives a packet, or another CPU sends an inter-processor interrupt.
The processor consults an interrupt vector or descriptor table to locate the appropriate
handler.
Exceptions arise from the current instruction stream itself.
Typical examples are page faults, divide-by-zero, invalid opcodes, and protection faults.
Some exceptions are recoverable faults; a page fault may be satisfied by installing a page.
Others terminate the current operation or process.

Many synchronous exceptions are reflected to user processes as signals.
`signal(7)` lists hardware-exception-related signals such as `SIGSEGV`, `SIGBUS`, `SIGFPE`,
`SIGILL`, and `SIGTRAP`.
It also warns that the exact signal may vary by architecture for similar low-level faults.
Interrupt handling also involves priority.
Architectures define which vectors are reserved for exceptions, and kernels often mask or
deflect lower-priority work while urgent interrupts run.
Deferred work mechanisms keep interrupt latency low without allowing arbitrary nesting to
corrupt shared state.
### 1.4 Context Switching
A context switch stops execution of one thread and resumes another.
To do that safely, the kernel saves enough CPU state from the old thread and restores the
saved state of the new one: general registers, program counter, stack pointer, status flags,
and any architecture-specific state that matters for resumption.
If the next thread belongs to another process, the kernel also switches address-space state,
such as the page-table base or address-space identifier.

A switch may be voluntary.
A thread that blocks in a system call, sleeps waiting for I/O, or explicitly yields cannot
make progress and lets the scheduler run something else.
A switch may also be involuntary.
A timer interrupt may preempt the current thread when its time slice expires, or the kernel
may notice that a higher-priority runnable thread should run first.

```c
save_cpu_state(current);
next = pick_next_runnable();
load_mm_if_needed(next);
restore_cpu_state(next);
return_to_execution(next);
```
Context switches are expensive compared with straight-line execution.
Register save/restore is only part of the cost; cache locality, branch prediction, TLB
entries, and pipeline state are disturbed as well.
This is why excessive blocking, lock contention, and wakeup storms reduce throughput.
### 1.5 Kernel Re-entrancy
Traditional Unix kernels were largely non-preemptive while executing kernel code.
Once a thread entered the kernel, it typically ran until it blocked, completed the syscall,
or explicitly yielded.
This simplified critical sections because many invariants were protected by "run to
completion" on a CPU rather than by fine-grained preemption control.
The trade-off was latency: a long kernel path could delay interactive work or scheduling.

Modern kernels are much more preemptible and re-entrant.
Linux can preempt kernel execution at many points, subject to rules about locks,
interrupt-disabled regions, and explicitly non-preemptible sections.
Correctness now depends on spinlocks, mutexes, atomic operations, memory-ordering rules, and
careful separation between hard-interrupt, soft-interrupt, and process contexts.
`signal(7)` shows a related controlled re-entry path on return to user space: before the
kernel resumes user mode, it checks for pending unblocked signals, builds a signal frame if
needed, and later restores the interrupted state via `sigreturn(2)`.

## 2. Block I/O and the Buffer Cache
### 2.1 Purpose of the Buffer Cache
Block devices are far slower than CPU and RAM, and they work best with aligned block-sized
transfers.
A kernel therefore caches disk blocks in memory between the filesystem layer and the device.
The buffer cache reduces repeated disk reads, absorbs bursts of writes, and lets the kernel
coalesce small updates into larger, better-ordered I/O.
It also gives filesystems a uniform block-oriented interface instead of forcing every caller
to manage raw device operations.
On modern Linux, much regular-file data is handled through the page cache, but the classical
buffer-cache model still explains cached block metadata and delayed write-back.
### 2.2 Cache Structure
A classic design keeps buffers in a hash table keyed by `(device, block_number)`.
That supports fast lookup of a cached block.
Each buffer has a header describing the cached object and its state.
Typical metadata includes the device number, logical block number, a pointer to the data,
and status flags such as `busy`, `valid`, `delayed_write`, and `async`.
The header also contains linkage for the hash bucket and for a free or recyclable list.
The free list is a list of buffers that are not currently busy and may be reused.
Recycling policy is usually some approximation of LRU or aging so recently used blocks stay
cached longer.
### 2.3 Buffer Lookup and Allocation
Lookup starts with the hash table.
On a hit, if the matching buffer is present and not busy, the kernel marks it busy and
returns it immediately.
If the matching buffer exists but another thread is using it, the caller sleeps until the
buffer becomes available.
On a miss, the kernel takes a buffer from the free list and retags it for the requested block.
If the candidate victim is dirty, it must be written back before reuse.
If no free buffers exist, the caller sleeps waiting for one to be released.

Wakeups are advisory, so the caller must recheck shared state after every sleep.
Another thread may have filled the requested block or consumed the newly freed buffer before
the sleeper runs again.
That makes the allocation path a retry loop, not a single linear decision tree.

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
A block read helper often called `bread()` performs "lookup first, I/O on miss".
If the buffer is present and valid, `bread()` returns it from cache.
Otherwise the kernel allocates a buffer, submits device I/O, and sleeps until completion.
The interrupt path marks the buffer valid and wakes waiters when the transfer finishes.

A synchronous write, traditionally `bwrite()`, submits the write and waits for completion.
A delayed write, `bdwrite()`, marks the buffer dirty and releases it for later write-back
instead of forcing immediate I/O.
That improves throughput when the same block is rewritten several times in quick succession.
An asynchronous write starts the transfer and lets the caller continue before completion.
Read-ahead applies the same idea to reads: when access looks sequential, the kernel fetches
later blocks early so they are likely to be in memory when requested.
### 2.5 Cache Coherency and Sync
Caching raises the question of when modified state reaches stable storage.
`fsync(2)` says it flushes modified in-core file data and associated metadata needed for
retrieval, while `fdatasync(2)` may omit metadata not required for a correct later read.
`fsync(2)` also notes that syncing the file alone does not necessarily persist the directory
entry containing it; a directory `fsync()` may also be needed.
`sync(2)` and `syncfs(2)` push broader filesystem state to disk.

Ordering matters as much as flushing.
If allocation metadata reaches disk before the data block it describes, a crash can expose
stale or uninitialized contents.
Older filesystems relied on careful write ordering and periodic flushers.
Journaling is a modern alternative: metadata updates, or metadata plus data depending on the
mode, are first recorded in a log so recovery can replay committed operations after a crash.
### 2.6 Advantages and Limitations
The buffer cache provides a uniform block abstraction, reduces physical I/O, and improves
throughput by coalescing writes and exploiting locality.
It is especially effective for frequently reused filesystem metadata.
Its limitations are equally important.
Memory is finite, so poor locality causes eviction churn.
Dirty data can be lost on power failure before write-back, making `fsync(2)`, `sync(2)`, and
journaling important.
There is also overhead from copying data among user buffers, page cache, and block-oriented
kernel buffers, plus concurrency complexity from locks, wait queues, and wakeups.

## 3. On-Disk File System Layout
### 3.1 Disk Abstraction
A filesystem views persistent storage as an array of logical blocks.
The underlying device may expose sectors or other physical units, but the on-disk format is
built around logical block numbers and allocation units.
A filesystem is usually created inside a partition, a whole disk, or a logical volume.
Once mounted, the kernel exposes it through a common VFS interface while preserving its own
internal layout rules.
`statfs(2)` reports high-level properties of the mounted filesystem such as block size, total
blocks, free blocks, total inodes, and free inodes.
Ext2 and ext4 further divide the volume into block groups so related metadata and data can be
kept physically near one another.
### 3.2 Superblock
The superblock is the master record that describes the volume format.
It stores global metadata such as block size, inode count, free block and free inode counts,
feature flags, filesystem state, and identifiers like a UUID.
Without a readable superblock the kernel cannot interpret the rest of the disk safely.
Ext-family filesystems also maintain per-group descriptors describing local metadata areas.
`ext4(5)` documents features such as `sparse_super` and `sparse_super2`, where backup
superblocks and group descriptors are replicated only in selected block groups.
Replication improves recoverability while avoiding the space cost of storing full copies in
every group.
Mount-state and feature bits are important because they tell the kernel whether recovery,
compatibility checks, or journal replay are required.
### 3.3 Inode Structure
An inode is the per-file metadata record.
As summarized by `inode(7)` and `stat(2)`, it stores file type, permission bits, owner UID,
group GID, size, timestamps, link count, and the information needed to find the file's data
blocks.
Device special files also encode the represented device number.
Directories, regular files, symlinks, and special files all have inodes, even though their
data is interpreted differently.

The classic Unix layout uses direct pointers plus single-indirect, double-indirect, and
triple-indirect pointers.
A direct pointer references a data block directly.
A single-indirect pointer references a block full of block numbers; double- and
triple-indirect pointers add one or two more levels.
If block size is `B` and each block number occupies `P` bytes, one indirect block holds
`N = B / P` pointers, so the classic maximum data-block count is `12 + N + N^2 + N^3`.
With 4 KiB blocks and 4-byte block numbers, `N = 1024`, giving about 4 TiB + 4 GiB + 4 MiB
+ 48 KiB of addressable file data before other filesystem limits apply.
Ext4 often uses extents instead, but the indirect-pointer scheme remains the classic model.
### 3.4 Directory Structure
A directory is a file whose contents map names to inode numbers.
Path lookup reads directory entries component by component and follows the referenced inode
for the next step.
By convention, every directory contains `.` for itself and `..` for its parent, except that
root is a special case.
In ext2/ext4, directory entries are variable-length records so names of different lengths can
be packed efficiently.
`ext4(5)` also documents file-type information stored in directory entries.
Larger directories may use indexing structures for faster lookup, but the fundamental model is
still a name-to-inode mapping stored as file data.
### 3.5 Free Space Management
The filesystem must also track free blocks and free inodes.
A bitmap-based design uses one bit per allocatable object, giving compact storage and fast
search for free space or runs of free blocks.
Ext2 and ext4 use block and inode bitmaps within each block group (`ext4(5)`).
A linked-list design chains free blocks together and is simpler conceptually, but it makes
locality-aware allocation and contiguous placement harder.
Bitmaps work well with block-group allocation strategies because the allocator can search near
a file's inode or parent directory.
That locality reduces seeks and often improves cache behavior as well.
### 3.6 Path Resolution
Path resolution turns a pathname into a filesystem object.
`path_resolution(7)` describes a component-by-component walk.
If the path starts with `/`, lookup begins at the process root directory; otherwise it begins
at the current working directory or the directory file descriptor supplied to an *at() call.
For each nonfinal component, the kernel must find the named directory entry and verify search
permission on the current directory.
If search permission is missing, the result is `EACCES`; a missing component yields `ENOENT`;
an intermediate nondirectory yields `ENOTDIR` (`path_resolution(7)`).
Symbolic links can redirect the walk, subject to loop limits.
The final component is handled similarly but may be allowed not to exist yet when a creating
system call is used.
A trailing `/` forces the preceding component to resolve as a directory.
On directories, the execute bit means search or traversal permission, so path lookup is a
security check at every level, not just on the final object.
