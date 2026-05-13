# Level 2 feature: mixed record method + standalone function
# Tests that standalone clamp() gets no (self:) param while Wallet.credit gets (self: wallet)

def clamp(v, lo, hi):
    if v < lo:
        return lo
    else:
        if v > hi:
            return hi
        else:
            return v


class Wallet:
    def __init__(self):
        self._balance = 0

    def credit(self, n):
        self._balance += n
        return self._balance

    def debit(self, n):
        if n <= self._balance:
            self._balance -= n
        return self._balance
