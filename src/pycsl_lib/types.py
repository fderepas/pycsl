"""PyCSL mock for Python's types module.

Provides trusted stubs for dynamic type creation functions and class
constructors.  Objects returned by these functions (classes, modules,
namespaces, etc.) are modelled as opaque integers (>= 0).

Type names used only for isinstance() checks (NoneType, FunctionType,
GeneratorType, etc.) are not callable constructors and cannot be mocked
as functions — they are skipped.
"""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def new_class(name: str) -> int:
    """Mock: dynamically create a class object — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prepare_class(name: str) -> int:
    """Mock: calculate metaclass and create class namespace — opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resolve_bases(bases: int) -> int:
    """Mock: resolve MRO entries — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_original_bases(cls: int) -> int:
    """Mock: return original bases tuple — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result == gen_func
def coroutine(gen_func: int) -> int:
    """Mock: wrap generator function as coroutine — identity passthrough."""
    return gen_func

#@ \trusted
#@ ensures \result >= 0
def DynamicClassAttribute(fget: int) -> int:
    """Mock: descriptor routing attribute access — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ModuleType(name: str) -> int:
    """Mock: create a module object — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def GenericAlias(t_origin: int, t_args: int) -> int:
    """Mock: create a parameterized generic alias — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SimpleNamespace(x: int) -> int:
    """Mock: create a simple namespace object — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def MappingProxyType(mapping: int) -> int:
    """Mock: create a read-only mapping proxy — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CodeType(code: int) -> int:
    """Mock: create a code object — modelled as opaque int."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def TracebackType(tb_next: int, tb_frame: int, tb_lasti: int, tb_lineno: int) -> int:
    """Mock: create a traceback object — modelled as opaque int."""
    return 0
