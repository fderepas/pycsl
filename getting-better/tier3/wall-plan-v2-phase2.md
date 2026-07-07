# Wall-plan-v2 Phase 2 — verified NO-GO on the whole-body acceptance criterion (2026-07-07)

**Independently verified** (re-run against HEAD `0353e061`, count 1248, tree clean, ledger==3).

## Verdict: Phase 2 is a measured NO-GO — 0 of 2 benchmark methods whole-body-prove

The v2 approach's **foundation is proven and certified** (Phase 0 refuted the fmap NO-GO; Phase 1 landed
the `pydict`/`pyval`/`irkey`/`size`/`wf_ir`/`doc` theory with **axiom-free Rocq 8.20 + Lean 4.29
certificates, ledger held at 3**, and a proving `irx.py` accessor). But the **integration (routing rules
E1–E5) that connects the foundation to real walkers does not, as specified, convert either frozen
benchmark method** — and the reason sharpens the open problem rather than closing it.

## What is verified

- **E1/E2/E4 are not wired.** `needs_pydict` is set nowhere outside `preamble.py` (grep = 0), and there
  is no `key_of_string` / `get n K_*` / `is_PStr` read-routing in `expressions.py`/`types.py`/`statements.py`.
  The certified theory is **inert dead code** at HEAD.
- **Benchmark 1 — `find_return_type(stmts: List[Dict[str,Any]]) -> str`: FAILS.** Verbatim body fails with
  the plan's own `array int` vs `int` (the recursive `stmt[key]` read lowers as `array int` in the default
  int-model), **plus** 6× "termination cannot be proved" (the emitter lowers the nested walkers + outer
  recursion as WhyML `rec` **without a `variant`**), **plus** a 26–30 s timeout on `", ".join(["int"]*n)`
  (string-op modeling). To prove verbatim it needs **three** unbuilt features at once: E1+E2 pydict read
  routing, **D3 program-form termination-variant synthesis over `pydict`** (the existing
  `variant { size p }` synthesis at `functions.py:1101` is gated to the certified ADT param types
  `ExprIR`/`StmtIR`/`IRNode`, and does **not** fire for `List[Dict[str,Any]]`), and str-op modeling.
- **Benchmark 2 — `find_named_expr_targets(obj, targets: Set[str])`: FAILS — the key finding.**
  1. As a staticmethod it is hard-**rejected** on `targets.add(...)`: E5 (WL-05b, `612cbb2e`) exists but is
     deliberately scoped to standalone functions and **excludes methods** (`functions.py:322-324`).
  2. Past that exclusion (standalone form), the mutation is handled and the **next wall is the real one**:
     `for k, v in obj.items()` emits **broken WhyML** (`unbound … 'k'`). There is **no lowering for generic
     `.items()` iteration over a heterogeneous dict + recursion into each `v: Any`.** This is
     **essential-generic reflection** — recursion over an *unbounded* heterogeneous shape — for which
     neither E1–E5 nor the emitter has a bounded construction.

## The sharpened wall (what an external reviewer should now be asked)

The v2 work **narrows the wall**. The original question — "how to model a generic `Dict[str,Any]` value
in WhyML" — is **answered** (Phase 0/1: `pydict` is sound, SMT-tractable via compute-before-solve +
interned keys, and certified axiom-free). The **residual, sharper** question is:

> **How do you lower, and prove *terminating* under a type-safety-only contract, a generic
> `for k, v in d.items()` walk that recurses into each heterogeneous value `v` — i.e. a `pydict`
> *iteration protocol* with a synthesized `variant { size v }` decrease over the universal value —
> when the walk's recursion shape is unbounded and schema-agnostic?**

Plus the two supporting emitter features benchmark 1 needs: **program-form termination-variant synthesis
over `pydict` params** (generalize the ADT-gated `size`-variant to `pydict`), and **string-op modeling**
for the emitted-string builders (or the F4 `doc` ADT so no walker VC touches strings).

## What v2 delivered vs where it stopped

- **Delivered & banked (real assets):** the certified universal-value foundation (`pydict` theory +
  axiom-free Rocq/Lean certificate, ledger==3), the `wf_ir` generator, the proving `irx.py` accessor, and
  the **refutation of the fmap NO-GO** (compute-not-axiomatize works for the encoding). Count held at 1248,
  baseline genuinely green at 34/34.
- **Stopped at:** the integration. E1–E5 as written are **insufficient**; the true boundary is
  **essential-generic iteration + unbounded-recursion termination over the universal value**, not the
  value type. This is the honest Phase-2 result — a NO-GO on the acceptance criterion, with the boundary
  pinned.

## Options from here
1. **Extend to Phase 2′:** build the missing features — a `pydict` iteration protocol with synthesized
   `size`-variant (benchmark 2), generalize the termination-variant synthesis to `pydict` params +
   str-op/`doc` modeling (benchmark 1), and E5-for-methods. A larger, uncertain build that would be the
   real test of whether the *sharpened* wall falls.
2. **Bank the certified foundation and close v2:** accept the essential-generic reflective walkers as
   `TRUSTED(essential)`, keep the banked foundation, and fold the sharpened question into the external-
   review problem statement (`generic-dict-str-any-2.md`). The foundation stands for any future attempt.
