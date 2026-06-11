# os verification — handoff / resume guide

Entry point for a fresh session continuing the `stronger-than-os.md` effort (functionally verifying
`pure_lib/os` through its **public API**). Read this + the skill + the latest gap docs, then drive.

## Where it stands (committed milestone)

- **Directory namespace: fully functionally verified THROUGH THE PUBLIC API.** All 7 consequences in
  `pure_lib_test/formal_os_namespace.py` prove Valid: `mkdir`→present, `access`, `rmdir`/`unlink`→absent,
  `link`→present, `rename`→old-absent+new-present. No simulation — real syscalls.
- **Directory uniqueness PROVEN as a class invariant, OUT OF THE TCB** (was `\trusted`). See
  `docs/proven-uniqueness.md`. Backed by 6 dual-kernel `UnixFs.Dir.*` axioms.
- **fd chain: 3/5 through the API** (`pure_lib_test/formal_os_fd.py`): `open_existing`, `fstat`, `dup` prove
  Valid. They rest on **7 narrow `\trusted` fidelity clauses** (dirscan-fidelity + fd-resolution-fidelity in
  `UnixInodeFileSystem.py`) — provable later (uniqueness was the precedent).
- **20 cross-validated dual-kernel axioms** (Rocq+Lean, offline) in `_AXIOM_REGISTRY`; os GREEN ~1210 body VCs.
- Metrics: LOS:LOC ≈ 743:1215 (`p/answer.md`).

## The frontier (next work, in priority order)

1. **Content round-trip `write→read==data`** — the flagship, a MULTI-GAP arc (NOT one step). spec-16
   (`11-2140-convergence-spec-16.md`) found:
   - `UnixFs.Content.write_then_read_agree` (block read-after-write byte agreement) is VALIDATED in both
     kernels but is a **prerequisite brick** — it proves the block bytes, while the test is gated by the
     **reopened inode SIZE**, and the abstract `dir_lookup` reopen severs the link.
   - **gap-17 (the keystone, named in spec-16):** register `UnixFs.Dir.lookup_after_insert_recovers_inode`
     (name→inode identity across create — finite slot case-split), cite `UnixFs.Struct.i18.round_trip`,
     introduce inode-keyed `inode_content`/`inode_size` in `_AXIOM_FUNCTIONS` threaded through
     write/close/open/read with a close-frame + create-skip frame. May spawn gap-18.
2. **`open_absent`** (`open(absent)→ENOENT`) — a TEST-STRUCTURE fix, not a model gap: the test must
   ESTABLISH absence first (e.g. `mkdir(d); rmdir(d); open(d)→ENOENT`), not assert `-1` on a havoc'd shared
   `_filesystem` global. A test-agent turn.
3. **Remaining os syscalls** beyond the namespace + fd chain — `stat`/`lstat`/`listdir`/`getcwd`/`chdir`/
   `chmod`/`chown`/`truncate` consequence tests (call the API, assert the consequence).

## How to resume (kickoff)

- **The skill:** `config/skills/pycsl-stdlib-coverage` — the **Convergence Principle** + the **4-agent loop**:
  coordinator / stdlib-agent (model, `pure_lib/os/`) / **test-agent** (formal test, `pure_lib_test/`, calls
  ONLY the public API) / tool-agent (`src/pycsl/`). Read it.
- **The plan:** `stronger-than-os.md` (Phase 3 = fd chain + content).
- **The trail:** the dated `11-*-convergence-{gap,spec}-N.md` chain (gap-7 → spec-16) is the audit trail.
- **Kickoff prompt:** *"Drive gap-17 (the os content round-trip keystone, per spec-16) via the convergence
  loop"* — or *"apply the convergence principle to the os content round-trip."*

## The discipline (NON-NEGOTIABLE — this is what kept every result trustworthy)

- **INDEPENDENTLY GATE every subagent claim.** Re-run the STANDARD pipeline yourself
  (`pycsl pure_lib_test/formal_os_*.py`), verify the consequence's per-function verdict, run the parallel
  byte-diff (`bin/byte-diff-sweep.sh`), confirm os GREEN. Three subagent over-claims were caught this
  session (a hand-edited-mlw "flip", a partial wall, a stale figure) — never trust a self-report.
- **A formal test CALLS the public API — never simulates.** The test-agent is internals-blind (no `disk`,
  `_dir_lookup`, `sys_*`). [[feedback-test-calls-api]]
- **Track the `\trusted` count (currently 7).** Flag every new trust; prefer body-proven; prove it later.
- **Inductive/loop walls → cross-validated Rocq+Lean axioms** (BOTH kernels accept, allowlisted —
  Rocq `Print Assumptions` Closed / Lean `#print axioms ⊆ {propext, Quot.sound}`). Never a bare SMT skip,
  never re-trust to dodge a real gap. [[feedback-no-more-int]]
- **Commit each gated brick** with careful staging (inspect the staged set — watch for stray deletions);
  use the `fabrice:` prefix (no Claude trailer) for changes Fabrice made himself.
- Parallelize sweeps with `bin/byte-diff-sweep.sh` (half the CPU via the canonical `get_cpu_count`), not
  serial loops.
