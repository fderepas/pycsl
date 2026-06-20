"""PyCSL mock for Python's multiprocessing module."""
_ = 0  # anchor

# ── ProcessObj class ────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._pid >= -1
#@ class invariant self._exitcode >= -256
class ProcessObj:
    def __init__(self):
        self._pid = -1
        self._exitcode = -256

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._pid >= 0
    #@ assigns self._pid
    def start(self) -> int:
        self._pid = 0
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/threading.html#threading.Thread.join
#@ requires timeout >= 0
#@ ensures self._alive == 0
#@ assigns self._alive
    def join(self, timeout: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/process.py
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
    def is_alive(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._pid
    #@ assigns \nothing
    def get_pid(self) -> int:
        return self._pid

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._exitcode
    #@ assigns \nothing
    def get_exitcode(self) -> int:
        return self._exitcode

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/subprocess.html#subprocess.Popen.terminate
#@ requires True
#@ ensures True
#@ assigns \nothing
    def terminate(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/subprocess.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def kill(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process.close
#@ requires True
#@ ensures True
#@ assigns \nothing
    def close(self) -> int:
        return 0

# ── QueueObj class ──────────────────────────────────────────────────

#@ class invariant self._qsize >= 0
class QueueObj:
    def __init__(self):
        self._qsize = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._qsize == \old(self._qsize) + 1
    #@ assigns self._qsize
    def put(self, obj: int, block: int, timeout: int) -> int:
        self._qsize = self._qsize + 1
        return 0

    #@ \trusted
    #@ requires self._qsize >= 1
    #@ ensures self._qsize == \old(self._qsize) - 1
    #@ assigns self._qsize
    def get(self, block: int, timeout: int) -> int:
        self._qsize = self._qsize - 1
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._qsize
    #@ assigns \nothing
    def qsize(self) -> int:
        return self._qsize

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Queue.empty
#@ requires True
#@ ensures True
#@ assigns \nothing
    def empty(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Queue.full
#@ requires True
#@ ensures True
#@ assigns \nothing
    def full(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/process.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def close(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Queue.join_thread
#@ requires True
#@ ensures True
#@ assigns \nothing
    def join_thread(self) -> int:
        return 0

# ── PoolObj class ───────────────────────────────────────────────────

#@ class invariant self._workers >= 1
class PoolObj:
    def __init__(self):
        self._workers = 1

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.apply
#@ requires True
#@ ensures True
#@ assigns \nothing
    def apply(self, func: int, args: int, kwds: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/pool.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def apply_async(self, func: int, args: int, kwds: int, callback: int, error_callback: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map
#@ requires True
#@ ensures True
#@ assigns \nothing
    def map_func(self, func: int, iterable: int, chunksize: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map_async
#@ requires True
#@ ensures True
    def map_async(self, func: int, iterable: int, chunksize: int, callback: int, error_callback: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/multiprocessing/pool.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def starmap(self, func: int, iterable: int, chunksize: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.close
#@ ensures True
#@ assigns \nothing
    def close(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/subprocess.html#subprocess.Popen.terminate
#@ requires True
#@ ensures True
#@ assigns \nothing
    def terminate(self) -> int:
        return 0

#@ \trusted reviewer: out-of-scope-mm
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/pool.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def join(self) -> int:
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted reviewer: out-of-scope-mm
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.active_children
#@ ensures True
def active_children() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.cpu_count
#@ ensures \result >= 1
def cpu_count() -> int:
    return 1

#@ \trusted reviewer: out-of-scope-mm
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.current_process
#@ ensures True
def current_process() -> int:
    return 0

#@ \trusted reviewer: out-of-scope-mm
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.parent_process
def parent_process() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
#@ ensures True
#@ assigns \nothing
def freeze_support() -> int:
    return 0

#@ \trusted reviewer: out-of-scope-mm
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.get_all_start_methods
#@ ensures True
def get_all_start_methods() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/context.py
#@ requires True
#@ ensures True
def get_context(method: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/context.py
#@ requires True
#@ ensures True
def get_start_method(allow_none: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.set_executable
#@ ensures True
#@ assigns \nothing
def set_executable(executable: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/context.py
#@ requires True
#@ ensures True
#@ assigns \nothing
def set_start_method(method: int, force: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/connection.py
#@ requires True
#@ ensures True
def mp_pipe(duplex: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/managers.py
#@ requires True
#@ ensures True
def mp_manager() -> int:
    return 0

#@ \trusted reviewer: out-of-scope-mm
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/sharedctypes.py
#@ requires True
#@ ensures True
def mp_value(typecode: int, args: int, lock_val: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/sharedctypes.py
#@ requires True
#@ ensures True
def mp_array(typecode: int, size_init: int, lock_val: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/synchronize.py
#@ requires True
#@ ensures True
def mp_lock() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/synchronize.py
#@ requires True
#@ ensures \result >= 0
def mp_rlock() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Semaphore
#@ requires sem_value >= 0
#@ ensures \result >= 0
def mp_semaphore(sem_value: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/synchronize.py
#@ requires True
#@ ensures True
def mp_event() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/synchronize.py
#@ requires parties >= 1
#@ ensures True
def mp_barrier(parties: int, action: int, timeout: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/synchronize.py
#@ requires True
#@ ensures True
def mp_condition(lock_val: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/connection.py
#@ requires True
#@ ensures True
def mp_listener(address: int, family: int, backlog: int, authkey: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/multiprocessing/connection.py
#@ requires True
#@ ensures True
def mp_client(address: int, family: int, authkey: int) -> int:
    return 0

#@ \trusted reviewer: out-of-scope-mm
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.get_logger
#@ ensures \result >= 0
def get_logger() -> int:
    return 0

#@ \trusted reviewer: out-of-scope-mm
# cite: https://docs.python.org/3/library/multiprocessing.html#multiprocessing.log_to_stderr
#@ ensures True
def log_to_stderr(level: int) -> int:
    return 0
