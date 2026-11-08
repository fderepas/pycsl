# OPEN ROUTE #341 — A CLASS BASE NOT WRITTEN AS THE CLASS'S OWN NAME SILENTLY DROPS THE INHERITANCE EDGE (Liskov/R5/#335/invariants skipped)
**Status: REPAIRED, candidate (gen #37, 2026-10-24; r341 executor off 8984dce3 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r341/`: `Base = B; class S(Base)`, `class S(base())`, `class S(me.B if False else B)`, tuple-unpacked alias, `Base: Type[B] = B` — S becomes an
unrelated record: R5 skipped (o09), base `ensures \result == 1` broken by an override returning 2 (o10), no inherited invariant (o11), o13-o16.
Same-file (distinct from the declared imported-base residual).
Repair: resolve a base expression to a class of the file when it is a provable alias (Name bound once to a class); REFUSE any class whose base
expression is not a plain class name / resolvable alias / known builtin or library base (calls, conditionals, unpacked aliases, annotated
aliases, attribute chains that do not resolve).

## REPAIR (2026-10-24, r341 executor off 8984dce3; code 88a8a4c7, corpus 0904473f, census/audit 41dddc52, docs 83deebdc + route docs)
**Design: sound refusal, not resolution.** One inline block in `_run_pipeline` after the resolved-IR boundary validation (mirror twin
`\trusted`; no new def; no emission change; ledger 3). About twenty independent readers of `ClassDef.bases` (Module 3 / 5 / 6, the
`_run_pipeline` checks of routes #175/#216/#264/#305/#330/#333/#334/#338 ...) take a base by `b.id` / `b.attr`; resolving an alias at
one of them leaves the others reading an unknown (imported-looking) name, and R5 / #278 SKIP such a pair — so a partial resolution
would keep o09/o10 open. CENSUS (both corpora, 53 mirrors, `pycsl_lib`): 305 file-class names, 49 imported names, 48 builtin
exception / type names, 9 imported attribute chains, 3 `Generic[T]`, ZERO alias / call / conditional / other subscript bases (the
5 `pure_ast` `Constant` bases are a `globals()`-injected name, not an assignment). A refusal therefore moves nothing and closes
every shape. RULE (`PYCSL-R341-CLASS-BASE-NOT-A-NAME`), per base of every class of the file: a bare name is admitted unless the file
also binds it otherwise than by `class` / import (any store / del `Name`, a `def`, a parameter, an `except` / `match` capture); an
attribute only as a dotted chain rooted at an imported name never rebound; a subscript only on `Generic` / `Protocol`; anything
else refused. Annotations §7.25 (1), translational §T.6.36.
**Probe table** (full pycsl proof via heavy.sh; base = 8984dce3 worktree; CPython 1 = the `__main__` assertion fails):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| o09 alias base, float override of `-> int` (R5) | 4550 | violates | rc=0 PROVED | rc=1 REFUSED R341 |
| o10 alias base, override returns 2 under `ensures \result == 1` | 4551 | violates | rc=0 PROVED | rc=1 REFUSED |
| o11 alias base, inherited invariant dropped | 4552 | violates | rc=0 PROVED | rc=1 REFUSED |
| o13 `class S(base())` | 4553 | violates | rc=0 PROVED | rc=1 REFUSED |
| o14 conditional base (corpus: `B if False else B`; the self-import needs a non-digit module name — the original witness file is REFUSED too) | 4554 | violates | rc=0 PROVED | rc=1 REFUSED |
| o15 `Base, Other = B, int` | 4555 | violates | rc=0 PROVED | rc=1 REFUSED |
| o16 `Base: Type[B] = B` | 4556 | violates | rc=0 PROVED | rc=1 REFUSED |
| control: direct `class S(B)`, unrelated alias used as a value | 4572 | ok | rc=0 | rc=0 PROVED |
**Blast radius**: root 2239 base / 2244 candidate 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref 2186/2186 0/0/0; mirror
53/53 0/0/0 — no OWED proof, no latent false proof. **Gates**: see route #342 (shared block, shared gate run).
**Residuals.** (1) Over-refusal: a provable alias (`Base = B` bound once) is refused, not resolved (0 users measured). (2) A base
name injected without an assignment (`globals()["Base"] = B`, `exec`) is not seen (as for every name the file does not bind
syntactically) and is treated as an unknown/imported base. (3) `me.B` through a SELF-import resolves by its tail `B` (pre-existing;
correct when `me` is this module). (4) Class keywords (`metaclass=`), `__init_subclass__`, `__mro_entries__` are not modelled.
