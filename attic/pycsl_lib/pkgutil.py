"""PyCSL mock for Python's pkgutil module — Utilities for the import system."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def extend_path(path: int, name: int) -> int:
    """Mock: Extend the search path for the modules which comprise a package.  Intended use is to place the following code in a packa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_importer(path_item: int) -> int:
    """Mock: Retrieve a :term:`finder` for the given *path_item*. The returned finder is cached in :data:`sys.path_importer_cache` if..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iter_importers(fullname: int) -> int:
    """Mock: Yield :term:`finder` objects for the given module name. If *fullname* contains a ``'.'``, the finders will be for the pa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iter_modules(path: int, prefix: int) -> int:
    """Mock: Yields :class:`ModuleInfo` for all submodules on *path*, or, if *path* is ``None``, all top-level modules on :data:`sys...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def walk_packages(path: int, prefix: int, onerror: int) -> int:
    """Mock: Yields :class:`ModuleInfo` for all modules recursively on *path*, or, if *path* is ``None``, all accessible modules. *pa..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_data(package: int, resource: int) -> int:
    """Mock: Get a resource from a package. This is a wrapper for the :term:`loader` :meth:`get_data <importlib.abc.ResourceLoader.ge..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resolve_name(name: int, strict: int) -> int:
    """Mock: Resolve a name to an object. This functionality is used in numerous places in the standard library (see :issue:`12915`) ..."""
    return 0
