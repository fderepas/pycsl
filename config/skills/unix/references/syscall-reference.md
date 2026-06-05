# Unix Syscall Quick Reference

## File Operations
### open
`int open(const char *path, int flags, ... /* mode_t mode */);`
Open and possibly create a file. **Errors**: EACCES, EEXIST, ENOENT, EMFILE
### close
`int close(int fd);`
Close a file descriptor. **Errors**: EBADF, EINTR, EIO, ENOSPC
### read
`ssize_t read(size_t count; int fd, void buf[count], size_t count);`
Read from a file descriptor. **Errors**: EAGAIN/EWOULDBLOCK, EBADF, EINTR, EINVAL
### write
`ssize_t write(size_t count; int fd, const void buf[count], size_t count);`
Write to a file descriptor. **Errors**: EAGAIN/EWOULDBLOCK, EBADF, EINTR, EPIPE
### lseek
`off_t lseek(int fd, off_t offset, int whence);`
Reposition read/write file offset. **Errors**: EBADF, EINVAL, ENXIO, ESPIPE
### creat
`int creat(const char *path, mode_t mode);`
Open and possibly create a file. **Errors**: EACCES, ENOENT, EMFILE, ENFILE
### dup
`int dup(int oldfd);`
Duplicate a file descriptor. **Errors**: EBADF, EBUSY, EINTR, EINVAL
### dup2
`int dup2(int oldfd, int newfd);`
Duplicate a file descriptor. **Errors**: EBADF, EBUSY, EINTR, EINVAL
### fcntl
`int fcntl(int fd, int op, ...);`
Manipulate file descriptor. **Errors**: EACCES/EAGAIN, EAGAIN, EBADF, EINVAL
### fstat
`int fstat(int fd, struct stat *statbuf);`
Get file status. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### stat
`int stat(const char *restrict path, struct stat *restrict statbuf);`
Get file status. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### lstat
`int lstat(const char *restrict path, struct stat *restrict statbuf);`
Get file status. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### access
`int access(const char *path, int mode);`
Check user's permissions for a file. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### chmod
`int chmod(const char *path, mode_t mode);`
Change permissions of a file. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### fchmod
`int fchmod(int fd, mode_t mode);`
Change permissions of a file. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### chown
`int chown(const char *path, uid_t owner, gid_t group);`
Change ownership of a file. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### fchown
`int fchown(int fd, uid_t owner, gid_t group);`
Change ownership of a file. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### link
`int link(const char *oldpath, const char *newpath);`
Make a new name for a file. **Errors**: EACCES, EDQUOT, EEXIST, EFAULT
### unlink
`int unlink(const char *path);`
Delete a name and possibly the file it refers to. **Errors**: EACCES, EBUSY, EFAULT, EIO
### rename
`int rename(const char *oldpath, const char *newpath);`
Change the name or location of a file. **Errors**: EACCES, EBUSY, EDQUOT, EFAULT
### symlink
`int symlink(const char *target, const char *linkpath);`
Make a new name for a file. **Errors**: EACCES, EBADF, EDQUOT, EEXIST
### readlink
`ssize_t readlink(size_t bufsiz; const char *restrict path, char buf[restrict bufsiz], size_t bufsiz);`
Read value of a symbolic link. **Errors**: EACCES, EBADF, EFAULT, EINVAL
### truncate
`int truncate(const char *path, off_t length);`
Truncate a file to a specified length. **Errors**: EACCES, EFAULT, EFBIG, EINTR
### ftruncate
`int ftruncate(int fd, off_t length);`
Truncate a file to a specified length. **Errors**: EACCES, EFAULT, EFBIG, EINTR

## Directory Operations
### mkdir
`int mkdir(const char *path, mode_t mode);`
Create a directory. **Errors**: EACCES, EBADF, EDQUOT, EEXIST
### rmdir
`int rmdir(const char *path);`
Delete a directory. **Errors**: EACCES, EBUSY, ENOTEMPTY, ENOTDIR
### chdir
`int chdir(const char *path);`
Change working directory. **Errors**: EACCES, EFAULT, EIO, ELOOP
### fchdir
`int fchdir(int fd);`
Change working directory. **Errors**: EACCES, EFAULT, EIO, ELOOP
### chroot
`int chroot(const char *path);`
Change root directory. **Errors**: EACCES, EFAULT, EIO, ELOOP
### getcwd
`char *getcwd(size_t size; char buf[size], size_t size);`
Get current working directory. **Errors**: EACCES, EINVAL, ENOENT, ERANGE

## File System Operations
### mount
`int mount(const char *source, const char *target, const char *filesystemtype, unsigned long mountflags, const void *_Nullable data);`
Mount filesystem. **Errors**: EACCES, EBUSY, EINVAL, ENODEV
### umount
`int umount(const char *target);`
Unmount filesystem. **Errors**: EBUSY, EINVAL, ENOENT, EPERM
### sync
`void sync(void);`
Commit filesystem caches to disk. **Errors**: none
### fsync
`int fsync(int fd);`
Synchronize a file's in-core state with storage device. **Errors**: EBADF, EINTR, EIO, ENOSPC
### fdatasync
`int fdatasync(int fd);`
Synchronize a file's in-core state with storage device. **Errors**: EBADF, EINTR, EIO, ENOSPC
### mknod
`int mknod(const char *path, mode_t mode, dev_t dev);`
Create a special or ordinary file. **Errors**: EACCES, EBADF, EDQUOT, EEXIST
### mkfifo
`int mkfifo(const char *path, mode_t mode);`
Make a FIFO special file (a named pipe). **Errors**: EACCES, EEXIST, ENOENT, ENOSPC

## Process Control
### fork
`pid_t fork(void);`
Create a child process. **Errors**: EAGAIN, ENOMEM
### execve
`int execve(const char *path, char *const _Nullable argv[], char *const _Nullable envp[]);`
Execute program. **Errors**: E2BIG, EACCES, EAGAIN, EFAULT
### _exit
`[[noreturn]] void _exit(int status);`
Terminate the calling process. **Errors**: none
### wait
`pid_t wait(int *_Nullable wstatus);`
Wait for process to change state. **Errors**: ECHILD, EINTR, EINVAL
### waitpid
`pid_t waitpid(pid_t pid, int *_Nullable wstatus, int options);`
Wait for process to change state. **Errors**: ECHILD, EINTR, EINVAL
### wait4
`pid_t wait4(pid_t pid, int *_Nullable wstatus, int options, struct rusage *_Nullable rusage);`
Wait for process to change state, BSD style. **Errors**: ECHILD, EINTR, EINVAL
### getpid
`pid_t getpid(void);`
Get the calling process ID. **Errors**: none
### getppid
`pid_t getppid(void);`
Get the parent process ID. **Errors**: none
### getuid
`uid_t getuid(void);`
Get the real user ID. **Errors**: none
### geteuid
`uid_t geteuid(void);`
Get the effective user ID. **Errors**: none
### getgid
`gid_t getgid(void);`
Get the real group ID. **Errors**: none
### getegid
`gid_t getegid(void);`
Get the effective group ID. **Errors**: none
### setuid
`int setuid(uid_t uid);`
Set user identity. **Errors**: EAGAIN, EINVAL, EPERM
### setgid
`int setgid(gid_t gid);`
Set group identity. **Errors**: EINVAL, EPERM
### setsid
`pid_t setsid(void);`
Creates a session and sets the process group ID. **Errors**: EPERM
### setpgid
`int setpgid(pid_t pid, pid_t pgid);`
Set/get process group. **Errors**: EACCES, EINVAL, EPERM, ESRCH
### getpgrp
`pid_t getpgrp(void); /* POSIX.1 version */`
Get the calling process group ID. **Errors**: none

## Signal Operations
### signal
`sighandler_t signal(int signum, sighandler_t handler);`
ANSI C signal handling. **Errors**: EINVAL
### sigaction
`int sigaction(int signum, const struct sigaction *_Nullable restrict act, struct sigaction *_Nullable restrict oldact);`
Examine and change a signal action. **Errors**: EFAULT, EINVAL
### sigprocmask
`int sigprocmask(int how, const sigset_t *_Nullable restrict set, sigset_t *_Nullable restrict oldset);`
Examine and change blocked signals. **Errors**: EFAULT, EINVAL
### sigsuspend
`int sigsuspend(const sigset_t *mask);`
Wait for a signal. **Errors**: EFAULT, EINTR
### sigpending
`int sigpending(sigset_t *set);`
Examine pending signals. **Errors**: EFAULT
### alarm
`unsigned int alarm(unsigned int seconds);`
Set an alarm clock for delivery of a signal. **Errors**: none
### pause
`int pause(void);`
Wait for signal. **Errors**: EINTR

## Memory Management
### brk
`int brk(void *addr);`
Change data segment size. **Errors**: ENOMEM
### sbrk
`void *sbrk(intptr_t increment);`
Change data segment size. **Errors**: ENOMEM
### mmap
`void *mmap(size_t length; void addr[length], size_t length, int prot, int flags, int fd, off_t offset);`
Map or unmap files or devices into memory. **Errors**: EACCES, EAGAIN, EBADF, EEXIST
### munmap
`int munmap(size_t length; void addr[length], size_t length);`
Map or unmap files or devices into memory. **Errors**: EACCES, EAGAIN, EBADF, EEXIST
### mprotect
`int mprotect(size_t size; void addr[size], size_t size, int prot);`
Set protection on a region of memory. **Errors**: EACCES, EINVAL, ENOMEM
### msync
`int msync(size_t length; void addr[length], size_t length, int flags);`
Synchronize a file with a memory map. **Errors**: EBUSY, EINVAL, ENOMEM
### madvise
`int madvise(size_t size; void addr[size], size_t size, int advice);`
Give advice about use of memory. **Errors**: EACCES, EAGAIN, EBADF, EBUSY
### mlock
`int mlock(size_t size; const void addr[size], size_t size);`
Lock and unlock memory. **Errors**: EAGAIN, EINVAL, ENOMEM, EPERM
### munlock
`int munlock(size_t size; const void addr[size], size_t size);`
Lock and unlock memory. **Errors**: EAGAIN, EINVAL, ENOMEM, EPERM

## IPC — Pipes
### pipe
`int pipe(int pipefd[2]);`
Create pipe. **Errors**: EFAULT, EINVAL, EMFILE, ENFILE
### pipe2
`int pipe2(int pipefd[2], int flags);`
Create pipe. **Errors**: EFAULT, EINVAL, EMFILE, ENFILE

## IPC — System V Messages
### msgget
`int msgget(key_t key, int msgflg);`
Get a System V message queue identifier. **Errors**: EACCES, EEXIST, ENOENT, ENOMEM
### msgsnd
`int msgsnd(size_t msgsz; int msqid, const void msgp[msgsz], size_t msgsz, int msgflg);`
System V message queue operations. **Errors**: EACCES, EAGAIN, EFAULT, EIDRM
### msgrcv
`ssize_t msgrcv(size_t msgsz; int msqid, void msgp[msgsz], size_t msgsz, long msgtyp, int msgflg);`
System V message queue operations. **Errors**: EACCES, EAGAIN, EFAULT, EIDRM
### msgctl
`int msgctl(int msqid, int op, struct msqid_ds *buf);`
Perform control operations on a System V message queue. **Errors**: EACCES, EFAULT, EIDRM, EINVAL

## IPC — System V Shared Memory
### shmget
`int shmget(key_t key, size_t size, int shmflg);`
Allocates a System V shared memory segment. **Errors**: EACCES, EEXIST, EINVAL, ENFILE
### shmat
`void *shmat(int shmid, const void *_Nullable shmaddr, int shmflg);`
Attach a System V shared memory segment. **Errors**: EACCES, EIDRM, EINVAL, ENOMEM
### shmdt
`int shmdt(const void *shmaddr);`
Detach a System V shared memory segment. **Errors**: EINVAL
### shmctl
`int shmctl(int shmid, int op, struct shmid_ds *buf);`
Control a System V shared memory segment. **Errors**: EACCES, EFAULT, EIDRM, EINVAL

## IPC — System V Semaphores
### semget
`int semget(key_t key, int nsems, int semflg);`
Get a System V semaphore set identifier. **Errors**: EACCES, EEXIST, EINVAL, ENOENT
### semop
`int semop(int semid, struct sembuf *sops, size_t nsops);`
Perform operations on System V semaphores. **Errors**: E2BIG, EACCES, EAGAIN, EFAULT
### semctl
`int semctl(int semid, int semnum, int op, ...);`
Control a System V semaphore set or semaphore. **Errors**: EACCES, EFAULT, EIDRM, EINVAL

## IPC — Sockets
### socket
`int socket(int domain, int type, int protocol);`
Create an endpoint for communication. **Errors**: EACCES, EAFNOSUPPORT, EINVAL, EMFILE
### bind
`int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);`
Bind a name to a socket. **Errors**: EACCES, EADDRINUSE, EBADF, EINVAL
### listen
`int listen(int sockfd, int backlog);`
Listen for connections on a socket. **Errors**: EADDRINUSE, EBADF, ENOTSOCK, EOPNOTSUPP
### accept
`int accept(int sockfd, struct sockaddr *_Nullable restrict addr, socklen_t *_Nullable restrict addrlen);`
Accept a connection on a socket. **Errors**: EAGAIN/EWOULDBLOCK, EBADF, ECONNABORTED, EFAULT
### connect
`int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);`
Initiate a connection on a socket. **Errors**: EACCES, EPERM, EADDRINUSE, EADDRNOTAVAIL
### send
`ssize_t send(size_t size; int sockfd, const void buf[size], size_t size, int flags);`
Send a message on a socket. **Errors**: EACCES, EAGAIN/EWOULDBLOCK, EALREADY, EBADF
### recv
`ssize_t recv(size_t size; int sockfd, void buf[size], size_t size, int flags);`
Receive a message from a socket. **Errors**: EAGAIN/EWOULDBLOCK, EBADF, ECONNREFUSED, EFAULT
### sendto
`ssize_t sendto(size_t size; int sockfd, const void buf[size], size_t size, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);`
Send a message on a socket. **Errors**: EACCES, EAGAIN/EWOULDBLOCK, EALREADY, EBADF
### recvfrom
`ssize_t recvfrom(size_t size; int sockfd, void buf[restrict size], size_t size, int flags, struct sockaddr *_Nullable restrict src_addr, socklen_t *_Nullable restrict addrlen);`
Receive a message from a socket. **Errors**: EAGAIN/EWOULDBLOCK, EBADF, ECONNREFUSED, EFAULT
### shutdown
`int shutdown(int sockfd, int how);`
Shut down part of a full-duplex connection. **Errors**: EBADF, EINVAL, ENOTCONN, ENOTSOCK
### getsockname
`int getsockname(int sockfd, struct sockaddr *restrict addr, socklen_t *restrict addrlen);`
Get socket name. **Errors**: EBADF, EFAULT, EINVAL, ENOBUFS
### getpeername
`int getpeername(int sockfd, struct sockaddr *restrict addr, socklen_t *restrict addrlen);`
Get name of connected peer socket. **Errors**: EBADF, EFAULT, EINVAL, ENOBUFS
### getsockopt
`int getsockopt(socklen_t *restrict optlen; int sockfd, int level, int optname, void optval[_Nullable restrict *optlen], socklen_t *restrict optlen);`
Get and set options on sockets. **Errors**: EBADF, EFAULT, EINVAL, ENOPROTOOPT
### setsockopt
`int setsockopt(socklen_t optlen; int sockfd, int level, int optname, const void optval[optlen], socklen_t optlen);`
Get and set options on sockets. **Errors**: EBADF, EFAULT, EINVAL, ENOPROTOOPT

## Process Tracing
### ptrace
`long ptrace(enum __ptrace_request op, pid_t pid, void *addr, void *data);`
Process trace. **Errors**: EBUSY, EFAULT, EINVAL, EIO

## Device Control
### ioctl
`int ioctl(int fd, unsigned long op, ...); /* glibc, BSD */`
Control device. **Errors**: EBADF, EFAULT, EINVAL, ENOTTY

## Time
### time
`time_t time(time_t *_Nullable tloc);`
Get time in seconds. **Errors**: EOVERFLOW, EFAULT
### times
`clock_t times(struct tms *buf);`
Get process times. **Errors**: EFAULT
### gettimeofday
`int gettimeofday(struct timeval *restrict tv, struct timezone *_Nullable restrict tz);`
Get / set time. **Errors**: EFAULT
### clock_gettime
`int clock_gettime(clockid_t clockid, struct timespec *tp);`
Clock and time functions. **Errors**: EACCES, EFAULT, EINVAL, ENODEV
### nanosleep
`int nanosleep(const struct timespec *duration, struct timespec *_Nullable rem);`
High-resolution sleep. **Errors**: EFAULT, EINTR, EINVAL

## Miscellaneous
### nice
`int nice(int inc);`
Change process priority. **Errors**: EPERM
### setpriority
`int setpriority(int which, id_t who, int prio);`
Get/set program scheduling priority. **Errors**: EACCES, EINVAL, EPERM, ESRCH
### getpriority
`int getpriority(int which, id_t who);`
Get/set program scheduling priority. **Errors**: EINVAL, ESRCH
### getrlimit
`int getrlimit(int resource, struct rlimit *rlim);`
Get/set resource limits. **Errors**: EFAULT, EINVAL
### setrlimit
`int setrlimit(int resource, const struct rlimit *rlim);`
Get/set resource limits. **Errors**: EFAULT, EINVAL, EPERM
### umask
`mode_t umask(mode_t mask);`
Set file mode creation mask. **Errors**: none
### select
`int select(int nfds, fd_set *_Nullable restrict readfds, fd_set *_Nullable restrict writefds, fd_set *_Nullable restrict exceptfds, struct timeval *_Nullable restrict timeout);`
Synchronous I/O multiplexing. **Errors**: EBADF, EINTR, EINVAL, ENOMEM
### poll
`int poll(struct pollfd *fds, nfds_t nfds, int timeout);`
Wait for some event on a file descriptor. **Errors**: EFAULT, EINTR, EINVAL, ENOMEM
