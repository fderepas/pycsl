# OPEN ROUTE #276 — `ord(s) < 256` / `ord(chr(n)) == n` FOR CODE POINTS >= 256 (residual of route #69)
**Status: RESOLVED (declared assumption LATIN1-STR), gen #37, 2026-10-19** — was OPEN (gen #36, 2026-10-18), Severity 1. See "Resolution" at the end. Red-team round 5; driver-reproduced at HEAD (s11/s12 rc=0; CPython 8364/300).
Witnesses `witnesses-r276/`. `ord_op` ensures `0 <= result < 256` (Why3 Char covers 0..255); #69's guard only catches
locals bound to non-ASCII literals. Repair: `ord` of an arbitrary str returns a code point in [0, 0x10FFFF] (no < 256
bound unless provably ASCII); `chr(n)` for n >= 256 must not round-trip through Char; ord("")/ord("ab") under
no_exception must owe len == 1.

## MEASUREMENTS (2026-10-18, r275 executor; status stays OPEN — every sound option measured disproportionate)
- Re-confirmed at 5a307a33: s11 (`ord(s) < 256` for a 1-char param) and s12 (`ord(chr(300)) != 300`) rc=0.
  New: `requires len(s) == 2; no_exception \all; return ord(s)` also PROVES — but `TypeError` is not in
  `KNOWN_EXCEPTIONS` (the five Phase-1 exceptions), so `no_exception \all` does not claim it; a `("call", "ord")`
  TypeError row would need TypeError added to the no_exception universe (scope change, not a local repair).
- ROOT: Why3's `string.Char` has `axiom code: forall c. 0 <= code c < 256`, and every str VALUE (a parameter as
  much as a literal) is a Why3 `string` of such chars. Removing `0 <= result < 256` from `ord_op`/`char_code_at`
  changes nothing (their `result = Char.code (...)` re-derives it). The bound can only go if `ord` stops being
  `Char.code`, in BOTH the body vals and the contract lowering (they must agree atom-for-atom).
- Cheapest axiom-free model found: `py_ord_at s i = Char.code (Char.get s i) + 256 * hi s i` with `hi` an
  uninterpreted function clamped to [0, 4351] by a definitional `if` (range exactly [0, 0x10FFFF]; `py_ord_at <
  256 -> = Char.code` is linear). BLAST RADIUS (by reading, not run): every proof that feeds `ord(name[i])`
  into a cited lemma stated over `Char.code` loses its antecedent — corpus 0708 (`field_to_str_round_trip`),
  0712, 0702 (`chr(ord(c)) == c`), and the os stub (`_pad_name`, `_build_direntry` -> `dir_blit_marker*_intro`,
  `_byte_codec_char`, whose `chr(ord(c)) == c` is TRUE in CPython for every char and becomes unprovable). A
  Latin-1 hypothesis (`ord(name[i]) < 256`) restores them, but it cannot be DISCHARGED for a literal name at a
  call site (`hi "a" 0` is as unknown as `hi s 0`: the model cannot tell a literal from a parameter), so every
  os caller with a literal name would regress. Distinguishing them needs per-value code-point state — a model
  change, not an inline repair.
- `chr(n)` for n >= 256: an obligation `requires { n < 256 }` on `chr_op` alone closes s12, but it also lands on
  the mirror's `pure_ast.py::visit_FormattedValue` (`chr(node.conversion)`, not `\trusted`, unconstrained
  argument) — a mirror regression; and the contract-side `(Char.chr n).contents` still lets `ord(chr(300))`
  be `< 256` inside a contract. Making `chr` opaque above 255 does NOT close s12 (ord of any 1-char string is
  still `< 256`). So #276 is ONE repair (the ord model), not two.

## Resolution (gen #37, 2026-10-19) — RESOLVED as the declared model assumption LATIN1-STR

Re-reproduced at c5a2cebe before the change: s11 and s12 rc=0 (still open). Decision **(B)**, the
FLOAT-FINITE / BUILTIN-EXACT precedent: the default keeps the 8-bit `string.Char` model and DECLARES
it; an opt-in strict mode drops it. Option (A) (a faithful default) was decided against BY
MEASUREMENT: the strict mode below IS the cheapest axiom-free faithful `ord`/`chr` model (an
uninterpreted, clamped code point not linked to `Char.code`), and its measured cost as a default
would be 3 of the 12 default-PASS root files among the 22 that mention `ord`/`chr` (below) plus every
os-stub codec proof keyed to `Char.code` — a disproportionate regression, as the r275 executor
predicted by reading. No cheaper faithful repair was found: anything keeping the `< 256` law
available to the cited lemmas keeps the witnesses proving.

**Covered.**
- `pycsl --soundness-report` lists `LATIN1-STR` ("every str value consists of code points 0..255
  ...: ord(c) < 256, and chr(n) is modelled only for 0 <= n < 256; str values in general rely on
  it, ord/chr sites directly") under `model_assumptions`, `strict_mode: --strict-latin1`,
  `relied_on_by` = every `ord`/`chr` call (`f: ord(...) in body|contract`) and, per function,
  the str values read (`f: str values (8-bit string model) s, \result, a string literal`).
  Conservative (over-, never under-reported). Inline in `_build_soundness_report` (mirror twin
  `\trusted`).
- Docs: static-semantics τ(str) note + Appendix C.1 row + "What `--strict-latin1` covers";
  translational §T.10.1 row + §T.10.5 entry; README (declared model assumptions paragraph);
  `bin/check-assumed-facts.py` docstring.
- `--strict-latin1` (opt-in; `expressions.py::_call_named_builtins`, inline, mirror twin
  `\trusted`): `function pycsl_cp (s) (i) = let r = pycsl_cp_raw s i in if 0 <= r <= 1114111
  then r else 0` (definition over an uninterpreted function, no axiom); `ord(s[i])` ->
  `pycsl_cp s i`, `ord(x)` -> `pycsl_cp x 0` (body vals `pycsl_vord_at` / `pycsl_vord_op`, same
  atom; the route-#67 IndexError wrap kept); `chr(n)` -> `pycsl_chr n` (uninterpreted) in a
  contract, body val `pycsl_vchr_op` ensuring length 1, `result = pycsl_chr n`, `0 <= n <
  0x110000 -> pycsl_cp result 0 = n` (route-#66 ValueError wrap kept); a 1-char ASCII literal's
  `ord` folds to its code point.
- `no_exception`: `ord(s)` with `len(s) != 1` raises `TypeError`, which is NOT in
  `KNOWN_EXCEPTIONS` (`no_exception \all` = the five Phase-1 exceptions; `no_exception TypeError`
  is refused as unknown). Documented as SCOPE (static-semantics C.1, translational §T.10.5), not
  widened.

**Corpus (block 3020-3039; 3020-3029 used).**

| file | program | default | `--strict-latin1` |
|---|---|---|---|
| 3020 / 3024 | `requires len(s)==1 ensures \result < 256`, `return ord(s)` | PASS (assumed) | FAIL (Unknown) |
| 3021 / 3025 | `ensures \result != 300`, `return ord(chr(300))` | PASS (assumed) | FAIL (Unknown) |
| 3022 / 3026 | contract `ensures ord(s) < 256` | PASS (assumed) | FAIL (Unknown) |
| 3023 / 3027 | `ensures \result < 256`, `return ord(s[0])` | PASS (assumed) | FAIL (Timeout) |
| 3028 | controls: range [0,0x10FFFF], congruence, `ord(s[1])` body/contract, `len(chr(65))==1` + ValueError | PASS | (twin 3029) |
| 3029 | 3028's controls + `ord("a")==97` + `ord(chr(n))==n` for `0<=n<0x110000` | — | PASS |

`ord("a") == 97` is not a default control: the provers do not evaluate `Char.code (Char.get "a" 0)`
(measured Timeout); the full-range round trip is TRUE and default-unprovable.

**Measured strict cost** (the 22 pre-existing root corpus files mentioning `ord(`/`chr(`; no
python-reference file does): every expected-FAIL file stays FAIL (10); of the 12 default-PASS files,
9 stay PASS (0824, 0835, 0862, 0864, 0865, 1159, 1161, 1168, 1183) and 3 FAIL —
0702 (`ord_range`'s `0 <= ord(name[0]) <= 255`, FALSE in CPython, correctly lost; `roundtrip`'s
`chr(ord(c)) == c`, TRUE, lost), 0708 (`encode_field`/`decode_field` via the cited
`field_to_str_round_trip` over `Char.code`), 0712 (`write_name_field`, cited
`slot_name_byte_decode`/`field_to_str_round_trip`). The os stub (`src/pycsl_lib/os/`) proofs that
feed `ord(name[i])` to the `dir_blit_marker*` preamble facts over `Char.code` are not re-proved
under the flag here (by construction they cannot fire on `pycsl_cp`).

**Gates** (default emission): root corpus 1782/1792 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (10 new
sources); pyref 2186/2186, 0 MOVED / 0 GONE / 0 APPEARED; mirror 53/53, 0 MOVED; fidelity rc=0
(920 un-trusted mirror functions verbatim; 53 mirrors in sync); `\trusted` count 454 (unchanged);
no axiom added (ledger unchanged). No refusal message added or edited. Planes: fast 61/61 green;
`--slow` 84/84 green (rc=0).

**Not covered (residuals).** (1) Even under the flag the str SORT is the 8-bit Why3 string:
`==`/`len`/slicing/concat are those of 8-bit chars, so a pigeonhole argument over more than 256
distinct one-character values with distinct code points is derivable in principle (not by the
provers in practice); only a sequence-of-code-points str sort closes it (corpus-wide sort change,
like `ieee_float` for #250). (2) A non-ASCII string LITERAL is emitted as its UTF-8 bytes in both
modes (route #69 refuses `ord` over it; `len` of such a literal is constant-folded correctly, but
the literal's Why3 value is the byte string). (3) Contract-side `ord(chr(n)) == n` is unprovable
under the flag (only the body val carries the code-point fact). (4) The TRUE strict-mode losses
0702 `roundtrip`, 0708, 0712 and the os codec facts would need per-value code-point state (or
codec lemmas restated over `pycsl_cp`) — a model change.
