"""PyCSL mock for Python's uuid module — UUID objects (universally unique identifiers) according to RFC 9562."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def getnode() -> int:
    """Mock: Get the hardware address as a 48-bit positive integer.  The first time this runs, it may launch a separate program, whic..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid1(node: int, clock_seq: int) -> int:
    """Mock: Generate a UUID from a host ID, sequence number, and the current time according to :rfc:`RFC 9562, §5.1 <9562#section-5...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid3(namespace: int, name: int) -> int:
    """Mock: Generate a UUID based on the MD5 hash of a namespace identifier (which is a UUID) and a name (which is a :class:`bytes` ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid4() -> int:
    """Mock: Generate a random UUID in a cryptographically-secure method according to :rfc:`RFC 9562, §5.4 <9562#section-5.4>`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid5(namespace: int, name: int) -> int:
    """Mock: Generate a UUID based on the SHA-1 hash of a namespace identifier (which is a UUID) and a name (which is a :class:`bytes..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid6(node: int, clock_seq: int) -> int:
    """Mock: Generate a UUID from a sequence number and the current time according to :rfc:`RFC 9562, §5.6 <9562#section-5.6>`. This ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid7() -> int:
    """Mock: Generate a time-based UUID according to :rfc:`RFC 9562, §5.7 <9562#section-5.7>`. For portability across platforms lacki..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def uuid8(a: int, b: int, c: int) -> int:
    """Mock: Generate a pseudo-random UUID according to :rfc:`RFC 9562, §5.8 <9562#section-5.8>`. When specified, the parameters *a*,..."""
    return 0
