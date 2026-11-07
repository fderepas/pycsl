# OPEN ROUTE #72 — `str.split("")` RAISES `ValueError` AND HAS NO TRIGGER ROW
# (found 2026-09-11 by relaunch #55, at `e5b4cbf4`)

## THE CARRIER

```python
#@ no_exception \all
#@ ensures True
def f() -> int:
    s = "ab"
    parts = s.split("")      # CPython: ValueError: empty separator
    return 0
```

**`[+] Verification SUCCESS! All contracts formally proven.`**

The emitted body shows the same shape route #68's `float(<str>)` had — **the separator is
HASHED TO AN INT before it reaches an opaque val**:

```whyml
  val s_split_1 (x0: int) : int
  ...
    let parts = ref (s_split_1 313406155) in
```

So there is nothing to write a condition over, and no trigger row exists for `.split`.

## THIS IS THE SEVENTH CARRIER OF ONE DEFECT, AND THAT IS THE HEADLINE

`#64` (a missing row), `#65` (four rows consulted by NOTHING), `#66` (three missing rows),
`#68` (three more, one of them a row that existed and was never injected), `#71` (an ERASED
operation), and now `#72`. **Every single probe aimed at the exception model has found
something.** That is no longer a series of bugs; it is one defect — **nothing relates
`exception_model.TRIGGERS` to the set of operations the emitter actually EMITS** — wearing
seven route numbers.

**`#@ no_exception \all` should today be read as "none of the exceptions this table happens
to model", which is not what the directive says and not what a user will assume.** The
completeness gate named in route #66 is worth more than any further individual repair, and
each new carrier raises its value rather than lowering it.

## THE REPAIR SHAPE

REFUSE, as for `float(<str>)` — the argument is hashed away, so no faithful obligation can be
injected. Conservative form: under a `ValueError` (or `\all`) `no_exception` context, refuse
`.split(sep)` unless `sep` is a NON-EMPTY string literal. That keeps the common
`s.split(" ")` working and refuses both the definitely-raising `s.split("")` and the
undecidable symbolic separator.

`"a b".split(" ")[5]` (an `IndexError` on the result) is a SEPARATE shape and is currently an
EMISSION-FAIL, so it is unreachable rather than safe — retry it if the split-element path
ever lowers.

## STATUS: **CLOSED**

Refused under a `ValueError`/`\all` `no_exception` context unless the separator is a
NON-EMPTY string LITERAL. That keeps `s.split(" ")` working (control `1174`), refuses the
definitely-raising `s.split("")` and also refuses an undecidable SYMBOLIC separator — the
conservative direction, since the separator is hashed away and no condition can be written
over it.

**REFUSES THE CLAIM, NOT THE OPERATION:** `s.split("")` WITHOUT a `no_exception` context
still emits and proves, exactly as before. Measured.

### GATES
All 32 planes green; fidelity 887/887 verbatim; mirror type-clean and byte-inert; both
corpora byte-inert; metric unchanged at 459. Witnesses `1173` (negative, anti-vacuity
verified both ways by disabling the guard) and `1174` (positive control).
