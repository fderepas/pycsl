#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self) -> None:
        self._balance: int = 0

    def deposit(self, amount: int) -> None:
        self._balance = self._balance + amount

    def withdraw(self, amount: int) -> None:
        self._balance = self._balance - amount
