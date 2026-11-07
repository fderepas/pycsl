# OPEN ROUTE #402 — A USER `__hash__` ON THE STATIC CLASS ITSELF IS NEVER CALLED IN THE MODEL
**Status: REPAIRED, candidate (gen #37, 2026-10-26; e3 executor off 526d534de -- sound refusal, see REPAIR). Was OPEN, Severity 1.** Found by executor e1 (run #3, residual of route #395), driver-reproduced 2026-10-26 on the e1+e2
integration tree (rc=0 "Verification SUCCESS"; CPython `ValueError: h`). Witness `witnesses-r402/p1_own_hash_raise.py`:
`class D` defines `def __hash__(self)` that raises when `self.x == 1`; `f(d: D)` builds `{d}` under `#@ no_exception \all`.

Mechanism: a hashing position checks only whether the value's class is HASHABLE (route #349 family / §7.46-§7.50); a class that
defines `__hash__` counts as hashable, and the call to that `__hash__` (and to `__eq__` on a collision) is not emitted, so its
exceptions and preconditions are invisible. #395 (e1) requires a verified `no_exception \all` `__hash__` only on file SUBCLASSES;
requiring it on the static class too refuses PASS controls 4694, 4940, 5043 (measured by e1).

Repair options: (a) lower every hashing position as a call to the class's `__hash__` (with its contract: `raises`, `requires`),
the faithful model; (b) refuse unless the class's `__hash__` is verified `#@ no_exception \all` and give 4694/4940/5043 that
contract (their `__hash__` bodies are total); measure (b) first.

## REPAIR (2026-10-26, e3 executor off 526d534de; docs annotations §7.57 / translational §T.6.68)
**Design: option (b), an allow-list step in the §7.33 / §7.50 hashability fixpoint plus an EQ-RISKY fixpoint (inline in
`_run_pipeline`, mirror twin `\trusted`, no emission change).**
A `__hash__` / `__eq__` is VERIFIED when it is ONE top-level undecorated `def` whose IR function is neither `\trusted` nor `\abstract`,
carries `#@ no_exception \all`, has no `requires` (a hashing site discharges none) and returns `int` / `bool`. Along the C3 MRO, a
deciding `def __hash__` that is not verified makes the class unhashable (`PYCSL-R349-UNHASHABLE-RECORD`, both messages extended);
the narrowed verified set also tightens #395's subclass step. A class is EQ-RISKY when its MRO-deciding `__eq__` is not one verified
`def`, or it compares fields (`@dataclass` with `eq`, NamedTuple, functional namedtuple) of a non-eq-safe annotation, or a file
subclass is eq-risky; a value of an eq-risky class at a hashing site that may compare (every site but `hash(x)` and one-element set /
dict displays) is refused (`PYCSL-R402-UNVERIFIED-EQ`).

Measurements (base worktree at 526d534de, `getting-better/systematic-soundness-r3/e3-r402/`):
- option (b), before any corpus edit: root 2438 -> 2435, 0 MOVED / 3 GONE (4694, 4940, 5043 -- exactly e1's three) / 0 APPEARED;
  pyref 2192 -> 2192 0/0/0; mirror 53/53 0/0/0; `pycsl_lib` --no-proof screen identical (104 files, 87 rc 0 / 17 rc 1).
  The three controls' `__hash__` bodies are total (`return 0` / `return 1`): given `#@ no_exception \all` (M1 corpus edit), their
  emission is byte-identical to base and they PROVE at base and candidate.
- option (a) (lower each hashing site as a call to `__hash__`, and `__eq__` on a possible collision): its emission movers are the
  emitted files hashing a class with a user `__hash__` / `__eq__` -- measured by a probe build treating every such method as
  unverified over the 39 emitted root files that bind one: 4 files (4694, 4940, 5043, 5592); pyref 0, mirror 0. It needs a new
  Module 6 lowering (mirrored, `module6_whyml`) plus a collision model for `__eq__`, for no fewer movers: not taken.
Final candidate: root 2438 -> 2440 (+2 controls; 10 witnesses refused), 0 MOVED / 0 GONE / 0 APPEARED; pyref 0/0/0; mirror 0/0/0.
Witnesses (PROVED rc=0 at base -> REFUSED rc=1): 5780 own raising `__hash__`, 5781 `requires`-guarded verified `__hash__`, 5782
inherited raising `__hash__`, 5783 tuple element, 5784 frozen-record field, 5785 raising `__eq__` in `{a, b}`, 5786 tuple pair,
5787 dataclass field `__eq__`, 5788 file subclass `__eq__`, 5789 starred display. Controls 5800 / 5801 PROVED at base and candidate.
Probes that were NOT witnesses (not PROVED at base): `hash(d)` of a user class and a dict with user-class keys (WhyML type errors),
`a in s` with `s: Set[D]` (R252 erased-operand VC already fails), `{a}; s.add(b)`, `frozenset([a, b])`, `{x for x in (a, b)}`.
Residuals: a cyclic value compared by field-wise `__eq__` (RecursionError) is not modelled; `__eq__` reached through a stdlib
container element (a `frozenset` of user objects inside a set) is not traced.
