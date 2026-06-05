# Unix Kernel Internals: Data Structures

This reference is based on local Linux man pages, POSIX-visible C interfaces, glibc headers, and Linux kernel headers/documentation concepts.
Where a structure is part of the user-kernel ABI, the code block shows a public definition or the standard man-page form.
Where a topic is a kernel concept rather than a stable public struct, the code block is explicitly marked as conceptual.

## 1. File System Structures
### `struct stat`
```c
struct stat {
    dev_t      st_dev;
    ino_t      st_ino;
    mode_t     st_mode;
    nlink_t    st_nlink;
    uid_t      st_uid;
    gid_t      st_gid;
    dev_t      st_rdev;
    off_t      st_size;
    blksize_t  st_blksize;
    blkcnt_t   st_blocks;
    struct timespec st_atim;
    struct timespec st_mtim;
    struct timespec st_ctim;
};
```
- `st_dev`: device containing the file's inode.
- `st_ino`: inode number within that filesystem.
- `st_mode`: file type bits plus permission bits.
- `st_nlink`: hard-link count.
- `st_uid`: owning user ID.
- `st_gid`: owning group ID.
- `st_rdev`: device number for character/block special files.
- `st_size`: byte size of the file.
- `st_blksize`: preferred I/O block size.
- `st_blocks`: number of allocated 512-byte blocks.
- `st_atim`: last access time.
- `st_mtim`: last data modification time.
- `st_ctim`: last status-change time.
How the kernel uses it: The VFS gathers inode and filesystem metadata and copies it into a `stat` result; System calls such as `stat()`, `fstat()`, `lstat()`, and `fstatat()` expose file state to user space; Fields come from inode state, mount state, and sometimes filesystem-specific translation.
### `struct dirent`
```c
struct dirent {
    ino_t          d_ino;
    off_t          d_off;
    unsigned short d_reclen;
    unsigned char  d_type;
    char           d_name[256];
};
```
- `d_ino`: inode number associated with the directory entry.
- `d_off`: position value used by `telldir()`/`seekdir()`; not a portable byte offset.
- `d_reclen`: size of this directory record.
- `d_type`: entry type hint such as regular file, directory, symlink, or `DT_UNKNOWN`.
- `d_name`: null-terminated filename component.
How the kernel uses it: Filesystems iterate directory data and present entries through the VFS `readdir` path; The kernel converts on-disk directory formats into `dirent`-like records for user space; `d_type` is an optimization; callers must still handle `DT_UNKNOWN` and fall back to `stat()`.
### Superblock concept
```c
/* Conceptual Unix superblock; not a stable public UAPI struct. */
struct superblock_concept {
    unsigned long block_size;
    unsigned long total_blocks;
    unsigned long free_blocks;
    unsigned long total_inodes;
    unsigned long free_inodes;
    unsigned long first_data_block;
    unsigned long filesystem_state;
    unsigned long mount_flags;
    unsigned long magic;
};
```
- `block_size`: allocation and I/O granularity for the filesystem.
- `total_blocks`: total data blocks managed by the filesystem.
- `free_blocks`: free block count.
- `total_inodes`: total inode count.
- `free_inodes`: available inode count.
- `first_data_block`: where usable data blocks begin.
- `filesystem_state`: clean/dirty/error state.
- `mount_flags`: read-only, synchronous, noatime, and similar state.
- `magic`: filesystem type identifier.
How the kernel uses it: The superblock is the in-memory object representing one mounted filesystem instance; It anchors mount-wide state: root inode/dentry, operations tables, limits, and allocator metadata; Filesystem code reads the on-disk superblock at mount time, validates it, and builds the VFS superblock.
### Inode concept
```c
/* Conceptual Unix inode; actual layouts are filesystem-specific. */
struct inode_concept {
    mode_t        i_mode;
    uid_t         i_uid;
    gid_t         i_gid;
    nlink_t       i_nlink;
    off_t         i_size;
    time_t        i_atime;
    time_t        i_mtime;
    time_t        i_ctime;
    blkcnt_t      i_blocks;
    unsigned long i_flags;
    unsigned long i_direct[12];
    unsigned long i_indirect;
    unsigned long i_double_indirect;
    unsigned long i_triple_indirect;
};
```
- `i_mode`: object type and permission bits.
- `i_uid` / `i_gid`: owner identifiers.
- `i_nlink`: hard-link count.
- `i_size`: logical file size.
- `i_atime`, `i_mtime`, `i_ctime`: access, modification, and status-change timestamps.
- `i_blocks`: storage blocks consumed.
- `i_flags`: immutable, append-only, and filesystem-specific flags.
- `i_direct[]`: direct block pointers for small files.
- `i_indirect`: block pointer to a table of block pointers.
- `i_double_indirect`: pointer to a table of indirect blocks.
- `i_triple_indirect`: pointer to a table of double-indirect blocks.
How the kernel uses it: The inode is the core in-memory identity for a file, directory, device node, pipe, or symlink; The VFS caches inodes and routes operations like lookup, read, write, chmod, and truncate through them; Traditional Unix filesystems used direct and indirect pointers to map file offsets to disk blocks; Modern Linux filesystems may use extents instead of classic direct/indirect arrays, but the inode concept is unchanged.
### Buffer header concept
```c
/* Conceptual buffer header. Linux has struct buffer_head internally. */
struct buffer_header_concept {
    dev_t         b_dev;
    unsigned long b_blocknr;
    unsigned long b_state;
    void         *b_data;
    struct buffer_header_concept *b_hash_next;
    struct buffer_header_concept *b_hash_prev;
    struct buffer_header_concept *b_free_next;
    struct buffer_header_concept *b_free_prev;
};
```
- `b_dev`: device containing the cached block.
- `b_blocknr`: logical block number on that device.
- `b_state`: dirty, locked, uptodate, mapped, delayed, and related flags.
- `b_data`: pointer to the cached block data in memory.
- `b_hash_next` / `b_hash_prev`: links in the lookup hash for `(device, block)`.
- `b_free_next` / `b_free_prev`: links in free/LRU style lists.
How the kernel uses it: Historically, buffer headers tracked cached disk blocks and block I/O state; Linux still has `struct buffer_head`, but modern block I/O is centered on bio/folio/page structures; Buffer headers remain useful for block mapping, metadata buffers, and compatibility paths such as `submit_bh()`.

## 2. Process Structures
### Process control block concept
```c
/* Conceptual process control block; Linux uses task_struct plus related structs. */
struct pcb_concept {
    pid_t         pid;
    pid_t         ppid;
    uid_t         ruid, euid, suid;
    gid_t         rgid, egid, sgid;
    int           state;
    void         *saved_registers;
    void         *kernel_stack;
    void         *memory_map;
    void         *fd_table;
    void         *signal_table;
    int           priority;
    struct rusage usage;
};
```
- `pid`: process identifier.
- `ppid`: parent process identifier.
- `ruid`, `euid`, `suid`: real, effective, and saved user IDs.
- `rgid`, `egid`, `sgid`: real, effective, and saved group IDs.
- `state`: runnable, sleeping, stopped, zombie, and similar scheduler states.
- `saved_registers`: CPU context saved during traps or context switches.
- `kernel_stack`: per-thread kernel stack.
- `memory_map`: address-space descriptor.
- `fd_table`: open-file descriptor table.
- `signal_table`: dispositions, masks, and pending signals.
- `priority`: scheduler priority / policy state.
- `usage`: accumulated resource accounting.
How the kernel uses it: A PCB is the scheduler-visible record that lets the kernel stop and later resume a process or thread; Linux splits this across `task_struct`, credential structures, signal structures, files tables, and `mm_struct`; Context switching, credential checks, signal delivery, and `/proc` reporting all depend on this state.
### `struct rusage`
```c
struct rusage {
    struct timeval ru_utime;
    struct timeval ru_stime;
    long ru_maxrss;
    long ru_ixrss;
    long ru_idrss;
    long ru_isrss;
    long ru_minflt;
    long ru_majflt;
    long ru_nswap;
    long ru_inblock;
    long ru_oublock;
    long ru_msgsnd;
    long ru_msgrcv;
    long ru_nsignals;
    long ru_nvcsw;
    long ru_nivcsw;
};
```
- `ru_utime`: user CPU time consumed.
- `ru_stime`: system CPU time consumed.
- `ru_maxrss`: maximum resident set size.
- `ru_ixrss`: integral shared memory size; unmaintained on Linux.
- `ru_idrss`: integral unshared data size; unmaintained on Linux.
- `ru_isrss`: integral unshared stack size; unmaintained on Linux.
- `ru_minflt`: soft page faults.
- `ru_majflt`: hard page faults requiring I/O.
- `ru_nswap`: swap count; unmaintained on Linux.
- `ru_inblock`: block input operations.
- `ru_oublock`: block output operations.
- `ru_msgsnd`: SysV IPC messages sent; unmaintained on Linux.
- `ru_msgrcv`: SysV IPC messages received; unmaintained on Linux.
- `ru_nsignals`: signals received; unmaintained on Linux.
- `ru_nvcsw`: voluntary context switches.
- `ru_nivcsw`: involuntary context switches.
How the kernel uses it: The kernel accumulates execution, memory-fault, I/O, and scheduling counters per task and descendants; `getrusage()` and `wait4()` export these counters to user space; Resource accounting is useful for profiling, quotas, shells, and job-control tools.
### `sigset_t`
```c
typedef struct {
    unsigned long int __val[_SIGSET_NWORDS];
} __sigset_t;
typedef __sigset_t sigset_t;
```
- `__val[]`: bitset holding one bit per signal number.
How the kernel uses it: Signal masks decide which signals are currently blocked for a thread; Pending-signal queues are checked against the blocked mask before delivery; The kernel uses signal sets for thread masks, shared process pending sets, and system-call interfaces like `sigprocmask()`.
### `struct sigaction`
```c
struct sigaction {
    void     (*sa_handler)(int);
    void     (*sa_sigaction)(int, siginfo_t *, void *);
    sigset_t   sa_mask;
    int        sa_flags;
    void     (*sa_restorer)(void);
};
```
- `sa_handler`: one-argument handler used when `SA_SIGINFO` is not set.
- `sa_sigaction`: three-argument handler used when `SA_SIGINFO` is set.
- `sa_mask`: signals additionally blocked while the handler runs.
- `sa_flags`: behavior modifiers.
- `sa_restorer`: C library / ABI support hook on some architectures.
Common `sa_flags`: `SA_NOCLDSTOP`: suppress `SIGCHLD` on child stop/continue; `SA_NOCLDWAIT`: do not leave zombie children; `SA_NODEFER`: do not automatically block the delivered signal during its handler; `SA_ONSTACK`: run handler on an alternate signal stack; `SA_RESETHAND`: restore default disposition on entry; `SA_RESTART`: restart some interrupted system calls; `SA_SIGINFO`: enable `sa_sigaction` and `siginfo_t` delivery.
How the kernel uses it: Each process tracks one disposition per signal number; On delivery, the kernel consults the disposition, the thread mask, and signal semantics; If caught, the kernel builds a signal frame on the user stack and arranges return via `sigreturn`.

## 3. IPC Structures
### `struct ipc_perm`
```c
struct ipc_perm {
    key_t          __key;
    uid_t          uid;
    gid_t          gid;
    uid_t          cuid;
    gid_t          cgid;
    unsigned short mode;
    unsigned short __seq;
};
```
- `__key`: key supplied to `msgget()`, `semget()`, or `shmget()`.
- `uid`: effective owner UID.
- `gid`: effective owner GID.
- `cuid`: creator UID.
- `cgid`: creator GID.
- `mode`: permission bits plus status flags.
- `__seq`: sequence number used with IPC identifiers.
How the kernel uses it: SysV IPC objects share a common ownership and permission record; Access checks compare caller credentials against `uid`, `gid`, capability state, and requested mode; The sequence number helps distinguish reused identifiers from stale references.
### `struct msqid_ds`
```c
struct msqid_ds {
    struct ipc_perm msg_perm;
    time_t          msg_stime;
    time_t          msg_rtime;
    time_t          msg_ctime;
    unsigned long   msg_cbytes;
    msgqnum_t       msg_qnum;
    msglen_t        msg_qbytes;
    pid_t           msg_lspid;
    pid_t           msg_lrpid;
};
```
- `msg_perm`: ownership and access permissions.
- `msg_stime`: time of last `msgsnd()`.
- `msg_rtime`: time of last `msgrcv()`.
- `msg_ctime`: creation time or last metadata change.
- `msg_cbytes`: current bytes queued.
- `msg_qnum`: current message count.
- `msg_qbytes`: queue byte limit.
- `msg_lspid`: PID of last sender.
- `msg_lrpid`: PID of last receiver.
How the kernel uses it: The message-queue descriptor is the metadata object for one SysV message queue; The kernel uses it to enforce queue limits, permissions, wakeups, and `msgctl()` operations; Timestamps and PIDs support administration and debugging.
### `struct msgbuf`
```c
struct msgbuf {
    long mtype;
    char mtext[1];
};
```
- `mtype`: positive message type used for selection and priority-style grouping.
- `mtext`: message payload; callers normally use a larger application-defined array.
How the kernel uses it: User space passes a buffer beginning with `mtype`, followed by raw bytes; The kernel copies the payload into queue storage and later copies it back out on receive; `mtype` lets receivers request exact types or relative type orderings.
### `struct shmid_ds`
```c
struct shmid_ds {
    struct ipc_perm shm_perm;
    size_t          shm_segsz;
    time_t          shm_atime;
    time_t          shm_dtime;
    time_t          shm_ctime;
    pid_t           shm_cpid;
    pid_t           shm_lpid;
    shmatt_t        shm_nattch;
};
```
- `shm_perm`: ownership and permission record.
- `shm_segsz`: segment size in bytes.
- `shm_atime`: last attach time.
- `shm_dtime`: last detach time.
- `shm_ctime`: creation time or last control change.
- `shm_cpid`: creator PID.
- `shm_lpid`: PID of the last attach/detach operation.
- `shm_nattch`: number of current attachments.
How the kernel uses it: The shared-memory descriptor tracks one SysV shared memory segment; The kernel uses it to manage attach counts, destruction-on-last-detach, and permission checks; It ties IPC metadata to actual mapped pages in the VM subsystem.
### `struct semid_ds`
```c
struct semid_ds {
    struct ipc_perm sem_perm;
    time_t          sem_otime;
    time_t          sem_ctime;
    unsigned long   sem_nsems;
};
```
- `sem_perm`: ownership and access permissions.
- `sem_otime`: last `semop()` time.
- `sem_ctime`: creation time or last `semctl()` change.
- `sem_nsems`: number of semaphores in the set.
How the kernel uses it: SysV semaphores are allocated in sets, not as isolated single counters; The kernel consults this descriptor for permission checks, statistics, and control operations; The actual semaphore values and wait queues live in associated kernel-internal storage.
### `struct sembuf`
```c
struct sembuf {
    unsigned short sem_num;
    short          sem_op;
    short          sem_flg;
};
```
- `sem_num`: index of the target semaphore inside the set.
- `sem_op`: operation to perform.
- `sem_flg`: per-operation flags.
`sem_op` meanings: `> 0`: increment semaphore value; `== 0`: wait until the semaphore value becomes zero; `< 0`: decrement by `abs(sem_op)`, blocking if the value is too small.
Important flags: `IPC_NOWAIT`: do not sleep; fail immediately if the operation cannot proceed; `SEM_UNDO`: automatically reverse the process's adjustment on exit.
How the kernel uses it: `semop()` takes an array of `sembuf` operations and applies them atomically; The kernel checks whether the whole batch can succeed before committing it; Wait queues, undo lists, and wakeups are keyed from these operation records.

## 4. Terminal Structures
### `struct termios`
```c
struct termios {
    tcflag_t c_iflag;
    tcflag_t c_oflag;
    tcflag_t c_cflag;
    tcflag_t c_lflag;
    cc_t     c_line;
    cc_t     c_cc[NCCS];
    speed_t  c_ispeed;
    speed_t  c_ospeed;
};
```
- `c_iflag`: input processing flags.
- `c_oflag`: output processing flags.
- `c_cflag`: hardware/control-line settings.
- `c_lflag`: local line-discipline behavior.
- `c_line`: line discipline selector on Linux.
- `c_cc[]`: special control characters and noncanonical timing values.
- `c_ispeed`: input baud rate.
- `c_ospeed`: output baud rate.
Key flags: `ICANON`: canonical line mode; input is edited and delivered line by line; `ECHO`: echo typed characters; `ISIG`: generate signals for special characters such as interrupt and quit; `ICRNL`: translate carriage return to newline on input; `OPOST`: enable output post-processing; `IXON` / `IXOFF`: software flow control; `NOFLSH`: do not flush queues when generating terminal signals; `IEXTEN`: enable implementation-defined line discipline features.
Important `c_cc[]` entries: `VERASE`: erase previous character in canonical mode; `VKILL`: erase the current input line; `VINTR`: send `SIGINT`; `VQUIT`: send `SIGQUIT`; `VEOF`: send end-of-file to the reader in canonical mode; `VMIN`: minimum byte count for noncanonical reads; `VTIME`: timeout in deciseconds for noncanonical reads; `VSUSP`: send `SIGTSTP`; `VSTART` / `VSTOP`: XON/XOFF flow control characters.
How the kernel uses it: The tty layer stores terminal mode in a `termios`-style record for each terminal device; Read and write paths consult these flags to translate characters, echo input, and generate signals; Canonical editing, job control, and line discipline behavior are all driven from this state.

## 5. Socket Structures
### `struct sockaddr` and `struct sockaddr_in`
```c
struct sockaddr {
    sa_family_t sa_family;
    char        sa_data[14];
};
struct sockaddr_in {
    sa_family_t    sin_family;
    in_port_t      sin_port;
    struct in_addr sin_addr;
    unsigned char  sin_zero[8];
};
```
- `sa_family`: generic address family tag for dispatch.
- `sa_data`: family-specific raw address bytes in the generic form.
- `sin_family`: must be `AF_INET`.
- `sin_port`: TCP/UDP port in network byte order.
- `sin_addr`: IPv4 address.
- `sin_zero`: padding so the structure matches generic `sockaddr` size.
How the kernel uses it: Socket system calls inspect `sa_family` / `sin_family` to choose the protocol family; The IPv4 stack uses `sin_addr` and `sin_port` during bind, connect, send, and receive setup; The generic `sockaddr` exists so one API can carry many address families.
### `struct sockaddr_un`
```c
struct sockaddr_un {
    sa_family_t sun_family;
    char        sun_path[108];
};
```
- `sun_family`: must be `AF_UNIX` (also called `AF_LOCAL`).
- `sun_path`: pathname socket name or abstract-namespace bytes on Linux.
How the kernel uses it: The Unix-domain socket layer matches local endpoints by pathname or abstract name; `bind()` installs the name; `connect()` looks it up and attaches peer state; Permissions are enforced using filesystem checks for pathname sockets.
### `struct sockaddr_in6`
```c
struct sockaddr_in6 {
    sa_family_t     sin6_family;
    in_port_t       sin6_port;
    uint32_t        sin6_flowinfo;
    struct in6_addr sin6_addr;
    uint32_t        sin6_scope_id;
};
```
- `sin6_family`: must be `AF_INET6`.
- `sin6_port`: transport-layer port number.
- `sin6_flowinfo`: IPv6 flow label / traffic information.
- `sin6_addr`: 128-bit IPv6 address.
- `sin6_scope_id`: interface or scope identifier for scoped addresses such as link-local.
How the kernel uses it: The IPv6 stack uses these fields to route packets and bind sockets; `sin6_scope_id` is especially important for link-local addresses; `sin6_flowinfo` is carried through the API even if many applications ignore it.

## 6. Memory Management Structures
### Page table entry concept
```c
/* Conceptual page table entry. Actual format is architecture-specific. */
struct pte_concept {
    unsigned long frame_number;
    unsigned int  present:1;
    unsigned int  writable:1;
    unsigned int  user:1;
    unsigned int  accessed:1;
    unsigned int  dirty:1;
    unsigned int  executable:1;
    unsigned int  global:1;
    unsigned int  copy_on_write:1;
};
```
- `frame_number`: physical page frame backing the virtual page.
- `present`: mapping is valid in RAM.
- `writable`: writes are permitted.
- `user`: accessible from user mode rather than supervisor-only.
- `accessed`: hardware or software tracks whether the page was referenced.
- `dirty`: page has been written and may need write-back.
- `executable`: instruction fetch allowed or denied, depending on architecture.
- `global`: translation may stay in TLB across context switches.
- `copy_on_write`: conceptual flag used to describe shared-write fault handling.
How the kernel uses it: Every memory access eventually resolves through page-table entries; The MM subsystem builds and tears down PTEs during `mmap()`, `fork()`, faults, and unmap operations; Accessed/dirty bits support reclamation, swapping, and write-back decisions; Protection bits enforce process isolation and W^X style execution policies.
### Memory region / VMA concept
```c
/* Conceptual VMA; Linux uses struct vm_area_struct. */
struct vma_concept {
    unsigned long vm_start;
    unsigned long vm_end;
    unsigned long vm_flags;
    pgprot_t      vm_page_prot;
    struct file  *vm_file;
    unsigned long vm_pgoff;
    void         *vm_private_data;
};
```
- `vm_start`: inclusive start virtual address.
- `vm_end`: exclusive end virtual address.
- `vm_flags`: read/write/exec/shared/grows-down/don't-copy and similar attributes.
- `vm_page_prot`: architecture-specific page protection value.
- `vm_file`: backing file for file mappings, or `NULL` for anonymous memory.
- `vm_pgoff`: offset into the backing object, in page units.
- `vm_private_data`: filesystem or driver private mapping state.
How the kernel uses it: A VMA represents one contiguous region with uniform protection and backing rules; The process address space is a collection of VMAs describing text, heap, stack, shared libraries, and mapped files; Page faults first locate the VMA, then decide whether the access is legal and how to materialize the page; `mmap()`, `munmap()`, `mprotect()`, `brk()`, and `fork()` primarily manipulate VMA state.
