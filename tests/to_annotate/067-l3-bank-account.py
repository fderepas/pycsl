# Level 3 feature: class invariant with deposit/withdraw pattern
# Tests: invariant-guarding preconditions on mutating methods
# Inspired by Creusot's type invariant enforcement at function boundaries

class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        self._balance -= amount
        return self._balance

    def get_balance(self):
        return self._balance

    def transfer_to(self, other_balance, amount):
        self._balance -= amount
        return other_balance + amount
