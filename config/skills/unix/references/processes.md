# Process Representation and States

Full detail on process representation, states, credentials, and relationships.

## 6. Process Representation and States
### 6.1 Process Control Block

A process is represented in the kernel by a process control block, or PCB. Modern kernels may use several linked structures rather than one
literal struct, but the idea is the same: the kernel keeps all execution state needed to stop, schedule, signal, inspect, and resume the
process. The PCB includes identifiers such as the PID and parent PID. `getpid(2)` returns the caller's PID. `getppid(2)` returns the parent
PID, or the reaper to which the process has been reparented if the original parent has exited. Credentials are part of the PCB. `getuid(2)`
and `geteuid(2)` expose the real and effective user IDs. `getgid(2)` and `getegid(2)` do the same for groups. Linux also tracks saved IDs,
filesystem IDs, and supplementary groups. The PCB also carries scheduling and execution context. That includes the saved CPU register state
for context switches, the current process state, scheduling parameters, signal dispositions, timers, resource accounting, and pointers to
the process's memory map. Open file descriptor tables and working-directory/root-directory references are also associated with the process
context. `/proc/<pid>/status` provides a user-visible summary of much of this state. Fields documented in `proc_pid_status(5)` include
`State`, `Pid`, `PPid`, `Uid`, `Gid`, `Groups`, `FDSize`, thread count, capability masks, and many memory-usage fields. That file is a view
exported by the kernel, not the canonical storage format itself.
### 6.2 The Process Table

Historically, UNIX descriptions speak of a process table. Modern kernels do not need a fixed-size array, but the abstraction is still
useful: the kernel maintains a global set of live process entries keyed by PID. PID allocation chooses an unused identifier, subject on
Linux to limits such as `/proc/sys/kernel/pid_max`; see `fork(2)` and `proc(5)`. Two special process numbers are traditional landmarks.
Process 0 is the kernel's idle or swapper task and is not an ordinary user process. Process 1 is the init process, which on current Linux
systems is often `systemd`. When a parent exits before its child, the child is reparented to PID 1 or to a designated subreaper; see
`getpid(2)`. The `/proc` filesystem presents a live view of this global process set. Directories such as `/proc/<pid>` expose per-process
files including `stat`, `status`, `fd`, `maps`, and many others; see `proc(5)`. This interface is observational and administrative: it lets
user space inspect kernel-maintained process state using ordinary file operations.
### 6.3 Process States

A process can be running, runnable, sleeping, stopped, or zombified. Only a running task is currently on a CPU. A runnable task is ready to
run but waiting for the scheduler to assign CPU time. A sleeping or blocked task is waiting for an event such as I/O completion, a signal,
or a timer. Linux exposes states through `/proc/<pid>/status` and `/proc/<pid>/stat`. `proc_pid_status(5)` documents values such as `R
(running)`, `S (sleeping)`, `D (disk sleep)`, `T (stopped)`, `t (tracing stop)`, and `Z (zombie)`. These are implementation-visible
refinements of the broader textbook states. A stopped process is not executing because it has been suspended, commonly by `SIGSTOP`,
job-control signals, or tracing with `ptrace`. A zombie is different: execution has already ended, but the kernel keeps a small
process-table entry so the parent can collect the exit status with `wait()`. A zombie has no runnable thread of execution and no normal
memory image, but it still occupies a PID slot until reaped. A compact state diagram is:
```text
new/forked -> runnable -> running -> exited -> zombie -> reaped
                    ^         |
                    |         v
               event ready <- sleeping/blocked
                              |
                              v
                           stopped
```
This diagram hides many scheduler details, but it captures the core lifecycle seen in classic UNIX and Linux process management.
### 6.4 Credentials

UNIX separates real and effective credentials. The real UID/GID identify who started the process. The effective UID/GID determine which
owner/group permission class is normally used for access checks. Saved IDs let a process that executed a privileged image drop and later
regain its effective privilege in a controlled way. The key transition happens on `execve()` of a setuid or setgid program. If the
executable's mode bits request it, and if no inhibiting condition applies, the effective UID or GID changes to that of the file owner or
group; see `execve(2)`. Linux ignores those privilege transitions if `no_new_privs` is set, if the filesystem is mounted `nosuid`, or if the
process is being ptraced. After any such change, the effective IDs are copied into the saved set-ID slots. Supplementary groups extend the
credential set beyond a single effective GID. They matter directly for filesystem permissions because the group class is selected when the
file's group matches either the effective GID or one of the supplementary groups; see `path_resolution(7)` and `proc_pid_status(5)`. Linux
also decomposes traditional root privilege into capabilities. Instead of treating UID 0 as one indivisible power, the kernel tracks
fine-grained privileges such as `CAP_DAC_OVERRIDE`, `CAP_CHOWN`, and `CAP_SYS_CHROOT`. This model preserves UNIX compatibility while making
privilege separation more precise.
### 6.5 Process Relationships

`fork(2)` creates a child process. The child gets a new PID, inherits most of the parent's execution environment, and starts as a near-copy
with separate memory state but shared references to open file descriptions. This parent-child edge is the basis of the UNIX process
hierarchy. Process groups sit above individual processes. A child normally inherits the parent's process group. `setpgid(2)` can place
related processes into the same group, which is how shells build jobs and pipelines. Signals from the terminal, such as `SIGINT`, are
directed to the foreground process group rather than to one process at a time; see `setpgid(2)`. Sessions sit above process groups.
`setsid(2)` creates a new session and makes the caller both session leader and leader of a new process group. A session can own a
controlling terminal, and exactly one process group in that session is the foreground group for that terminal. This hierarchy underlies
login sessions and shell job control. Orphaned process groups are handled specially. `setpgid(2)` documents that if a process group becomes
orphaned and any of its members are stopped, the kernel sends `SIGHUP` followed by `SIGCONT` to each member. This prevents stopped
background jobs from being stranded forever without a supervising parent in the same session. Taken together, PID, parentage, process
groups, and sessions give UNIX its layered model of execution. The scheduler sees runnable tasks. The credential system sees principals and
privileges. The terminal layer sees foreground and background jobs. And `/proc` exposes all of these views through ordinary files for tools
such as `ps`, `top`, `kill`, and debuggers.

