# ROUTE #191 — a `None` STORED into a list element, a dict value, a field or by `append` reads back as the integer 0

**Status: route #56's GENERAL REPAIR.** Severity 1.
Generator: the four carriers route #184 measured and recorded OPEN ("Measured and NOT adopted").

## Measured at `202c9c00`

    xs: List[Optional[int]] = [1]; xs[0] = None;   v = xs[0]; if v == 0: return 1   PROVED   (CPython 2)
    d: Dict[str, Optional[int]] = {"a": 1}; d["a"] = None; v = d["a"]; if v == 0: ... PROVED (CPython 2)
    b = Box(); b.v = None;                            if b.v == 0: return 1         PROVED   (CPython 2)
    xs: List[Optional[int]] = []; xs.append(None); v = xs[0]; if v == 0: return 1   PROVED   (CPython 2)

`_expr_to_whyml` has TWO `None` arms — the TYPED leaf (`isinstance(node, NoneExpr)`) and its
dict-shaped twin (`t == "None"`). Route #44 gave the dict-shaped one route #44's opaque
`pycsl_none`; route #184 did the same for a `None` ELEMENT of a list literal and a `None` VALUE of
a dict literal, at the two literal BUILDERS. The TYPED leaf still answered the literal `0`, and
every STORE position reaches it — so the stored value was a DEFINITE zero and `== 0` was decided,
wrongly.

The baseline entry that blessed the typed arm in `bin/check-singleton-constant-lowering.py` said the
value positions "are intercepted upstream of this arm". That was a claim about the code, and these
four measurements refute it: nothing intercepts a store.

## Repair

The typed `NoneExpr` leaf answers the SAME opaque `pycsl_none` as its dict-shaped twin. `None` is
one shared singleton, so `x is None` after a `None` store still PROVES (witness 1678) while
`x == 0` becomes UNDECIDED (witnesses 1673-1676). An ordinary integer store is untouched
(witness 1677). The `check-singleton-constant-lowering` baseline entry is RETIRED, not
re-justified — the arm no longer answers a constant, exactly as for `UnknownPyExprExpr` and `str`.

## The prerequisite it needed — and the latent defect that prerequisite exposed

Route #184 measured this change as moving **16 mirror emissions**, which is why it was deferred.
Re-measured here it moves 13 mirrors, 19 corpus files and 2 python-reference files — and ONE of
those, `0933`, moved by **+277 lines**: the whole `emit_ir` ADT theory was spliced into it.

That had nothing to do with `None`. `Module6_WhyMLTranspiler._exprir_theory_symbols` computes the
set of names the deferred ADT theory DECLARES by regexing the theory's own emitted text — but,
unlike its sibling `_opaque_accessor_symbols`, it did NOT strip comments first. The theory's prose
contains the phrase `` `val function` ``, so `\bval\s+(\w+)` captured a symbol named **`function`**,
which the theory does not declare. The deferral then re-inserted the entire theory into any
`@mutable_state` file whose emitted body contained the words `val function` — i.e. any file that
declares an abstract op. Route #191 is the first change that makes such a file declare one.

The same defect read the other way is the dangerous one: a theory symbol REALLY declared as
`val function f` would be captured as `function`, the real name `f` would be MISSED, and a file
that referenced `f` would lose the theory it needs and fail to type-check. The theory declares no
such symbol today, which is the only reason this has not bitten.

Repaired in the same increment: strip comments and string literals first, and let the `val` pattern
skip an optional `function` / `predicate` keyword. With that in place `0933`'s emission moves by
EXACTLY the one intended line, `val function pycsl_none : int`.

## Lesson

>>> A DEFERRAL THAT DECIDES BY "DOES THE REST OF THE FILE MENTION A NAME I DECLARE?" IS ONLY AS
>>> GOOD AS ITS LIST OF NAMES, AND A LIST OF NAMES SCRAPED FROM TEXT THAT INCLUDES ITS OWN PROSE
>>> CONTAINS WORDS THE CODE NEVER DECLARED. The sibling routine three definitions away already
>>> stripped comments and said why in its docstring; the one that did not was never exercised on a
>>> file that could trip it until an unrelated change made one.
