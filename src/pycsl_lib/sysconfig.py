"""PyCSL mock for Python's sysconfig module — Python's configuration information."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def get_config_vars() -> int:
    """Mock: With no arguments, return a dictionary of all configuration variables relevant for the current platform. With arguments,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_config_var(name: int) -> int:
    """Mock: Return the value of a single variable *name*. Equivalent to ``get_config_vars().get(name)``. If *name* is not found, ret..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_scheme_names() -> int:
    """Mock: Return a tuple containing all schemes currently supported in :mod:`!sysconfig`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_default_scheme() -> int:
    """Mock: Return the default scheme name for the current platform. .. versionadded:: 3.10 This function was previously named ``_ge..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_preferred_scheme(key: int) -> int:
    """Mock: Return a preferred scheme name for an installation layout specified by *key*. *key* must be either ``'prefix'``, ``'home..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _get_preferred_schemes() -> int:
    """Mock: Return a dict containing preferred scheme names on the current platform. Python implementers and redistributors may add ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_path_names() -> int:
    """Mock: Return a tuple containing all path names currently supported in :mod:`!sysconfig`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_path(name: int, scheme: int, vars: int, expand: int) -> int:
    """Mock: Return an installation path corresponding to the path *name*, from the install scheme named *scheme*. *name* has to be a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_paths(scheme: int, vars: int, expand: int) -> int:
    """Mock: Return a dictionary containing all installation paths corresponding to an installation scheme. See :func:`get_path` for ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_python_version() -> int:
    """Mock: Return the ``MAJOR.MINOR`` Python version number as a string.  Similar to ``'%d.%d' % sys.version_info[:2]``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_platform() -> int:
    """Mock: Return a string that identifies the current platform. This is used mainly to distinguish platform-specific build directo..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_python_build() -> int:
    """Mock: Return ``True`` if the running Python interpreter was built from source and is being run from its built location, and no..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def parse_config_h(fp: int, vars: int) -> int:
    """Mock: Parse a :file:`config.h`\-style file. *fp* is a file-like object pointing to the :file:`config.h`\-like file. A dictiona..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_config_h_filename() -> int:
    """Mock: Return the path of :file:`pyconfig.h`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_makefile_filename() -> int:
    """Mock: Return the path of :file:`Makefile`."""
    return 0
