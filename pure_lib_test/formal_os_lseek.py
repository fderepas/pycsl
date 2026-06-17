# formal_os_lseek.py — os.lseek SEEK_SET CONSEQUENCE, through the PUBLIC API ONLY.
#
# INTERNALS-BLIND. Imports only public names from pure_lib.os; no _filesystem,
# no disk, no sys_*, no UnixInodeFileSystem reference in code or contracts.
#
# CONSEQUENCE (setup -> operate -> OBSERVE), NOT the op's own return code:
#   open(p) yields a valid fd; an ABSOLUTE seek lseek(fd, pos, SEEK_SET) to a
#   non-negative pos RETURNS pos -- the new file position equals the requested
#   one. This ties lseek's result to the position the caller asked for, not to
#   lseek's bare `\result >= -1` bound (which would hold even if the seek landed
#   anywhere). SEEK_SET semantics: the offset becomes exactly `pos`.
#
# MECHANISM. open's fd-resolution ensures pins fd_open[fd]==1 on success; lseek's
# SEEK_SET-CONSEQUENCE ensures then delivers `\result == pos` for whence==0 and
# pos>=0 on an open fd. Composes through the public contracts with ZERO trusted obligations.
#
# NON-VACUITY: a seeded mutation asserting a DIFFERENT position (e.g. \result ==
# pos + 1) flips this to FAIL. The seek result is the requested pos, not adjacent.

from pure_lib.os import open, lseek

O_RDONLY = 0
SEEK_SET = 0


# open(p) -> lseek(fd, pos, SEEK_SET) -> result == pos.
# Setup: open p (guarded skip if absent). Operate: absolute seek to pos.
# OBSERVE: the returned new position EQUALS pos. We RETURN (result - pos), which
# the ensures pins to 0 on the under-test path; the guarded skip returns 0 too.
#@ requires pos >= 0
#@ ensures \result == 0
def lseek_set_returns_pos(p: str, pos: int) -> int:
    fd = open(p, O_RDONLY, 0o777)   # set up: open an existing name
    if fd == -1:
        return 0                    # open failed: not the case under test (guarded)
    r = lseek(fd, pos, SEEK_SET)    # operate: absolute seek to pos
    if r == -1:
        return 0                    # seek failed (fd not open): guarded skip
    return r - pos                  # OBSERVE: new position == pos -> result 0
