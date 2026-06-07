# Pure model for unittest — testing framework
# Models TestResult as pass/fail counters.

""" # pycsl"""


#@ class invariant self._tests >= 0
#@ class invariant self._failures >= 0
#@ class invariant self._errors >= 0
class TestResult:
    """Abstract test result tracking outcomes."""

    #@ ensures self._tests == 0
    #@ ensures self._failures == 0
    #@ ensures self._errors == 0
    def __init__(self) -> None:
        self._tests: int = 0
        self._failures: int = 0
        self._errors: int = 0

    #@ ensures self._tests == \old(self._tests) + 1
    #@ assigns self._tests
    def addSuccess(self, test: int) -> None:
        """Record a test success."""
        self._tests = self._tests + 1

    #@ ensures self._tests == \old(self._tests) + 1
    #@ ensures self._failures == \old(self._failures) + 1
    #@ assigns self._tests, self._failures
    def addFailure(self, test: int) -> None:
        """Record a test failure."""
        self._tests = self._tests + 1
        self._failures = self._failures + 1

    #@ ensures self._tests == \old(self._tests) + 1
    #@ ensures self._errors == \old(self._errors) + 1
    #@ assigns self._tests, self._errors
    def addError(self, test: int) -> None:
        """Record a test error."""
        self._tests = self._tests + 1
        self._errors = self._errors + 1

    #@ ensures \result == self._tests
    def testsRun(self) -> int:
        """Return number of tests run."""
        return self._tests

    #@ ensures \result >= 0
    #@ ensures \result <= 1
    def wasSuccessful(self) -> int:
        """Return 1 if no failures or errors, else 0."""
        if self._failures == 0 and self._errors == 0:
            return 1
        return 0
