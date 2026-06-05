# Anti-patterns to avoid

- **Starting with the formal semantics before the annotation
  surface exists.** Formal semantics anchors to a *stable*
  surface. Build the surface first.
- **Skipping the traceability matrix.** Without it, the
  reference corpus drifts from the language. With it, drift is
  a build-time error.
- **Letting the registry drift from cited theorems.** The
  mechanical cross-check (Phase 10) makes this impossible to
  ignore. Wire it into CI on day one of Phase 7.
- **Trying to verify the *runtime* library.** It's trusted; only
  the stub contracts matter. The stub layer is intentionally
  Tier-2.
- **Per-language one-off naming** (`pyCSL`, `c-csl`, `Go.csl`).
  Pick the uniform `<lang>csl` convention early. PyCSL,
  ccsl, gocsl, jscsl, rustcsl, cppcsl. No exceptions.
- **Premature LLM agent automation.** The agents work on the
  mature surface, not the under-construction one. Build Phases
  1-9 by hand.
- **Adding a new IR node / backend case for a form that is sugar
  over existing primitives.** It grows the TCB and the
  Module 5/6/formal-mirror surface for *zero* proving power.
  Desugar it in the front-end instead (Phase 4b).
- **Enumerating syntactic writes to "the protected name" for a
  whole-program meta-property.** It silently misses indirect
  (callee) writes and aliases, and a CSL has no points-to analysis
  to recover them. State each obligation at the **location written**
  and inject at **every** body's own sites (universal coverage); close
  the bodyless gap with a *synthesized* trust-boundary declaration, not
  a pattern-matched one. Write the soundness theorem before the pass
  (Phase 4c).
- **Inventing your own SMT-bridge.** Use Why3. Anything else is
  a different (much larger) project.
- **Verifying Module 6 by hand.** Phase 6's `wp_gen_correct` +
  the `proof2why3` cross-check are how you verify Module 6 at
  scale. Don't reinvent.
- **Letting auto-trust become permanent.** Every auto-trust
  rule is a tracked TODO, not a long-term policy.
- **Using `apply IH` in soundness proofs with record-type
  postconditions.** `outcome_satisfies` is a `Definition`; Coq
  unifies structurally before reducing. Use forward reasoning
  (`exact (IH pre_es _ _ _ _ _ Hwp)`) — see
  [`references/phase-formal-semantics.md`](phase-formal-semantics.md).
- **Ignoring eval_expr / eval_int consistency.** When `eval_expr`
  and helper evaluators extract values from different patterns
  (e.g., `VBool true → 1` in one but not the other), desugaring
  proofs silently break. Always ensure pattern coverage matches.
- **Treating Admitted as "done".** Every `Admitted` is technical
  debt with compound interest. Track them in the Makefile output
  and the trust-chain diagram. Report admitted count on every
  build.
- **Proving `exec_deterministic` or `desugar_correct` before
  `soundness`.** These are verbose, low-payoff proofs. Soundness
  catches real bugs; determinism is mostly mechanical. Prioritize
  the theorem that provides the most trust value first.
- **Adding a phase without a mechanical gate.** Every phase
  should introduce at least one machine-checkable constraint
  (a squeeze). If a phase produces only documentation or
  refactoring with no new CI gate, the squeeze is missing and
  regressions are invisible. Ask: "what command fails if this
  phase's invariant is violated?"
- **Delegating to an agent without a squeeze perimeter.** If an
  agent's output can't be mechanically validated (by SMT, proof
  assistant, test suite, or schema checker), the agent operates
  outside any squeeze and its output requires full manual review.
  Prefer tasks where at least one squeeze gate exists.
- **Treating extracted OCaml output as fresh after a Rocq source
  change.** The byte-diff driver (and any other binary built
  from extracted ML) is gated on `[ -x "$DRIVER" ]` — an
  existence check, not a freshness check. After touching
  `Phase1b_IrToStmt.v` or any extracted module, the driver
  binary must be force-rebuilt or tests run against the OLD
  extraction. The failure mode is insidious: a corpus case that
  *should* now pass still reports the pre-fix blocker, looking
  like the source change didn't take effect. Always
  `rm -f extracted/<driver> && ocamlfind ocamlc … -o <driver>`
  after editing extracted-module sources, or wire the rebuild
  into the driver script.
- **Following a deferred plan without re-running the empirical
  step.** Plans (`todo-saturday.md`, `closer-to-code.md`) carry
  decisions based on the state when written. Before executing a
  deferred item, re-run the relevant empirical check —
  byte-diff blocker breakdown, `Print Assumptions` audit,
  cross-check FAIL list, `extraction-byte-diff-upward.sh`
  tally. Categories the plan listed may have shifted as other
  work landed. A PyCSL example: a deferred item estimated 3-arg
  `range` would unblock corpus tests; the live blocker
  breakdown showed zero existing corpus tests use 3-arg range,
  and the "1 blocker:For" was actually `arr.append` inside a
  for body. The plan was directionally right (the feature was
  worth adding) but the verification expectation needed
  updating.
- **Reasoning over an opaque value when a concrete lowering
  exists.** If a Python expression is concrete (a class constant,
  a slice, a packed-int field) but lowers to an uninterpreted
  `val` (`getattr_<cls>`, `array_slice`, an unwatched
  `struct.unpack`), every functional goal over it is unprovable —
  or vacuously "true" if the spec itself degenerated (e.g.
  `\array_eq` outside the `hoare` model). Lower to the literal /
  `Array.sub` / `Array.blit` / arithmetic form instead. See
  [`references/cross-cutting-concerns.md`](cross-cutting-concerns.md)
  §"Keep values prover-known".
- **Gaming an acceptance claim.** An `**Acceptance:**` claim is the
  phase's definition of done; the change that closes it must be the
  feature it stands for, not a shortcut that flips the bit. A claim
  `pycsl.py NNNN.py exits 0` is satisfiable by *any* verifying file
  — so the fixture must genuinely exercise the new capability, and
  you should confirm the mechanism in the emitted artifact (e.g.
  Phase-0 class constants: `0440.py` references `self.CAP` and the
  `.mlw` shows it lowered to `(64)`, not a `getattr`). The honest
  signal that a claim is real: it FAILS before the feature and
  PASSES *because* of it. A claim that already passes against an
  existing artifact (a regression guard) and one that fails until
  built do different jobs — keep both, don't conflate.
