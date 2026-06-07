# pure_lib/iomod — pure-Python io module
# StreamModel: flush-through (write routes to fs.sys_write).
# StringIO: in-memory buffer (no fd). TextIOWrapper: Specified.


#@ class invariant self._size >= 0
class StringIO:
    def __init__(self, initial_value):
        self._buf = []
        self._pos = 0
        self._size = 0
        if initial_value != 0:
            n = len(initial_value)
            i = 0
            #@ loop invariant 0 <= i
            #@ loop invariant i <= n
            #@ loop variant n - i
            while i < n:
                self._buf.append(initial_value[i])
                i = i + 1
            self._size = n

    #@ ensures \result >= 0
    def read(self, n) -> int:
        if n < 0:
            n = self._size - self._pos
        if n <= 0:
            return 0
        start = self._pos
        end = self._pos + n
        if end > self._size:
            end = self._size
        self._pos = end
        return end - start

    #@ ensures \result >= 0
    def write(self, data) -> int:
        n = len(data)
        i = 0
        #@ loop invariant 0 <= i
        #@ loop invariant i <= n
        #@ loop variant n - i
        while i < n:
            if self._pos < self._size:
                self._buf[self._pos] = data[i]
            else:
                self._buf.append(data[i])
                self._size = self._size + 1
            self._pos = self._pos + 1
            i = i + 1
        return n

    #@ ensures \result >= 0
    def tell(self) -> int:
        return self._pos

    def seek(self, pos):
        if pos < 0:
            pos = 0
        if pos > self._size:
            pos = self._size
        self._pos = pos

    #@ ensures \result >= 0
    def getvalue(self) -> int:
        return self._buf


#@ ensures \result >= 0
def open(name, mode) -> int:
    return 0


#@ ensures \result >= 0
def text_encoding(encoding) -> int:
    return encoding
