# ROUTE #166 — one abstract stub NAME for two callees: `_add_abstract_op` keeps the LONGER contract

**Status: CLOSED by gen #29 (battery L green: suite 3694/3712, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1. Generator: hand (the
Liskov-default WATCH row, followed to its mechanism).

## Measured at `0a9723c0`

    class C: ... #@ ensures \result == 1     def get(self): return 1
    class D: ... #@ ensures \result == 700   def get(self): return 700
    def f():  o = C(); return o.get()        #@ ensures \result == 700   PROVED   (CPython 1)
    def g():  o = D(); return o.get()

Both calls register the stub `o_get_0` (the name is built from the call's spelling). On a
same-name/same-arity clash `_add_abstract_op` keeps the LONGER declaration, so `f` was verified
against `D.get`'s `ensures { result = 700 }`.

The same mechanism is behind the Liskov WATCH shape: an inherited clone `b__call_m` calls `self.m()`,
whose stub `self_m_0` was registered first by `a__call_m` with A's contract; B's override contract
never reached the clone, so `B().call_m() == 1` PROVED by default (CPython 7).

## Repair (draft)

In `_handle_dotted_call` (trusted), a declaration that differs from one already registered under the
same stub name gets its own name (`<name>_c<hash of the declaration>`) at that call site; identical
re-registrations are unchanged. The clone now sees B's contract and its inherited `ensures == 1`
fails. Witnesses 1566/1568 (XFAIL), 1567 (PASS).

## Still to measure

Other `_add_abstract_op` producers (module functions, getattr/setattr ops, builtins) share the
keep-longer rule; a root fix (never merge two different declarations) needs a conflict census over
the corpus and the mirrors first.
