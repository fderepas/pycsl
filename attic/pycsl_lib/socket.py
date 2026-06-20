"""PyCSL mock for Python's socket module — Low-level networking interface."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def socketpair(family: int, type_: int, proto: int) -> int:
    """Mock: Build a pair of connected socket objects using the given address family, socket type, and protocol number.  Address fami..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_connection(address: int, timeout: int, source_address: int, all_errors: int) -> int:
    """Mock: Connect to a TCP service listening on the internet *address* (a 2-tuple ``(host, port)``), and return the socket object...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_server(address: int, family: int, backlog: int, reuse_port: int, dualstack_ipv6: int) -> int:
    """Mock: Convenience function which creates a TCP socket bound to *address* (a 2-tuple ``(host, port)``) and returns the socket o..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def has_dualstack_ipv6() -> int:
    """Mock: Return ``True`` if the platform supports creating a TCP socket which can handle both IPv4 and IPv6 connections. .. versi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fromfd(fd: int, family: int, type_: int, proto: int) -> int:
    """Mock: Duplicate the file descriptor *fd* (an integer as returned by a file object's :meth:`~io.IOBase.fileno` method) and buil..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fromshare(data: int) -> int:
    """Mock: Instantiate a socket from data obtained from the :meth:`socket.share` method.  The socket is assumed to be in blocking m..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def close(fd: int) -> int:
    """Mock: Close a socket file descriptor. This is like :func:`os.close`, but for sockets. On some platforms (most notably Windows)..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getaddrinfo(host: int, port: int, family: int, type_: int, proto: int, flags: int) -> int:
    """Mock: This function wraps the C function ``getaddrinfo`` of the underlying system. Translate the *host*/*port* argument into a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfqdn(name: int) -> int:
    """Mock: Return a fully qualified domain name for *name*. If *name* is omitted or empty, it is interpreted as the local host.  To..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gethostbyname(hostname: int) -> int:
    """Mock: Translate a host name to IPv4 address format.  The IPv4 address is returned as a string, such as  ``'100.50.200.5'``.  I..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gethostbyname_ex(hostname: int) -> int:
    """Mock: Translate a host name to IPv4 address format, extended interface. Return a 3-tuple ``(hostname, aliaslist, ipaddrlist)``..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gethostname() -> int:
    """Mock: Return a string containing the hostname of the machine where  the Python interpreter is currently executing. .. audit-ev..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gethostbyaddr(ip_address: int) -> int:
    """Mock: Return a 3-tuple ``(hostname, aliaslist, ipaddrlist)`` where *hostname* is the primary host name responding to the given..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getnameinfo(sockaddr: int, flags: int) -> int:
    """Mock: Translate a socket address *sockaddr* into a 2-tuple ``(host, port)``. Depending on the settings of *flags*, the result ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getprotobyname(protocolname: int) -> int:
    """Mock: Translate an internet protocol name (for example, ``'icmp'``) to a constant suitable for passing as the (optional) third..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getservbyname(servicename: int, protocolname: int) -> int:
    """Mock: Translate an internet service name and protocol name to a port number for that service.  The optional protocol name, if ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getservbyport(port: int, protocolname: int) -> int:
    """Mock: Translate an internet port number and protocol name to a service name for that service.  The optional protocol name, if ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ntohl(x: int) -> int:
    """Mock: Convert 32-bit positive integers from network to host byte order.  On machines where the host byte order is the same as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ntohs(x: int) -> int:
    """Mock: Convert 16-bit positive integers from network to host byte order.  On machines where the host byte order is the same as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def htonl(x: int) -> int:
    """Mock: Convert 32-bit positive integers from host to network byte order.  On machines where the host byte order is the same as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def htons(x: int) -> int:
    """Mock: Convert 16-bit positive integers from host to network byte order.  On machines where the host byte order is the same as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def inet_aton(ip_string: int) -> int:
    """Mock: Convert an IPv4 address from dotted-quad string format (for example, '123.45.67.89') to 32-bit packed binary format, as ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def inet_ntoa(packed_ip: int) -> int:
    """Mock: Convert a 32-bit packed IPv4 address (a :term:`bytes-like object` four bytes in length) to its standard dotted-quad stri..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def inet_pton(address_family: int, ip_string: int) -> int:
    """Mock: Convert an IP address from its family-specific string format to a packed, binary format. :func:`inet_pton` is useful whe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def inet_ntop(address_family: int, packed_ip: int) -> int:
    """Mock: Convert a packed IP address (a :term:`bytes-like object` of some number of bytes) to its standard, family-specific strin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CMSG_LEN(length: int) -> int:
    """Mock: Return the total length, without trailing padding, of an ancillary data item with associated data of the given *length*...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CMSG_SPACE(length: int) -> int:
    """Mock: Return the buffer size needed for :meth:`~socket.recvmsg` to receive an ancillary data item with associated data of the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getdefaulttimeout() -> int:
    """Mock: Return the default timeout in seconds (float) for new socket objects. A value of ``None`` indicates that new socket obje..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setdefaulttimeout(timeout: int) -> int:
    """Mock: Set the default timeout in seconds (real number) for new socket objects.  When the socket module is first imported, the ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sethostname(name: int) -> int:
    """Mock: Set the machine's hostname to *name*.  This will raise an :exc:`OSError` if you don't have enough rights. .. audit-event..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def if_nameindex() -> int:
    """Mock: Return a list of network interface information (index int, name string) tuples. :exc:`OSError` if the system call fails...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def if_nametoindex(if_name: int) -> int:
    """Mock: Return a network interface index number corresponding to an interface name. :exc:`OSError` if no interface with the give..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def if_indextoname(if_index: int) -> int:
    """Mock: Return a network interface name corresponding to an interface index number. :exc:`OSError` if no interface with the give..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def send_fds(sock: int, buffers: int, fds: int, flags: int, address: int) -> int:
    """Mock: Send the list of file descriptors *fds* over an :const:`AF_UNIX` socket *sock*. The *fds* parameter is a sequence of fil..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def recv_fds(sock: int, bufsize: int, maxfds: int, flags: int) -> int:
    """Mock: Receive up to *maxfds* file descriptors from an :const:`AF_UNIX` socket *sock*. Return ``(msg, list(fds), flags, addr)``..."""
    return 0
