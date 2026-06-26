# `NoReturn` (PEP 484) — Two-Plane Spec

**Status:** Two-plane spec for the `NoReturn` construct. Authored by the
typing-spec-agent under the TY1 tier. Per `typing-global-impl.md` §5 item 2,
`NoReturn` carries the SHARPEST new TY1 obligation: its lowering produces a
`false` / `\diverges` postcondition, which is byte-identical — at the
non-vacuity gate (`--check-vacuity` / `bin/false-twin.py`) — to the signature
of a vacuously-green function. The spec must state how the gate EXEMPTS a
declared-`NoReturn` function from the vacuity probe; that exemption (clause
NR4) is the load-bearing clause of this document. Four sections that must NOT
be merged. Cites the S1–S7 authorities per §3.1 of `typing-global-impl.md`.
Proposes NO lowering (that is the core-agent's job); each static obligation
clause is stated so it maps to one VC or one S5 conformance case, and each
runtime claim is checked against S3's negative sentence resolved by S4.

**Authorities cited in this spec:**
- **S1** — the typing specification (typing.readthedocs.io, Typing Council /
  PEP 729). S1 defines `NoReturn` as the signal that a function never
  returns normally (it raises or diverges).
- **S2** — PEP 484 (introduces `typing.NoReturn`). S1 supersedes S2 on any
  conflict.
- **S3** — the library reference (`docs.python.org/3/library/typing.html`);
  central sentence is NEGATIVE: the runtime does not enforce annotations.
- **S4** — CPython `Lib/typing.py` observable behaviour (the runtime lower
  bound): `NoReturn` is an introspectable alias object; the runtime does not
  enforce divergence.
- **S5** — the typing conformance test suite (static executable ground truth).
- **S7** — PyCSL front-end current behaviour (TY0 baseline; see VERDICTS.md —
  S7 has NO existing arm for `NoReturn`; per `VERDICTS.md` S7's closest kin is
  S7's `-> None` disposition (IGNORED for non-lemma functions), which is
  related but DISTINCT: `None` says "returns the `None` singleton", `NoReturn`
  says "does not return").

**Related construct:** `-> None` (TY0-witness S7, VERDICTS.md §4): the
front-end currently IGNORES `-> None` for non-lemma functions (emits
`-> int`). `NoReturn` is distinct: it is not a return-value claim but a
no-normal-return claim. No S7 witness for `NoReturn` exists today — every
`NoReturn` annotation is silently dropped to default `int` by S7, which this
spec corrects at TY1.

**Prior art in the codebase:** the `#@ \diverges` directive
(`Module2_Parser.py:302`, `Module3_Weaver.py:265`,
`core_ir_semantic.py:659` `_check_diverges`,
`module6_whyml/functions.py:292` emits the WhyML `diverges` effect,
`module6_whyml/preamble.py:2310` justifies it) is the PyCSL-native spelling
of the same claim. `NoReturn` is the typing-surface spelling of that
directive; the two share the same IR `diverges` flag (`ir_schema.py:80`)
and the same Module 6 emission (`    diverges`). The non-vacuity gate's
`_probe_one` (`pycsl.py:849`) injects `ensures { [@expl:vacprobe] false }`
into every body-bearing `let` and flags a function whose injected
`false`-goal proves Valid; this is the exact interaction NR4 resolves.

---

## 1. STATIC PLANE

The static plane treats `-> NoReturn` as a JUDGMENT ABOUT THE FUNCTION'S
CONTROL FLOW, not about a return value: a `NoReturn`-annotated function
does not return normally — it either raises or diverges. The negation of
"returns normally" is exactly the `false` postcondition: at every normal
exit the function must NOT be at a normal exit, i.e. `false`. Nothing here
claims anything happens at runtime; runtime claims live in §2.

### 1.0 Definitional lowering

- **NR1 (false postcondition — the load-bearing static clause).** A function
  annotated `-> NoReturn` carries the postcondition `false`: it never
  returns normally. Formally, at every NORMAL-EXIT path of the body the
  function's postcondition is `false` (equivalently `ensures { false }`).
  This is S1's meaning of `NoReturn` (PEP 484, S2): the type has no
  inhabitants, so a function returning a value of type `NoReturn` cannot
  exist. — *cites S1, PEP 484 (S2).* The clause maps to one VC: the
  WhyML `ensures { false }` goal per normal-exit path, as the gate's
  `_probe_one` already emits per `pycsl.py:870`. This is the SAME
  obligation shape the non-vacuity gate INJECTS — see NR4.
- **NR2 (divergence — the alternative spelling).** The `false`
  postcondition (NR1) is equivalent, in PyCSL's IR, to setting the
  function's `diverges` flag (`ir_schema.py:80`, the same flag set by
  `#@ \diverges`). The obligation is: the function either raises (an
  exit handled by PyCSL's exception model — see
  `.claude/skills/pycsl-exception-model/SKILL.md`) or does not
  terminate (`#@ \diverges`, `core_ir_semantic.py:659` `_check_diverges`).
  The postcondition is the NEGATION of normal-return; both spellings
  (`ensures { false }` and `diverges` effect) discharge the same VC family.
  — *cites S1, PEP 484 (S2); cross-references the `#@ \diverges` IR seam.*
- **NR2a (body must support divergence).** Per `_check_diverges`
  (`core_ir_semantic.py:668`), a function carrying `diverges` MUST have a
  body with a potentially-diverging construct (`While`/`For`/`CriticalSection`
  /`Call`) or a guaranteed raise; a `NoReturn` annotation on a body that
  provably terminates is a static ERROR (the `false` postcondition is
  genuinely unprovable — not vacuous, just wrong). This rejects
  `def f() -> NoReturn: return 1` at the static plane. — *cites S1; cross-
  references `core_ir_semantic.py:675`.*

### 1.1 Unreachable successor

- **NR3 (dead-code report on the successor).** A statement immediately
  following a call to a `NoReturn`-annotated function is statically
  UNREACHABLE: the callee's `false` postcondition (NR1) makes the
  continuation path's path-condition contradictory. PyCSL reports this as
  dead code (the same dead-branch class `soundness-issue.md` §7 identifies
  — a dead branch proves `false` SOUNDLY, which is NOT vacuity). The
  successor is not a VC-failure; it is a static warning/error that the
  program contains code that cannot execute. — *cites S1; cross-references
  `soundness-issue.md` §7 item 3 (the dead-branch over-flagging
  precision gap, which is the dual problem: a dead branch is sound, but
  the gate must not treat its `false` proof as a vacuity signal).*

### 1.2 The vacuity-gate exemption (THE LOAD-BEARING CLAUSE)

- **NR4 (vacuity-gate exemption).** A function declared `-> NoReturn`
  carries the postcondition `false` BY DESIGN (NR1). The non-vacuity gate
  (`--check-vacuity`, `_probe_one` at `pycsl.py:849`) detects a vacuous
  context by INJECTING `ensures { [@expl:vacprobe] false }` into a
  body-bearing function and flagging the function if the injected
  `false`-goal proves Valid. A faithful `NoReturn` function ALREADY HAS
  a `false` postcondition; it is INDISTINGUISHABLE from a vacuous one
  under the gate's probe, and would be FALSE-POSITIVELY FLAGGED. The gate
  MUST EXEMPT declared-`NoReturn` functions from the vacuity probe.
  Mechanism (precise, so the core-agent can implement it):
    1. The exemption is KEYED ON THE `-> NoReturn` RETURN ANNOTATION —
       not on the inferred `false` postcondition (the latter would
       exempt every genuinely-vacuous function, defeating the gate).
       Concretely: the front-end normalization
       (`frontend/Module5_IREmitter.py`, the `return_annotation` capture
       arm — currently S7 captures `"None"` at `:1761`, the new
       `NoReturn` arm captures `"NoReturn"`) records the declared
       `NoReturn` on the IR function node.
    2. `_run_vacuity_gate` / `_function_body_eqs` (`pycsl.py:812`,
       `pycsl.py:829`) MUST SKIP any function whose IR carries the
       declared-`NoReturn` flag. The probe is not emitted for it; the
       function is treated as expected-false. This is sound because the
       `false` postcondition on a `NoReturn` function is the SPEC, not an
       inconsistency: the function's OWN proof (NR2a, the diverges
       obligation) establishes that it never reaches a normal exit, so
       the `false` postcondition is discharged by the absence of a
       normal-exit path, not by an inconsistent context.
    3. The exemption MUST NOT extend to (a) a function with a `false`
       postcondition for any OTHER reason (e.g. a dead-branch collapse —
       that is the `soundness-issue.md` §7 precision gap, addressed by
       the occurrence-keyed merge, NOT by this exemption), nor (b) a
       function whose `NoReturn` annotation is present but whose body
       provably terminates (NR2a rejects this BEFORE the gate runs).
  — *cites S1, PEP 484 (S2); `typing-global-impl.md` §5 item 2;
  `soundness-issue.md` §7.* NR4 is the sharpest new TY1 obligation:
  without it, every `NoReturn` function is a spurious vacuity failure.

### 1.3 Expressibility check (dischargeability, NOT a lowering proposal)

Each clause above is stated so it can be discharged by the PyCSL-native
mechanisms the core-agent already operates: NR1/NR2 map to the
`ensures { false }` VC family (the same goal the gate injects) and to
the `diverges` IR flag (`ir_schema.py:80`) emitted by
`module6_whyml/functions.py:292`. NR2a is discharged by
`_check_diverges` (`core_ir_semantic.py:659`). NR3 is the existing
dead-branch reporter. NR4 is a gate-level filter keyed on the IR flag
the front-end already records for `#@ \diverges`. The spec-agent
confirms each clause is dischargeable by these mechanisms; the choice
of which spelling (`ensures { false }` vs `diverges` effect) is the
core-agent's, and `NoReturn` introduces no new IR shape beyond the
existing `diverges` flag.

---

## 2. RUNTIME PLANE

The runtime plane says what `NoReturn` does when the program runs. S3's
central sentence is NEGATIVE: the Python runtime does NOT enforce
function and variable type annotations. So the runtime meaning of
`NoReturn` is almost nothing — it is an introspectable alias object,
not a check. A function annotated `-> NoReturn` that DOES return (a bug
in the program, undetected by the static plane iff the body is not
proven) returns at runtime without error.

### 2.1 `NoReturn` is a runtime alias object, not a check

- **NR-R1 (alias identity).** `typing.NoReturn` is a singleton object
  (`typing.NoReturn` is itself a special form, not a subscriptable
  generic). `NoReturn` as a return annotation evaluates to the
  `typing.NoReturn` object; it is NOT a distinct runtime type and it is
  NOT `None`. — *cites S3 (`typing.NoReturn`); resolved by S4
  (`Lib/typing.py`'s `NoReturn` special-form).*
- **NR-R2 (introspection).** A function `def f() -> NoReturn: ...`
  carries `f.__annotations__["return"] is typing.NoReturn`. The
  annotation is introspectable via `typing.get_type_hints` and on the
  raw `__annotations__` dict. `typing.get_origin(NoReturn)` is
  `typing.NoReturn`; `typing.get_args(NoReturn)` is `()`. — *cites S3;
  resolved by S4.*
- **NR-R3 (no enforcement — the central negative sentence).** The
  runtime does NOT check that a `NoReturn`-annotated function diverges
  or raises. A function annotated `-> NoReturn` that RETURNS a value
  (a program bug) returns at runtime without error; the runtime does
  not raise, does not warn, does not trap. The annotation is
  documentation, not a runtime contract. — *cites S3 (central negative
  sentence).*

### 2.2 Identity / shim faithfulness

- **NR-R4 (no validation in the shim).** Any `src/pycsl_lib/typing`
  surface for `NoReturn` must agree with S4: it constructs the
  introspectable alias object (the `typing.NoReturn` special form) and
  performs no validation of the function's control flow at runtime. A
  shim that CHECKED whether a `NoReturn`-annotated function actually
  diverged would be unfaithful in exactly the way an over-strong axiom
  is. — *cites S3, S4.*
- **NR-R5 (`NoReturn` is not `None`).** A faithful shim does NOT
  conflate `NoReturn` with `None`: the two are distinct at the runtime
  plane (`None` is a value, `NoReturn` is a type-marker that the
  function does not return). This mirrors the S7/TY0 distinction in
  `VERDICTS.md` §4 (where the front-end IGNORES `-> None` for non-lemma
  functions) and sharpens it: `NoReturn` is the no-return marker,
  `None` is a return-value marker. — *cites S3, S4; cross-references
  `typing-engagement/ty0-witness/VERDICTS.md` S7.*

---

## 3. DIVERGENCE

The two planes disagree, and the disagreement is permanent: neither
plane's claim may stand in for the other. Stating them as a single
contract is the canonical coherent-and-wrong failure (typing edition).
The `NoReturn` divergence is unusually sharp because the static claim is
NEGATIVE ("does not return") and the runtime claim is also negative
("does not enforce") — but the two negatives are about different things.

- **NR-D1 (false postcondition vs no enforcement).** The static plane
  (§1) treats `-> NoReturn` as a `false` postcondition (NR1): a proof
  obligation that the function never reaches a normal exit. The runtime
  plane (§2) treats `NoReturn` as an introspectable alias object that
  enforces nothing (NR-R1–NR-R5). The static claim "this function
  does not return" is NOT carried by the runtime alias object; the
  alias object does NOT check it. A `NoReturn` function that actually
  returns is a static error (the false postcondition is violated) but
  runs fine at runtime.
- **NR-D2 (the no-blend rule).** The static plane's `false` postcondition
  (NR1) MUST NOT be discharged by the runtime's behaviour. Concretely:
  a `NoReturn`-annotated function that, at runtime, is observed to
  raise (e.g. in a test) does NOT thereby satisfy the NR1 obligation —
  the static proof requires a proof-time argument (NR2a, a diverges-
  supporting body) that EVERY normal-exit path is absent. Conversely, a
  `NoReturn` function that the static plane proves divergent may, at
  runtime, terminate (e.g. on an input the proof's preconditions do not
  cover) without that being a static-plane failure. The runtime must
  not be allowed to "pass" the static false-postcondition. — *cites S3
  (central negative sentence); cross-references `typing-global-impl.md`
  §0 (the no-blending rule).*
- **NR-D3 (the vacuity-gate interaction is a static-plane concern).**
  The NR4 exemption (§1.2) is a STATIC-PLANE mechanism: it prevents the
  non-vacuity gate from false-positively flagging a faithful
  `NoReturn` function. The runtime plane has no analogous concern
  (there is no runtime vacuity probe). The exemption does NOT bleed into
  the runtime plane: the runtime shim does not "know" that a function
  is `NoReturn` in any behaviour-affecting way (NR-R4 — it only
  constructs the alias object). The two planes remain separate even at
  the exemption.
- **NR-D4 (no-blend invariant).** The static plane's `false`/
  `diverges` obligation (§1) and the runtime plane's alias-object/
  introspection behaviour (§2) are carried as SEPARATE contracts,
  separately labelled. A `NoReturn` whose runtime shim passes the
  static `false`-postcondition VC is a finding (gap doc), not a
  success. The no-blend rule is defended by author separation: this
  spec-agent and the conformance-agent never read the core-agent's
  lowering.

---

## 4. CLASSIFICATION

- **Static plane: INTERPRETED.** `-> NoReturn` is consumed by the
  static plane and lowered — through the existing `diverges` IR flag
  (`ir_schema.py:80`) and the `ensures { false }` VC family — to
  obligations: the false postcondition (NR1), the divergence/
  raise obligation (NR2/NR2a), the dead-code report on the successor
  (NR3), and the vacuity-gate exemption (NR4). Each clause maps to one
  VC or one S5 conformance case, discharged by the existing diverges
  machinery. The construct is classified **Interpreted** in
  `--soundness-report`.
- **Runtime plane: SHIMMED.** The runtime meaning of `NoReturn` is the
  introspectable alias object (the `typing.NoReturn` special form) with
  no enforcement (NR-R1–NR-R5). Any `src/pycsl_lib/typing` surface for
  `NoReturn` is a thin shim that constructs the alias object and
  performs no validation of the function's control flow (NR-R4). The
  construct is classified **Shimmed** in `--soundness-report`.
- **Combined classification:** `NoReturn` is **Interpreted on the
  static plane, Shimmed on the runtime plane** — both classifications
  apply, separately, per the no-blend rule (§0/§3 of
  `typing-global-impl.md`).

### GT gap codes tagged in this spec

- **No GT gap.** `NoReturn` is SOUND: the false postcondition is a
  genuine proof obligation (the function must be shown to diverge or
  raise), not an unsoundness. There is no `Any`-like consistency escape
  (GT1), no `# type: ignore` honour (GT6), no runtime/static split
  (GT7). The NR4 vacuity-gate exemption is a gate-precision concern,
  not a soundness gap: it prevents a false POSITIVE (flagging a
  faithful `NoReturn` function), not a false negative (a green that
  proves nothing). The dead-branch over-flagging precision gap
  (`soundness-issue.md` §7 item 3) is the DUAL concern and is
  referenced at NR3, but is owned by the gate's existing occurrence-
  keyed merge fix, not by a new GT code.

No GT gap is tagged in this spec. GT2 (variance), GT3 (`ParamSpec`/
`TypeVarTuple`), GT4 (polymorphic recursion), GT5 (forward-reference
resolution order, owned by TY0), GT6 (`# type: ignore`), GT7
(`Protocol` runtime/static split), and GT8 (the declared S5 conformance
subset, owned by the conformance-agent) are out of scope for `NoReturn`
at TY1 — `NoReturn` takes no type arguments, introduces no forward-
reference or ignore behaviour, and carries no runtime/static split beyond
the standard Interpreted/Shimmed split that every typing construct
carries.
