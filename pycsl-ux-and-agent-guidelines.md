# PyCSL — A User's Field Report and Guidelines

**Author vantage point:** I cloned `fderepas/pycsl` at `main`, installed it (`libcst` + `lark`,
then `pip install -e . --no-deps`), and ran `pycsl --no-proof --keep-mlw` across roughly a dozen
hand-written files — datatypes, recursive and mutually-recursive functions, quantifiers, spec
functions, recursive predicates. I read `SKILL.md` and its reference files, and I grepped the
reference corpus heavily. I could exercise the **front end** (parse → typecheck → WhyML
generation); I could **not** run the SMT backend (no `why3`/`alt-ergo`/`z3` in my environment).
These guidelines come from that hands-on experience, with each one tied to something I actually hit.

---

## What already works well (keep it)

- **The corpus is excellent.** Numbered `test-suite/corpus/pycsl-reference/NNNN.py` files, each with
  a docstring stating *what it tests*, and many with PASS/FAIL twins, were my most reliable way to
  learn what the tool actually supports. This dual-test discipline is genuinely good.
- **`#@`-as-comments is elegant.** Files stay valid Python and parse via libcst; the contract layer
  is invisible to the interpreter. The "where is `Json` defined in pure Python? — nowhere" property
  is a feature, not a bug.
- **Light dependencies.** Once the path was right, install was trivial.
- **A principled assume/prove spectrum.** `\trusted` (assume), `#@ proof` (external, audited), and
  the three-level validation story are conceptually clean.
- **`--no-proof` as a fast loop** is the right idea — it just over-promises (see G2).

---

## Part A — Improving the user experience

### A1 (Highest priority). Make every "success" signal mean what it says.
**What I hit:** `--no-proof` reported `Verification SUCCESS (WhyML generated, proof skipped)` for
contracts whose generated WhyML was **ill-typed** and would be rejected by Why3 — e.g. a quantifier
over a datatype emitted `Array.length x` on a `json`, and `\forall j; sum_numbers(j)` emitted
`forall j : int` then applied a `json -> int` function to an `int`. The front end was green; the
output was unsound.
**Guideline:** Add a real `--typecheck` mode that runs Why3's *typechecker* on the generated `.mlw`
and gates the success message on it. Reserve the word "SUCCESS" for something verified. Until then,
`--no-proof` should print explicitly: "Levels 1–2 only; WhyML not typechecked, not proved."

### A2. Never silently drop or mis-lower an annotation.
**What I hit (two cases):** (1) the documented blank-line trap — a blank line between `#@` and `def`
"silently drops all contracts for that function"; (2) an un-annotated/datatype quantifier binder
silently became `forall i : int`.
**Guideline:** Both are silent correctness failures, the worst kind. A `#@` line not adjacent to the
construct it annotates should be an **error**, not a silent drop. A binder whose type can't be an
`int` (used as a datatype value) should be an **error**, not a silent default. Silence here actively
misleads.

### A3. Fix packaging so the CLI runs out of the box.
**What I hit:** `python3 src/pycsl/pycsl.py` failed with `ModuleNotFoundError: No module named
'pure_ast'`; I needed `PYTHONPATH=src`. The console-script entry point works, but direct invocation
(the natural first thing a new user tries) doesn't.
**Guideline:** Use package-relative imports (`from . import pure_ast`) so the module runs both as a
script and via the entry point. First-run friction sets the tone.

### A4. Turn internal crashes into diagnostics.
**What I hit:** adding a `#@ proof` line citing a non-existent lemma crashed with
`UNEXPECTED PIPELINE ERROR: name 'PyCSLIRError' is not defined` — an unhandled exception in the
error path. The guardrail *worked* (it should reject), but via a stack-trace-style crash.
**Guideline:** Every rejection path should raise a defined, caught error that prints a clean message
("`#@ proof` cites `X`, which has no reconciled Rocq/Lean artifact"). An exception class that isn't
defined is itself a bug on the most user-facing path.

### A5. Clean up the emitted WhyML.
**What I hit:** generated `.mlw` carried a block of dead `val constant head : int`, `val constant n
: int`, … for match-capture names that are already bound (and shadowed) inside the `match` arms.
Harmless to the proof, but confusing to read and a trust smell.
**Guideline:** Don't emit module-level abstracts for names that are pattern-bound. Readable WhyML is
part of the UX — users *do* read `--keep-mlw` output when debugging.

### A6. Make output paths predictable and printed.
**What I hit:** `--keep-mlw` wrote `/tmp/json_sum.mlw` for a loose file but a `NNNN.proofs/NNNN.mlw`
subdirectory for a corpus file; I had to `find` for it.
**Guideline:** One documented rule for where artifacts land, and print the absolute path on stdout.

### A7. Report *which* validation level passed.
**What I hit:** the three-level model (syntax / static-semantics / WhyML-and-proof) is real and
important, but the output didn't say which level my run reached.
**Guideline:** End every run with an explicit status line per level (e.g. `L1 ✓  L2 ✓  L3 (typecheck)
✓  L3 (proof) skipped`). This is the single best antidote to the A1 false-green confusion.

---

## Part B — Making PyCSL more AI-agent-friendly

The meta-principle behind all of these: **an agent trusts the tool's output literally and will
confidently emit broken artifacts on a false signal.** So agent-friendliness is mostly about making
every signal loud, structured, and truthful.

### B1. Ship a machine-readable capability manifest.
**What I hit:** to learn what works I had to grep the corpus and read scattered references. The skill
said generics "fail today" (corpus 0540) but said *nothing* about mutually-recursive datatypes —
which **do** work (corpus 0533/0534). I only learned that by grepping. The authoritative knowledge
was split between prose docs and the corpus, with the corpus winning.
**Guideline:** Emit `pycsl --capabilities --json`: a versioned list of supported constructs
(datatype: recursive ✓, mutual ✓, polymorphic ✗), contract operators with arities, and known
limits. Generate it from the passing corpus so it cannot drift from reality. An agent should never
have to grep test files to answer "is X supported."

### B2. Structured, coded diagnostics.
**What I hit:** messages were prose, sometimes a crash. There was no stable error code or source span
to key off.
**Guideline:** `--json` diagnostics with `{code, level, message, file, line, col, rule_id,
suggested_fix}`. Stable codes (e.g. `PYCSL-L2-BINDER-DEFAULT-INT`) let an agent recognize and
auto-repair a class of error without parsing English.

### B3. A fast, trustworthy, offline typecheck.
**What I hit:** the only honest "is this well-formed" signal required the OCaml `why3` typechecker,
which isn't installed by default; `--no-proof` was fast but lied (A1). So an agent's quick edit-loop
had no trustworthy cheap signal.
**Guideline:** Provide a deterministic Level-3 *typecheck* that does not require a full solver
install (bundle or vendor the minimal Why3 typecheck, or replicate the type rules in-tool). Agents
iterate dozens of times; the cheap loop must be sound about types even if proof is deferred.

### B4. Expose the contract mini-language formally.
**What I hit:** the rules for `#@` expressions live across `forbidden-expressions.md` and others as
50+ NEVER rules (`**` forbidden, `\old(arr)` unsupported, `val`/`match` reserved, no bare function
calls, `==>` pitfalls…). I learned them by reading prose and tripping over them.
**Guideline:** Publish a formal grammar (EBNF) for the `#@` language plus a typed signature table for
every `\`-operator (`\length: array → int`, `\sum: array×int×int → int`, …). An agent can then
generate valid contracts by construction instead of guessing-and-checking against a prose blocklist.

### B5. Make the corpus an indexed, queryable asset.
**What I hit:** the corpus docstrings are gold ("Test 0528 — recursive function over a recursive
datatype…", "Test 0540 — `[T]` syntax fails today"), but only discoverable by opening files.
**Guideline:** Generate a `corpus-index.json` mapping feature → example IDs → expected outcome →
one-line description, from the docstrings. This is the highest-value, lowest-effort agent affordance
you have, because the corpus is already the de facto source of truth.

### B6. Whole-run machine output.
**What I hit:** results were human prose; an agent has to scrape them.
**Guideline:** `--json` run report: per-function and per-VC status, the validation level reached, the
`.mlw` path, and any dropped/defaulted-annotation **warnings** (B2 + A2 surfaced as data, never
silent).

### B7. Pin behaviour to a version.
**What I hit:** I cloned `main`; the exact emitter output (including the A5 dead block) reflects that
commit and could differ tomorrow. For reproducible agent runs that's a problem.
**Guideline:** Stamp every run and every capability manifest with a tool version/commit, and key the
corpus expectations to it.

---

## Priority ordering

If only a few things get done, do these — they are the ones that actively caused (or would cause an
agent to produce) wrong results:

1. **A1 / A7 — honest success signals + per-level status.** The false green is the single most
   dangerous behaviour I encountered.
2. **A2 — no silent drops or silent int-defaults.** Silent correctness failures are worse than loud
   ones, especially for an agent.
3. **B1 / B5 — capability manifest + corpus index, generated from the passing corpus.** Removes the
   "grep the tests to learn the truth" tax that I paid repeatedly.
4. **B2 / B6 — structured diagnostics and run reports.** The substrate for any agent self-repair.
5. **A3 / A4 — clean first-run and no internal crashes.** Table stakes for trust.

Everything else (A5 readability, A6 paths, B3 offline typecheck, B4 formal grammar, B7 versioning)
is high-value but secondary to "never lie, never go silent."

---

### One-line summary

The tool's ideas are sound and the corpus is a genuine asset; the friction is almost entirely about
**truthfulness of signals**. A human can absorb a false green or a silent contract drop with a raised
eyebrow; an agent will build a tower on top of it. Make every success mean *verified to a stated
level*, make every failure *loud and structured*, and generate the "what works" knowledge from the
corpus so it can never drift — and PyCSL becomes both pleasant for people and safe for agents.
