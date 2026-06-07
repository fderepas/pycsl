# Formal tests for pure_lib/ipadr — ipaddress module
from pure_lib.ipadr import ip_network, ip_version


#@ requires addr >= 0
#@ requires prefix >= 0
#@ requires prefix <= 128
#@ ensures \result >= 0
def test_network_nonneg(addr: int, prefix: int) -> int:
    """ip_network returns non-negative."""
    return ip_network(addr, prefix)


#@ requires addr >= 0
#@ ensures \result >= 4
def test_version_at_least_4(addr: int) -> int:
    """IP version is at least 4."""
    return ip_version(addr)
