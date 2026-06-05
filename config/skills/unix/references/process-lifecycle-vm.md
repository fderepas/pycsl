# Process Lifecycle, Scheduling, and Virtual Memory

Full detail on process creation, execution, termination, waiting, signals,
CPU scheduling, timekeeping, and virtual memory management.

## 7. Process Lifecycle

Process control is the core Unix pattern: create a process, replace its image,
run it, observe state changes, and reap it.

### 7.1 Process Creation — `fork()`

`fork()` creates a new child process by duplicating the calling process. Parent and child then continue independently in separate virtual address spaces. On Linux, `fork()` is implemented with copy-on-write pages rather than eagerly copying all memory. A page is copied only if one side later writes to it. The child inherits copies of the parent's open file descriptors. Each copied descriptor refers to the same open file description as the parent's descriptor. Shared open file descriptions mean shared file offset, status flags, and signal-driven I/O settings. Signal dispositions are inherited across `fork()`. The child is not an identity clone: it gets a new PID and some attributes are reset or not inherited. `fork()` returns `0` in the child and the child's PID in the parent. On failure it returns `-1` in the parent and no child is created. In a multithreaded program, only the calling thread appears in the child after `fork()`. `vfork()` is a constrained variant intended for the immediate exec case. With `vfork()`, the child shares the parent's address space and the parent is suspended. The child must quickly call `execve()` or `_exit()` and must not carelessly modify shared state.

### 7.2 Program Execution — `execve()`

`execve(pathname, argv, envp)` replaces the current process image with a new program. It does not create a new PID; it reuses the same process identity. `pathname` names the executable, `argv` supplies argument strings, and `envp` supplies environment strings. The kernel first verifies what is being executed. The target may be a native binary or a script whose first line begins with `#!`. For ELF binaries, the kernel reads the executable headers and may invoke the ELF interpreter. For interpreter scripts, the named interpreter runs with the script path and remaining arguments. After validation, the old text, data, BSS, heap, stack, and mappings are discarded. The kernel loads the new program image and builds a fresh user stack. That stack contains the argument vector, environment, and startup information. Open file descriptors normally survive across `execve()`. Descriptors marked `FD_CLOEXEC` are closed during the transition. Caught signal handlers reset to their default dispositions in the new image. Signals that were already ignored stay ignored; Linux also keeps ignored `SIGCHLD` ignored. The alternate signal stack is not preserved. Set-user-ID and set-group-ID mode bits may change the effective credentials of the process. Linux suppresses those privilege transitions when `no_new_privs` is set, the filesystem is `nosuid`, or the process is being traced. After any effective-ID change, the effective IDs are copied into the saved set-ID fields.

### 7.3 Process Termination — `_exit()`

`_exit(status)` terminates the calling process immediately. It is the low-level exit primitive and is the safe post-`fork()` failure path before `execve()`. Unlike `exit(3)`, `_exit()` does not run `atexit()` handlers. It also does not flush stdio buffers in user space. The kernel tears down the process image and releases process-owned resources. Memory mappings, page tables, and most kernel bookkeeping attached to the process are dropped. Open file descriptors are closed, which may also release associated locks. The parent is notified by delivery of `SIGCHLD`. The exit status is retained so the parent can later collect it with a wait call. A dead child normally becomes a zombie instead of disappearing immediately. A zombie keeps only minimal state such as PID, exit status, and resource usage. If the parent does not wait, the zombie persists. If the parent has already exited, the child is reparented to `init` or to a designated subreaper. Once some parent waits for it, the zombie is finally removed. Running children of an exiting parent are reparented as well so they remain supervised.

### 7.4 Waiting for Children — `wait()`, `waitpid()`, `wait4()`

The wait family lets a parent observe child state changes and reap dead children. `wait()` is the simplest form and is equivalent to `waitpid(-1, ...)`. `waitpid()` lets the caller select one child, a process group, or any child. By default these calls block until a matching child terminates. A successful wait returns the PID of the child whose state changed. The returned status must be decoded with macros such as `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, and `WTERMSIG`. `WNOHANG` makes the check nonblocking. `WUNTRACED` also reports children stopped by signals. `WCONTINUED` can report children resumed by `SIGCONT`. `wait4()` extends `waitpid()` by also returning `struct rusage` information. That resource usage includes CPU time and related accounting data. Reaping is what finally removes a zombie from the system. This is why shells, supervisors, and init systems must eventually wait for children. Waited-for terminated children also contribute to the child CPU totals reported by `times(2)`.

### 7.5 Signals

Signals are asynchronous software notifications delivered to processes or threads. They report events such as termination requests, timers, child exit, faults, or broken pipes. Common examples are `SIGTERM`, `SIGKILL`, `SIGSTOP`, `SIGSEGV`, `SIGCHLD`, `SIGPIPE`, and `SIGALRM`. Each signal has a disposition: default action, ignore, or catch with a handler. Default actions include terminate, dump core, stop, continue, or ignore. `sigaction()` is the preferred interface for installing handlers; `signal()` is older and less portable. A generated but currently blocked signal becomes pending. Each thread has a signal mask controlling which signals are blocked. In a single-threaded program, `sigprocmask()` changes the mask. When the kernel is about to return a thread to user mode, it checks for pending unblocked signals. A handler then runs with kernel-prepared context and normal execution may later resume. `SIGKILL` and `SIGSTOP` are special because they cannot be caught, blocked, or ignored. Signals may be generated by the kernel, by hardware faults, by timers, or by other processes. `kill(pid, sig)` sends a signal to a process or process group. Signal dispositions are inherited across `fork()`, but caught handlers reset on `execve()`.

### 7.6 The Shell as Fork-Exec-Wait

A Unix shell is the standard user-space demonstration of process lifecycle control. Its basic loop is read a command, launch it, and collect status. For a simple foreground command, the shell parses words, redirections, and environment assignments. The shell then calls `fork()`. The child process sets up redirections, often using `open()` and `dup2()`. After setup, the child calls `execve()` and the requested program image replaces the shell code. The parent shell usually waits for the foreground child with `waitpid()`. Pipelines are built by creating pipes and forking multiple children. One child writes to a pipe and the next child reads from it. Each stage remaps fd 0 or fd 1 with `dup2()` and closes unused pipe ends. Background jobs differ mainly in waiting policy. The shell does not wait immediately, returns to the prompt, and later reaps children via `SIGCHLD` handling or `waitpid(..., WNOHANG)`. Job control extends the same model with process groups and stop/continue signals. Most Unix command execution therefore reduces to fork, exec, optional pipes, and wait.

## 8. CPU Scheduling and Timekeeping

Scheduling decides which runnable thread gets CPU time next, and timekeeping
provides the clocks and accounting used to measure that execution.

### 8.1 Scheduling Goals

Fairness means runnable tasks should all make progress over time. A scheduler should avoid starvation of ordinary work. Responsiveness matters most for interactive tasks. Terminal shells, editors, and GUI work should wake and run quickly. Throughput matters for batch workloads. The system should finish as much useful work as possible per unit time. Priority support lets administrators and applications express importance. Not every runnable task needs the same urgency. Real-time work adds a stricter requirement. Some threads must run predictably enough to meet timing constraints. These goals often conflict with one another. Scheduling policy is the art of balancing them with acceptable trade-offs.

### 8.2 Traditional Unix Scheduling

Traditional Unix schedulers were priority-based and time-sliced. Runnable processes competed for the CPU according to dynamic priority. The classic model combines a base priority with recent CPU usage. Heavy CPU consumption pushes a process toward lower effective priority. I/O-bound and interactive processes sleep frequently. When they wake, they often get a priority boost and quick service. CPU-bound jobs consume their quanta repeatedly. Their dynamic priority decays so they do not dominate the machine. `nice(2)` and `setpriority(2)` adjust the user-visible base priority. The nice range is `-20` to `+19`, and higher nice means lower priority. Historically, priority recalculation was tied to the clock tick. Periodic accounting updated usage estimates and influenced the next choice. The result was a scheduler that favored short, blocking work. That matched the interactive style of classic Unix systems.

### 8.3 Scheduling Classes (POSIX/Linux)

POSIX and Linux expose several scheduling policies. The default time-sharing class is `SCHED_OTHER`. `SCHED_FIFO` is a real-time first-in, first-out policy. A runnable FIFO thread runs until it blocks, yields, or is preempted. `SCHED_RR` is the round-robin real-time policy. It behaves like FIFO, but equal-priority threads rotate by quantum. Real-time priorities outrank normal scheduling. On Linux, `SCHED_FIFO` and `SCHED_RR` use static priorities 1 through 99. Normal policies such as `SCHED_OTHER`, `SCHED_BATCH`, and `SCHED_IDLE` use `sched_priority == 0` and are ordered by the normal scheduler logic. Linux kernel documentation describes CFS as tracking virtual runtime. Runnable tasks are kept in a red-black tree and the smallest `vruntime` runs next. Conceptually, CFS aims to approximate an ideal fair CPU. Instead of fixed old-style quanta heuristics, it charges actual runtime fairly.

### 8.4 Timekeeping

A hardware timer provides the kernel with periodic time events. Traditionally this appears as the clock tick interrupt. Tick handling updates kernel time and scheduler accounting. It can charge user time, system time, and trigger rescheduling decisions. The same machinery supports profiling and time-slice expiration. Even when Linux uses high-resolution or tickless modes, the accounting role remains. `clock_gettime()` reads kernel-maintained clocks. `CLOCK_REALTIME` is wall-clock time and can jump if the clock is set. `CLOCK_MONOTONIC` measures monotonic elapsed time since boot. It does not go backward when wall time is adjusted. `times(2)` reports per-process CPU accounting. It returns user time, system time, and waited-for children's totals in clock ticks. The number of ticks per second comes from `_SC_CLK_TCK`. That makes raw `times()` values meaningful to user programs.

### 8.5 Alarms and Timers

`alarm(seconds)` schedules delivery of `SIGALRM` after a delay. Setting a new alarm replaces any previous one for the process. `alarm(0)` cancels a pending alarm. The return value reports how many seconds were left on the old timer. The alarm timer is not inherited across `fork()`. It is preserved across `execve()` unless changed by the new program. `setitimer()` offers interval timers with finer control. It can generate periodic signals instead of a one-shot alarm. POSIX timers such as `timer_create()` support per-clock timers. They are the more general interface for precise and repeated timing events. `sleep()` and `nanosleep()` are built on the same kernel timing ideas. A thread blocks until a timer event wakes it or a signal interrupts it.

### 8.6 Context Switch Mechanics

A context switch begins when the running thread blocks, yields, or is preempted. The kernel saves register state and other execution context for that thread. The scheduler then chooses the next runnable thread from a run queue. Policy and priority determine which entry is selected. If the next thread belongs to a different address space, the kernel also switches memory-management context. The saved state of the chosen thread is restored. Program counter, stack pointer, and CPU registers return to prior values. Control then returns to user mode or kernel continuation for that thread. To the thread, execution appears to resume where it last stopped. Context switches are necessary but not free. They can flush TLB entries, disturb caches, and waste pipeline work. Excessive switching therefore hurts throughput. Good scheduling balances latency against the cost of preemption.

## 9. Virtual Memory Management

Virtual memory lets each process see a large, private address space while the
kernel maps that space onto physical memory and backing storage page by page.

### 9.1 Address Space Layout

A process address space is divided into logical regions. Typical regions are text, data, BSS, heap, mapped areas, and stack. The text segment holds executable code and read-only data. File-backed text is commonly shareable among processes running the same binary. The data segment holds initialized global and static variables. The BSS holds zero-initialized globals and is zero-filled at program start. The heap supports dynamic allocation. `brk()` and `sbrk()` move the program break at the end of the data segment. Memory-mapped regions hold shared libraries, mapped files, and anonymous memory. The user stack usually grows downward from high virtual addresses. Layout details vary by architecture and ASLR policy. What remains constant is that virtual addresses are translated before use.

### 9.2 Paging

Paging divides virtual memory into fixed-size pages. Physical RAM is divided into page frames of the same size. A page table maps each virtual page to a physical frame. If no valid mapping exists, access raises a page fault. Page-table entries carry more than a frame number. They also record presence, permissions, dirty state, and accessed state. Modern systems use multi-level page tables to save memory. x86 uses two-level schemes on older 32-bit systems and four or five levels on 64-bit systems. Hardware caches recent translations in the TLB. A TLB hit avoids a full page-table walk on every memory reference. Protection changes such as `mprotect()` update mapping permissions. Violating those permissions causes the kernel to send `SIGSEGV`.

### 9.3 Demand Paging

Demand paging loads pages only when they are actually touched. Starting a program does not require reading every page up front. A first access to an unmapped-but-valid page triggers a page fault. The fault traps into the kernel for resolution. The kernel checks whether the address lies in a valid mapped region. If not, the access is invalid and the process usually gets `SIGSEGV`. For a valid region, the kernel allocates a frame and fills it appropriately. The contents may come from an executable file, a mapped file, swap, or zeros. The page table is updated and the faulting instruction is restarted. From user space, the access appears to succeed transparently.

### 9.4 Page Replacement

Physical memory is finite, so the kernel must sometimes reclaim pages. Page replacement chooses victim pages when free memory runs low. Exact LRU is expensive, so real kernels use approximations. Accessed bits support clock-style or second-chance style aging schemes. Clean file-backed pages are cheap victims. They can often be discarded because their contents already exist on disk. Dirty pages are more expensive to evict. They must be written back to swap or to the backing file before reuse. Linux performs background reclaim with helpers such as `kswapd`. This tries to free memory before allocation pressure becomes critical.

### 9.5 Copy-on-Write

Copy-on-write is a central optimization for `fork()`. Parent and child initially share the same physical pages. The shared pages are marked read-only in both address spaces. That allows reads to proceed while trapping writes. On a write fault, the kernel allocates a new frame and copies the page. The faulting process then receives a private writable mapping. Pages that are only read never need duplication. Pages discarded by a later `execve()` also avoid pointless copying. `MAP_PRIVATE` file mappings use the same idea. Modifications become private copies instead of visible shared writes.

### 9.6 Memory-Mapped Files — `mmap()`

`mmap(addr, length, prot, flags, fd, offset)` creates a mapping. File-backed mappings start at a page-aligned file offset. `MAP_SHARED` creates a shared mapping. Writes are visible to other mappers and are associated with the file. `MAP_PRIVATE` creates a private copy-on-write mapping. Updates are not visible to other mappers and are not written through directly. `MAP_ANONYMOUS` creates zero-filled memory not backed by a file. Allocators often use it for larger dynamic allocations. `munmap()` removes a mapping, and `msync()` requests write-back. `madvise()` can also give hints such as `WILLNEED`, `DONTNEED`, `RANDOM`, or `SEQUENTIAL`.

### 9.7 Swapping and Thrashing

Anonymous pages that cannot simply be dropped may be written to swap. Swap extends memory by using disk as a slow backing store. Thrashing happens when the working set exceeds available RAM. The kernel spends most of its time faulting and paging instead of computing. In a thrashing system, throughput collapses. The CPU waits on disk traffic generated by constant page replacement. The working-set idea explains the failure mode. Performance is good only when the actively used pages fit in memory. Linux treats the OOM killer as a last resort. If reclaim and swap cannot satisfy demand, the kernel may kill a process.


