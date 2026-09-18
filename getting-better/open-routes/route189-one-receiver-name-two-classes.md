# ROUTE #189 — one receiver name, two classes, one contract

**Status: REPAIR DRAFTED by gen #29 (worktree wtAI, branch wip/g29-r189, on top of #188).** Severity 1.
Generator: reading `IRScanner.find_record_var_classes` for the assumption it makes (the #188 lesson —
a resolution that maps many things to one).

## Measured at `8a30d42f`

    class C:  #@ ensures \result == 1   def get(self) -> int: return 1
    class D:  #@ ensures \result == 2   def get(self) -> int: return 2

    #@ ensures \result == 1
    def probe(flag: int) -> int:
        if flag > 0: o = D()
        else:        o = C()
        return o.get()                       PROVED   (CPython 2 for flag > 0)

`find_record_var_classes` `update()`s every nested scope into ONE FLAT MAP, so the last branch
scanned wins: `o` resolved to `C`, and the single call site was emitted as one abstract stub
carrying `C.get`'s `ensures`. The emitted WhyML says it plainly — both branches bind a local that
goes out of scope, then `(o_get_0 ())` with `ensures { result = 1 }`.

This is route #166 from the other end: there, two call sites collapsed onto one stub NAME; here, one
call site collapses onto one CLASS.

## Repair (draft)

The scanner is lowered by the certified `sdict` dict-fold (`recognize_dictfold`), and every shape
that carries the ambiguity marker inside it loses that lowering — measured three ways (a
list-of-dicts local, a `Set[str]`, a read of the map's own values), each ending in
`This expression has type int, but is expected to have type string` in the mirror's emission. So the
refusal reads the SOURCE, like routes #175/#179/#187: a non-trusted function that binds one name to
TWO different record classes and then calls a method on that name is refused
(`PYCSL-R189-AMBIGUOUS-RECEIVER-CLASS`). Measured emission-inert: scanning `src/` and the whole
reference corpus for the shape gives ZERO hits. Witnesses 1666 (XFAIL), 1667 (PASS control — one
local per class still proves).
