# Wall-plan-v2 Phase 2′a — target-shape feasibility spike: **GO** (2026-07-07)

Make-or-break spike for the SHARPENED wall of Phase 2 (`wall-plan-v2-phase2.md`):
**essential-generic `.items()` iteration + unbounded recursion over the universal value**,
plus benchmark-1's `List[Dict[str,Any]]` recursion with a string-building tail.

**Question:** hand-written as their TARGET WhyML, do the two full benchmark patterns
whole-body-prove under `requires True / ensures True / writes …` — i.e. is the emitter
LOWERING these patterns feasible, or is there a deeper obstruction?

**Verdict: GO.** Both S1 and S2 whole-body-prove — every VC (termination + type-safety +
frame) **Valid on Alt-Ergo AND Z3**, **no new axiom**, reusing only the Phase-0 lemma pack.
Both false twins stay **unproven** on both provers. The sharpened wall is *lowerable*: the
obstruction Phase 2 hit was integration-not-built, not a deeper semantic impossibility.
The emitter build (Phase 2′b) is authorized.

Constraints honoured: SPIKE only — **no `src/pycsl`/mirror edit** (`git status --short
src/pycsl/ src/self-annotate/` filtered = empty); `\trusted` count **1248** unchanged;
`why3-semantics`/`src/formal-semantics` untouched; **0** `axiom` declarations
(`grep -nE '^\s*axiom\s'` = none in both fixtures; the only textual "axiom" hits are prose
comments). System `why3` 1.8.2, Alt-Ergo + Z3.

---

## S1 — `v2_iter_mutate_spike.mlw` (benchmark 2: `find_named_expr_targets`) — THE MAKE-OR-BREAK

Target lowering: `let rec walk (v: pyval) (targets: ref (map string bool))` with a mutual
`walk_dict` iterating the `pydict` cons spine (the generic `.items()` protocol) and `walk_list`,
recursing into each heterogeneous value, mutating the by-ref set (WL-05b / E5 `writes { targets }`),
reading `obj["target"]` via `get_target` (E2 literal-schema-key read, lowered as a direct
`K_target`-constructor spine match — R-B: zero `=`, zero string theory), all under
`requires True / ensures True / writes { targets } / variant { size v | size_dict d | size_list xs }`.

**Commands**
```
why3 prove -P alt-ergo test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw
why3 prove -P z3      test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw
```

**Per-VC (verbatim)** — mechanism: **direct `size`-variant** (Phase-0 +1-per-cons measure + nonneg pack):

| Goal | Alt-Ergo | Z3 |
|---|---|---|
| `get_target'vc`      | Valid (0.08s, 342 steps)   | Valid (0.01s, 1295 steps)    |
| `size_pos'vc`        | Valid (0.08s, 497 steps)   | Valid (0.02s, 23133 steps)   |
| `size_list_nonneg'vc`| Valid (0.06s, 239 steps)   | Valid (0.01s, 14299 steps)   |
| `size_dict_nonneg'vc`| Valid (0.07s, 248 steps)   | Valid (0.02s, 15540 steps)   |
| **`walk'vc`**        | **Valid (0.08s, 221 steps)** | **Valid (0.02s, 21408 steps)** |
| **`walk_dict'vc`**   | **Valid (0.07s, 120 steps)** | **Valid (0.02s, 15903 steps)** |
| **`walk_list'vc`**   | **Valid (0.04s, 115 steps)** | **Valid (0.01s, 14653 steps)** |
| `driver'vc` (frame escapes) | Valid (0.05s, 45 steps) | Valid (0.01s, 1702 steps) |

The three make-or-break VCs (`walk'vc` / `walk_dict'vc` / `walk_list'vc`) carry, together in one
mutual group: generic iteration + unbounded recursion into the universal value + by-ref mutation +
termination + frame. **All Valid on both provers.** The by-ref set frame threaded through the whole
mutual-recursion group discharges cleanly (WL-05b/E5 scales to the recursive walk).

**False twin** `walk_bad` — claims `variant { size v }` but recurses on `PDict d` itself
(`size (PDict d) ≮ size (PDict d)`, a genuinely false VC):
- `walk_bad'vc`: **Timeout (5.00s)** on Alt-Ergo (45212 steps) AND Z3 (4562588 steps) → **stays UNPROVEN** ✓.
  The shape can fail; the model can say no.

---

## S2 — `v2_listdict_recurse_spike.mlw` (benchmark 1: `find_return_type`)

Target lowering: `let rec find_rt (stmts: list pyval) : doc variant { size_list stmts }` recursing
over `List[pydict]`, reading keys via `get_type`/`get_body` (E2 literal-key constructor matches),
descending into the nested `stmt["body"]` list, and building the `", "`-join tail as a **`doc`-ADT
`DCat` fold** (F4) so **no walker VC contains a string term**. `find_return_type` renders once to a
`string` via a program `render` whose only VC is termination (string payloads stay opaque; program
`concat` from `string.OCaml`). Nested-recursion termination discharged by the **PROVEN sub-term lemma
`get_body_lt`** (`get_body d = Some b → size_list b < size_dict d`) — `let rec lemma`, NO axiom.

**Commands**
```
why3 prove -P alt-ergo test-suite/corpus/conformance/spikes/v2_listdict_recurse_spike.mlw
why3 prove -P z3      test-suite/corpus/conformance/spikes/v2_listdict_recurse_spike.mlw
```

**Per-VC (verbatim)** — mechanism: **direct `size_list`-variant + proven `get_body_lt` sub-term
lemma**; string tail carried by the **`doc` ADT** (no SMT string-theory goal anywhere):

| Goal | Alt-Ergo | Z3 |
|---|---|---|
| `size_pos'vc`        | Valid (0.11s, 523 steps)  | Valid (0.02s, 32340 steps) |
| `size_list_nonneg'vc`| Valid (0.06s, 253 steps)  | Valid (0.02s, 23442 steps) |
| `size_dict_nonneg'vc`| Valid (0.06s, 261 steps)  | Valid (0.02s, 24797 steps) |
| `get_type'vc`        | Valid (0.13s, 555 steps)  | Valid (0.01s, 2364 steps)  |
| `get_body'vc`        | Valid (0.21s, 879 steps)  | Valid (0.02s, 25240 steps) |
| **`get_body_lt'vc`** (sub-term lemma) | **Valid (0.67s, 3183 steps)** | **Valid (0.03s, 38752 steps)** |
| `render'vc`          | Valid (0.08s, 198 steps)  | Valid (0.02s, 30906 steps) |
| **`find_rt'vc`**     | **Valid (0.08s, 221 steps)** | **Valid (0.02s, 33753 steps)** |
| `find_return_type'vc`| Valid (0.05s, 52 steps)   | Valid (0.01s, 2963 steps)  |

`find_rt'vc` (the read-and-recurse walker with the nested `stmt["body"]` descent) is **Valid on both
provers**; its termination rests on `get_body_lt`, discharged as a proven lemma — not an axiom. The
`doc` ADT kept every walker VC string-free (confirmed: no goal invokes string theory; the 26–30 s
`", ".join` timeout Phase 2 measured is eliminated).

**False twin** `find_rt_bad` — claims `variant { size_list stmts }` but recurses on `stmts` itself
(`size_list stmts ≮ size_list stmts`):
- `find_rt_bad'vc`: **Timeout (5.00s)** on Alt-Ergo (47319 steps) AND Z3 (3208774 steps) →
  **stays UNPROVEN** ✓.

---

## No-axiom check

```
$ grep -nE '^\s*axiom\s' test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw \
                          test-suite/corpus/conformance/spikes/v2_listdict_recurse_spike.mlw
(no output — 0 axiom declarations)
```
Both fixtures reuse only the Phase-0 lemma pack (`let rec lemma` size_pos / size_list_nonneg /
size_dict_nonneg) plus, in S2, one further proven `let rec lemma get_body_lt`. Zero `axiom` keyword.

---

## Overall verdict: **GO**

Both benchmark patterns, hand-written as their target WhyML, whole-body-prove on **both** provers with
**no new axiom**, and both false twins stay unproven. The three feasibility risks Phase 2 pinned are
each discharged:

1. **Generic `.items()` iteration + unbounded recursion + by-ref mutation (S1, the make-or-break):**
   feasible. A mutual `walk` / `walk_dict` / `walk_list` over `pyval`/`pydict` with per-function
   `size`/`size_dict`/`size_list` variants proves termination + type-safety + a threaded
   `writes { targets }` frame, on both provers.
2. **`pydict`-param termination-variant synthesis + nested-key recursion (S2):** feasible. A
   `size_list` variant + one proven sub-term lemma (`get_body_lt`) discharges the recursion that reads
   `stmt["body"]` and descends into it.
3. **String tail without string theory (S2, F4):** feasible. The `doc` ADT keeps every walker VC
   string-free; `render` is a boundary program function whose sole VC is termination.

**This authorizes the emitter build (Phase 2′b):** the E-iteration rule (lower
`for k, v in d.items()` to a `walk_dict`-shaped cons-spine recursion), termination-variant synthesis
over `pydict`/`list pyval` params (generalize the ADT-gated `size`-variant at `functions.py:1101` to
these shapes), E5-for-methods (WL-05b by-ref frame threaded through a mutual-recursion group), and the
`doc`/str-op modeling for the emitted string tail. The literal-schema-key read (E2) lowers as a direct
key-constructor spine match (no program-level polymorphic `=`, which WhyML does not provide — a
concrete emitter constraint surfaced by this spike).

## Fixtures & artifacts
- `test-suite/corpus/conformance/spikes/v2_iter_mutate_spike.mlw` (S1)
- `test-suite/corpus/conformance/spikes/v2_listdict_recurse_spike.mlw` (S2)
- reuse: `test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw` (Phase-0 encoding + lemma pack)
