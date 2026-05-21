"""PyCSL mock for Python's importlib.metadata module — Accessing package metadata."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def entry_points() -> int:
    """Mock: Returns a :class:`EntryPoints` instance describing entry points for the current environment. Any given keyword parameter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def metadata(distribution_name: int) -> int:
    """Mock: Return the distribution metadata corresponding to the named distribution package as a :class:`PackageMetadata` instance...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def version(distribution_name: int) -> int:
    """Mock: Return the installed distribution package `version <https://packaging.python.org/en/latest/specifications/core-metadata/..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def files(distribution_name: int) -> int:
    """Mock: Return the full set of files contained within the named distribution package as :class:`PackagePath` instances. Raises :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def requires(distribution_name: int) -> int:
    """Mock: Return the declared dependency specifiers for the named distribution package. Raises :exc:`PackageNotFoundError` if the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def packages_distributions() -> int:
    """Mock: Return a mapping from the top level module and import package names found via :data:`sys.meta_path` to the names of the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def distribution(distribution_name: int) -> int:
    """Mock: Return a :class:`Distribution` instance describing the named distribution package. Raises :exc:`PackageNotFoundError` if..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def distributions() -> int:
    """Mock: Returns an iterable of :class:`Distribution` instances for all packages. The *kwargs* argument may contain either a keyw..."""
    return 0
