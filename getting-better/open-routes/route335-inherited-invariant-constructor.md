# OPEN ROUTE #335 — AN INHERITED CLASS INVARIANT ASSUMES THE BASE CONSTRUCTOR'S FIELD VALUES FOR A SUBCLASS THAT NEVER RAN IT
**Status: REPAIRED (gen #37, 2026-10-24; opened the same day; sound refusal), Severity 1.** Red-team round 22; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r335/`: a subclass inherits the base's `#@ class invariant`; the inherited goal `_check_class_inv_s` assumes the BASE
constructor's field values (`forall s_n. s_n = 0 -> ...`) — wrong when `S.__init__` never calls super: class attribute `n = -1` + `__init__: pass`
(i35, CPython -1), `__init__` sets only another field (i36; `no_exception \all` proves, CPython AttributeError), `__init__(k)` + class attribute
`n = 3` (i37), a subclass property `x` returning 7 (i33), `class S(M, B)` where MRO runs `M.__init__` first (i38). A parameter `b: B` may hold a
subclass (default since #277), so it receives an invariant no subclass instance established. Controls hold when the subclass constructor
assigns the field itself (with or without super) and for grandchildren. Likely a residual of route #226 (inheritance section).
Repair: the inherited-invariant establishment goal for a subclass must be built from the subclass's ACTUAL construction (its own __init__ per
Python MRO: explicit super() calls inlined, otherwise base __init__ NOT run; class-attribute / property shadowing of invariant fields
considered) — or refuse a subclass of an invariant-carrying class whose __init__ does not provably call the base __init__ (and whose
class attributes/properties shadow invariant fields).

## REPAIR (2026-10-24, r335 executor off 87b4eca6; commits abff40d6 (code + corpus), 56aa4b8b (census + docs), 2969cbf4 (0448 line-neutral) + route docs)
**Design: sound refusal at the merge, no emission change.** The goal `_check_class_inv_<sub>` and route #277's receiver
assumption read the MERGED `field_defaults`, which `apply_inheritance` unions from the bases in declared-base order. The
faithful alternative (rebuild each subclass's field values from its real constructor chain and re-emit the goal) would
change emission for every based class; the refusal moves no emitted file (measured below), so it was taken.
Rule (`ir_resolve.apply_inheritance`, end of `merge_one`, inline, no new def; mirror twin `\trusted` + `#@ raises
PyCSLSemanticError when True`): over the C3 MRO, Python's constructor chain is walked — a class without `__init__` is
walked through (records with `init_inherits`; a fieldless base-less class only if Module 5's new side channel
`nonrecord335` says it defines no `__init__`/`__new__` and is not a dataclass), a class defining one contributes its
top-level stores (fields minus `init_unknown_cf_fields`) and continues ONLY through a leading `super().__init__(...)`
(`init_super150`), a synthesized dataclass constructor contributes the MRO's dataclass fields and ends it, anything
unmodelled ends it. owner(f) = first chain class storing f. For every invariant field (own or inherited invariant) that
belongs to a base and is not a definite own store of the subclass: no owner -> REFUSED; owner's literal != merged
default (unless bound in the merged `init_body`, unknown, or `init_opaque150`) -> REFUSED; a method / `@property` /
non-constant class-body binding of that name anywhere in the MRO -> REFUSED (`PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION`).
Snapshot of each record's raw construction is taken before any merge; `nonrecord335` is popped (resolved IR unchanged).

**Probe table** (full proofs via heavy.sh; CPython rc 1 = contract violated):
| witness | corpus | CPython | base 87b4eca6 | after |
|---|---|---|---|---|
| i33 subclass `@property x` shadows invariant field | 4460 | violates | rc=0 PROVED | rc=1 REFUSED R335 |
| i35 class attr `n = -1` + `__init__: pass` | 4461 | violates | rc=0 PROVED | rc=1 REFUSED |
| i36 `__init__` stores only `m`, `no_exception \all` | 4462 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| i37 `__init__(k)` + class attr `n = 3` | 4463 | violates | rc=0 PROVED | rc=1 REFUSED |
| i38 `S(M, B)`, MRO runs `M.__init__` | 4464 | violates | rc=0 PROVED | rc=1 REFUSED |
| p1 `S(M, B)`, `M.__init__` = cooperative `super()` then `n = -1` (NEW latent false proof) | 4465 | violates | rc=0 PROVED | rc=1 REFUSED |
| p2 subclass's OWN invariant over an unstored inherited field (NEW) | 4466 | violates | rc=0 PROVED | rc=1 REFUSED |
| p3 fieldless mixin `__init__: pass` first in MRO (NEW) | 4467 | violates | rc=0 PROVED | rc=1 REFUSED |
| p4 store only under `if`, no super (NEW) | 4468 | violates | rc=0 PROVED | rc=1 REFUSED |
| controls: own store w/o super 4469, `super().__init__()` 4470, grandchild chain 4471, `S(B): pass` 4472, super then store 4473, fieldless mixin w/o `__init__` 4474, `super().__init__(3)` into a `requires` base 4475, subclass invariant over inherited field 4476 | 4469-4476 | ok | rc=0 | rc=0 PROVED |
| p5 `B.__init__(self)` explicit (not filed) | - | ok | rc=0 | rc=1 REFUSED (over-refusal, sound) |

**Blast radius / latent.** Root 2223 base / 2231 candidate: 0 MOVED, 0 GONE, 0 APPEARED (8 new controls). The first
sweep showed ONE GONE: corpus 0448 (`FunctionAnalyzer(vb.NodeVisitor)` whose `__init__` stores only `count`, never
running the imported base's `__init__`, invariant `self._depth >= 0` assumed; CPython `a._depth` -> AttributeError) — a
LATENT false assumption in an expected-PASS file. Repaired in the corpus by a leading `super().__init__()` (CPython PASS;
emission byte-identical to base; PROVED rc=0). Pyref 2186/2186 0/0/0. Mirror 53/53: 1 MOVED, exactly the intended
`raises { PyCSLSemanticError -> true }` on `apply_inheritance` in `frontend__ir_resolve.mlw`; type-checked and the whole
file PROVED rc=0 (no OWED proof). 0 mirror GONE.
**Gates** (logs in `.r335tmp/`, removed after the run; base sweeps taken in this worktree at 87b4eca6 before any edit):
byte-diff-compare root rc=0, pyref rc=0, mirror rc=0 with `--expect-moved frontend__ir_resolve`; check-self-annotate-sync.sh
rc=0 (926); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast 61/61 rc=0 (first run 60/61: `frontend-only-conformance` 0448 golden line numbers shifted by a
multi-line fix; the fix was made line-neutral `super().__init__(); self.count = 0`, goldens 38/38, re-proved rc=0); doc-coherency --check
rc=0; check-assumed-facts rc=0 (ledger 3); check-trusted-raises-honesty rc=0 (19 declared / 61 silent, ratchet 61);
check-refusal-witness-coverage rc=0 (282 demonstrated / 5 not, ceiling 5; rows 4460-4468 by `_census_row`);
check-dropped-mutation rc=0. `--slow` planes NOT run (heavy queue shared).
**Residuals.** (1) Over-refusal: `B.__init__(self)` / non-leading or conditional `super()` / both-branch stores are
refused (route #150 models only a leading `super()`). (2) Imported FIELDLESS classes in the MRO (no `nonrecord335`
entry crosses the import cache) end the chain -> refusal (sound, possibly over-refusing). (3) A base-less record with
fields but no `__init__` (`#@ touches_field` mixin) is treated as defining one (stores its declared fields, no super);
for a field also stored by a later base this can accept a value from the wrong class only if the literals coincide.
(4) Non-inherited classes: an invariant over a field the class's OWN `__init__` stores only conditionally is route
#226's out-of-scope (no goal, assumed) — unchanged here. (5) Descriptors set by metaclasses / `__getattr__` /
`__slots__` tricks are not scanned.
