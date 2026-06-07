# pure_lib/world — the shared mutable World aggregate
#
# making-it-pure-5.md §1.2: "Single mutable state — one fs, one proc
# table, one clock. Region-partitioned (see §2)."
#
# The World is the pure-Python kernel. Every subsystem that mutates
# state holds a reference to the same World instance, ensuring:
#   - One filesystem (inodes, blocks, fd table)
#   - One process table (pid, cwd, environ, argv, umask)
#   - One clock (monotonic counter for timestamps)
#
# Coherence is maintained by ownership confinement (HAPPY, §2):
#   - Only fs methods write world.fs.* fields
#   - Only proc methods write world.proc.* fields
#   - Only clock.monotonic writes world.clock._ticks

from pure_lib.tm import ClockModel
from pure_lib.os.UnixInodeFileSystem import UnixInodeFileSystem
from pure_lib.proc import ProcessState


class World:
    """Single shared mutable state — one fs, one proc table, one clock.

    Region-partitioned by ownership (making-it-pure-5.md §2):
      clock_ownership: protects world.clock._ticks (except: monotonic)
      fs_ownership:    protects world.fs.disk, .fd_* (except: fs methods)
      proc_ownership:  protects world.proc.* (except: proc methods)
    """

    def __init__(self):
        self.clock = ClockModel()
        self.fs = UnixInodeFileSystem(clock=self.clock)
        self.proc = ProcessState(fs=self.fs, clock=self.clock)
        # Wire standard environment
        self.proc.setenv("PATH", "/usr/bin:/bin")
        self.proc.setenv("HOME", "/")
        self.proc.setenv("USER", "root")
        self.proc.setenv("LANG", "C")
