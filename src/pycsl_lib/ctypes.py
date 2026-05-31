"""PyCSL mock for Python's ctypes module — A foreign function library for Python."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def find_library(name: int) -> int:
    """Mock: :module: ctypes.util Try to find a library and return a pathname. *name* is the 'short' library name without any prefix ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def find_msvcrt() -> int:
    """Mock: :module: ctypes.util Returns the filename of the VC runtime library used by Python, and by the extension modules. If the..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def CFUNCTYPE(restype: int, use_errno: int, use_last_error: int) -> int:
    """Mock: The returned function prototype creates functions that use the standard C calling convention.  The function will release..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def WINFUNCTYPE(restype: int, use_errno: int, use_last_error: int) -> int:
    """Mock: The returned function prototype creates functions that use the ``stdcall`` calling convention.  The function will releas..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def PYFUNCTYPE(restype: int) -> int:
    """Mock: The returned function prototype creates functions that use the Python calling convention.  The function will *not* relea..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def addressof(obj: int) -> int:
    """Mock: Returns the address of the memory buffer as integer.  *obj* must be an instance of a ctypes type. .. audit-event:: ctype..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def alignment(obj_or_type: int) -> int:
    """Mock: Returns the alignment requirements of a ctypes type. *obj_or_type* must be a ctypes type or instance."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def byref(obj: int, offset: int) -> int:
    """Mock: Returns a light-weight pointer to *obj*, which must be an instance of a ctypes type.  *offset* defaults to zero, and mus..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CopyComPointer(src: int, dst: int) -> int:
    """Mock: Copies a COM pointer from *src* to *dst* and returns the Windows specific :c:type:`!HRESULT` value. If *src* is not ``NU..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cast(obj: int, type_: int) -> int:
    """Mock: This function is similar to the cast operator in C. It returns a new instance of *type* which points to the same memory ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_string_buffer(init: int, size: int) -> int:
    """Mock: This function creates a mutable character buffer. The returned object is a ctypes array of :class:`c_char`. If *size* is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def create_unicode_buffer(init: int, size: int) -> int:
    """Mock: This function creates a mutable unicode character buffer. The returned object is a ctypes array of :class:`c_wchar`. The..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def DllCanUnloadNow() -> int:
    """Mock: This function is a hook which allows implementing in-process COM servers with ctypes.  It is called from the DllCanUnloa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def DllGetClassObject() -> int:
    """Mock: This function is a hook which allows implementing in-process COM servers with ctypes.  It is called from the DllGetClass..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dllist() -> int:
    """Mock: :module: ctypes.util Try to provide a list of paths of the shared libraries loaded into the current process.  These path..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FormatError(code: int) -> int:
    """Mock: Returns a textual description of the error code *code*.  If no error code is specified, the last error code is used by c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def GetLastError() -> int:
    """Mock: Returns the last error code set by Windows in the calling thread. This function calls the Windows ``GetLastError()`` fun..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_errno() -> int:
    """Mock: Returns the current value of the ctypes-private copy of the system :data:`errno` variable in the calling thread. .. audi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_last_error() -> int:
    """Mock: Returns the current value of the ctypes-private copy of the system :data:`!LastError` variable in the calling thread. ....."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def memmove(dst: int, src: int, count: int) -> int:
    """Mock: Same as the standard C memmove library function: copies *count* bytes from *src* to *dst*. *dst* and *src* must be integ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def memset(dst: int, c: int, count: int) -> int:
    """Mock: Same as the standard C memset library function: fills the memory block at address *dst* with *count* bytes of value *c*...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def POINTER(type_: int) -> int:
    """Mock: Create or return a ctypes pointer type. Pointer types are cached and reused internally, so calling this function repeate..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pointer(obj: int) -> int:
    """Mock: Create a new pointer instance, pointing to *obj*. The returned object is of the type ``POINTER(type(obj))``. Note: If yo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resize(obj: int, size: int) -> int:
    """Mock: This function resizes the internal memory buffer of *obj*, which must be an instance of a ctypes type.  It is not possib..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_errno(value: int) -> int:
    """Mock: Set the current value of the ctypes-private copy of the system :data:`errno` variable in the calling thread to *value* a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_last_error(value: int) -> int:
    """Mock: Sets the current value of the ctypes-private copy of the system :data:`!LastError` variable in the calling thread to *va..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sizeof(obj_or_type: int) -> int:
    """Mock: Returns the size in bytes of a ctypes type or instance memory buffer. Does the same as the C ``sizeof`` operator."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def string_at(ptr: int, size: int) -> int:
    """Mock: Return the byte string at *void \*ptr*. If *size* is specified, it is used as size, otherwise the string is assumed to b..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def WinError(code: int, descr: int) -> int:
    """Mock: Creates an instance of :exc:`OSError`.  If *code* is not specified, :func:`GetLastError` is called to determine the erro..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wstring_at(ptr: int, size: int) -> int:
    """Mock: Return the wide-character string at *void \*ptr*. If *size* is specified, it is used as the number of characters of the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def memoryview_at(ptr: int, size: int, readonly: int) -> int:
    """Mock: Return a :class:`memoryview` object of length *size* that references memory starting at *void \*ptr*. If *readonly* is t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ARRAY(type_: int, length: int) -> int:
    """Mock: Create an array. Equivalent to ``type * length``, where *type* is a :mod:`!ctypes` data type and *length* an integer. ....."""
    return 0
