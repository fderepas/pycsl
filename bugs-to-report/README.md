# bugs-to-report/

Candidate PyCSL bugs (emitter / prover / gate behaviour) encountered by the
`test-supervise-sl` / `formal-test-sl` loops.

- One bug per file.
- Filename: `YYYYMMDD-hhmm-simple-name.md` (e.g. `20260616-1547-handle-reference.md`).
- **Loud-fail, never approximate.** Each file carries a `STATUS:` line —
  `CONFIRMED` (minimal repro reproduces deterministically) or `UNCONFIRMED`
  (suspected; state exactly what would confirm it). Never file an unconfirmed bug
  as confirmed.

Suggested body shape: **STATUS** · **Symptom** · **Minimal repro** · **Expected vs
actual** · **What would confirm / next step**.
