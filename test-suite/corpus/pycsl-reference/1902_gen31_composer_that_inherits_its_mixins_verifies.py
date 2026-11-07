r"""Test 1902 — gen #31 (expected PASS): a `#@ compose_from` class that ALSO INHERITS its
mixins — the first composing class in this corpus that is executable Python.

WHY THIS FILE EXISTS. Measured in gen #31: all eleven composing classes in the corpus
compose a provider they do not inherit, and in ten of the eleven the provided name is
ABSENT from the instance at runtime. `0549`'s `Facade().run(3)` is an `AttributeError`;
`0554`'s `Service().tick()` is an `AttributeError`. `#@ compose_from` flattens the provider
IN THE VERIFIER, and Python's MRO does not.

Writing the composition the way Python composes it —

    class Facade(CoreEmit, MapOps):

— makes the program RUN (`run(3)` is 3, `run(-1)` is 0, both `>= 0`), and until this
increment PyCSL REFUSED it, because route #95's shadow check computes `own_tails` from the
IR function list, where the base-class binding has already materialised `facade__emit`. An
INHERITED method was indistinguishable from a DEFINED one, and the diagnostic said
"'Facade' defines its own 'emit'" of a class whose entire body is `run`.

The exemption is narrow and it is a SAMENESS test, not a syntactic one: the composer's
method is exempt only when it IS the provider — same line, same column, same body, same
contracts. There is then nothing substituted, so there is nothing left unverified.

WHAT WOULD BREAK IF THIS GOES RED: the exemption has stopped recognising an inherited
provider, and the only spelling of `#@ compose_from` that produces a running Python
program is refused again.

Its two controls are `1903` (the provider does NOT refine the declared dependency — still
FAILS, the exemption does not reopen route #95) and `1904` (the composer defines a
DIFFERENT `emit` of its own — still REFUSED).

`getting-better/open-routes/finding-a-contract-over-a-function-that-never-returns.md`
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0


#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)


#@ compose_from CoreEmit, MapOps
class Facade(CoreEmit, MapOps):
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
