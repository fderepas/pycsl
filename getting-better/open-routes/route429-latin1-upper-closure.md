# OPEN ROUTE #429 — str.upper() OF A LATIN-1 STRING CAN LEAVE LATIN-1; THE MODEL KEEPS EVERY CODE POINT < 256 
**Status: NOT REPAIRED (declared assumption), Severity 2 (arguable).** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r429/` (2): `p03_upper_ydiaeresis.py`, `p04_upper_micro.py`.

```
#429 str.upper() OF A LATIN-1 STRING CAN LEAVE LATIN-1; THE MODEL KEEPS EVERY CODE POINT < 256   [arguable: LATIN1-STR closure]  (2)
  p03  ensures ord(s.upper()[0]) < 256, s = "ÿ" PROVED                                       CPython 376 (U+0178)
  p04  s = "µ" (micro sign)                                                                  CPython 924 (U+039C)
  The INPUT is inside LATIN1-STR's domain; the result of a str method is not, while the model asserts it is. (Length changes
  -- "ß".upper() / casefold / title / capitalize / swapcase -- FAIL, so the model does not claim length preservation.)
  REPAIR: either restrict LATIN1-STR's "every str" to exclude results of upper/title/capitalize/swapcase/casefold, or give
  these methods no code-point-range postcondition.

DECLARED MODEL ASSUMPTIONS / HELD ROUTES MEASURED LIVE (PROVED, NOT counted)
  x_a16 BUILTIN-EXACT; x_i17 FLOAT-FINITE; x_g03 / x_g04 / x_h07 / x_j22 / x_j26 route #411 (held; still PROVE at bcefbe788).

CORRECTLY REFUSED / FAILED (selection of what attacked the new rules head-on)
  #404 metaclass: ABCMeta / EnumMeta / builtins.type / `T = type` bases, an inherited metaclass M2(M), metaclass= via **KW,
       __init_subclass__ / class decorator / __set_name__ stores, type.__setattr__(M, "__hash__", ..) at module level or in
       the driver, setattr(*(..)) (a01-a12, s01-s04): refused.
  #403 / #402: unverified __eq__ / __ne__ / __lt__ / __gt__ / __bool__ / __len__ / __str__ / __format__ / __repr__ / __iter__
       / __contains__ / __index__ / __enter__ raising under no_exception (h20-h39): refused or failed.
  #226 flip: subclass __init__ breaking the invariant, module-function store, setattr, property setter, custom __setattr__,
       default-param violation, mutating method, class-attribute shadow, dataclass, list-param alias, fill alias, keyword
       super(): refused / failed (d01-d18). Explicit dynamic stores (__setattr__, object.__setattr__, __dict__, vars): n02-n06 failed.
  #412-#417: pow(0, -1), divmod(a, 0), x ** -1.0, mixed int/float overflow, slice step 0, bytes(10**20), ljust / zfill /
       center huge, to_bytes, chr, str/list.index, remove, pop, popitem, next, max/min empty, pow(.., .., 0), shifts by a
       negative count, range length with a step, str repetition (e01-e70): refused or failed. `%` with trailing '%', '%%'
       width, huge width / precision, %d past 4300 digits (k01-k30): refused or failed.
  #420: shapes with ensures / no_exception now go generic (r01-r06, o00-o06): refused, ill-typed or failed.
  Shared mutable state: mutable default args, class-attribute list, iterator exhaustion, closures, lru_cache, [row] * 2,
  dict.fromkeys / setdefault / get aliasing (p30-p39): refused or failed. Module-level / driver mutation of a global after
  its definition (m30-m43): refused or failed.
  Unicode: ß length changes, isalpha / isupper / isidentifier / isprintable / strip / split / splitlines on Latin-1
  whitespace and letters, isdigit '²' then int(): failed (p01-p23 except p03 / p04).

NOTES
  Further families tried after the first write-up, all REFUSED or FAILED (no false proof):
  u00-u23  stdlib / unbound-method mutation of a list / dict / set / bytearray argument (heapq, bisect, operator.setitem /
           iadd / delitem, list.append(xs, ..), dict.update(d, ..), struct.pack_into, map / reduce / sort-key side effects,
           genexp exhaustion, a generator function over the mutated dict): the frame is havocked or the call refused.
  v01-v35  hashing through lru_cache / Counter / dict.fromkeys / set().union / frozenset / dict(zip) of List[List[int]];
           json.dumps of unserializable values; the §7.83 listed stdlib functions with bad arguments (shlex.quote(int),
           os.path.join mixes, math domain / range errors, randint, unicodedata, textwrap widths): refused or failed.
  y00-y06  a subclass that becomes unhashable (own __eq__, @dataclass, __eq__ = A.__eq__, __hash__ = None, grandchild).
  z00-z14  subclasses / metaclasses defined in a nested class body or under if / try / with / for / while (closed world
           holds for every statement nesting), GD and override refinement through them.
  q00-q19  int -> float OverflowError in **0.5, pow, sum, math.isfinite / isinf / isnan / isclose / fabs / hypot / atan2 /
           sin / fsum / pow / exp, complex(n), divmod(n, 1.0), round(n * 1.0), random.uniform; time.sleep(-1).
  r00-r38  Python semantics of % and // with negative divisors (body and contract), divmod, str find / rfind / count /
           index / replace / split with empty needles, slices with negative steps, range lengths, round / int truncation,
           startswith(()), strip / lstrip / zfill / title / splitlines / split maxsplit / partition / min / < on str.
  xx01-18  raises-when narrowing, named no_exception sets vs subclasses (UnicodeDecodeError, JSONDecodeError,
           UnicodeEncodeError under ValueError; LookupError / ArithmeticError / Exception), finally-return, try/else,
           re-raise, handler raising, raise from, assert, contextlib.suppress, except tuples / bases.
  w00-w07  explicit / implicit dunder calls (__setitem__, __call__, __iadd__, A.put(a, ..), getattr(a, "put"), a bound
           method name) under a class invariant: all checked (only __init__ is the frame-less val, #425).
  f18 is an INVALID probe (the exception is raised by `f"{(2**40):c}"` in the driver). i-series first run used `-> object`
  (uninformative Unknown); re-run with `-> int` (the counted results). Timeouts are not counted (g01, j20, j21, j26, m16, p14-p16).
  Every pycsl run went through heavy.sh (<= 2 concurrent slots); no job of this team is left running.
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be)

Measured on the candidate: p03 / p04 PROVE by default and FAIL under `--strict-latin1`, so the false proof lies inside the DECLARED LATIN1-STR assumption (every str value has code points < 256; `'\u00ff'.upper()` is a str value outside it). Modelling upper()'s escape needs the opt-in model; refusing upper / title / capitalize / swapcase / casefold on symbolic strings was not measured (time box spent on #421-#428). Amending the assumption's report text touches `_build_soundness_report`, a VERBATIM mirrored driver function (fidelity + proof owed), so it was left for a dedicated change.

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

OPEN: the LATIN1-STR statement should name str case-mapping results explicitly.

## RUN #8, EXECUTOR u57 (2026-11-19/20) -- USER DECISION: refusal-only fix for non-Latin-1 str values

**Status: REPAIRED for str VALUES above Latin-1 that enter the model (`PYCSL-R429-NONLATIN1-STR-LITERAL`); the
LATIN1-STR assumption for SYMBOLIC str values (`ord(s) < 256`, `s.upper()` of a Latin-1 input, p03 / p04) stays
DECLARED (unchanged by this decision).** Branch `run8-u57`, base 97a4551d8 (main after L16).

### The bug (pre-existing, red team rt68)
`whyml_string_literal` wrote a code point > 255 as its 2..4 UTF-8 bytes, so the model's length / index / slice /
comparisons were the bytes': `x == "😀"` => `len(x) == 4` (p17) and `len(x[0:3]) == 3` (p19) PROVED at base
(CPython 1 / 1). rt68's p15 / p16 (negative bounds) prove only with batch D's R3; at base they are unconstrained.

### Measurement (base 97a4551d8, default model, every probe CPython-checked; logs `scratchpad/u57/meas{,2}/logs/`)
Probe shape: `if x == "a"+c+"b": if CLAIM: return 0 / return 1`, `ensures \result == 0`; a TRUE claim that proves is
faithful, a FALSE claim that proves is a false proof.

| claim on x == 'a'+c+'b' | ASCII 'z' | Latin-1 U+00E9 | Latin-1 U+0080 | Latin-1 U+00FF | BMP U+20AC | astral U+1F600 |
|---|---|---|---|---|---|---|
| `len(x)==3` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `x[1]==c` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `x[2]=='b'` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `x[1:2]==c` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `x[-1:]=='b'` | true:not proved | true:not proved / false:not proved | false:not proved | true:not proved / false:not proved | false:not proved | false:not proved |
| `x[0:2]=='a'+c` | true:proves | true:not proved / false:not proved | false:not proved | true:not proved / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `c in x` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:not proved | false:not proved |
| `x.find('b')==2` | true:not proved | true:not proved / false:not proved | false:not proved | true:not proved / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `x!='a'+alt+'b'` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:not proved | false:not proved |
| `len(x+c)==4` | true:proves | true:proves / false:not proved | false:not proved | true:proves / false:not proved | false:**PROVES (unsound)** | false:**PROVES (unsound)** |
| `len(x[:-1])==2` | true:not proved | true:not proved / false:not proved | false:not proved | true:not proved / false:not proved | false:not proved | false:not proved |
| `x[-2]==c` | true:not proved | true:not proved / false:not proved | false:not proved | true:not proved / false:not proved | false:not proved | false:not proved |

Reading: code points 0..255 (ASCII, Latin-1 incl. 0x80 and 0xFF) -- NO false claim proves for any operation (len,
index, positive / negative slices, concatenation, `in`, `find`, equality, `ord`); the true claims prove exactly where
ASCII's do (negative bounds / `find` / `ord` are incomplete for ASCII too). So Latin-1 is FAITHFUL and is NOT refused.
BMP (U+20AC, the combining U+0301) and astral (U+1F600): false claims PROVE for len, index, positive slices,
concatenation length and `find` (7 of the 12 claims per character), and `ord(x[1]) != cp`. Lone surrogate: the encoder crashed (refused by
accident). `chr(300)`: `len(chr(300)) != 1` and `chr(300) == chr(301)` do NOT prove (one length unit; its code is the
declared LATIN1-STR counterexample, corpus 3021, unchanged). `bytes.decode`: no model (both claims unproved).
`"\xff".upper()` (U+0178): not provable either way (raw `(pystr_chr 376)`, no law), refused by the emission rule.

### The rule (as landed)
Decided on what ENTERS THE MODEL (end of `_run_pipeline`, twin `\trusted`): `whyml_string_literal`'s UTF-8 arm writes
decimal escapes `\ddd` (same bytes for Why3; the mark of a code point > 255), route #411's literal pass reads each
WhyML string literal (comments / attributes skipped) back as its Python value; a value with a code point > 255 refuses
the program, except a value the source holds ONLY as `raise` / `print(..)` message text (payloads are never read:
wildcard arms + route #233; `print_1 (str_hash_op ..)` returns nothing; assembling the text raises nothing). Not
excused: any other occurrence of the value (docstrings included), a `#@` string token, a fold, an import, a file that
binds `print`.

### Over-refusal, measured BEFORE narrowing
1. First version = SOURCE refusal of every non-docstring str constant > 255 + the emission check: corpus root 14
   files refused (7 expected-PASS / unheadered: 1031, 3020, 3022, 3023, 3028, 3029, 8030 -- all literals in a
   `__main__` driver or an unread bare string; 7 expected-FAIL), pyref 0, mirror 14 / 53 (audit_proof,
   audit_proof_reverify, core_ir_semantic, Module3_Weaver, Module5_IREmitter, desugar, ir_inline, monomorphize,
   expressions, statements, stmt_control_flow, proof2why3/normalize, proof2why3/parser, pycsl -- messages of
   raise / print / return). Logs `scratchpad/u57/orf/broad-cand.tsv`, `broad-base.tsv`.
2. NARROWING 1 (sound: only what reaches the WhyML text can be decided on): emission-only. Mirror still refused: 7
   (audit_proof `"  ✓ "` print, desugar / Module5_IREmitter / expressions / stmt_control_flow `raise` messages with
   `—`, normalize `_UNICODE_OPS = {'∀': ..}` used by `out.replace(u, a)`, pycsl `_why3_typecheck`'s returned message
   `"why3 not found on PATH — ..."`). Corpus 0. Log `scratchpad/u57/orf/nonarrow-mir.tsv`.
3. NARROWING 2 (sound, see the rule): raise / print message text excused -> mirror 2 (normalize, pycsl).
4. pycsl: the `—` of `_why3_typecheck`'s message rewritten `--` in the live file and its mirror twin (text only).
   normalize: NOT narrowed -- the verified `normalize_prover_output` really does `str.replace` with 3-byte patterns
   over a Latin-1-modelled string (a Latin-1 input "\xe2\x88\x80" is rewritten in the model, not by CPython): a TRUE
   refusal. Per the driver's instruction (01:30Z) it is a SOUNDNESS-FORCED RE-TRUST (+1 marker, NOT progress;
   trusted-reasons `cost-scale:codepoint-str-model`, backlog heading "NAMED CAPABILITY -- route #429 soundness-forced
   re-trust"); the rest of the file emits unchanged and re-proves (4 / 4 Valid).
5. Stricter narrowing 2 (red-team hardening): no excusal for a value whose code point > 255 was written RAW (a fold, an
   import), and none at all in a file where any other non-statement str constant or `#@` token is above Latin-1.
   Re-measured: still 0 corpus / 0 pyref / 0 mirror refusals.
Final (candidate 50ffa6804, sweeps `scratchpad/u57/sw2/`): corpus root 3291 / 3298 0 MOVED / 0 GONE / 0 APPEARED (7 new
emitted sources), pyref 2185 / 2185 0/0/0 (each compared twice); mirror 53 / 53, 0 GONE, 3 MOVED: pycsl (the message),
frontend__Module3_Weaver (the stable hash of a `warnings.warn` literal holding `—` changed with its rendering;
`_coerce_to_int` hashes the escaped text; an opaque int nothing reads), proof2why3__normalize (the re-trust). All three
re-proved whole-file: pycsl 820 / 820, Module3_Weaver 331 / 331, normalize 4 / 4 (oom_kill 15 -> 15).

### Witnesses 10260-10279 (expected FAIL unless noted)
REFUSED in default / typed / store: 10260 (p15), 10261 (p16), 10262 (p17), 10263 (p19), 10264 (p18 "€"), 10265 (p21
combining), 10266 (p22), 10267 (contract-only literal), 10268 (fold "\xff".upper()), 10271 (`\N{GRINNING FACE}`), 10272
(module constant), 10274 (imported constant, multi_file_lib/consts429.py), 10275 (lone surrogate, p20). NOT refused,
FAIL by proof x3 (the literal never reaches the model): 10269 (f-string part), 10270 (format spec), 10273 (default).
Controls (expected PASS, default model): 10276 ASCII, 10277 Latin-1, 10278 comment emoji, 10279 docstring emoji.
(In typed / store, 10276-10279 fail Why3 typing -- "This function depends on external variables" -- a pre-existing
str-parameter limitation of those models; their emission is byte-identical to base.)
At base (hoare): 10262 / 10263 PROVED (the false proofs), 10260 / 10261 / 10264-10266 not proved.

## RUN #8, EXECUTOR u59 (2026-11-20) -- review rt71: narrowing 2 decided over the import closure

### The gap (rt71, PRE-EXISTING; confirmed by full proofs at u57's tip and its base)
Narrowing 2 excused a value > 255 that the MAIN file holds only as `raise` / statement-`print` text, deciding
"held elsewhere" (`_ne429` / `_nx429`) on the main file's AST and `#@` lines only. The model also takes str values from
IMPORTED modules: a parameter DEFAULT of an imported stub (`from m import h3`, `def h3(s: str = "€")`, called as
`h3()`) and a CONTRACT literal of an imported stub (`#@ ensures \result == "€"`). With `raise ValueError("€")` (or
`print("€")`) in the main file, `len(h3()) == 3` PROVED (CPython 1): rt71 k05 / h01 SUCCESS 2/2, h02 / k01 emitted.

### The rule (as landed, f11922e05; `pycsl.py::_run_pipeline`, twin `\trusted`)
Two more conditions, BOTH required for an excusal (on top of u57's source-side ones, unchanged):
1. EMITTED POSITION (`_np429`, computed in route #411's literal scan on the pre-rewrite text, with a stack of open
   parentheses -- comments / attributes / literals skipped as the scan skips them): from the literal, walk the
   enclosing groups outward; only `(str_concat_op ..)` groups (any argument), a group the literal itself opens, or a
   group whose first element is the inner group may be crossed; the walk must reach `(E ..)` right after `raise` (E a
   constructor), `(str_hash_op ..)` directly in `(print_1 ..)`, or a transparent group right after `let _ =` (the
   discarded message of a builtin raise, `let _ = (..) in raise ValueError`). A default argument, a contract term,
   any call argument, a comparison operand is NOT a payload: not excused, whatever module produced the value.
2. IMPORT CLOSURE: every `import` / `from .. import` (any depth, function-local ones included) of every module reached,
   transitively, resolved with `_resolve_module_path` (package prefixes; `from X import Y` also tried as submodule
   `X.Y`; `from . import y` takes the package `__init__.py`). In each NON-main module, every str constant OUTSIDE that
   module's own raise / print text (same closure as the main file's; `print` only when the module does not bind it;
   docstrings included) and every `#@` string token joins `_ne429`. An import the resolver refuses (exception on a
   module path), or a module that cannot be read / parsed, sets `_nx429` (no excusal at all).
Why sound: a payload is never read (Module 6 handler arms are wildcards, route #233 refuses `except .. as e` reads,
builtin tags carry no payload), `print_1 (str_hash_op ..)` and `let _ =` discard the value, and `str_concat_op` has no
precondition; the crossed groups contain no call taking the literal, so no obligation, branch, return value or contract
depends on it. (2) keeps u57's source-side guarantee across modules (no other module holds the value as data).
Choice: the brief's three options were measured. "Never excuse a value any non-main module holds, and let any
non-main >255 constant cancel" (the first WIP, f57b98601, per code point) refused the mirror desugar and
Module5_IREmitter: their closure reaches the LIVE `frontend` package (via `--import-path src/pycsl`), whose message
constants (and two non-message ones, ir_resolve.py:3287, monomorphize.py:711) carry the same U+2014 -- not a hole (no
such text enters those emissions). The emitted-position condition is what closes rt71's class directly (the
dependency value lands as `h3 ("\226\130\172")` / in a `ensures { result = .. }`), and makes the per-file / per-code-
point cancellation for dependencies unnecessary: any fold of dependency text placed outside a payload is refused.

### Probes (cwd = tree root, `--import-path src/pycsl`, logs `scratchpad/u59/e4/`; before = rt71 logs)
| probe | before (u57 tip / int73) | after f11922e05 (hoare / typed / store) |
|---|---|---|
| rt71 k05_import_default_clean (+ m429d) | PROVED 2/2 (rt71 ph2) | REFUSED R429 x3 |
| rt71 h01_import_func_exc (+ m429f) | PROVED 2/2 (rt71 ph2) | REFUSED R429 x3 |
| rt71 h02_import_func_print | emitted rc 0 (rt71 e7h) | REFUSED R429 x3 |
| rt71 k01_import_attr | emitted rc 0 (rt71 e9h) | REFUSED R429 x3 |
| controls k05b / h01b (no raise) | REFUSED | REFUSED R429 x3 |
| u57 n1 | R506 | R506 x3 |
| u57 n2 n3 n7 n8 n9 n10 | R429 | R429 x3 |
| u57 n4 (raise "— .." + str(n)), n5 (print f"✓ ..") | emit / PROVE | emit x3 (proofs: see w2) |
| u57 n6 (docstring read) | not refused, FAIL | not refused (rc 1, L3-tc), unchanged |
| t1 re-export (main -> mid -> default) / t2 `from pkg import mod` | - | not refused: the import is opaque (`val h3_0 () : int`), no literal enters; FAIL by proof |

### Witnesses 10320-10324 (census rows via `_census_row`, commit 578c57342)
10320 (rt71 k05: imported DEFAULT + main raise), 10321 (h01: imported CONTRACT literal + raise), 10322 (h02: contract
+ statement print), 10323 (k01: `import multi_file_lib.r429x_contract` attribute call): expected FAIL, REFUSED R429 in
hoare / typed / store (full pipeline, `scratchpad/u59/w2/`); CPython: VIOLATION (len 1). Dependencies:
`multi_file_lib/r429x_default.py`, `r429x_contract.py`. Control 10324 (expected PASS; ASCII-only dependency
`r429x_ascii.py`, main raise "€"): PROVED in hoare (2/2); typed / store fail Why3 typing ("variable int_mem does not
occur"), a pre-existing typed-model limitation of the import (the emission is untouched by the rule: corpus byte-diff 0).
u57's 10260-10279 re-run x3 at f11922e05: same verdicts as u57 (13 x 3 REFUSED; 10269 / 10270 / 10273 FAIL by proof;
10276 / 10277 PROVE x3; 10278 / 10279 PROVE in hoare, typed / store Why3-typing FAIL as before).

### Over-refusal (final rule, f11922e05; sweeps `scratchpad/u59/{bd2,mir2}`)
corpus root 3309 / 3310 vs `run8/v72/bd-int`: 0 MOVED / 0 GONE / 0 APPEARED (1 new source = 10324; 10320-10323 refused);
pyref 2185 / 2185 0/0/0; mirror 53 / 53 vs `v72/mir-int`, 0 MOVED / 0 GONE (audit_proof, desugar, Module5_IREmitter,
expressions, stmt_control_flow still emit, byte-identical). The first variant (f57b98601, closure-only, per-code-point
cancellation) had mirror 51 / 53: desugar and Module5_IREmitter GONE (`scratchpad/u59/D-mir.txt`), replaced.
