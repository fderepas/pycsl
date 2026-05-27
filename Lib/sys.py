"""PyCSL mock for Python's sys module — Access system-specific parameters and functions."""
_ = 0  # anchor

# Module-level attributes used by src/
executable = 0
path = 0
stderr = 0
stdin = 0
stdout = 0

#@ \trusted
#@ ensures \result == 0
def addaudithook(hook: int) -> int:
    """Mock: Append the callable *hook* to the list of active auditing hooks for the current (sub)interpreter. When an auditing event..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def audit(event: int) -> int:
    """Mock: .. index:: single: auditing Raise an auditing event and trigger any active auditing hooks. *event* is a string identifyi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def call_tracing(func: int, args: int) -> int:
    """Mock: Call ``func(*args)``, while tracing is enabled.  The tracing state is saved, and restored afterwards.  This is intended ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _clear_type_cache() -> int:
    """Mock: Clear the internal type cache. The type cache is used to speed up attribute and method lookups. Use the function *only* ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _clear_internal_caches() -> int:
    """Mock: Clear all internal performance-related caches. Use this function *only* to release unnecessary references and memory blo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _current_frames() -> int:
    """Mock: Return a dictionary mapping each thread's identifier to the topmost stack frame currently active in that thread at the t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _current_exceptions() -> int:
    """Mock: Return a dictionary mapping each thread's identifier to the topmost exception currently active in that thread at the tim..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def breakpointhook() -> int:
    """Mock: This hook function is called by built-in :func:`breakpoint`.  By default, it drops you into the :mod:`pdb` debugger, but..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _debugmallocstats() -> int:
    """Mock: Print low-level information to stderr about the state of CPython's memory allocator. If Python is :ref:`built in debug m..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def displayhook(value: int) -> int:
    """Mock: If *value* is not ``None``, this function prints ``repr(value)`` to ``sys.stdout``, and saves *value* in ``builtins._``...."""
    return 0

#@ \trusted
#@ ensures \result == 0
def excepthook(type_: int, value: int, traceback: int) -> int:
    """Mock: This function prints out a given traceback and exception to ``sys.stderr``. When an exception other than :exc:`SystemExi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exception() -> int:
    """Mock: This function, when called while an exception handler is executing (such as an ``except`` or ``except*`` clause), return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exc_info() -> int:
    """Mock: This function returns the old-style representation of the handled exception. If an exception ``e`` is currently handled ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exit(arg: int) -> int:
    """Mock: Raise a :exc:`SystemExit` exception, signaling an intention to exit the interpreter. The optional argument *arg* can be ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getallocatedblocks() -> int:
    """Mock: Return the number of memory blocks currently allocated by the interpreter, regardless of their size.  This function is m..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getunicodeinternedsize() -> int:
    """Mock: Return the number of unicode objects that have been interned. .. versionadded:: 3.12"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getandroidapilevel() -> int:
    """Mock: Return the build-time API level of Android as an integer. This represents the minimum version of Android this build of P..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getdefaultencoding() -> int:
    """Mock: Return ``'utf-8'``. This is the name of the default string encoding, used in methods like :meth:`str.encode`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getdlopenflags() -> int:
    """Mock: Return the current value of the flags that are used for :c:func:`dlopen` calls.  Symbolic names for the flag values can ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfilesystemencoding() -> int:
    """Mock: Get the :term:`filesystem encoding <filesystem encoding and error handler>`: the encoding used with the :term:`filesyste..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfilesystemencodeerrors() -> int:
    """Mock: Get the :term:`filesystem error handler <filesystem encoding and error handler>`: the error handler used with the :term:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_int_max_str_digits() -> int:
    """Mock: Returns the current value for the :ref:`integer string conversion length limitation <int_max_str_digits>`. See also :fun..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_lazy_imports() -> int:
    """Mock: Returns the current lazy imports mode as a string. * ``'normal'``: Only imports explicitly marked with the ``lazy`` keyw..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_lazy_imports_filter() -> int:
    """Mock: Returns the current lazy imports filter function, or ``None`` if no filter is set. The filter function is called for eve..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrefcount(object: int) -> int:
    """Mock: Return the reference count of the *object*.  The count returned is generally one higher than you might expect, because i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrecursionlimit() -> int:
    """Mock: Return the current value of the recursion limit, the maximum depth of the Python interpreter stack.  This limit prevents..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsizeof(object: int, default: int) -> int:
    """Mock: Return the size of an object in bytes. The object can be any type of object. All built-in objects will return correct re..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getswitchinterval() -> int:
    """Mock: Return the interpreter's 'thread switch interval' in seconds; see :func:`setswitchinterval`. .. versionadded:: 3.2"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _getframe(depth: int) -> int:
    """Mock: Return a frame object from the call stack.  If optional integer *depth* is given, return the frame object that many call..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _getframemodulename(depth: int) -> int:
    """Mock: Return the name of a module from the call stack.  If optional integer *depth* is given, return the module that many call..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getobjects(limit: int, type_: int) -> int:
    """Mock: This function only exists if CPython was built using the specialized configure option :option:`--with-trace-refs`. It is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getprofile() -> int:
    """Mock: .. index:: single: profile function single: profiler Get the profiler function as set by :func:`setprofile`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettrace() -> int:
    """Mock: .. index:: single: trace function single: debugger Get the trace function as set by :func:`settrace`. .. impl-detail:: T..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getwindowsversion() -> int:
    """Mock: Return a named tuple describing the Windows version currently running.  The named elements are *major*, *minor*, *build*..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_asyncgen_hooks() -> int:
    """Mock: Returns an *asyncgen_hooks* object, which is similar to a :class:`~collections.namedtuple` of the form ``(firstiter, fin..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_coroutine_origin_tracking_depth() -> int:
    """Mock: Get the current coroutine origin tracking depth, as set by :func:`set_coroutine_origin_tracking_depth`. .. versionadded:..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def intern(string: int) -> int:
    """Mock: Enter *string* in the table of 'interned' strings and return the interned string -- which is *string* itself or a copy. ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _is_gil_enabled() -> int:
    """Mock: Return :const:`True` if the :term:`GIL` is enabled and :const:`False` if it is disabled. .. versionadded:: 3.13 .. impl-..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_finalizing() -> int:
    """Mock: Return :const:`True` if the main Python interpreter is :term:`shutting down <interpreter shutdown>`. Return :const:`Fals..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def _is_immortal(op: int) -> int:
    """Mock: Return :const:`True` if the given object is :term:`immortal`, :const:`False` otherwise. .. note:: Objects that are immor..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _is_interned(string: int) -> int:
    """Mock: Return :const:`True` if the given string is 'interned', :const:`False` otherwise. .. versionadded:: 3.13 .. impl-detail:..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setdlopenflags(n: int) -> int:
    """Mock: Set the flags used by the interpreter for :c:func:`dlopen` calls, such as when the interpreter loads extension modules. ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_int_max_str_digits(maxdigits: int) -> int:
    """Mock: Set the :ref:`integer string conversion length limitation <int_max_str_digits>` used by this interpreter. See also :func..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_lazy_imports(mode: int) -> int:
    """Mock: Sets the global lazy imports mode. The *mode* parameter must be one of the following strings: * ``'normal'``: Only impor..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def set_lazy_imports_filter(filter: int) -> int:
    """Mock: Sets the lazy imports filter callback. The *filter* parameter must be a callable or ``None`` to clear the filter. The fi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setprofile(profilefunc: int) -> int:
    """Mock: .. index:: single: profile function single: profiler Set the system's profile function, which allows you to implement a ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setrecursionlimit(limit: int) -> int:
    """Mock: Set the maximum depth of the Python interpreter stack to *limit*.  This limit prevents infinite recursion from causing a..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setswitchinterval(interval: int) -> int:
    """Mock: Set the interpreter's thread switch interval (in seconds).  This floating-point value determines the ideal duration of t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def settrace(tracefunc: int) -> int:
    """Mock: .. index:: single: trace function single: debugger Set the system's trace function, which allows you to implement a Pyth..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_asyncgen_hooks(firstiter: int, finalizer: int) -> int:
    """Mock: Accepts two optional keyword arguments which are callables that accept an :term:`asynchronous generator iterator` as an ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_coroutine_origin_tracking_depth(depth: int) -> int:
    """Mock: Allows enabling or disabling coroutine origin tracking. When enabled, the ``cr_origin`` attribute on coroutine objects w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def activate_stack_trampoline(backend: int) -> int:
    """Mock: Activate the stack profiler trampoline *backend*. The only supported backend is ``'perf'``. Stack trampolines cannot be ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def deactivate_stack_trampoline() -> int:
    """Mock: Deactivate the current stack profiler trampoline backend. If no stack profiler is activated, this function has no effect..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_stack_trampoline_active() -> int:
    """Mock: Return ``True`` if a stack profiler trampoline is active. .. availability:: Linux. .. versionadded:: 3.12"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def remote_exec(pid: int, script: int) -> int:
    """Mock: Executes *script*, a file containing Python code in the remote process with the given *pid*. This function returns immed..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unraisablehook(unraisable: int) -> int:
    """Mock: Handle an unraisable exception. Called when an exception has occurred but there is no way for Python to handle it. For e..."""
    return 0
