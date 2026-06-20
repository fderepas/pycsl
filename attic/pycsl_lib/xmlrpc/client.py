"""PyCSL mock for Python's xmlrpc.client module — XML-RPC client access."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def dumps(params: int, methodname: int, methodresponse: int, encoding: int, allow_none: int) -> int:
    """Mock: Convert *params* into an XML-RPC request, or into a response if *methodresponse* is true. *params* can be either a tuple..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def loads(data: int, use_datetime: int, use_builtin_types: int) -> int:
    """Mock: Convert an XML-RPC request or response into Python objects, a ``(params, methodname)``.  *params* is a tuple of argument..."""
    return 0
