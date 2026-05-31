"""PyCSL mock for Python's operator module — Functions corresponding to the standard operators."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def lt(a: int, b: int) -> int:
    """Mock: Perform 'rich comparisons' between *a* and *b*. Specifically, ``lt(a, b)`` is equivalent to ``a < b``, ``le(a, b)`` is e..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def not_(obj: int) -> int:
    """Mock: Return the outcome of :keyword:`not` *obj*.  (Note that there is no :meth:`!__not__` method for object instances; only t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def truth(obj: int) -> int:
    """Mock: Return :const:`True` if *obj* is true, and :const:`False` otherwise.  This is equivalent to using the :class:`bool` cons..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_(a: int, b: int) -> int:
    """Mock: Return ``a is b``.  Tests object identity."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_not(a: int, b: int) -> int:
    """Mock: Return ``a is not b``.  Tests object identity."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_none(a: int) -> int:
    """Mock: Return ``a is None``.  Tests object identity. .. versionadded:: 3.14"""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_not_none(a: int) -> int:
    """Mock: Return ``a is not None``.  Tests object identity. .. versionadded:: 3.14"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def abs(obj: int) -> int:
    """Mock: Return the absolute value of *obj*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def add(a: int, b: int) -> int:
    """Mock: Return ``a + b``, for *a* and *b* numbers."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def and_(a: int, b: int) -> int:
    """Mock: Return the bitwise and of *a* and *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def floordiv(a: int, b: int) -> int:
    """Mock: Return ``a // b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def index(a: int) -> int:
    """Mock: Return *a* converted to an integer.  Equivalent to ``a.__index__()``. .. versionchanged:: 3.10 The result always has exa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def inv(obj: int) -> int:
    """Mock: Return the bitwise inverse of the number *obj*.  This is equivalent to ``~obj``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lshift(a: int, b: int) -> int:
    """Mock: Return *a* shifted left by *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mod(a: int, b: int) -> int:
    """Mock: Return ``a % b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mul(a: int, b: int) -> int:
    """Mock: Return ``a * b``, for *a* and *b* numbers."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def matmul(a: int, b: int) -> int:
    """Mock: Return ``a @ b``. .. versionadded:: 3.5"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def neg(obj: int) -> int:
    """Mock: Return *obj* negated (``-obj``)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def or_(a: int, b: int) -> int:
    """Mock: Return the bitwise or of *a* and *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pos(obj: int) -> int:
    """Mock: Return *obj* positive (``+obj``)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pow(a: int, b: int) -> int:
    """Mock: Return ``a ** b``, for *a* and *b* numbers."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def rshift(a: int, b: int) -> int:
    """Mock: Return *a* shifted right by *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sub(a: int, b: int) -> int:
    """Mock: Return ``a - b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def truediv(a: int, b: int) -> int:
    """Mock: Return ``a / b`` where 2/3 is .66 rather than 0.  This is also known as 'true' division."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def xor(a: int, b: int) -> int:
    """Mock: Return the bitwise exclusive or of *a* and *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def concat(a: int, b: int) -> int:
    """Mock: Return ``a + b`` for *a* and *b* sequences."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def contains(a: int, b: int) -> int:
    """Mock: Return the outcome of the test ``b in a``. Note the reversed operands."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def countOf(a: int, b: int) -> int:
    """Mock: Return the number of occurrences of *b* in *a*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def delitem(a: int, b: int) -> int:
    """Mock: Remove the value of *a* at index *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getitem(a: int, b: int) -> int:
    """Mock: Return the value of *a* at index *b*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def indexOf(a: int, b: int) -> int:
    """Mock: Return the index of the first of occurrence of *b* in *a*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setitem(a: int, b: int, c: int) -> int:
    """Mock: Set the value of *a* at index *b* to *c*."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def length_hint(obj: int, default: int) -> int:
    """Mock: Return an estimated length for the object *obj*. First try to return its actual length, then an estimate using :meth:`ob..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def call(obj: int) -> int:
    """Mock: Return ``obj(*args, **kwargs)``. .. versionadded:: 3.11"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def attrgetter(attr: int) -> int:
    """Mock: Return a callable object that fetches *attr* from its operand. If more than one attribute is requested, returns a tuple ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def itemgetter(item: int) -> int:
    """Mock: Return a callable object that fetches *item* from its operand using the operand's :meth:`~object.__getitem__` method.  I..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def methodcaller(name: int) -> int:
    """Mock: Return a callable object that calls the method *name* on its operand.  If additional arguments and/or keyword arguments ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iadd(a: int, b: int) -> int:
    """Mock: ``a = iadd(a, b)`` is equivalent to ``a += b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iand(a: int, b: int) -> int:
    """Mock: ``a = iand(a, b)`` is equivalent to ``a &= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iconcat(a: int, b: int) -> int:
    """Mock: ``a = iconcat(a, b)`` is equivalent to ``a += b`` for *a* and *b* sequences."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ifloordiv(a: int, b: int) -> int:
    """Mock: ``a = ifloordiv(a, b)`` is equivalent to ``a //= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ilshift(a: int, b: int) -> int:
    """Mock: ``a = ilshift(a, b)`` is equivalent to ``a <<= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def imod(a: int, b: int) -> int:
    """Mock: ``a = imod(a, b)`` is equivalent to ``a %= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def imul(a: int, b: int) -> int:
    """Mock: ``a = imul(a, b)`` is equivalent to ``a *= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def imatmul(a: int, b: int) -> int:
    """Mock: ``a = imatmul(a, b)`` is equivalent to ``a @= b``. .. versionadded:: 3.5"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ior(a: int, b: int) -> int:
    """Mock: ``a = ior(a, b)`` is equivalent to ``a |= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ipow(a: int, b: int) -> int:
    """Mock: ``a = ipow(a, b)`` is equivalent to ``a **= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def irshift(a: int, b: int) -> int:
    """Mock: ``a = irshift(a, b)`` is equivalent to ``a >>= b``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isub(a: int, b: int) -> int:
    """Mock: ``a = isub(a, b)`` is equivalent to ``a -= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def itruediv(a: int, b: int) -> int:
    """Mock: ``a = itruediv(a, b)`` is equivalent to ``a /= b``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ixor(a: int, b: int) -> int:
    """Mock: ``a = ixor(a, b)`` is equivalent to ``a ^= b``."""
    return 0
