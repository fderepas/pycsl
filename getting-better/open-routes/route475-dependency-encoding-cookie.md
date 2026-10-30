# OPEN ROUTE #475 — DEPENDENCY SOURCE READ AS UTF-8, PEP 263 COOKIE IGNORED
**Status: REPAIRED (executor x3, driver run #3, 2026-10-30), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r475/` (10): `g30_b313_dep_latin1_value.py`, `g38_q701_utf7_hidden_rebind.py`, `g38_q702_utf7_string_len.py`, `g38_q707_latin1_string_eq.py`, `g38_q710_cp1252_string_len.py`, `g38_q711_vim_cookie_latin1.py`, `g38_q712_pkg_init_latin1.py`, `g38_q713_shebang_then_cookie.py`, `g41_q731_utf7_str_const_index.py`, `g51_e1905_utf7_const_bool.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F2 DEPENDENCY SOURCE READ AS UTF-8, PEP 263 COOKIE IGNORED (10)
  WHAT: the emitter folds an imported module's constants from `open(path).read()` (locale UTF-8), while CPython (and route #466's own import) decode the file by its coding cookie (latin-1 / cp1252 / utf-7 / vim-style / after a shebang)
  EXEMPLAR: g30/b313_dep_latin1_value.py (h313.py starts `# -*- coding: latin-1 -*-` and holds `S = '<bytes C3 A9>'`; f: `#@ ensures \result == 1`, `return len(S)`); g38/q701_utf7_hidden_rebind.py (h701.py `# -*- coding: utf-7 -*-`, `K = 1`, then the comment `# +AAo-K = 0`, which UTF-7 decodes to a NEWLINE followed by the statement `K = 0`; f: `n // K`)
  CPYTHON: b313: f() returns 2 (latin-1 decodes C3 A9 to two characters) -> VIOLATION contract; q701: ZeroDivisionError (CPython runs the hidden `K = 0`). Also cp1252, a vim-style `fileencoding=` cookie, a cookie on line 2 after a shebang, a package __init__, a utf-7 constant indexed / compared / used as a divisor.
  WHY IT PROVES: The emitter reads a dependency with the platform default codec, ignoring PEP 263: frontend/ir_resolve.py:200 (`_process_dependency`: `with open(filepath) as f: dep_source = f.read()`), also :168 (`_get_module_exports`), :1288 (`_process_dependency_structural`), :3256; the imported constant table (F1's `collect_module_constants`) is built from that UTF-8 text. Route #465's cookie-aware compile gate covers only the CLAIMED file, and route #466 decodes / compiles / runs the dependency correctly (it REFUSES q700 / q705 where the hidden code raises at import) but its values are not what the emitter folds.
  PROPOSED SYSTEMATIC REPAIR: ONE DECODER FOR EVERY SOURCE: read every dependency (and every file any frontend pass opens: ir_resolve, pure_ast.py:3787, #461's scans) as BYTES and decode with `importlib.util.decode_source` / `tokenize.open` (cookie + BOM, exactly CPython's rule); or, allow-list polarity, apply route #465's gate to every resolved program module: decode with `tokenize.detect_encoding`, and REFUSE a dependency whose decoded text differs from its UTF-8 reading (which also refuses every utf-7 trick). Witness: the 10 F2 probes; control: a dependency with a `utf-8` cookie and non-ASCII text keeps verifying.
  PROBES: g30/b313_dep_latin1_value.py g38/q701_utf7_hidden_rebind.py g38/q702_utf7_string_len.py g38/q707_latin1_string_eq.py g38/q710_cp1252_string_len.py g38/q711_vim_cookie_latin1.py g38/q712_pkg_init_latin1.py g38/q713_shebang_then_cookie.py g41/q731_utf7_str_const_index.py g51/e1905_utf7_const_bool.py
```

## Repair (executor x3, driver run #3, 2026-10-30)

ONE DECODER, allow-list polarity: route #465's gate applied to every resolved module at `_resolve_module_path`
(`frontend/ir_resolve.py`), the single function every frontend reader (`_process_dependency`,
`_get_module_exports`, `_process_dependency_structural`, the #143 / #326 passes) obtains a dependency path from
(inline, restructured to one tail; mirror twin `\trusted`; no axiom): the file's BYTES are decoded by CPython's
`tokenize.detect_encoding` (cookie, BOM), and that text must equal its UTF-8 reading (newlines / BOM normalised),
else the import is REFUSED (`PYCSL-R475-DEPENDENCY-ENCODING`, new code), as is a file CPython cannot decode. The
route #474 binding table parses the dependency's BYTES with CPython's own `ast.parse` (cookie-aware). All 10
witnesses: PROVED at base 8aaa864ca, REFUSED (route #475) at the repair (q712's package `__init__` included).
Corpus `7460`-`7462` (PROVED at base, REFUSED now), controls `7463` (utf-8 cookie, non-ASCII), `7464` (latin-1
cookie, ASCII text). Over-refusal: no repo module other than the new witness helpers trips the gate (scan of
`src/pycsl/Lib`, `src/pycsl_lib`, both corpora). annotations.md 7.311.
