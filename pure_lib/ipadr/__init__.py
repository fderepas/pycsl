# Pure model for ipaddress — IPv4/IPv6 manipulation
# Models addresses as bounded integers.

""" # pycsl"""


#@ class invariant self._addr >= 0
#@ class invariant self._version >= 0
class IPAddress:
    """Abstract IP address (v4 or v6)."""

    #@ requires addr >= 0
    #@ requires version >= 4
    #@ requires version <= 6
    #@ ensures self._addr == addr
    #@ ensures self._version == version
    def __init__(self, addr: int, version: int) -> None:
        self._addr: int = addr
        self._version: int = version

    #@ ensures \result == self._version
    def version(self) -> int:
        """Return IP version (4 or 6)."""
        return self._version

    #@ ensures \result == self._addr
    def packed(self) -> int:
        """Return packed integer representation."""
        return self._addr

    #@ ensures \result >= 0
    #@ ensures \result <= 1
    def is_private(self) -> int:
        """Return 1 if private address, else 0."""
        return 0

    #@ ensures \result >= 0
    #@ ensures \result <= 1
    def is_loopback(self) -> int:
        """Return 1 if loopback, else 0."""
        return 0


#@ requires addr >= 0
#@ requires prefix >= 0
#@ requires prefix <= 128
#@ ensures \result >= 0
def ip_network(addr: int, prefix: int) -> int:
    """Create network from address and prefix length."""
    return addr


#@ requires addr >= 0
#@ ensures \result >= 4
#@ ensures \result <= 6
def ip_version(addr: int) -> int:
    """Determine IP version from address value."""
    return 4
