# Concurrent feature: shared counter with mutex protection
# Tests: basic shared variable, mutex invariant, critical section
# Use with: --memory-model concurrent

import threading

lock = threading.Lock()
counter = 0

def increment() -> int:
    with lock:
        counter += 1
    return counter

def decrement() -> int:
    with lock:
        if counter > 0:
            counter -= 1
    return counter

def get_count() -> int:
    with lock:
        result = counter
    return result
