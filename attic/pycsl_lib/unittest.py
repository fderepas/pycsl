"""PyCSL mock for Python's unittest module — Unit testing framework for Python."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def main(module_: int, defaultTest: int, argv: int, testRunner: int, __testLoader: int, exit: int, verbosity: int) -> int:
    """Mock: A command-line program that loads a set of tests from *module* and runs them; this is primarily for making test modules ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def addModuleCleanup(function_: int) -> int:
    """Mock: Add a function to be called after :func:`tearDownModule` to cleanup resources used during the test class. Functions will..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def enterModuleContext(cm: int) -> int:
    """Mock: Enter the supplied :term:`context manager`.  If successful, also add its :meth:`~object.__exit__` method as a cleanup fu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def doModuleCleanups() -> int:
    """Mock: This function is called unconditionally after :func:`tearDownModule`, or after :func:`setUpModule` if :func:`setUpModule..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def installHandler() -> int:
    """Mock: Install the control-c handler. When a :const:`signal.SIGINT` is received (usually in response to the user pressing contr..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def registerResult(result_: int) -> int:
    """Mock: Register a :class:`TestResult` object for control-c handling. Registering a result stores a weak reference to it, so it ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def removeResult(result_: int) -> int:
    """Mock: Remove a registered result. Once a result has been removed then :meth:`~TestResult.stop` will no longer be called on tha..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def removeHandler(function_: int) -> int:
    """Mock: When called without arguments this function removes the control-c handler if it has been installed. This function can al..."""
    return 0
