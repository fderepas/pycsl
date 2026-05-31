"""PyCSL mock for Python's ssl module — TLS/SSL wrapper for socket objects."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def create_default_context(purpose: int, __cafile: int, capath: int, cadata: int) -> int:
    """Mock: Return a new :class:`SSLContext` object with default settings for the given *purpose*.  The settings are chosen by the :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_sigalgs() -> int:
    """Mock: Return a list of available TLS signature algorithm names used by servers to complete the TLS handshake or clients reques..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def RAND_bytes(num: int) -> int:
    """Mock: Return *num* cryptographically strong pseudo-random bytes. Raises an :class:`SSLError` if the PRNG has not been seeded w..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def RAND_status() -> int:
    """Mock: Return ``True`` if the SSL pseudo-random number generator has been seeded with 'enough' randomness, and ``False`` otherw..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def RAND_add(bytes: int, entropy: int) -> int:
    """Mock: Mix the given *bytes* into the SSL pseudo-random number generator.  The parameter *entropy* (a float) is a lower bound o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cert_time_to_seconds(cert_time: int) -> int:
    """Mock: Return the time in seconds since the epoch, given the ``cert_time`` string representing the 'notBefore' or 'notAfter' da..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_server_certificate(addr: int, ssl_version: int, __ca_certs: int, timeout: int) -> int:
    """Mock: Given the address ``addr`` of an SSL-protected server, as a (*hostname*, *port-number*) pair, fetches the server's certi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def DER_cert_to_PEM_cert(der_cert_bytes: int) -> int:
    """Mock: Given a certificate as a DER-encoded blob of bytes, returns a PEM-encoded string version of the same certificate."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PEM_cert_to_DER_cert(pem_cert_string: int) -> int:
    """Mock: Given a certificate as an ASCII PEM string, returns a DER-encoded sequence of bytes for that same certificate."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_default_verify_paths() -> int:
    """Mock: Returns a named tuple with paths to OpenSSL's default cafile and capath. The paths are the same as used by :meth:`SSLCon..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def enum_certificates(store_name: int) -> int:
    """Mock: Retrieve certificates from Windows' system cert store. *store_name* may be one of ``CA``, ``ROOT`` or ``MY``. Windows ma..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def enum_crls(store_name: int) -> int:
    """Mock: Retrieve CRLs from Windows' system cert store. *store_name* may be one of ``CA``, ``ROOT`` or ``MY``. Windows may provid..."""
    return 0
