"""PyCSL mock for Python's venv module — Creation of virtual environments."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def create(env_dir: int, system_site_packages: int, clear: int, __symlinks: int, with_pip: int, prompt: int, __upgrade_deps: int) -> int:
    """Mock: Create an :class:`EnvBuilder` with the given keyword arguments, and call its :meth:`~EnvBuilder.create` method with the ..."""
    return 0
