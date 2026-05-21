"""PyCSL mock for Python's test module — Regression tests package containing the testing suite for Python."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def busy_retry(timeout: int, err_msg: int, error: int) -> int:
    """Mock: Run the loop body until ``break`` stops the loop. After *timeout* seconds, raise an :exc:`AssertionError` if *error* is ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sleeping_retry(timeout: int, err_msg: int, init_delay: int, max_delay: int, error: int) -> int:
    """Mock: Wait strategy that applies exponential backoff. Run the loop body until ``break`` stops the loop. Sleep at each loop ite..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_resource_enabled(resource: int) -> int:
    """Mock: Return ``True`` if *resource* is enabled and available. The list of available resources is only set when :mod:`test.regr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_resource_value(resource: int) -> int:
    """Mock: Return the value specified for *resource* (as :samp:`-u {resource}={value}`). Return ``None`` if *resource* is disabled ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def python_is_optimized() -> int:
    """Mock: Return ``True`` if Python was not built with ``-O0`` or ``-Og``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def with_pymalloc() -> int:
    """Mock: Return :const:`_testcapi.WITH_PYMALLOC`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def requires(resource: int, msg: int) -> int:
    """Mock: Raise :exc:`ResourceDenied` if *resource* is not available. *msg* is the argument to :exc:`ResourceDenied` if it is rais..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sortdict(dict: int) -> int:
    """Mock: Return a repr of *dict* with keys sorted."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def findfile(filename: int, subdir: int) -> int:
    """Mock: Return the path to the file named *filename*. If no match is found *filename* is returned. This does not equal a failure..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_pagesize() -> int:
    """Mock: Get size of a page in bytes. .. versionadded:: 3.12"""
    return 0

#@ \trusted
#@ ensures \result == 0
def setswitchinterval(interval: int) -> int:
    """Mock: Set the :func:`sys.setswitchinterval` to the given *interval*.  Defines a minimum interval for Android systems to preven..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_impl_detail() -> int:
    """Mock: Use this check to guard CPython's implementation-specific tests or to run them only on the implementations guarded by th..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_memlimit(limit: int) -> int:
    """Mock: Set the values for :data:`max_memuse` and :data:`real_max_memuse` for big memory tests."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def record_original_stdout(stdout: int) -> int:
    """Mock: Store the value from *stdout*.  It is meant to hold the stdout at the time the regrtest began."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_original_stdout() -> int:
    """Mock: Return the original stdout set by :func:`record_original_stdout` or ``sys.stdout`` if it's not set."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def args_from_interpreter_flags() -> int:
    """Mock: Return a list of command line arguments reproducing the current settings in ``sys.flags`` and ``sys.warnoptions``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def optim_args_from_interpreter_flags() -> int:
    """Mock: Return a list of command line arguments reproducing the current optimization settings in ``sys.flags``."""
    return 0

#@ \trusted
#@ ensures \result == 0
def captured_stdin() -> int:
    """Mock: A context managers that temporarily replaces the named stream with :class:`io.StringIO` object. Example use with output ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def disable_faulthandler() -> int:
    """Mock: A context manager that temporary disables :mod:`faulthandler`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gc_collect() -> int:
    """Mock: Force as many objects as possible to be collected.  This is needed because timely deallocation is not guaranteed by the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def disable_gc() -> int:
    """Mock: A context manager that disables the garbage collector on entry. On exit, the garbage collector is restored to its prior ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def swap_attr(obj: int, attr: int, new_val: int) -> int:
    """Mock: Context manager to swap out an attribute with a new object. Usage:: with swap_attr(obj, 'attr', 5): ... This will set ``..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def swap_item(obj: int, attr: int, new_val: int) -> int:
    """Mock: Context manager to swap out an item with a new object. Usage:: with swap_item(obj, 'item', 5): ... This will set ``obj['..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def flush_std_streams() -> int:
    """Mock: Call the ``flush()`` method on :data:`sys.stdout` and then on :data:`sys.stderr`. It can be used to make sure that the l..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def print_warning(msg: int) -> int:
    """Mock: Print a warning into :data:`sys.__stderr__`. Format the message as: ``f'Warning -- {msg}'``. If *msg* is made of multipl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wait_process(pid: int, exitcode: int, timeout: int) -> int:
    """Mock: Wait until process *pid* completes and check that the process exit code is *exitcode*. Raise an :exc:`AssertionError` if..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def calcobjsize(fmt: int) -> int:
    """Mock: Return the size of the :c:type:`PyObject` whose structure members are defined by *fmt*. The returned value includes the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def calcvobjsize(fmt: int) -> int:
    """Mock: Return the size of the :c:type:`PyVarObject` whose structure members are defined by *fmt*. The returned value includes t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def checksizeof(test: int, o: int, size: int) -> int:
    """Mock: For testcase *test*, assert that the ``sys.getsizeof`` for *o* plus the GC header size equals *size*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def system_must_validate_cert(f: int) -> int:
    """Mock: A decorator that skips the decorated test on TLS certification validation failures."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def linked_to_musl() -> int:
    """Mock: Return ``False`` if there is no evidence the interpreter was compiled with ``musl``, otherwise return a version triple, ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_syntax_error(testcase: int, statement: int, errtext: int, lineno: int, offset: int) -> int:
    """Mock: Test for syntax errors in *statement* by attempting to compile *statement*. *testcase* is the :mod:`unittest` instance f..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open_urlresource(url: int) -> int:
    """Mock: Open *url*.  If open fails, raises :exc:`TestFailed`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reap_children() -> int:
    """Mock: Use this at the end of ``test_main`` whenever sub-processes are started. This will help ensure that no extra children (z..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_attribute(obj: int, name: int) -> int:
    """Mock: Get an attribute, raising :exc:`unittest.SkipTest` if :exc:`AttributeError` is raised."""
    return 0

#@ \trusted
#@ ensures \result == 0
def catch_unraisable_exception() -> int:
    """Mock: Context manager catching unraisable exception using :func:`sys.unraisablehook`. Storing the exception value (``cm.unrais..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def load_package_tests(pkg_dir: int, loader: int, standard_tests: int, pattern: int) -> int:
    """Mock: Generic implementation of the :mod:`unittest` ``load_tests`` protocol for use in test packages.  *pkg_dir* is the root d..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def detect_api_mismatch(ref_api: int, other_api: int, ignore: int) -> int:
    """Mock: Returns the set of attributes, functions or methods of *ref_api* not found on *other_api*, except for a defined list of ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def patch(test_instance: int, object_to_patch: int, attr_name: int, new_value: int) -> int:
    """Mock: Override *object_to_patch.attr_name* with *new_value*.  Also add cleanup procedure to *test_instance* to restore *object..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def run_in_subinterp(code: int) -> int:
    """Mock: Run *code* in subinterpreter.  Raise :exc:`unittest.SkipTest` if :mod:`tracemalloc` is enabled."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_free_after_iterating(test: int, iter: int, cls: int, args: int) -> int:
    """Mock: Assert instances of *cls* are deallocated after iterating."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def missing_compiler_executable(cmd_names: int) -> int:
    """Mock: Check for the existence of the compiler executables whose names are listed in *cmd_names* or all the compiler executable..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def check__all__(test_case: int, module_: int, name_of_module: int, extra: int, not_exported: int) -> int:
    """Mock: Assert that the ``__all__`` variable of *module* contains all public names. The module's public names (its API) are dete..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def skip_if_broken_multiprocessing_synchronize() -> int:
    """Mock: Skip tests if the :mod:`multiprocessing.synchronize` module is missing, if there is no available semaphore implementatio..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_disallow_instantiation(test_case: int, tp: int) -> int:
    """Mock: Assert that type *tp* cannot be instantiated using *args* and *kwds*. .. versionadded:: 3.10"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def adjust_int_max_str_digits(max_digits: int) -> int:
    """Mock: This function returns a context manager that will change the global :func:`sys.set_int_max_str_digits` setting for the d..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def find_unused_port(family: int, socktype: int) -> int:
    """Mock: Returns an unused port that should be suitable for binding.  This is achieved by creating a temporary socket with the sa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bind_port(sock: int, host: int) -> int:
    """Mock: Bind the socket to a free port and return the port number.  Relies on ephemeral ports in order to ensure we are using an..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bind_unix_socket(sock: int, addr: int) -> int:
    """Mock: Bind a Unix socket, raising :exc:`unittest.SkipTest` if :exc:`PermissionError` is raised."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def transient_internet(resource_name: int, timeout: int, errnos: int) -> int:
    """Mock: A context manager that raises :exc:`~test.support.ResourceDenied` when various issues with the internet connection manif..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def interpreter_requires_environment() -> int:
    """Mock: Return ``True`` if ``sys.executable interpreter`` requires environment variables in order to be able to run at all. This..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def run_python_until_end() -> int:
    """Mock: Set up the environment based on *env_vars* for running the interpreter in a subprocess.  The values can include ``__isol..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def assert_python_ok() -> int:
    """Mock: Assert that running the interpreter with *args* and optional environment variables *env_vars* succeeds (``rc == 0``) and..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def assert_python_failure() -> int:
    """Mock: Assert that running the interpreter with *args* and optional environment variables *env_vars* fails (``rc != 0``) and re..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def spawn_python(stdout: int, stderr: int) -> int:
    """Mock: Run a Python subprocess with the given arguments. *kw* is extra keyword args to pass to :func:`subprocess.Popen`. Return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def kill_python(p: int) -> int:
    """Mock: Run the given :class:`subprocess.Popen` process until completion and return stdout."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_script(script_dir: int, script_basename: int, source: int, omit_suffix: int) -> int:
    """Mock: Create script containing *source* in path *script_dir* and *script_basename*. If *omit_suffix* is ``False``, append ``.p..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_zip_script(zip_dir: int, zip_basename: int, script_name: int, name_in_zip: int) -> int:
    """Mock: Create zip file at *zip_dir* and *zip_basename* with extension ``zip`` which contains the files in *script_name*. *name_..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_pkg(pkg_dir: int, init_source: int) -> int:
    """Mock: Create a directory named *pkg_dir* containing an ``__init__`` file with *init_source* as its contents."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_zip_pkg(zip_dir: int, zip_basename: int, pkg_name: int, script_basename: int, __source: int, depth: int, compiled: int) -> int:
    """Mock: Create a zip package directory with a path of *zip_dir* and *zip_basename* containing an empty ``__init__`` file and a f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def join_thread(thread: int, timeout: int) -> int:
    """Mock: Join a *thread* within *timeout*.  Raise an :exc:`AssertionError` if thread is still alive after *timeout* seconds."""
    return 0

#@ \trusted
#@ ensures \result == 0
def start_threads(threads: int, unlock: int) -> int:
    """Mock: Context manager to start *threads*, which is a sequence of threads. *unlock* is a function called after the threads are ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def threading_cleanup() -> int:
    """Mock: Cleanup up threads not specified in *original_values*.  Designed to emit a warning if a test leaves running threads in t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def threading_setup() -> int:
    """Mock: Return current thread count and copy of dangling threads."""
    return 0

#@ \trusted
#@ ensures \result == 0
def wait_threads_exit(timeout: int) -> int:
    """Mock: Context manager to wait until all threads created in the ``with`` statement exit."""
    return 0

#@ \trusted
#@ ensures \result == 0
def catch_threading_exception() -> int:
    """Mock: Context manager catching :class:`threading.Thread` exception using :func:`threading.excepthook`. Attributes set when an ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def run_concurrently(worker_func: int, nthreads: int, args: int, kwargs: int) -> int:
    """Mock: Run the worker function concurrently in multiple threads. Re-raises an exception if any thread raises one, after all thr..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def can_symlink() -> int:
    """Mock: Return ``True`` if the OS supports symbolic links, ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def can_xattr() -> int:
    """Mock: Return ``True`` if the OS supports xattr, ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def change_cwd(path: int, quiet: int) -> int:
    """Mock: A context manager that temporarily changes the current working directory to *path* and yields the directory. If *quiet* ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_empty_file(filename: int) -> int:
    """Mock: Create an empty file with *filename*.  If it already exists, truncate it."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fd_count() -> int:
    """Mock: Count the number of open file descriptors."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def fs_is_case_insensitive(directory: int) -> int:
    """Mock: Return ``True`` if the file system for *directory* is case-insensitive."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_bad_fd() -> int:
    """Mock: Create an invalid file descriptor by opening and closing a temporary file, and returning its descriptor."""
    return 0

#@ \trusted
#@ ensures \result == 0
def rmdir(filename: int) -> int:
    """Mock: Call :func:`os.rmdir` on *filename*.  On Windows platforms, this is wrapped with a wait loop that checks for the existen..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def rmtree(path: int) -> int:
    """Mock: Call :func:`shutil.rmtree` on *path* or call :func:`os.lstat` and :func:`os.rmdir` to remove a path and its contents.  A..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def temp_cwd(name: int, quiet: int) -> int:
    """Mock: A context manager that temporarily creates a new directory and changes the current working directory (CWD). The context ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def temp_dir(path: int, quiet: int) -> int:
    """Mock: A context manager that creates a temporary directory at *path* and yields the directory. If *path* is ``None``, the temp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def temp_umask(umask: int) -> int:
    """Mock: A context manager that temporarily sets the process umask."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unlink(filename: int) -> int:
    """Mock: Call :func:`os.unlink` on *filename*.  As with :func:`rmdir`, on Windows platforms, this is wrapped with a wait loop tha..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def forget(module_name: int) -> int:
    """Mock: Remove the module named *module_name* from ``sys.modules`` and delete any byte-compiled files of the module."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def import_fresh_module(name: int, fresh: int, blocked: int, deprecated: int) -> int:
    """Mock: This function imports and returns a fresh copy of the named Python module by removing the named module from ``sys.module..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def import_module(name: int, deprecated: int, required_on: int) -> int:
    """Mock: This function imports and returns the named module. Unlike a normal import, this function raises :exc:`unittest.SkipTest..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def modules_setup() -> int:
    """Mock: Return a copy of :data:`sys.modules`."""
    return 0

#@ \trusted
#@ ensures \result == 0
def modules_cleanup(oldmodules: int) -> int:
    """Mock: Remove modules except for *oldmodules* and ``encodings`` in order to preserve internal cache."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unload(name: int) -> int:
    """Mock: Delete *name* from ``sys.modules``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_legacy_pyc(source: int) -> int:
    """Mock: Move a :pep:`3147`/:pep:`488` pyc file to its legacy pyc location and return the file system path to the legacy pyc file..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ignore_warnings(category: int) -> int:
    """Mock: Suppress warnings that are instances of *category*, which must be :exc:`Warning` or a subclass. Roughly equivalent to :f..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def check_no_resource_warning(testcase: int) -> int:
    """Mock: Context manager to check that no :exc:`ResourceWarning` was raised.  You must remove the object which may emit :exc:`Res..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_syntax_warning(testcase: int, statement: int, errtext: int, lineno: int, offset: int) -> int:
    """Mock: Test for syntax warning in *statement* by attempting to compile *statement*. Test also that the :exc:`SyntaxWarning` is ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_warnings(quiet: int) -> int:
    """Mock: A convenience wrapper for :func:`warnings.catch_warnings` that makes it easier to test that a warning was correctly rais..."""
    return 0
