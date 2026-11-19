# OPEN ROUTE #609 — ROUTE #605 BYPASS THROUGH ROUTE #171: try: y = v[0] except IndexError: return 0 ON A PyVal SEQUENCE — THE ELEMENT READ HAS NO BOUNDS CHECK, SO THE HANDLER IS DEAD IN THE PROOF WHILE CPYTHON TAKES IT
**Status: REPAIRED (driver run #7, executor u46, branch run7-u46 off run7-int62 c4159443b; annotations §7.609). Mechanism: the §7.603 / §7.605 fail-closed FRONT-END refusal pass in `pycsl.py::_run_pipeline` (twin `\trusted`); Module 6 untouched (mirror-inert). Rule: PYCSL-R609-PYVAL-READ-UNDER-HANDLER (a subscript read of a PyVal value / sequence inside a `try` body whose handler catches IndexError / KeyError / TypeError / LookupError / Exception / BaseException / bare -- TypeError and its bases only for a str key on a value not narrowed to a dict -- or inside `with suppress(..)` of one, every non-`\trusted` function).** Opened as: OPEN, Severity 1, PRE-EXISTING (proves at L9 and at the lvT tip). Red team rt60 F3 (d22). R605 fires only on a declared IndexError claim.

## The repair (driver run #7, executor u46)

- Rule: see the status line; annotations §7.609.
- rt60 exemplar d22: PROVED at base int62 c4159443b (re-measured by u46), REFUSED at HEAD in the default / typed / store models.
- u46 probes (`witnesses-r609/u46-probes/`), all held at base already: q07 `except Exception` (route #174; now reported as R609), q04 a same-file callee doing the read (route #178), q08 `with suppress(IndexError)` (route #257; R609 at HEAD), q11 a str key on a narrowed dict under `except KeyError` (L3-tc), q16 `v.pop()` / q17 tuple unpack / q18 `int(v)` under their handlers (refused by the callee whitelist / unpack / int rules).
- Corpus witness (expected FAIL, refused x3): 10036. Control (expected PASS): 10048.
- Advice followed: `witnesses-r609/advice/a609_test_before_read` (= control 10048).
