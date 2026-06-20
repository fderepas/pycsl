"""PyCSL mock for Python's unittest.mock module — Mock object library."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def patch(target: int, new: int, spec: int, create: int, spec_set: int, autospec: int, new_callable: int) -> int:
    """Mock: :func:`patch` acts as a function decorator, class decorator or a context manager. Inside the body of the function or wit..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def call() -> int:
    """Mock: :func:`call` is a helper object for making simpler assertions, for comparing with :attr:`~Mock.call_args`, :attr:`~Mock...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_autospec(spec: int, spec_set: int, instance: int) -> int:
    """Mock: Create a mock object using another object as a spec. Attributes on the mock will use the corresponding attribute on the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mock_open(mock: int, read_data: int) -> int:
    """Mock: A helper function to create a mock to replace the use of :func:`open`. It works for :func:`open` called directly or used..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def seal(mock: int) -> int:
    """Mock: Seal will disable the automatic creation of mocks when accessing an attribute of the mock being sealed or any of its att..."""
    return 0
