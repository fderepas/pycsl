# OPEN ROUTE #276 — `ord(s) < 256` / `ord(chr(n)) == n` FOR CODE POINTS >= 256 (residual of route #69)
**Status: OPEN (gen #36, 2026-10-18), Severity 1.** Red-team round 5; driver-reproduced at HEAD (s11/s12 rc=0; CPython 8364/300).
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
