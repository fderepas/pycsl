# Finish the `os` Formal-Test Coverage — Task Brief (for Claude Code)

This brief tells a Claude Code session how to extend the formal verification of the
`os` module so that every system call documented in the source of truth is crowned
by a formal test, not only the five already done. It is an executable work order.

**Starting point.** `pure_lib_test/formal_0008.py` already carries a formal test for
five syscalls: `open`, `write`, `read`, `close`, `lseek`. These are the worked
reference — read them first to learn the house style (how a syscall's English
promise is re-stated as a postcondition over symbolic inputs and discharged).

**Source of truth.** `test-suite/library_reference/os.rst` is the normative English
specification for what each `os` syscall means. Per the *CSL source-of-truth
discipline, `os.rst` bounds each contract from above (the strongest claim the spec
justifies) and the reference behaviour (CPython / POSIX semantics the faithful WhyML
inode model already encodes) bounds it from below. Where they disagree, stop and
surface it — never pick the convenient reading.

**Global strategy.** This task is one execution of the arc described in
`docs/formal-filesystem.md` (the `os` inode filesystem, proved with 0 unproven goals
on a one-line trusted base). Read that document before starting; everything below is
its **descent and return** applied syscall-by-syscall:

- **Descent.** A syscall's `os.rst` sentence becomes a faithful model obligation on
  the inode/disk state, which becomes the smallest checkable contracts
  (`requires`/`ensures`/`assigns`, plus the leaf facts beneath them).
- **Return.** The syscall is crowned by a **formal test**: a driver whose inputs are
  *symbolic* and whose postcondition transcribes the `os.rst` promise, discharged by
  Why3 + Alt-Ergo (then Z3) — *Valid* meaning each goal's negation is unsatisfiable —
  for **every** input the verification condition ranges over, not a sampled few.

---

## 1. Roles

Subagents cannot spawn subagents, so the **main thread is the coordinator** and runs
the implementers **strictly in sequence, one syscall at a time** (the user requires
no parallelization). Sequencing is not only a constraint — it lets each syscall reuse
the proved leaf contracts of the ones before it (compose, don't re-derive), and keeps
whole-module proof time affordable.

### 1.1 Coordinator (the main thread — you)

1. Reads `os.rst` and `pure_lib_test/formal_0008.py`, enumerates the syscalls
   documented in `os.rst` that are **not** already tested, and writes the English
   test scenarios for them into one **requirements document**,
   `pure_lib_test/os-formal-requirements.md` (§3 gives its structure).
2. For each not-yet-tested syscall, in sequence, delegates to a fresh
   `pycsl-os-formal-implementer` subagent (§2), passing the requirements-doc path and
   the one syscall name in the delegation prompt (a subagent starts with fresh
   context — write the syscall name, the `os.rst` section, and the path explicitly).
3. Runs the three acceptance gates (§4) before moving to the next syscall: the
   implementation-plan gate, the **proven** gate, and the **coverage** gate. Does not
   start syscall *n+1* until syscall *n* has passed all three.
4. On any gate failure, returns a structured diff to the implementer and retries; on
   an `os.rst`-vs-model disagreement, halts that syscall and surfaces it rather than
   shipping a convenient contract.
5. After all syscalls pass, performs the **skill-enrichment** step (§6).

The coordinator never writes a formal test itself; it specifies, validates, and
sequences.

### 1.2 `pycsl-os-formal-implementer` (subagent)

Drop at `.claude/agents/pycsl-os-formal-implementer.md`:

```markdown
---
name: pycsl-os-formal-implementer
description: MUST BE USED to formally test exactly one os system call from the requirements document. Reads the English scenario, restates it as an implementation plan, gets coordinator acceptance, then writes the PyCSL contracts/model extension needed and delivers a proving formal-test driver in the style of pure_lib_test/formal_0008.py.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
memory: project
skills:
  - pycsl-annotate
  - pycsl-stdlib-coverage
  - pycsl-docs
  - csl-philosophy
---

You formally test exactly one os syscall, named in your prompt, against the English
scenario in the requirements document.

Hard rules:
- The contract transcribes os.rst (the source of truth), resolved by the faithful
  inode model where os.rst is silent. Anchor each ensures to the sentence it encodes
  with a `# cite:` to the os.rst section and a `# cite:_note:` paraphrase. A contract
  that proves but does not transcribe os.rst is coherent and wrong — the worst green.
- Name the exact mechanism in any prose you write (WhyML, Why3 WP VCs, Alt-Ergo/Z3,
  Valid = negation unsatisfiable, val vs let, leaf-first/compose). Never hand-wave.
- Reuse the proved leaf contracts of already-tested syscalls; do not re-derive facts
  over the whole disk state (compose, don't re-derive). If a goal is genuinely
  SMT-hard, prove the reusable lemma in Rocq AND Lean offline, register it, and cite
  it with `#@ proof` — no Rocq/Lean kernel runs during the pycsl proof itself.
- You do not declare "done". Done is the coordinator's gates passing.

Workflow for your assigned syscall:
1. Read its scenario in the requirements doc and os.rst section. Restate it as an
   implementation plan written to <syscall>-impl-plan.md: the contracts/model
   obligations, which leaf contracts you will reuse, the symbolic-input formal-test
   driver you will deliver, and the os.rst clauses each ensures transcribes. STOP and
   hand back for the implementation-plan gate.
2. After acceptance, implement: add/extend the syscall's PyCSL contracts and any
   model support, keeping the existing module proof affordable (use #@ no_inline /
   contract opacity if a heavy method inflates whole-module E-matching).
3. Deliver the formal test in the style of pure_lib_test/formal_0008.py: symbolic
   inputs, postcondition transcribing the os.rst promise, verifying end-to-end with
   no \trusted and no --no-proof. Report the exact pycsl command to check it and the
   clause -> VC coverage map.
```

---

## 2. Per-syscall pipeline (repeat in sequence)

```
Coordinator delegates syscall N (requirements path + name in prompt)
        │
        ├─ implementer writes <syscall>-impl-plan.md
        ▼
GATE 1  Implementation-plan accepted vs requirements doc   ── fail → diff, retry
        │ pass
        ▼
implementer implements + delivers symbolic-input formal-test driver
        │
        ▼
GATE 2  PROVEN: pycsl <driver> → SUCCESS, no \trusted, no --no-proof
        │ pass                                              ── fail → diff, retry
        ▼
GATE 3  COVERAGE: formal test transcribes the os.rst English ── fail → diff, retry
        │ pass
        ▼
syscall N DONE → record driver + coverage map → delegate syscall N+1
```

---

## 3. The requirements document (coordinator authors first)

Write `pure_lib_test/os-formal-requirements.md`. It is a generic requirements
document, not a PyCSL reference doc (no Normative preamble). Structure:

1. **Scope.** The syscalls already tested (`open`, `write`, `read`, `close`,
   `lseek`) and the list of not-yet-tested syscalls enumerated from `os.rst`, in the
   sequence they will be implemented (order by leaf-dependency: syscalls whose facts
   others reuse go first — e.g. allocation/lookup before the operations that depend
   on them).
2. **Per syscall, an English test scenario** containing:
   - the `os.rst` section reference (the source-of-truth anchor);
   - the English promise in plain language — what the call guarantees on success,
     what it does to the inode/disk state, and what it raises and when (the
     `OSError`/`errno` conditions os.rst specifies), written so a reader can
     enumerate the obligation clauses;
   - the **acceptance criterion**: a formal test, in the style of
     `pure_lib_test/formal_0008.py`, whose symbolic-input postcondition transcribes
     those clauses and verifies *Valid*, plus the clause → VC coverage map the
     implementer must fill.

**Candidate not-yet-tested syscalls** (derive the authoritative list from `os.rst`;
this is only a seed and the repo's own `sys_*` naming suggests several are modelled):
`lstat`/`stat`/`fstat`, `lseek` edge behaviours if any remain, `pread`/`pwrite`,
`ftruncate`/`truncate`, `mkdir`/`rmdir`, `unlink`, `rename`, `link`/`symlink`/
`readlink`, `dup`/`dup2`, `fsync`/`fdatasync`, `chmod`/`chown`, `listdir`/`scandir`,
`access`. Keep only those `os.rst` actually documents and the model can faithfully
support; drop the rest with a one-line note (out-of-model boundary), since an
unsupported syscall is a residual gap to record, not a contract to fake.

---

## 4. The three gates (coordinator runs per syscall)

### Gate 1 — Implementation plan accepted

The plan in `<syscall>-impl-plan.md` names the contracts/model obligations, the leaf
contracts being reused, the formal-test driver, and the os.rst clause → ensures map.
The implementer may not implement until this matches the requirements scenario.

### Gate 2 — Proven (machine-checked)

- `pycsl <driver>` → `Verification SUCCESS`, with **no `\trusted`** in the tested
  path and **no `--no-proof`**; every contract and the formal-test postcondition is
  *Valid*. Use a `pycsl-verifier`-style read-only run (see note below) to keep the
  verbose Alt-Ergo step counts out of the coordinator context.
- The whole `os` module still proves: re-run the module/`formal_0008.py` proof and the
  reference suite so the new syscall has not pushed whole-module proof past its
  wall-clock budget (if it has, require a modular boundary — `#@ no_inline` / contract
  opacity — rather than a weaker contract).
- Any `# cite:` points to a real `os.rst` section (auditable transcription).

### Gate 3 — Coverage of the English source of truth (load-bearing)

This is the gate the user emphasized: confirm the formal test **covers the English
description from `os.rst`**, i.e. proves the right theorem.

1. **Extract clauses.** From the syscall's English scenario (success guarantee,
   state change, and each documented `OSError`/error condition), enumerate the
   obligation clauses.
2. **Map clause → VC.** Each clause maps to a specific *Valid* VC in the formal-test
   driver. A clause with no VC means the test under-covers `os.rst` — reject.
3. **Error paths covered.** Each error condition `os.rst` documents is exercised
   (e.g. a `raises`/exceptional postcondition or a negative companion that the
   error fires under its condition). A success-only test of a call that `os.rst`
   says can fail is under-coverage — reject.
4. **Coherent-and-wrong guard.** Confirm the proven postcondition is the `os.rst`
   promise, not a weaker or adjacent property that merely happens to prove (e.g.
   proving a write returns a byte count while os.rst also requires the bytes land at
   the file offset and the offset advances). If the theorem proved is not the
   theorem `os.rst` states, reject despite the *Valid* verdict.

Record the filled clause → VC map next to the driver. Gate 3 passing is the
definition of the formal test "covering" the source of truth.

**Optional `pycsl-verifier` subagent** (read-only) isolates the verbose prover output
and returns only per-goal verdicts; define it as in the HAPPY brief if you want the
coordinator context kept clean during Gate 2.

---

## 5. Definition of done (global)

Done when, for every not-yet-tested syscall enumerated from `os.rst`:

- Gates 1–3 passed and recorded (driver path + filled clause → VC coverage map).
- The formal-test driver is committed in the `pure_lib_test/` style of
  `formal_0008.py`, verifying with no `\trusted` and no `--no-proof`.
- The full `os` proof and the reference suite still pass with the new drivers
  included; every `# cite:` resolves to an `os.rst` section.
- Any syscall `os.rst` documents but the model cannot faithfully support is recorded
  as an explicit residual gap, not silently skipped.

Do not mark done because drivers were created or because an implementer reported
success — done is the gates passing, the same machine-checked discipline the project
uses elsewhere (a phase is complete when its acceptance claims pass).

---

## 6. Enrich the skills with the acquired knowledge (final step)

After the syscalls are done, fold what was learned back into the governing
documents so the next contributor inherits it. Treat this as a real deliverable, not
a footnote.

- **`config/skills/pycsl-stdlib-coverage`** — the discipline that governs stdlib
  annotation and the `os` source-of-truth squeeze. Add any new, reusable patterns the
  exercise surfaced: recurring `os.rst` → contract transcription idioms, the standard
  way to encode a documented `OSError` as an exceptional postcondition, and which
  leaf contracts are now proved and reusable across syscalls.
- **`config/skills/pycsl-annotate`** — if a new contract/ghost/`#@ for` idiom proved
  necessary for filesystem-state postconditions (e.g. expressing offset advance, or
  per-inode state preservation), add it with a corpus pointer.
- **`config/skills/pycsl-exception-model`** — if any new implicit-exception trigger
  was needed for a syscall's error path, record it in the trigger table.
- **`docs/formal-filesystem.md`** — update the worked-example narrative to reflect the
  now-broader syscall coverage: the new descent/return instances, any leaf-first
  composition that beat an SMT timeout, and any modular boundary (`#@ no_inline`)
  introduced to keep whole-module proof affordable. If `os.rst` documents syscalls
  the model cannot yet support, list them as the named residual gaps the doc is
  answerable to.

Run `bin/doc-coherency.py --check` and the stdlib-coverage gate after editing so the
enrichment does not drift the parity invariants. Enrichment is done when those gates
are green and a reader of the skills/doc could repeat a syscall's formal test from
the recorded patterns alone.
