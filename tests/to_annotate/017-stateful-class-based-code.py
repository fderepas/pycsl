class Counter:
    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value

    def increment(self, amount=1):
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._value += amount
        return self._value

    def reset(self):
        self._value = 0


if __name__ == "__main__":
    counter = Counter()
    counter.increment()
    counter.increment(4)
    print("value:", counter.value)
    counter.reset()
    print("after reset:", counter.value)

