"""PyCSL mock for Python's importlib module.

Provides trusted stubs for the import machinery.
Covers importlib top-level functions, importlib.abc abstract base
classes, importlib.machinery classes, importlib.util utilities, and
importlib.resources access helpers.  All values are modelled as
opaque integers.
"""
_ = 0  # anchor

# ── importlib top-level functions ────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def __import__(name: int, globals: int, locals: int, fromlist: int, level: int) -> int:
    """Mock: built-in __import__ implementation."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.import_module
#@ requires name != 0
#@ ensures \result != 0
def import_module(name: int, package: int) -> int:
    """Mock: import a module by name."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.invalidate_caches
#@ ensures True
#@ assigns \nothing
def invalidate_caches() -> int:
    """Mock: invalidate internal caches of all finders."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.reload
#@ requires mod_obj != 0
#@ ensures \result == mod_obj
def reload(mod_obj: int) -> int:
    """Mock: reload a previously imported module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/__init__.py
#@ requires True
#@ ensures True
def find_loader(name: int, path: int) -> int:
    """Mock: find the loader for a module (deprecated)."""
    return 0

# ── importlib.abc — MetaPathFinder ───────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/abc.py
#@ requires True
#@ ensures True
def MetaPathFinder() -> int:
    """Mock: create a MetaPathFinder instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder.find_spec
#@ requires True
#@ ensures True
def MetaPathFinder_find_spec(fullname: int, path: int, target: int) -> int:
    """Mock: find a module spec on the meta path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder.invalidate_caches
#@ requires True
#@ ensures True
def MetaPathFinder_invalidate_caches() -> int:
    """Mock: invalidate the finder's internal cache."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/abc.py
#@ requires True
#@ ensures True
def MetaPathFinder_discover(parent: int) -> int:
    """Mock: search for possible specs with given parent."""
    return 0

# ── importlib.abc — PathEntryFinder ──────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.PathEntryFinder
#@ requires True
#@ ensures True
def PathEntryFinder() -> int:
    """Mock: create a PathEntryFinder instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.PathEntryFinder.find_spec
#@ requires True
#@ ensures True
def PathEntryFinder_find_spec(fullname: int, target: int) -> int:
    """Mock: find a module spec in the path entry."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.PathEntryFinder.invalidate_caches
#@ requires True
#@ ensures True
def PathEntryFinder_invalidate_caches() -> int:
    """Mock: invalidate the path entry finder's cache."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/abc.py
#@ requires True
#@ ensures True
def PathEntryFinder_discover(parent: int) -> int:
    """Mock: search for possible specs with given parent."""
    return 0

# ── importlib.abc — Loader ───────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/__init__.py
#@ requires True
#@ ensures True
def Loader() -> int:
    """Mock: create a Loader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.create_module
#@ requires True
#@ ensures True
def Loader_create_module(mod_spec: int) -> int:
    """Mock: return the module object for importing."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.Loader.exec_module
#@ requires True
#@ ensures True
def Loader_exec_module(mod_obj: int) -> int:
    """Mock: execute the module in its own namespace."""
    return 0

# ── importlib.abc — ResourceLoader ───────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.ResourceLoader
#@ requires True
#@ ensures True
def ResourceLoader() -> int:
    """Mock: create a ResourceLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.ResourceLoader.get_data
#@ requires True
#@ ensures True
def ResourceLoader_get_data(path: int) -> int:
    """Mock: return bytes for data at path."""
    return 0

# ── importlib.abc — InspectLoader ────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.InspectLoader
#@ requires True
#@ ensures True
def InspectLoader() -> int:
    """Mock: create an InspectLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.InspectLoader.get_code
#@ requires True
#@ ensures True
def InspectLoader_get_code(fullname: int) -> int:
    """Mock: return the code object for a module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/abc.py
#@ requires True
#@ ensures True
def InspectLoader_get_source(fullname: int) -> int:
    """Mock: return the source of a module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/abc.py
#@ requires True
#@ ensures True
def InspectLoader_is_package(fullname: int) -> int:
    """Mock: return true if the module is a package."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.InspectLoader.source_to_code
#@ requires True
#@ ensures True
def InspectLoader_source_to_code(data: int, path: int, fullname: int) -> int:
    """Mock: create a code object from Python source."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.InspectLoader.exec_module
#@ requires True
#@ ensures True
def InspectLoader_exec_module(mod_obj: int) -> int:
    """Mock: execute the module in its namespace."""
    return 0

# ── importlib.abc — ExecutionLoader ──────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.ExecutionLoader
#@ requires True
#@ ensures True
def ExecutionLoader() -> int:
    """Mock: create an ExecutionLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.ExecutionLoader.get_filename
#@ requires True
#@ ensures True
def ExecutionLoader_get_filename(fullname: int) -> int:
    """Mock: return __file__ value for the module."""
    return 0

# ── importlib.abc — FileLoader ───────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def FileLoader(fullname: int, path: int) -> int:
    """Mock: create a FileLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.FileLoader.get_filename
#@ requires True
#@ ensures True
def FileLoader_get_filename(fullname: int) -> int:
    """Mock: return the path to the file."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.FileLoader.get_data
#@ requires True
#@ ensures True
def FileLoader_get_data(path: int) -> int:
    """Mock: read path as binary and return bytes."""
    return 0

# ── importlib.abc — SourceLoader ─────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.SourceLoader
#@ requires True
#@ ensures True
def SourceLoader() -> int:
    """Mock: create a SourceLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.SourceLoader.path_stats
#@ requires True
#@ ensures True
def SourceLoader_path_stats(path: int) -> int:
    """Mock: return metadata dict for the specified path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceLoader_path_mtime(path: int) -> int:
    """Mock: return modification time for the path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceLoader_set_data(path: int, data: int) -> int:
    """Mock: write bytes to a file path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.abc.SourceLoader.get_code
#@ requires True
#@ ensures True
def SourceLoader_get_code(fullname: int) -> int:
    """Mock: return the code object for a module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceLoader_exec_module(mod_obj: int) -> int:
    """Mock: execute the module in its namespace."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceLoader_get_source(fullname: int) -> int:
    """Mock: return the source of a module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/abc.py
#@ requires True
#@ ensures True
def SourceLoader_is_package(fullname: int) -> int:
    """Mock: return true if the module is a package."""
    return 0

# ── importlib.machinery — module-level ───────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def all_suffixes() -> int:
    """Mock: return combined list of all recognized module suffixes."""
    return 0

# ── importlib.machinery — BuiltinImporter ────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap.py
#@ requires True
#@ ensures True
def BuiltinImporter() -> int:
    """Mock: create a BuiltinImporter instance — opaque."""
    return 0

# ── importlib.machinery — FrozenImporter ─────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap.py
#@ requires True
#@ ensures True
def FrozenImporter() -> int:
    """Mock: create a FrozenImporter instance — opaque."""
    return 0

# ── importlib.machinery — WindowsRegistryFinder ──────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def WindowsRegistryFinder() -> int:
    """Mock: create a WindowsRegistryFinder instance — opaque."""
    return 0

# ── importlib.machinery — PathFinder ─────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.PathFinder
#@ requires True
#@ ensures True
def PathFinder() -> int:
    """Mock: create a PathFinder instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def PathFinder_find_spec(fullname: int, path: int, target: int) -> int:
    """Mock: find a spec for fullname on sys.path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.PathFinder.invalidate_caches
#@ requires True
#@ ensures True
def PathFinder_invalidate_caches() -> int:
    """Mock: invalidate all cached path entry finders."""
    return 0

# ── importlib.machinery — FileFinder ─────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def FileFinder(path: int, loader_details: int) -> int:
    """Mock: create a FileFinder instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def FileFinder_find_spec(fullname: int, target: int) -> int:
    """Mock: find the spec for fullname within path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
#@ assigns \nothing
def FileFinder_invalidate_caches() -> int:
    """Mock: clear the internal cache."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def FileFinder_path_hook(loader_details: int) -> int:
    """Mock: return a closure for use on sys.path_hooks."""
    return 0

# ── importlib.machinery — NamespacePath ──────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def NamespacePath(name: int, path: int, path_finder: int) -> int:
    """Mock: create a NamespacePath instance — opaque."""
    return 0

# ── importlib.machinery — SourceFileLoader ───────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceFileLoader(fullname: int, path: int) -> int:
    """Mock: create a SourceFileLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.SourceFileLoader
#@ requires True
#@ ensures True
def SourceFileLoader_is_package(fullname: int) -> int:
    """Mock: return True if path is for a package."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceFileLoader_path_stats(path: int) -> int:
    """Mock: return metadata dict for path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourceFileLoader_set_data(path: int, data: int) -> int:
    """Mock: write bytes to a file path."""
    return 0

# ── importlib.machinery — SourcelessFileLoader ───────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.SourcelessFileLoader
#@ requires True
#@ ensures True
def SourcelessFileLoader(fullname: int, path: int) -> int:
    """Mock: create a SourcelessFileLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourcelessFileLoader_is_package(fullname: int) -> int:
    """Mock: determine if module is a package based on path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourcelessFileLoader_get_code(fullname: int) -> int:
    """Mock: return the code object for the module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def SourcelessFileLoader_get_source(fullname: int) -> int:
    """Mock: return None — bytecode files have no source."""
    return 0

# ── importlib.machinery — ExtensionFileLoader ────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.ExtensionFileLoader
#@ requires True
#@ ensures True
def ExtensionFileLoader(fullname: int, path: int) -> int:
    """Mock: create an ExtensionFileLoader instance — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def ExtensionFileLoader_create_module(mod_spec: int) -> int:
    """Mock: create module from spec per PEP 489."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.ExtensionFileLoader
#@ requires True
#@ ensures True
def ExtensionFileLoader_exec_module(mod_obj: int) -> int:
    """Mock: initialize the given module per PEP 489."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.ExtensionFileLoader
#@ requires True
#@ ensures True
def ExtensionFileLoader_is_package(fullname: int) -> int:
    """Mock: return True if path points to __init__."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.ExtensionFileLoader.get_code
#@ requires True
#@ ensures True
def ExtensionFileLoader_get_code(fullname: int) -> int:
    """Mock: return None — extension modules lack code objects."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.ExtensionFileLoader.get_source
#@ requires True
#@ ensures True
def ExtensionFileLoader_get_source(fullname: int) -> int:
    """Mock: return None — extension modules have no source."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def ExtensionFileLoader_get_filename(fullname: int) -> int:
    """Mock: return the path to the extension module."""
    return 0

# ── importlib.machinery — NamespaceLoader ────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def NamespaceLoader(name: int, path: int, path_finder: int) -> int:
    """Mock: create a NamespaceLoader instance — opaque."""
    return 0

# ── importlib.machinery — ModuleSpec ─────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.machinery.ModuleSpec
#@ requires True
#@ ensures True
def ModuleSpec(name: int, loader: int, origin: int, loader_state: int, is_package: int) -> int:
    """Mock: create a ModuleSpec instance — opaque."""
    return 0

# ── importlib.machinery — AppleFrameworkLoader ───────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def AppleFrameworkLoader(name: int, path: int) -> int:
    """Mock: create an AppleFrameworkLoader instance — opaque."""
    return 0

# ── importlib.util — utility functions ───────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/util.py
#@ requires True
#@ ensures True
def cache_from_source(path: int, optimization: int) -> int:
    """Mock: return PEP 3147/488 byte-compiled file path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/util.py
#@ requires True
#@ ensures True
def source_from_cache(path: int) -> int:
    """Mock: return source file path from a .pyc path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/util.py
#@ requires True
#@ ensures True
def decode_source(source_bytes: int) -> int:
    """Mock: decode source bytes to a string."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.util.resolve_name
#@ requires True
#@ ensures True
def resolve_name(name: int, package: int) -> int:
    """Mock: resolve a relative module name to absolute."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.util.find_spec
#@ requires True
#@ ensures True
def find_spec(name: int, package: int) -> int:
    """Mock: find the spec for a module."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.util.module_from_spec
#@ requires True
#@ ensures True
def module_from_spec(spec: int) -> int:
    """Mock: create a new module based on spec."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/util.py
#@ requires True
#@ ensures True
def spec_from_loader(name: int, loader: int, origin: int, is_package: int) -> int:
    """Mock: create a ModuleSpec from a loader."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.html#importlib.util.spec_from_file_location
#@ requires True
#@ ensures True
def spec_from_file_location(name: int, location: int, loader: int, submodule_search_locations: int) -> int:
    """Mock: create a ModuleSpec from a file path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/_bootstrap_external.py
#@ requires True
#@ ensures True
def source_hash(source_bytes: int) -> int:
    """Mock: return the hash of source bytes."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _incompatible_extension_module_restrictions(disable_check: int) -> int:
    """Mock: context manager to skip extension compat check."""
    return 0

# ── importlib.util — LazyLoader ──────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/util.py
#@ requires True
#@ ensures True
def LazyLoader(loader: int) -> int:
    """Mock: create a LazyLoader that defers module execution — opaque."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/__init__.py
#@ requires True
#@ ensures True
def LazyLoader_factory(loader: int) -> int:
    """Mock: return a callable that creates a lazy loader."""
    return 0

# ── importlib.resources ──────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/resources/__init__.py
#@ requires True
#@ ensures True
def files(package: int) -> int:
    """Mock: return a Traversable for the package's resources."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.resources.html#importlib.resources.as_file
#@ requires True
#@ ensures True
def as_file(traversable: int) -> int:
    """Mock: return a context manager providing a pathlib.Path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.resources.html#importlib.resources.open_binary
#@ requires True
#@ ensures True
#@ assigns \nothing
def open_binary(package: int, resource: int) -> int:
    """Mock: open a binary resource for reading."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.resources.html#importlib.resources.open_text
#@ requires True
#@ ensures True
def open_text(package: int, resource: int, encoding: int, errors: int) -> int:
    """Mock: open a text resource for reading."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.resources.html#importlib.resources.read_binary
#@ requires True
#@ ensures True
def read_binary(package: int, resource: int) -> int:
    """Mock: read and return a binary resource as bytes."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.resources.html#importlib.resources.read_text
#@ requires True
#@ ensures True
def read_text(package: int, resource: int, encoding: int, errors: int) -> int:
    """Mock: read and return a text resource as a string."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/resources/_legacy.py
#@ requires True
#@ ensures True
def path(package: int, resource: int) -> int:
    """Mock: return a context manager for a resource path."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/importlib.resources.html#importlib.resources.contents
#@ requires True
#@ ensures True
def contents(package: int) -> int:
    """Mock: return an iterable of resource names in the package."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/importlib/resources/__init__.py
#@ requires True
#@ ensures True
def is_resource(package: int, name: int) -> int:
    """Mock: return True if name is a resource in the package."""
    return 0
