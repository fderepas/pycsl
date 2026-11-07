# OPEN ROUTE #292 — CITED struct ROUND-TRIP AXIOM APPLIED TO '?' (bool) FORMATS
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r292/`. st001 `struct.pack(">??", x0, x1)` then unpack with `#@ proof rocq UnixFs.Struct.i2.round_trip` proves `\result == x0`; CPython roundtrip(5, 0) returns True. The slot id `i2` covers any two scalar slots incl. `?`, and the legacy axiom `unpack(pack x0 x1) = (x0, x1)` has no range/format guard; the soundness report does not list the cited axiom as a TCB entry. Repair: key the cited lemma on the exact format codes it was proved for (int widths/signedness, guards on ranges), refuse others; report cited axioms.

## REPAIR (2026-10-20, executor rA off 7313506b; commit 79a2d92f)
Probe table (rc; CPython ground truth in each corpus file's `__main__`):

| shape (citing the legacy law) | 7313506b | after |
|---|---|---|
| `>??` round-trip, `UnixFs.Struct.i2.round_trip`, `\result == x0` (st001 / 3352) | PROVED | FAIL |
| `<ff` (float32) same claim (3353) | PROVED | FAIL |
| `<dd` (float64) same claim (3354) | PROVED | FAIL |
| control: the documented `>HH` in range (3355; 0420's i2 function) | PASS | PASS |
| `>H30s` / `>IHHHHHII10Ixx` users (0420-0425, `unix-filesystem/`) | unchanged | byte-identical |

Rule (inline in `_handle_struct_call`, mirror `\trusted`; no new def/field; NO axiom or Rocq/Lean edit;
ledger 3): `UnixFs.Struct.{i2,i18,i1a1}.round_trip` are keyed on the EXACT format their Rocq/Lean
statements document (`>HH`, `>IHHHHHII10Ixx`, `>H30s`); any other format with that slot shape lowers to a
format-keyed symbol `struct_{pack,unpack}_<id>_h<hex(fmt)>` that no cited law names. The faithful
`Pycsl.Struct.Std` family (cleared-pack) was already keyed per width/signedness and in-range guarded.
TCB reporting: `--soundness-report` now lists every cited `#@ proof` lemma under "TCB entries: cited
proof-assistant lemmas (emitted as Why3 axioms)" with its provers and citing functions (JSON key
`cited_lemmas`); it listed none before.
Blast radius: corpus root 1 MOVED, declared: 1915 (`<bb6x` / `<hL`, a fold-collision CONTROL that cites no
law) now uses the two format-keyed symbols; re-proved PASS. pyref 0, mirror 0.
Gates (logs under the rA scratchpad; all heavy jobs via heavy.sh): witnesses at 7313506b vs after in
the table; byte-diff-sweep base/after rc=0 (2510 / 2529 sources); byte-diff-compare root rc=0 with ONE
declared mover (1915, below), pyref rc=0 (2186/2186, 0 MOVED / 0 GONE / 0 APPEARED); mirror-emit-sweep
base/after rc=0, compare `--min-files 45`: 1 MOVED (`frontend__pure_ast`, route #291, below), 0 GONE,
0 APPEARED; check-self-annotate-sync.sh rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53);
refusal-witness census +15 rows (3340-3344 REFUSAL, 3346-3350/3352-3354/3356-3357 VERIFY-FAIL) via
`--append-new` (that run also found 234 pre-existing FAIL witnesses with no row at 7313506b — not
appended here, out of scope; reported to the driver); run-soundness-planes.sh --slow rc=1 -> 82/84 green; vacuous-drivers (3358) and hashed-literal-purity
(re-keyed baseline rows for the format-keyed struct symbols) fixed and re-run rc=0; assigns-writes-survival
TRAP 1447 > 1445 is identical at 7313506b (pre-existing).
Residual (suspected, NOT reproduced): the legacy laws are unguarded shape models, so even the documented
formats state `unpack(pack x) = x` for out-of-range ints (CPython raises `struct.error`, ambient) and for a
`>H30s` name whose length is not 30 (CPython pads/truncates, does NOT raise). Every probe reading the
unpacked `30s` slot (`len(name)`) was ill-typed at 7313506b, so no false proof was obtained; a guarded
restatement would need a Rocq/Lean change (out of this route's remit). Recorded for the driver.
