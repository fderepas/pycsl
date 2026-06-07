"""
Python unit testing framework, based on Erich Gamma's JUnit and Kent Beck's
Smalltalk testing framework.

This module contains the core framework classes that form the basis of
specific test cases and suites (TestCase, TestSuite etc.), and also a
text-based utility class for running the tests and reporting the results
(TextTestRunner).

Note: This is a standalone reference copy. Relative subpackage imports
are stubbed since only the __init__.py is included.
"""

__all__ = ['TestResult', 'TestCase', 'IsolatedAsyncioTestCase', 'TestSuite',
           'TextTestRunner', 'TestLoader', 'FunctionTestCase', 'main',
           'defaultTestLoader', 'SkipTest', 'skip', 'skipIf', 'skipUnless',
           'expectedFailure', 'TextTestResult', 'installHandler',
           'registerResult', 'removeResult', 'removeHandler', 'addModuleCleanup',
           'enterModuleContext']

try:
    from unittest.result import TestResult
    from unittest.case import (addModuleCleanup, TestCase, FunctionTestCase,
                               SkipTest, skip, skipIf, skipUnless,
                               expectedFailure, enterModuleContext)
    from unittest.suite import BaseTestSuite, TestSuite
    from unittest.loader import TestLoader, defaultTestLoader
    from unittest.main import TestProgram, main
    from unittest.runner import TextTestRunner, TextTestResult
    from unittest.signals import installHandler, registerResult, removeResult, removeHandler
    from unittest.async_case import IsolatedAsyncioTestCase
except ImportError:
    # Stubs for standalone analysis
    class TestResult: pass
    class TestCase: pass
    class IsolatedAsyncioTestCase: pass
    class TestSuite: pass
    class TextTestRunner: pass
    class TestLoader: pass
    class FunctionTestCase: pass
    class SkipTest(Exception): pass
    def skip(reason): return lambda f: f
    def skipIf(condition, reason): return lambda f: f
    def skipUnless(condition, reason): return lambda f: f
    def expectedFailure(f): return f
    class TextTestResult: pass
    def installHandler(): pass
    def registerResult(result): pass
    def removeResult(result): pass
    def removeHandler(): pass
    def addModuleCleanup(f, *a, **kw): pass
    def enterModuleContext(cm): pass
    def main(**kwargs): pass
    defaultTestLoader = TestLoader()
