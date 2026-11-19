# Wall: `str(<int>) -> string` value-model (gates the Module6 emitter string-helpers + fstring)

**Status:** state-of-the-art wall statement (U). Awaiting an INDEPENDENT fable review with an oracle artifact.
**Base loop:** self-tcb-reduction of the PyCSL self-annotation mirror, branch ghost-assign-bc6, HEAD 5e7af18b, count 1043, ledger 3.
**Author:** driver (may be tainted — the fable reviewer must independently CONFIRM/REFUTE from the repo + oracle).

## 1. Context — the reachable frontier is exhausted; this is the next wall
The entire Module5 AST→IR lowering surface is converted (~1176→1043). A probe of the Module6 WhyML emitters
(`module6_whyml/expressions.py` ~52 trusted, `statements.py` ~47) found: the ExprIR-typed shallow-projection
emitters are ALREADY converted; what remains trusted is (a) int-erased deep-`.get("type")`-dict-reflection
handlers (a separate generic-dict wall) and (b) **~13 pure-string helpers** (`_coerce_to_int`,
`_str_operand_to_int`, … `whyml_str: string -> string`, duplicated across the two files' mixins) that fail
to TYPECHECK on conversion because of ONE gap:

## 2. The claim to adjudicate (CONFIRM or REFUTE with an oracle artifact)
**CLAIM A (the gap):** Python `str()` is modeled as `val str_conv (x: int) : int` (int→int). So a handler body
`return str(stable_hash(whyml_str))` lowers to `Return_str (str_conv (stable_hash x))` — an **`int` fed into a
`string` return channel** → hard typecheck error ("This expression has type int, but is expected to have type
string"). The faithful model is `str(<int>) -> string` (Why3 has an int→string conversion). (A secondary gap:
tuple-of-string literals like `("(Array.make", ...)` collapse to `int 0`.)

**CLAIM B (corpus-inertness — the crux for whether this is cheap or the big no-more-int project):** grep shows
**0 committed corpus `.mlw` reference `str_conv`** — suggesting `str()`-in-a-string-context is emitted ONLY by
the Module6 emitter's own helpers (building WhyML identifiers via `str(stable_hash(...))`), NOT by reference
corpus programs. IF SO, replacing `str_conv: int→int` with a faithful `str_of_int: int→string` (and gating so
any corpus `str()` usage is unaffected) is **corpus-byte-diff-0** and unlocks the ~13 string helpers +
`_py_expr_fstring` (`str(v.value)`) — a cheap ~15-30 marker cluster. If corpus programs DO emit `str_conv` in a
string context, this becomes the corpus-affecting "no-more-int" value-model project (EXTREME RIGOR, multi-session).

## 3. The question for fable (Gate R)
1. **CONFIRM CLAIM A** — with an oracle artifact (port one `-> str` helper that does `str(<int>)`, emit its `.mlw`,
   show the int-in-string-slot typecheck error; and inspect how `str_conv`/`str()` is emitted in
   `src/pycsl/module6_whyml/`).
2. **CONFIRM or REFUTE CLAIM B (corpus-inertness)** — the decisive question. Does ANY reference corpus program
   emit `str_conv` / rely on `str()`-returning-a-string? (Run `bin/byte-diff-sweep.sh`, grep the swept `.mlw` for
   `str_conv`; or emit a corpus program that calls `str(x)` and check.) Determine whether a faithful
   `str_of_int: int→string` model can be introduced CORPUS-BYTE-DIFF-0 (only the emitter helpers change), or
   whether it perturbs corpus emission (→ the big no-more-int build).
3. **VERDICT: CHEAP-BREAKABLE** (corpus-inert `str_of_int` model → est. yield across expressions.py +
   statements.py + fstring) / **BIG-BUILD** (corpus-affecting no-more-int value-model, authorize-first) /
   **BOUNDARY** (the string helpers have other blockers beyond `str(int)` — e.g. the tuple-of-string literals or
   `stable_hash` itself). If CHEAP-BREAKABLE, sketch the make-or-break spike (one helper → real `string` result,
   whole-file proof, corpus byte-diff 0).

## 4. Constraints (base-loop L)
Fixed contract shape; 3-axiom ledger unchanged (a `str_of_int` is a Why3-library/definitional function, NOT a new
axiom — verify); corpus byte-diff 0 is the make-or-break for the CHEAP verdict; whole-file proof is the gate
(`--fun` unreliable — see `config/skills/self-tcb-reduction/emit-ir-conversion-lessons.md` §1). Non-vacuity via an
observational fixture if a value is observed.
