# formal_os_close.py — os.close CONSEQUENCE, through the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names from pure_lib.os; no _filesystem,
# no disk, no sys_*, no UnixInodeFileSystem reference in code or contracts.
#
# CONSEQUENCE (setup -> operate -> OBSERVE), NOT the op's own return code:
#   open(p) yields a valid fd whose fstat is a valid inode; after close(fd),
#   fstat(fd) reports EBADF (-1) -- i.e. close MAKES THE FD UNUSABLE, observed
#   through fstat. This is a genuine consequence: it ties the post-close fstat
#   value to the close having taken effect, not to close's own 0/-1 return.
#
# MECHANISM. open's fd-resolution ensures pins (fd_open[fd]==1, 0<=fd_inode<32)
# so fstat(fd) >= 0 before close. close's CLOSE-POST-STATE ensures pins
# fd_open[fd]==0 on success; fstat's EBADF-direction ensures then delivers -1 for
# a closed in-range fd. The chain composes through the public contracts with ZERO
# trusted obligations.
#
# NON-VACUITY: the asserted observation (fstat==-1 after close) would be FALSE if
# close did not clear fd_open[fd] (fstat would still report the inode). A seeded
# mutation that drops close's CLOSE-POST-STATE (or asserts fstat>=0 post-close)
# flips this to FAIL. See the supervisor's non-vacuity re-check.

from pure_lib.os import open, close, fstat

O_RDONLY = 0


# open(p) -> close(fd) -> fstat(fd) reports EBADF (-1).
# Setup: open p (p must resolve, else open returns -1 and we skip -- guarded).
# Operate: close(fd). OBSERVE: the returned fstat value IS -1 (the fd is now
# unusable). We RETURN the observed fstat value and assert it equals -1 -- the
# strongest non-vacuous form (the guarded skips return -1 too, so the ensures
# pins the OBSERVATION, not a constant). A wrong assertion (\result >= 0) FAILS.
#@ requires True
#@ ensures \result == -1
def close_makes_fd_unusable(p: str) -> int:
    fd = open(p, O_RDONLY, 0o777)   # set up: open an existing name
    if fd == -1:
        return -1                   # open failed: not the case under test (guarded)
    rc = close(fd)                  # operate: close the fd
    if rc != 0:
        return -1                   # close failed: not the case under test (guarded)
    return fstat(fd)                # OBSERVE: EBADF after close -- ASSERTED == -1
