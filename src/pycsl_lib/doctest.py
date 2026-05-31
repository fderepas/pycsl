"""PyCSL mock for Python's doctest module — Test pieces of code within docstrings."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def register_optionflag(name: int) -> int:
    """Mock: Create a new option flag with a given name, and return the new flag's integer value.  :func:`register_optionflag` can be..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def testfile(filename: int, module_relative: int, name: int, package: int, globs: int, verbose: int, report: int) -> int:
    """Mock: All arguments except *filename* are optional, and should be specified in keyword form. Test examples in the file named *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def testmod(m: int, name: int, globs: int, verbose: int, report: int, optionflags: int, extraglobs: int) -> int:
    """Mock: All arguments are optional, and all except for *m* should be specified in keyword form. Test examples in docstrings in f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def run_docstring_examples(f: int, globs: int, verbose: int, name: int, compileflags: int, optionflags: int) -> int:
    """Mock: Test examples associated with object *f*; for example, *f* may be a string, a module, a function, or a class object. A s..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def DocFileSuite(module_relative: int, package: int, setUp: int, tearDown: int, globs: int, optionflags: int, parser: int) -> int:
    """Mock: Convert doctest tests from one or more text files to a :class:`unittest.TestSuite`. The returned :class:`unittest.TestSu..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def DocTestSuite(module_: int, globs: int, extraglobs: int, test_finder: int, setUp: int, tearDown: int, optionflags: int) -> int:
    """Mock: Convert doctest tests for a module to a :class:`unittest.TestSuite`. The returned :class:`unittest.TestSuite` is to be r..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_unittest_reportflags(flags: int) -> int:
    """Mock: Set the :mod:`!doctest` reporting flags to use. Argument *flags* takes the :ref:`bitwise OR <bitwise>` of option flags. ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def script_from_examples(s: int) -> int:
    """Mock: Convert text with examples to a script. Argument *s* is a string containing doctest examples.  The string is converted t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def testsource(module_: int, name: int) -> int:
    """Mock: Convert the doctest for an object to a script. Argument *module* is a module object, or dotted name of a module, contain..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def debug(module_: int, name: int, pm: int) -> int:
    """Mock: Debug the doctests for an object. The *module* and *name* arguments are the same as for function :func:`testsource` abov..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def debug_src(src: int, pm: int, globs: int) -> int:
    """Mock: Debug the doctests in a string. This is like function :func:`debug` above, except that a string containing doctest examp..."""
    return 0
