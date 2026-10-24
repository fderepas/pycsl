# OPEN ROUTE #324 — A STRING SLICE INSIDE A CONTRACT USES RAW Why3 `String.substring` (negative bounds give "")
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
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
| 4208 non-negative bounds (control) | ok | PROVED (emission identical) | PROVED |
| 4209 `len(s[1:-1]) == 1` true (control) | ok | FAIL† | PROVED |
| 4210 negative start true (control) | ok | FAIL† | PROVED |
| 4211 clamped negative true (control) | ok | FAIL† | PROVED |
| witnesses-r324 q03, q05; scratch q09 | violate | PROVED | FAIL |
| scratch q08, q10, q12 (true claims with negative bounds) | ok | FAIL | Q_AFTER |

(* base: the matching scratch probe q03/q05/q09 PROVED in the r322 executor's measured base run; the corpus files emit the same
raw `substring` at base. † inferred, not re-run: the base emission is the raw `substring`, under which the true claim is
false — the matching scratch probes q08/q10 FAILED at base.)
