"""PyCSL mock for Python's ipaddress module — IPv4/IPv6 manipulation library."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def ip_address(address: int) -> int:
    """Mock: Return an :class:`IPv4Address` or :class:`IPv6Address` object depending on the IP address passed as argument.  Either IP..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ip_network(address: int, strict: int) -> int:
    """Mock: Return an :class:`IPv4Network` or :class:`IPv6Network` object depending on the IP address passed as argument.  *address*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ip_interface(address: int) -> int:
    """Mock: Return an :class:`IPv4Interface` or :class:`IPv6Interface` object depending on the IP address passed as argument.  *addr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def v4_int_to_packed(address: int) -> int:
    """Mock: Represent an address as 4 packed bytes in network (big-endian) order. *address* is an integer representation of an IPv4 ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def v6_int_to_packed(address: int) -> int:
    """Mock: Represent an address as 16 packed bytes in network (big-endian) order. *address* is an integer representation of an IPv6..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def summarize_address_range(first: int, last: int) -> int:
    """Mock: Return an iterator of the summarized network range given the first and last IP addresses.  *first* is the first :class:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def collapse_addresses(addresses: int) -> int:
    """Mock: Return an iterator of the collapsed :class:`IPv4Network` or :class:`IPv6Network` objects.  *addresses* is an :term:`iter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_mixed_type_key(obj: int) -> int:
    """Mock: Return a key suitable for sorting between networks and addresses.  Address and Network objects are not sortable by defau..."""
    return 0
