# OPEN ROUTE #316 — A METHOD'S WRITES TO ITS ARGUMENTS (AND TO MODULE-LEVEL OBJECTS) ARE INVISIBLE TO EVERY CALLER
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day; inferred frame + refusals), Severity 1.** Red-team round 16; driver-reproduced on main eb75cbcf (e13c, e32, e07c, r01, w11 rc=0; CPython violates).
Mechanism: a call to a user method (instance, @staticmethod, `self.` sibling) goes through a generated `val` stub whose `writes` come ONLY
from the method's `assigns` on `self` (no assigns -> `val p_bump_0 () : unit`, not even self); the method body `let p__bump` is checked
only against a frame on `self`'s fields (`ensures { self.n = old self.n }`). A body writing a list parameter (`xs[0] = 5`, `xs[0] += 1`,
forwarding xs to a contracted mutator) or a field of a module-level object verifies, and every caller assumes nothing changed; a
declared `#@ assigns \nothing` / `#@ assigns self.n` is never checked against parameter writes (e32, e06b); a sibling call
`self.poke(self.xs)` mutates the object's own field through the parameter (n05); a subclass override mutating the argument called through
a base-typed variable passes the #277 refinement check because neither declares assigns (r01); method writing a field of module-level
`gq = Q()` (w11; the plain-function twin w12 is faithful). Dict/set params, .append/.reverse/del already fail closed.
Emitted (e13c): `val p_bump_1 (x0: array int) : unit` (no writes) ... `let p__bump (self: p) (xs: array int) : unit ensures { self.n = old self.n } = if Array.length xs > 0 then xs[0] <- 5`.
Repair: make method stubs carry the same frame discipline as plain functions: the method body must be checked against its declared
`assigns` for ALL locations (params, globals, self), the default frame (no assigns) must be inferred/checked like plain functions (or
the call refused), and the stub's `writes` must include every parameter/global location the method may write.

## REPAIR (2026-10-23, r316 executor off 6821931b; commits 20735828 (code+docs), 9acacbb3 (alias precision), 9e68a1d7 (witnesses + census), + this docs commit)
**How PLAIN functions are faithful (read first).** A verified plain function is applied as its `let`; Why3 INFERS its
write effect from the body, so `def g(xs): xs[0] = 5` havocs the caller's `ys` (an `assigns xs[0]` adds nothing in the
Hoare model — the effect is always the whole array). A method is applied through an abstract `val` stub, and a
`\trusted`/imported function is a bodyless `val`; their effect is only what is declared — before this repair `writes
{ self.f }` from `assigns self.f` and nothing else.

**Design: infer the same effect for every function and put it on the stub (b)+(c); refuse what a stub cannot carry.**
`transpile` (mirror twin `\trusted`; result under `self.ir["_r316_writes"]`, no new transpiler field, no new def) computes
per function the set W of formal parameters its body may write — the root of every store target (`a[i]=`, `a[i] op=`,
slice store, `del a[i]`, `a.f=`, `a += ..`), in-place mutator receivers (`append extend insert ... __iadd__`), the
`heapq`/`random.shuffle`/`bisect.insort*`/`operator.i*` argument mutators — through local aliases at TWO levels
(IDENTITY: name/subscript/attribute/`or`/conditional/dotted call on the receiver/module-function or element-returning
builtin results; CONTAINMENT: anything mentioned, used for stores two levels down and for arguments), plus `self` and
`<global>`; closed by a fixpoint over calls (a tainted argument at a written callee position, a tainted receiver of a
method writing `self`, a callee writing a global; a dotted call takes the union over every method of that name). A
`\trusted` callee WITH `assigns` keeps its declared frame. Dict/set parameters (WL-05 / route #244 own them) and
string-keyed item stores (dicts / immutable IR nodes, cf6 M1.4) are not seeded. Consumers (inline at the use sites,
mirror twins `\trusted` or absent): `_handle_dotted_call` adds `writes { x_i }` for every written position whose stub
type is an `array` (whole-array effect, = the plain `let`); `_emit_function_block` adds `writes { p }` to the bodyless
`val` of a `\trusted`/imported function with NO `assigns` (route #317) and raises the refusals:
`PYCSL-METHOD-FRAME` (a declared method frame omitting a written parameter: (a)), `PYCSL-METHOD-GLOBAL-WRITE` (a method
writing a module-level object: its stub is declared before the global, no `writes` can name it), `PYCSL-OVERRIDE-FRAME`
(an override writing a position its base does not: (d), route #277 pairs), `PYCSL-METHOD-ARG-UNFRAMED` /
`PYCSL-VAL-ARG-UNFRAMED` (a written parameter whose type is not an array: record arguments). `self`-field writes stay
checked by the body's `ensures { self.f = old self.f }` frame (route #34) — which is what makes n05 fail once `poke`'s
stub writes its argument. Measured the alternative first: a `writes` clause on every method `let` (Why3-checked) would
move ~151 corpus files with mutable-parameter methods; the inference moves 1.

Probe table (whole-file `pycsl.py` via heavy.sh; CPython ground truth = each file's `__main__`):

| probe | corpus | CPython | 6821931b | after |
|---|---|---|---|---|
| e06b_method_mut_arg (`assigns self.n`, writes xs) | 4070 | violates | PROVED | REFUSED (PYCSL-METHOD-FRAME) |
| e07c_static_guarded (@staticmethod) | 4071 | violates | PROVED | FAIL |
| e13_method_nocontract_store | 4072 | violates | PROVED | FAIL |
| e13c_method_guarded | 4073 | violates | PROVED | FAIL |
| e20_method_aug_param (`xs[0] += 1`) | 4074 | violates | PROVED | FAIL |
| e21_method_calls_mutator (forwards to `g`) | 4075 | violates | PROVED | FAIL |
| e29_sibling_call (`self.poke(xs)`) | 4076 | violates | PROVED | FAIL |
| e31_field_store_in_param_list (`xs[1]`) | 4077 | violates | PROVED | FAIL |
| e32_method_assigns_nothing | 4078 | violates | PROVED | REFUSED (PYCSL-METHOD-FRAME) |
| n05_self_list_to_method_param | 4079 | violates | PROVED | FAIL (`bump` self frame) |
| r01_override_param_mut | 4082 | violates | PROVED | REFUSED (PYCSL-OVERRIDE-FRAME) |
| w11_global_obj_method | 4083 | violates | PROVED | REFUSED (PYCSL-METHOD-GLOBAL-WRITE) |
| u01 method writes record arg `q.n = 5` | 4084 | violates | FAIL (ill-typed `int` slot) | REFUSED (PYCSL-METHOD-ARG-UNFRAMED) |
| k01 method only reads list arg (control) | 4088 | ok | PROVED | PROVED |
| k03 method writes arg, caller reads another list (control) | 4089 | ok | PROVED | PROVED |
| k04 `assigns xs[0]` method admitted (control) | 4090 | ok | PROVED | PROVED |
| w12 plain-function twin (c01, scratch) | — | violates | FAIL | FAIL |

Blast radius: corpus root 1 MOVED / 0 GONE / 0 APPEARED-from-refusal (2141/2141 + 20 new sources): `3195_gen37_r282_...`
(expected FAIL; `T.m` declares `assigns xs[0]`, its stub gains `writes { x0 }`) — re-proved: FAIL -> FAIL. pyref 0/0/0
(2186/2186). Mirror 0/0/0 (53/53) — after the precision commit (the first cut refused 8 mirror files: call results
treated as aliases of their arguments (`_N("Attribute")(value=atom)`; `out = set(); out |= f(a)`), a dict literal holding
`s.kind`, and `c["pattern"] = ..` on an IR node). No previously-PROVED corpus file moved: no latent false proof, no
regression; nothing OWED. Census: 16 rows via `_census_row` (4070-4085; 6 REFUSAL, 10 VERIFY-FAIL).

Gates (rc): witnesses/controls above; byte-diff root rc=1 only for the declared 3195 mover, pyref rc=0; mirror-emit-sweep
compare rc=0 (`--min-files 50`); check-self-annotate-sync.sh 0 (926 verbatim); self-annotate-mirror-check.sh and
run-soundness-planes.sh fast: see README entry; doc-coherency --check 0; check-assumed-facts 0 (85, ledger 3 unchanged);
check-trusted-raises-honesty 0 (61 = ratchet); check-refusal-witness-coverage 0 (264 demonstrated, 5 ceiling).

Residuals: (1) the analysis is syntactic: a write through a call result that aliases a PARAMETER of a builtin/constructor
not in the element-returning list (`a = sorted(rows); a[0][0] = 1` is caught at depth 2, `a = list(rows); a[0] = ..` writes
the fresh copy — correct) and dynamic dispatch through `getattr`-obtained callables are over/under the model like every
other syntactic route; (2) dict/set parameter writes stay with WL-05/#244 (a by-value map; dict ALIASING through a list
element, `rows[0]["k"] = v`, is not seen by either); (3) record-argument writes are refused rather than framed
(`writes { x.f }` per mutable label is the named extension); (4) a method writing a global is refused even when declared
(`assigns gq.n`); (5) `assigns xs[0]` is not checked against `xs[1]` writes (whole-array effect, same as plain functions).
