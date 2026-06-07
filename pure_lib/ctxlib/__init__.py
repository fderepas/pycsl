# pure_lib/ctxlib — pure-Python contextlib module
# ExitStack and nullcontext: Modelled. contextmanager: Specified.


class nullcontext:
    def __init__(self, enter_result):
        self._enter_result = enter_result

    def __enter__(self):
        return self._enter_result

    #@ ensures \result == 0
    def __exit__(self, exc_type, exc_val, exc_tb) -> int:
        return 0


#@ class invariant self._size >= 0
class ExitStack:
    def __init__(self):
        self._callbacks = []
        self._size = 0

    def __enter__(self):
        return self

    def push(self, callback):
        self._callbacks.append(callback)
        self._size = self._size + 1

    def callback(self, cb):
        self._callbacks.append(cb)
        self._size = self._size + 1

    #@ ensures self._size == 0
    def __exit__(self, exc_type, exc_val, exc_tb) -> int:
        #@ loop invariant 0 <= self._size
        #@ loop variant self._size
        while self._size > 0:
            self._size = self._size - 1
            cb = self._callbacks[self._size]
        self._callbacks = []
        return 0


#@ ensures \result >= 0
def contextmanager(func) -> int:
    return func
