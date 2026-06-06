# Concurrent feature: dining philosophers (simplified 2-fork variant)
# Tests: multiple mutexes, lock_order to prevent deadlock
# Use with: --memory-model concurrent

import threading

lock_left = threading.Lock()
lock_right = threading.Lock()
eating = 0

def philosopher(id: int) -> int:
    with lock_left:
        with lock_right:
            eating += 1
    return eating
