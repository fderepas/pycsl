"""PyCSL mock for Python's importlib module — The implementation of the import machinery."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def __import__(name: int, globals: int, locals: int, fromlist: int, level: int) -> int:
    """Mock: An implementation of the built-in :func:`__import__` function. .. note:: Programmatic importing of modules should use :f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def import_module(name: int, package: int) -> int:
    """Mock: Import a module. The *name* argument specifies what module to import in absolute or relative terms (e.g. either ``pkg.mo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def invalidate_caches() -> int:
    """Mock: Invalidate the internal caches of finders stored at :data:`sys.meta_path`. If a finder implements ``invalidate_caches()`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reload(module_: int) -> int:
    """Mock: Reload a previously imported *module*.  The argument must be a module object, so it must have been successfully imported..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def all_suffixes() -> int:
    """Mock: Returns a combined list of strings representing all file suffixes for modules recognized by the standard import machiner..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cache_from_source(path: int, optimization: int) -> int:
    """Mock: Return the :pep:`3147`/:pep:`488` path to the byte-compiled file associated with the source *path*.  For example, if *pa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def source_from_cache(path: int) -> int:
    """Mock: Given the *path* to a :pep:`3147` file name, return the associated source code file path.  For example, if *path* is ``/..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decode_source(source_bytes: int) -> int:
    """Mock: Decode the given bytes representing source code and return it as a string with universal newlines (as required by :meth:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resolve_name(name: int, package: int) -> int:
    """Mock: Resolve a relative module name to an absolute one. If  **name** has no leading dots, then **name** is simply returned. T..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def find_spec(name: int, package: int) -> int:
    """Mock: Find the :term:`spec <module spec>` for a module, optionally relative to the specified **package** name. If the module i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def module_from_spec(spec: int) -> int:
    """Mock: Create a new module based on **spec** and :meth:`spec.loader.create_module <importlib.abc.Loader.create_module>`. If :me..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spec_from_loader(name: int, loader: int, origin: int, is_package: int) -> int:
    """Mock: A factory function for creating a :class:`~importlib.machinery.ModuleSpec` instance based on a loader.  The parameters h..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spec_from_file_location(name: int, location: int, loader: int, submodule_search_locations: int) -> int:
    """Mock: A factory function for creating a :class:`~importlib.machinery.ModuleSpec` instance based on the path to a file.  Missin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def source_hash(source_bytes: int) -> int:
    """Mock: Return the hash of *source_bytes* as bytes. A hash-based ``.pyc`` file embeds the :func:`source_hash` of the correspondi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _incompatible_extension_module_restrictions(disable_check: int) -> int:
    """Mock: A context manager that can temporarily skip the compatibility check for extension modules.  By default the check is enab..."""
    return 0
