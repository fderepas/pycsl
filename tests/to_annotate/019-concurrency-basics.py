from threading import Lock, Thread


class SafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = Lock()

    @property
    def value(self):
        return self._value

    def increment(self):
        with self._lock:
            self._value += 1


def run_workers(counter, workers, increments_per_worker):
    threads = []
    for _ in range(workers):
        thread = Thread(target=lambda: [counter.increment() for _ in range(increments_per_worker)])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    counter = SafeCounter()
    run_workers(counter, workers=4, increments_per_worker=5000)
    print("counter:", counter.value)

