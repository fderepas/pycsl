# Pure model for socket — network socket interface
# Models as fd-based connection with send/recv byte counts.

""" # pycsl"""


#@ class invariant self._fd >= 0
#@ class invariant self._connected >= 0
#@ class invariant self._connected <= 1
class Socket:
    """Abstract network socket."""

    #@ requires family >= 0
    #@ ensures self._fd == family
    #@ ensures self._connected == 0
    #@ ensures self._bytes_sent == 0
    #@ ensures self._bytes_recv == 0
    def __init__(self, family: int) -> None:
        self._fd: int = family
        self._connected: int = 0
        self._bytes_sent: int = 0
        self._bytes_recv: int = 0

    #@ requires self._connected == 0
    #@ ensures self._connected == 1
    #@ assigns self._connected
    def connect(self, addr: int) -> None:
        """Connect to remote address."""
        self._connected = 1

    #@ requires self._connected == 1
    #@ requires nbytes > 0
    #@ ensures self._bytes_sent == \old(self._bytes_sent) + nbytes
    #@ assigns self._bytes_sent
    def send(self, nbytes: int) -> None:
        """Send bytes on connected socket."""
        self._bytes_sent = self._bytes_sent + nbytes

    #@ requires self._connected == 1
    #@ requires bufsize > 0
    #@ ensures \result >= 0
    #@ ensures \result <= bufsize
    def recv(self, bufsize: int) -> int:
        """Receive up to bufsize bytes. Returns actual count."""
        return 0

    #@ ensures self._connected == 0
    #@ assigns self._connected
    def close(self) -> None:
        """Close the socket."""
        self._connected = 0

    #@ ensures \result == self._fd
    def fileno(self) -> int:
        """Return file descriptor."""
        return self._fd


# Socket constants
AF_INET: int = 2
AF_INET6: int = 10
SOCK_STREAM: int = 1
SOCK_DGRAM: int = 2
