# FINDING (gen #33, 2026-09-29) — AN ORACLE'S ARGUMENT POOL WAS KEYED ON A NAME THAT IS NOT UNIQUE ACROSS THE CORPUS

**`bin/check-corpus-contract-truth-args.py` was ORDER-DEPENDENT ON FILENAMES.** Its `PARAM_POOL` was
keyed `(function name, parameter name)` with no file, and it is a module global built by `collect`
over the whole corpus — so whichever file it visited LAST won the key, and every other function of
that name was then called with the winner's argument pool.

## HOW IT SURFACED — BY ADDING ONE UNRELATED FILE

Battery #8 turned the plane RED, reporting FOUR pre-existing functions in OTHER files
(`0651.py::f`, `1310_route113::f`, `0540.py::use_str`, `1003_parametric_datatype_faithful::use_str`),
none of them touched by the change. **Isolated by bisecting my own commit in a worktree rather than
by guessing**: the emitter change was innocent, corpus 1918 was innocent, and **1919 alone did it** —
by declaring `def f(x: str)`, which wrote `PARAM_POOL[("f","x")] = STR_POOL` and handed strings to
every other corpus `f(x)`, including int-annotated ones, which then raised.

## THE CONTAMINATION IS NOT ABOUT ONE FILE

Measured over both corpora:

    distinct (funcname, paramname) keys                                   3249
    keys defined in MORE THAN ONE corpus file                              217
    of those, keys whose ANNOTATIONS DISAGREE across files                  39
    worst: ("f", "x")  ->  54 files, tags {Literal[b'x'], None, bool, float, int}

`f` and `x` are the two commonest names in a test corpus. The pool has been cross-contaminated for as
long as the key has omitted the file, and every inherited ceiling was measured under one particular
contamination pattern that a `sorted(glob)` happened to produce.

>>> **A CORPUS-WIDE TABLE KEYED ON A NAME THAT IS NOT UNIQUE ACROSS THE CORPUS IS AN ORDER-DEPENDENT
>>> ORACLE.** It does not announce itself: it passes, with a stable-looking number, until somebody
>>> adds a file whose name collides. The fix is the FILE in the key, never a bigger ceiling.

## THE FIX, AND WHAT IT DID TO THE NUMBERS

`PARAM_POOL` is now keyed `(basename, function, parameter)` at both writers and the reader.

    before fix (contaminated):  7702 evaluations, 14 inherited disagreements   [green]
    with 1919 added, unfixed:   RED — 16 > 14, and 3 no-normal-exit entries
    after fix, 1919 present:    7714 evaluations, 14 inherited disagreements   [green]

**The ceiling did not move**, so nothing had to be re-baselined — and the evaluation count ROSE by
12, because functions that were being handed the wrong pool are now handed their own. That is a
measurement improvement, not a tolerance increase.

## WHY THIS IS WORTH MORE THAN THE BUG IT BLOCKED

I nearly recorded this as "my corpus file broke a ratchet" and raised the ceiling. The two things that
stopped that were the campaign's own rules: **verify both ends** (the plane was green at the
pre-change commit, so the RED was mine to explain) and **isolate before attributing** (bisecting the
commit showed the emitter change was innocent and pointed at a single file). The ratchet was right;
what was wrong was an oracle nobody had asked whether its key was unique.
