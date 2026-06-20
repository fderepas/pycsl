"""PyCSL mock for Python's inspect module — Extract information and source code from live objects."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def getmembers(object: int, predicate_: int) -> int:
    """Mock: Return all the members of an object in a list of ``(name, value)`` pairs sorted by name. If the optional *predicate* arg..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getmembers_static(object: int, predicate_: int) -> int:
    """Mock: Return all the members of an object in a list of ``(name, value)`` pairs sorted by name without triggering dynamic looku..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getmodulename(path: int) -> int:
    """Mock: Return the name of the module named by the file *path*, without including the names of enclosing packages. The file exte..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismodule(object: int) -> int:
    """Mock: Return ``True`` if the object is a module."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isclass(object: int) -> int:
    """Mock: Return ``True`` if the object is a class, whether built-in or created in Python code. This function returns ``False`` fo..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismethod(object: int) -> int:
    """Mock: Return ``True`` if the object is a bound method written in Python."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ispackage(object: int) -> int:
    """Mock: Return ``True`` if the object is a :term:`package`. .. versionadded:: 3.14"""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isfunction(object: int) -> int:
    """Mock: Return ``True`` if the object is a Python function, which includes functions created by a :term:`lambda` expression."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isgeneratorfunction(object: int) -> int:
    """Mock: Return ``True`` if the object is a Python generator function. .. versionchanged:: 3.8 Functions wrapped in :func:`functo..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isgenerator(object: int) -> int:
    """Mock: Return ``True`` if the object is a generator."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def iscoroutinefunction(object: int) -> int:
    """Mock: Return ``True`` if the object is a :term:`coroutine function` (a function defined with an :keyword:`async def` syntax), ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def markcoroutinefunction(func: int) -> int:
    """Mock: Decorator to mark a callable as a :term:`coroutine function` if it would not otherwise be detected by :func:`iscoroutine..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def iscoroutine(object: int) -> int:
    """Mock: Return ``True`` if the object is a :term:`coroutine` created by an :keyword:`async def` function. .. versionadded:: 3.5"""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isawaitable(object: int) -> int:
    """Mock: Return ``True`` if the object can be used in :keyword:`await` expression. Can also be used to distinguish generator-base..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isasyncgenfunction(object: int) -> int:
    """Mock: Return ``True`` if the object is an :term:`asynchronous generator` function, for example: .. doctest:: >>> async def age..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isasyncgen(object: int) -> int:
    """Mock: Return ``True`` if the object is an :term:`asynchronous generator iterator` created by an :term:`asynchronous generator`..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def istraceback(object: int) -> int:
    """Mock: Return ``True`` if the object is a traceback."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isframe(object: int) -> int:
    """Mock: Return ``True`` if the object is a frame."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def iscode(object: int) -> int:
    """Mock: Return ``True`` if the object is a code."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isbuiltin(object: int) -> int:
    """Mock: Return ``True`` if the object is a built-in function or a bound built-in method."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismethodwrapper(object: int) -> int:
    """Mock: Return ``True`` if the type of object is a :class:`~types.MethodWrapperType`. These are instances of :class:`~types.Meth..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isroutine(object: int) -> int:
    """Mock: Return ``True`` if the object is a user-defined or built-in function or method."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isabstract(object: int) -> int:
    """Mock: Return ``True`` if the object is an abstract base class."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismethoddescriptor(object: int) -> int:
    """Mock: Return ``True`` if the object is a method descriptor, but not if :func:`ismethod`, :func:`isclass`, :func:`isfunction` o..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isdatadescriptor(object: int) -> int:
    """Mock: Return ``True`` if the object is a data descriptor. Data descriptors have a :attr:`~object.__set__` or a :attr:`~object...."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isgetsetdescriptor(object: int) -> int:
    """Mock: Return ``True`` if the object is a getset descriptor. .. impl-detail:: getsets are attributes defined in extension modul..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def ismemberdescriptor(object: int) -> int:
    """Mock: Return ``True`` if the object is a member descriptor. .. impl-detail:: Member descriptors are attributes defined in exte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getdoc(object: int, inherit_class_doc: int, fallback_to_class_doc: int) -> int:
    """Mock: Get the documentation string for an object, cleaned up with :func:`cleandoc`. If the documentation string for an object ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getcomments(object: int) -> int:
    """Mock: Return in a single string any lines of comments immediately preceding the object's source code (for a class, function, o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfile(object: int) -> int:
    """Mock: Return the name of the (text or binary) file in which an object was defined. This will fail with a :exc:`TypeError` if t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getmodule(object: int) -> int:
    """Mock: Try to guess which module an object was defined in. Return ``None`` if the module cannot be determined."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsourcefile(object: int) -> int:
    """Mock: Return the name of the Python source file in which an object was defined or ``None`` if no way can be identified to get ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsourcelines(object: int) -> int:
    """Mock: Return a list of source lines and starting line number for an object. The argument may be a module, class, method, funct..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsource(object: int) -> int:
    """Mock: Return the text of the source code for an object. The argument may be a module, class, method, function, traceback, fram..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cleandoc(doc: int) -> int:
    """Mock: Clean up indentation from docstrings that are indented to line up with blocks of code. All leading whitespace is removed..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def signature(callable: int, follow_wrapped: int, globals: int, locals: int, eval_str: int, annotation_format: int) -> int:
    """Mock: Return a :class:`Signature` object for the given *callable*: .. doctest:: >>> from inspect import signature >>> def foo(..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getclasstree(classes: int, unique: int) -> int:
    """Mock: Arrange the given list of classes into a hierarchy of nested lists. Where a nested list appears, it contains classes der..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getfullargspec(func: int, annotation_format: int) -> int:
    """Mock: Get the names and default values of a Python function's parameters.  A :term:`named tuple` is returned: ``FullArgSpec(ar..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getargvalues(frame: int) -> int:
    """Mock: Get information about arguments passed into a particular frame.  A :term:`named tuple` ``ArgInfo(args, varargs, keywords..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def formatargvalues(args: int, varargs: int, varkw: int, locals: int, formatarg: int, formatvarargs: int, formatvarkw: int) -> int:
    """Mock: Format a pretty argument spec from the four values returned by :func:`getargvalues`.  The format\* arguments are the cor..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getmro(cls: int) -> int:
    """Mock: Return a tuple of class cls's base classes, including cls, in method resolution order.  No class appears more than once ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getcallargs(func: int) -> int:
    """Mock: Bind the *args* and *kwds* to the argument names of the Python function or method *func*, as if it was called with them...."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getclosurevars(func: int) -> int:
    """Mock: Get the mapping of external name references in a Python function or method *func* to their current values. A :term:`name..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unwrap(func: int, stop: int) -> int:
    """Mock: Get the object wrapped by *func*. It follows the chain of :attr:`__wrapped__` attributes returning the last object in th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_annotations(obj: int, globals: int, locals: int, eval_str: int, format: int) -> int:
    """Mock: Compute the annotations dict for an object. This is an alias for :func:`annotationlib.get_annotations`; see the document..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getframeinfo(frame: int, context: int) -> int:
    """Mock: Get information about a frame or traceback object.  A :class:`Traceback` object is returned. .. versionchanged:: 3.11 A ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getouterframes(frame: int, context: int) -> int:
    """Mock: Get a list of :class:`FrameInfo` objects for a frame and all outer frames. These frames represent the calls that lead to..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getinnerframes(traceback: int, context: int) -> int:
    """Mock: Get a list of :class:`FrameInfo` objects for a traceback's frame and all inner frames.  These frames represent calls mad..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def currentframe() -> int:
    """Mock: Return the frame object for the caller's stack frame. .. impl-detail:: This function relies on Python stack frame suppor..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stack(context: int) -> int:
    """Mock: Return a list of :class:`FrameInfo` objects for the caller's stack.  The first entry in the returned list represents the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def trace(context: int) -> int:
    """Mock: Return a list of :class:`FrameInfo` objects for the stack between the current frame and the frame in which an exception ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getattr_static(obj: int, attr: int, default: int) -> int:
    """Mock: Retrieve attributes without triggering dynamic lookup via the descriptor protocol, :meth:`~object.__getattr__` or :meth:..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getgeneratorstate(generator: int) -> int:
    """Mock: Get current state of a generator-iterator. Possible states are: * GEN_CREATED: Waiting to start execution. * GEN_RUNNING..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getcoroutinestate(coroutine: int) -> int:
    """Mock: Get current state of a coroutine object.  The function is intended to be used with coroutine objects created by :keyword..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getasyncgenstate(agen: int) -> int:
    """Mock: Get current state of an asynchronous generator object.  The function is intended to be used with asynchronous iterator o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getgeneratorlocals(generator: int) -> int:
    """Mock: Get the mapping of live local variables in *generator* to their current values.  A dictionary is returned that maps from..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getcoroutinelocals(coroutine: int) -> int:
    """Mock: This function is analogous to :func:`~inspect.getgeneratorlocals`, but works for coroutine objects created by :keyword:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getasyncgenlocals(agen: int) -> int:
    """Mock: This function is analogous to :func:`~inspect.getgeneratorlocals`, but works for asynchronous generator objects created ..."""
    return 0
