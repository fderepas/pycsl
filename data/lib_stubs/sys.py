"""PyCSL mock for Python's sys module.

Provides trusted stubs for system-specific parameters and functions.
Side-effect functions ensure result == 0; functions returning sizes,
counts, or objects ensure result >= 0.
"""
_ = 0  # anchor

# ── Data attributes: version and build info ─────────────────────────
version = 0
version_info = 0
api_version = 0
hexversion = 0
implementation = 0
copyright = 0
abi_info = 0
abiflags = 0
winver = 0

# ── Data attributes: interpreter settings ───────────────────────────
flags = 0
float_info = 0
float_repr_style = 0
hash_info = 0
int_info = 0
thread_info = 0
maxsize = 0
maxunicode = 0
byteorder = 0
dont_write_bytecode = 0
pycache_prefix = 0
tracebacklimit = 0
dllhandle = 0
_xoptions = 0
_emscripten_info = 0
_jit = 0
monitoring = 0
platlibdir = 0

# ── Data attributes: path and modules ───────────────────────────────
argv = 0
orig_argv = 0
path = 0
path_hooks = 0
path_importer_cache = 0
meta_path = 0
modules = 0
builtin_module_names = 0
stdlib_module_names = 0
executable = 0
exec_prefix = 0
base_exec_prefix = 0
prefix = 0
base_prefix = 0
platform = 0
warnoptions = 0

# ── Data attributes: I/O streams ────────────────────────────────────
stdin = 0
stdout = 0
stderr = 0
__stdin__ = 0
__stdout__ = 0
__stderr__ = 0

# ── Data attributes: interactive and hooks ──────────────────────────
ps1 = 0
ps2 = 0
__interactivehook__ = 0
__breakpointhook__ = 0
__displayhook__ = 0
__excepthook__ = 0
__unraisablehook__ = 0

# ── Data attributes: exception state ────────────────────────────────
last_exc = 0
last_type = 0
last_value = 0
last_traceback = 0

# ── Process control ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def exit(arg: int = 0) -> int:
    """Mock: raise SystemExit to exit the interpreter."""
    return 0

# ── Exception handling ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def exc_info() -> int:
    """Mock: return current exception info tuple."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def exception() -> int:
    """Mock: return current handled exception instance."""
    return 0

#@ \trusted
#@ ensures \result == 0
def excepthook(type: int, value: int, traceback: int) -> int:
    """Mock: print exception and traceback to stderr."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unraisablehook(unraisable: int) -> int:
    """Mock: handle an unraisable exception."""
    return 0

# ── Display and breakpoint hooks ────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def displayhook(value: int) -> int:
    """Mock: display the result of an expression."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def breakpointhook(arg: int = 0) -> int:
    """Mock: hook called by built-in breakpoint()."""
    return 0

# ── Auditing ────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def addaudithook(hook: int) -> int:
    """Mock: append callable to active auditing hooks."""
    return 0

#@ \trusted
#@ ensures \result == 0
def audit(event: int, args: int = 0) -> int:
    """Mock: raise an auditing event."""
    return 0

# ── Encoding ────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getdefaultencoding() -> int:
    """Mock: return current default string encoding."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfilesystemencoding() -> int:
    """Mock: return filesystem encoding."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfilesystemencodeerrors() -> int:
    """Mock: return filesystem encoding error mode."""
    return 0

# ── Recursion and call stack ────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getrecursionlimit() -> int:
    """Mock: return maximum recursion depth."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setrecursionlimit(limit: int) -> int:
    """Mock: set maximum recursion depth."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _getframe(depth: int = 0) -> int:
    """Mock: return a frame object from the call stack."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _getframemodulename(depth: int = 0) -> int:
    """Mock: return module name of a frame in the call stack."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _current_frames() -> int:
    """Mock: return dict mapping thread id to topmost frame."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _current_exceptions() -> int:
    """Mock: return dict mapping thread id to current exception."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def call_tracing(func: int, args: int) -> int:
    """Mock: call func(*args) while tracing is enabled."""
    return 0

# ── Memory and object introspection ─────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getsizeof(obj: int, default: int = 0) -> int:
    """Mock: return size of object in bytes."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getrefcount(obj: int) -> int:
    """Mock: return reference count of object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getallocatedblocks() -> int:
    """Mock: return number of currently allocated memory blocks."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getunicodeinternedsize() -> int:
    """Mock: return number of unicode objects in the interned dict."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getobjects(limit: int, type: int = 0) -> int:
    """Mock: return list of objects tracked by the garbage collector."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _is_immortal(op: int) -> int:
    """Mock: return True if the given object is immortal."""
    return 0

# ── Interning ───────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def intern(string: int) -> int:
    """Mock: intern a string in the internal table."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def _is_interned(string: int) -> int:
    """Mock: return True if string is interned."""
    return 0

# ── Tracing and profiling ───────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def settrace(tracefunc: int) -> int:
    """Mock: set the system trace function."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gettrace() -> int:
    """Mock: return the current trace function."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setprofile(profilefunc: int) -> int:
    """Mock: set the system profile function."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getprofile() -> int:
    """Mock: return the current profile function."""
    return 0

# ── Thread switch interval ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getswitchinterval() -> int:
    """Mock: return the thread switch interval."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setswitchinterval(interval: int) -> int:
    """Mock: set the thread switch interval."""
    return 0

# ── Dynamic linker flags ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getdlopenflags() -> int:
    """Mock: return current dlopen flags."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setdlopenflags(n: int) -> int:
    """Mock: set dlopen flags for extension module loading."""
    return 0

# ── Integer string conversion limits ────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def get_int_max_str_digits() -> int:
    """Mock: return integer string conversion length limitation."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_int_max_str_digits(maxdigits: int) -> int:
    """Mock: set integer string conversion length limitation."""
    return 0

# ── Lazy imports ────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def get_lazy_imports() -> int:
    """Mock: return the current lazy imports mode."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_lazy_imports_filter() -> int:
    """Mock: return the current lazy imports filter callback."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_lazy_imports(mode: int) -> int:
    """Mock: set the global lazy imports mode."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_lazy_imports_filter(filter: int) -> int:
    """Mock: set the lazy imports filter callback."""
    return 0

# ── Async generator hooks ───────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def get_asyncgen_hooks() -> int:
    """Mock: return current async generator hooks."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_asyncgen_hooks(firstiter: int = 0, finalizer: int = 0) -> int:
    """Mock: set async generator hooks."""
    return 0

# ── Coroutine origin tracking ───────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def get_coroutine_origin_tracking_depth() -> int:
    """Mock: return coroutine origin tracking depth."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_coroutine_origin_tracking_depth(depth: int) -> int:
    """Mock: set coroutine origin tracking depth."""
    return 0

# ── Stack trampoline (perf profiling) ───────────────────────────────

#@ \trusted
#@ ensures \result == 0
def activate_stack_trampoline(backend: int) -> int:
    """Mock: activate stack profiler trampoline."""
    return 0

#@ \trusted
#@ ensures \result == 0
def deactivate_stack_trampoline() -> int:
    """Mock: deactivate current stack profiler trampoline."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def is_stack_trampoline_active() -> int:
    """Mock: return True if stack profiler trampoline is active."""
    return 0

# ── GIL and finalizing ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def _is_gil_enabled() -> int:
    """Mock: return True if the GIL is enabled."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def is_finalizing() -> int:
    """Mock: return True if the interpreter is shutting down."""
    return 0

# ── Windows version ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getwindowsversion() -> int:
    """Mock: return Windows version info as named tuple."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getandroidapilevel() -> int:
    """Mock: return Android API level as integer."""
    return 0

# ── Internal caches ─────────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def _clear_type_cache() -> int:
    """Mock: clear the internal type lookup cache."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _clear_internal_caches() -> int:
    """Mock: clear all internal performance caches."""
    return 0

#@ \trusted
#@ ensures \result == 0
def _debugmallocstats() -> int:
    """Mock: print malloc stats to stderr."""
    return 0

# ── Remote execution ────────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def remote_exec(pid: int, script: int) -> int:
    """Mock: execute script in a remote Python process."""
    return 0
