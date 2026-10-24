# OPEN ROUTE #324 — A STRING SLICE INSIDE A CONTRACT USES RAW Why3 `String.substring` (negative bounds give "")
**Status: REPAIRED (gen #37, 2026-10-24; candidate, gates partly OWED — see REPAIR), was OPEN (2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r324/`: `ensures \result == len(s[1:-1])` proves 0 (CPython 1) (q03); `len(s[-2:3])` (q05). expressions.py ~18829 emits the
raw `substring` for a contract-side slice; route #190 fixed the body side (guarded `str_sub_op`), route #262 contract-side INDEXING; contract
SLICES were missed.
Repair: lower contract-side str (and list) slices with Python slice semantics (normalise negative/out-of-range bounds as the body path does) or
refuse non-literal/negative bounds in contracts.

## REPAIR (2026-10-23, r322 executor off 67edf13c, finished by r322b; commit 6899062d (code + witnesses + docs) + route docs)
**Translation rule, no refusal** (`expressions.py` contract-side str slice, ~18841; mirror twin in
`src/self-annotate/src/module6_whyml/expressions.py` updated verbatim, sync rc=0): Why3's `String.substring s i x` equals CPython's
`s[i:i+x]` only for non-negative bounds (an offset outside `[0, |s|)` or a length `<= 0` gives `""`, the end is clipped). A contract
bound that is not a non-negative int literal, an omitted bound, or a bare `len(x)` (a single `(String.length x)` application) is
normalised exactly as CPython does: `b' = if b < 0 then max(b + |s|, 0) else b`; `s[a:b]` then reads `String.substring s a' (b' - a')`.
Non-negative literal / omitted / bare-`len` bounds keep the raw form, so every such contract emits byte-identically (corpus 0767,
`s[:len(p)]`, is the case that forced the bare-`len` arm: the first cut moved it). The body side keeps route #190's guarded
`str_sub_op`. List slices in contracts (`Array.sub` under an opaque `iter_length`) were already unprovable (q04, scratch t10: FAIL at
base and after) — not touched.

Probe table (base = 67edf13c; after = d9a53ce5):

| witness | CPython | base | after |
|---|---|---|---|
| 4200 `len(s[1:-1])` == 0 | violates | PROVED* | FAIL |
| 4201 negative start | violates | PROVED* | FAIL |
| 4202 variable negative bound | violates | PROVED* | FAIL |
| 4208 non-negative bounds (control) | ok | emits | emission byte-identical to base; proof OWED |
| 4209 `len(s[1:-1]) == 1` true (control) | ok | FAIL† | PROVED |
| 4210 negative start true (control) | ok | FAIL† | PROVED |
| 4211 clamped negative true (control) | ok | FAIL† | PROVED |
| witnesses-r324 q03, q05; scratch q09 | violate | PROVED | FAIL |
| scratch q08, q10, q12 (true claims with negative bounds) | ok | FAIL | emission changed (normalised); proof OWED |

(* base: the matching scratch probe q03/q05/q09 PROVED in the r322 executor's measured base run; the corpus files emit the same
raw `substring` at base. † inferred, not re-run: the base emission is the raw `substring`, under which the true claim is
false — the matching scratch probes q08/q10 FAILED at base.)

**Gates** (r322b; rc captured per leg; the heavy queue was saturated by two `--slow` plane runs and three whole-file mirror proofs
of other agents for most of the window, so the long legs below are OWED, not run):
- witness/control proofs above: rc as tabled (4200-4202, q03/q05/q09 rc=1 FAIL; 4203-4207, 4209-4211 rc=0 PROVED).
- corpus byte-diff: base = the r322 executor's 67edf13c sweep (`pycsl-r322-base` worktree, 2156 root / 2186 pyref); its candidate
  sweep had root 1 MOVED (0767) / pyref 0; the bare-`len` arm fixed 0767. r322b re-swept root files 1-1000 at d9a53ce5: 869/869
  identical, 0767 identical, 0 GONE. **OWED**: root 1001-2991 and pyref at d9a53ce5 —
  `heavy.sh bin/byte-diff-sweep.sh <out>` then `bin/byte-diff-compare.py <base> <out>` and
  `bin/byte-diff-compare.py <base>/pyref <out>/pyref --min-files 2000` (base: `/home/fabrice/git/pycsl-r322/.r322tmp/sweep/base`).
- mirror-emit-sweep base vs after: **OWED** (`heavy.sh bin/mirror-emit-sweep.sh <out>` in a 67edf13c worktree and here, then
  `bin/byte-diff-compare.py <base> <out> --min-files 50`). Only mirror source moved: `module6_whyml/expressions.py` (the #324 arm,
  verbatim twin); expected mover `src_module6_whyml_expressions.mlw` -> L3-tc + whole-file proof OWED
  (`HEAVY_LOW=1 heavy.sh env PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/module6_whyml/expressions.py --import-path src/pycsl`).
- check-self-annotate-sync.sh rc=0 (926 functions verbatim); self-annotate-mirror-check.sh rc=0 (53/53); doc-coherency --check rc=0;
  check-trusted-raises-honesty rc=0 (61 silent, ratchet 61). **OWED**: run-soundness-planes.sh fast (61), check-assumed-facts
  (`--emit-dir` of the after sweep), refusal-witness census rows for 4190-4202 via `_census_row` then the no-flag coverage check.
- Ledger 3 (no axiom), no gate loosened, no helper/nested def added in `src/pycsl`.

**Residuals**: list slices in contracts keep the opaque `iter_length (Array.sub ..)` (unprovable, not unsound); a slice whose bound is
`len(x) - k` is normalised (sound, slightly larger VC).
