"""PyCSL mock for Python's platform module — Retrieves as much platform identifying data as possible."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def architecture(executable: int, bits: int, linkage: int) -> int:
    """Mock: Queries the given executable (defaults to the Python interpreter binary) for various architecture information. Returns a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def machine() -> int:
    """Mock: Returns the machine type, e.g. ``'AMD64'``. An empty string is returned if the value cannot be determined. The output is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def node() -> int:
    """Mock: Returns the computer's network name (may not be fully qualified!). An empty string is returned if the value cannot be de..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def platform(aliased: int, terse: int) -> int:
    """Mock: Returns a single string identifying the underlying platform with as much useful information as possible. The output is i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def processor() -> int:
    """Mock: Returns the (real) processor name, e.g. ``'amdk6'``. An empty string is returned if the value cannot be determined. Note..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_build() -> int:
    """Mock: Returns a tuple ``(buildno, builddate)`` stating the Python build number and date as strings."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_compiler() -> int:
    """Mock: Returns a string identifying the compiler used for compiling Python."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_branch() -> int:
    """Mock: Returns a string identifying the Python implementation SCM branch."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_implementation() -> int:
    """Mock: Returns a string identifying the Python implementation. Possible return values are: 'CPython', 'IronPython', 'Jython', '..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_revision() -> int:
    """Mock: Returns a string identifying the Python implementation SCM revision."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_version() -> int:
    """Mock: Returns the Python version as string ``'major.minor.patchlevel'``. Note that unlike the Python ``sys.version``, the retu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def python_version_tuple() -> int:
    """Mock: Returns the Python version as tuple ``(major, minor, patchlevel)`` of strings. Note that unlike the Python ``sys.version..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def release() -> int:
    """Mock: Returns the system's release, e.g. ``'2.2.0'`` or ``'NT'``. An empty string is returned if the value cannot be determine..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def system() -> int:
    """Mock: Returns the system/OS name, such as ``'Linux'``, ``'Darwin'``, ``'Java'``, ``'Windows'``. An empty string is returned if..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def system_alias(system: int, release: int, version: int) -> int:
    """Mock: Returns ``(system, release, version)`` aliased to common marketing names used for some systems.  It also does some reord..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def version() -> int:
    """Mock: Returns the system's release version, e.g. ``'#3 on degas'``. An empty string is returned if the value cannot be determi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def uname() -> int:
    """Mock: Fairly portable uname interface. Returns a :func:`~collections.namedtuple` containing six attributes: :attr:`system`, :a..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def invalidate_caches() -> int:
    """Mock: Clear out the internal cache of information, such as the :func:`uname`. This is typically useful when the platform's :fu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def win32_ver(release: int, version: int, csd: int, ptype: int) -> int:
    """Mock: Get additional version information from the Windows Registry and return a tuple ``(release, version, csd, ptype)`` refer..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def win32_edition() -> int:
    """Mock: Returns a string representing the current Windows edition, or ``None`` if the value cannot be determined.  Possible valu..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def win32_is_iot() -> int:
    """Mock: Return ``True`` if the Windows edition returned by :func:`win32_edition` is recognized as an IoT edition. .. versionadde..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mac_ver(release: int, versioninfo: int, machine: int) -> int:
    """Mock: Get macOS version information and return it as tuple ``(release, versioninfo, machine)`` with *versioninfo* being a tupl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ios_ver(system: int, release: int, model_: int, is_simulator: int) -> int:
    """Mock: Get iOS version information and return it as a :func:`~collections.namedtuple` with the following attributes: * ``system..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def libc_ver(executable: int, lib: int, version: int, chunksize: int) -> int:
    """Mock: Tries to determine the libc version against which the file executable (defaults to the Python interpreter) is linked.  R..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def freedesktop_os_release() -> int:
    """Mock: Get operating system identification from ``os-release`` file and return it as a dict. The ``os-release`` file is a `free..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def android_ver(release: int, api_level: int, manufacturer: int, __model: int, device: int, is_emulator: int) -> int:
    """Mock: Get Android device information. Returns a :func:`~collections.namedtuple` with the following attributes. Values which ca..."""
    return 0
