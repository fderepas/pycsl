#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self) -> None:
        self._balance: int = 0
    #@ proof rocq: deposit_post
    #@ proof lean: deposit_post
    #@ requires self._balance >= 0
    #@ requires amount >= 0
    #@ ensures \result == (self._balance + amount)
    #@ assigns \nothing
    def deposit(self, amount: int) -> None:
        self._balance = self._balance + amount
    #@ proof rocq: withdraw_post
    #@ proof lean: withdraw_post
    #@ requires self._balance >= 0
    #@ requires amount >= 0
    #@ ensures (amount <= self._balance) ==> (\result == (self._balance - amount))
    #@ assigns \nothing
    def withdraw(self, amount: int) -> None:
        self._balance = self._balance - amount
