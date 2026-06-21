# formal_os_close.py — os.close CONSEQUENCE, through the PUBLIC API ONLY.
#
# MIGRATED to the FAITHFUL exception model (os.rst l.47-49).  open/close/fstat now
# RAISE on failure rather than returning -1.  The consequence is unchanged — close
# MAKES THE FD UNUSABLE — but it is now observed by fstat RAISING (EBADF) after the
# close, caught through `except OSError`, instead of fstat returning -1.
#
# INTERNALS-BLIND. Imports only public names from pycsl_lib.os.
#
# CONSEQUENCE (setup -> operate -> OBSERVE), NOT the op's own return code:
#   open(p) yields a valid fd whose fstat is a valid inode; after close(fd),
#   fstat(fd) RAISES (EBADF) -- i.e. close MAKES THE FD UNUSABLE, observed through
#   fstat's raise.
#
# MECHANISM. open's fd-resolution ensures pins (fd_open[fd]==1, 0<=fd_inode<32) so
# fstat(fd) succeeds before close.  close's CLOSE-POST-STATE ensures pins
# fd_open[fd]==0; fstat's `raises OSError` then fires for the closed in-range fd.
# The chain composes through the public contracts with ZERO trusted obligations.
#
# NON-VACUITY: `ensures \result == 1` is reached ONLY through the `except OSError`
# handler around the post-close fstat.  If close did not clear fd_open[fd], fstat
# would NOT raise, control would fall to `return 0`, and the postcondition fails.

from pycsl_lib.os import open, close, fstat

O_RDONLY = 0


# open(p) -> close(fd) -> fstat(fd) RAISES EBADF.
# Setup: open p.  Operate: close(fd).  OBSERVE: fstat(fd) RAISES (the fd is now
# unusable), caught by `except OSError`.
#@ requires True
#@ ensures \result == 1
def close_makes_fd_unusable(p: str) -> int:
    fd = open(p, O_RDONLY, 0o777)   # set up: open an existing name (raises if absent)
    close(fd)                       # operate: close the fd (raises on failure)
    try:
        fstat(fd)                   # OBSERVE: fstat on the closed fd...
        return 0                    # UNREACHABLE if close faithfully cleared the fd
    except OSError:
        return 1                    # ...RAISES EBADF — close took effect — ASSERTED == 1
