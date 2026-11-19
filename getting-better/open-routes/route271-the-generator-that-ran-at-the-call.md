# OPEN ROUTE #271 — CALLING A GENERATOR FUNCTION RUNS ITS BODY EAGERLY IN THE MODEL

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 4; driver-reproduced at HEAD eced7036 (rc=0; CPython 0).
Witness `witnesses-r271/h05_gen_method_field_eager.py`: method `bump(self) -> Iterator[int]` does `self.n += 1;
yield 0`; `c = C(); c.bump(); return c.n` proves `\result == 1`. `yield` lowers to `let _ = (any int) in ()` and the
function becomes an eager unit procedure whose `ensures self.n == old + 1` (itself false in Python) is applied at the
call.
Repair: a function containing `yield` must not be emitted as an eager procedure: refuse generator functions with
side effects / contracts about state (fail-closed), or model the call as returning an opaque generator with NO
effect, the body's effects happening only on iteration (refuse iteration unless modelled).

## REPAIR (2026-10-17, branch r270 off c9d7f157, landed with #270) — FAIL-CLOSED

**Rule** (inline in `pycsl.py::_run_pipeline`, right after route #257's `with` whitelist; mirror twin `\trusted`;
no new `def`). A COUNTED generator is a `def` with its OWN `yield`/`yield from` whose body is LOWERED (not
`\trusted`/`\abstract`, not nested in one) and that no dedicated generator model recognizes (Module 6's R-W2b
`recognize_walk_dicts_generator`, which lowers `_walk_dicts` onto a `list pyval` — exempt). For each:
- **(G1)** its own contract may not carry an `ensures` other than `True`, a `raises`, an interface `ensures`, or a
  `NoReturn`/`Never` return (`PYCSL-SEM-GENERATOR-CONTRACT`). `requires` and `assigns` stay: a precondition only
  burdens callers, and any frame over-approximates a call that writes nothing.
- **(G3)** it may not be invoked IMPLICITLY: a special-method name (`__init__`, `__iter__`, ...) or a decorator other
  than `staticmethod`/`classmethod`/`*contextmanager` (e.g. `@property`) is refused (`PYCSL-SEM-GENERATOR-IMPLICIT`).
- **(G2)** it may not be CALLED, or used as a VALUE (`h = gen`, `map(gen, xs)`, a bound method `h = c.bump`),
  from lowered code, except as the
  context expression of a `with` item — Module 5 lowers a bare `with` to its body alone, so that call is never
  emitted, and route #257 vets the producer (`PYCSL-SEM-GENERATOR-CALL`). `self.m(...)` in class K resolves through
  K's in-file bases (a non-generator `m` found first is not a generator call unless an in-file subclass of K overrides
  `m` with a generator); any other `x.m(...)` is matched by NAME against every counted generator method.
The `if __name__ == "__main__":` block is not lowered and not checked. `async def` never reaches the IR (0974's
refusal). Calls to a `\trusted` generator apply its reviewed contract (TCB, as every `\trusted`).

**Probe table** (c9d7f157 -> after; CPython column is the ground truth):

| file | shape | base | after | CPython |
|------|-------|------|-------|---------|
| witnesses-r271/h05 | generator method `ensures self.n == \old(self.n)+1`; `c.bump(); return c.n` == 1 | PROVED | REFUSED (G1) | 0 |
| 2905 | h05 as a corpus witness | PROVED | REFUSED (G1) | 0 |
| 2906 | no claim; `g.bump()` on a MODULE-GLOBAL instance is INLINED (inline.md), `ensures g.n == 1` | PROVED | REFUSED (G2) | 0 |
| 2907 | `def gen() -> int: yield 1; return 3`, `ensures \result == 3`; `return gen()` | PROVED | REFUSED (G1) | a generator |
| 2908 | generator `__init__` sets `self.n = 5`; `C().n == 5` | PROVED | REFUSED (G3) | TypeError |
| 2909 | control: 2905 with `bump` an ORDINARY method | PROVED | PROVED | 1 |
| 2910 | control: uncalled generator with only `requires`/`assigns` | PROVED | PROVED | — |
| 2911 | control: `self.block()` on a class whose `block` is ordinary, beside a generator `block` used only as a `with` item (the mirror's `_Parser`/`_Unparser` shape) | PROVED | PROVED | 2 |
| 2912 | control: the advice followed — a `list`-returning function iterated | PROVED | PROVED | 2 |
| 1031 / 2670 | existing `@contextmanager` controls used only as `with` items | PASS | PASS | — |
| probes | `h = bump; h(c)`, `map(gen, xs)`, `@property` generator, generator `__iter__` | type-error / FAIL | REFUSED | — |
| probe | 2906 with `h = g.bump; h()` (bound-method value) | — | REFUSED (G2) | 0 |

**Blast radius** (census over corpus + mirror + `pycsl_lib` with Modules 1-3, then the real pipeline): 11 generator
defs. Corpus: 1031 `blk` and 2670 `delimit` (with-items only, no claim) PASS kept; 2661/2664 `bump` (G1) keep #257's
earlier refusal (message unchanged); python-reference 0061/0141/0175 nested `gen()` called by name were already FAIL
and emit nothing either side; `multi_file_lib/r257_boxlib.py` / `r257_bumplib.py` — library helpers imported only by
the FAIL witnesses 2662/2663 (whose refusal is unchanged) — are now refused when run STANDALONE (G1: their
`ensures self.n == \old(self.n) + 1` on a `@contextmanager` generator is false of a call); no suite runs them
directly. Mirror: `ir_inline._walk_dicts` recognized (exempt); `pure_ast.iter_fields` called only from the `\trusted`
`iter_child_nodes`; `_Unparser.block`/`delimit` are `ensures True` and used only as `with` items; the 15
`self.block()` calls in `_Parser` resolve to `_Parser.block` (ordinary) — mirror 53/53 0 MOVED / 0 GONE.
`pycsl_lib/json/encoder.py`: already refused (Module 3), unchanged.

**Residuals** (stated): a generator IMPORTED from another file is a `trusted` dependency like every import — its
contract is applied at the call, and only its OWN run refuses it under G1-G3; a generator reached through a
dynamic path G2 cannot name (stored in a container field, returned by another function, passed through `getattr`) is
not tracked, though every such path first needs a G2-refused reference (a name, call or bound-method value); iteration over an `Iterator`-typed PARAMETER
is outside this route (it involves no generator function's body).

**Gates** (logs under the executor scratchpad `r270/`): witnesses base/after `wit/summary.txt`; corpus root 1755 ->
1760 .mlw (+5 new PASS controls 2904/2909/2910/2911/2912), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186/2186 0 MOVED /
0 GONE; mirror 53/53 0 MOVED / 0 GONE (no mirror re-proof owed); refusal-witness census +7 own rows (via the plane's
`_census_row`), 229 demonstrated / 5 undemonstrated; advice audit +3 FOLLOWABLE (route #271's three messages);
`run-soundness-planes.sh` 61/61 and `--slow` 84/84 green; `check-self-annotate-sync.sh`,
`self-annotate-mirror-check.sh`, `check-mirror-coverage.py` rc=0. Ledger 3 (no axiom), no new `def`.
