# ROUTE #104 — `#@ assigns self.xs[0]` ON A `\trusted` METHOD DROPS THE METHOD'S FRAME

**Severity 1. CLOSED gen #18 (2026-09-13). NOT on gen #17's carrier list — found by following
route #101's deferral to the guard it names and reading THAT guard's actual matching rule.**

## THE ONE-LINE STATEMENT

`_build_method_writes_map` (`module6_whyml/functions.py:7794`) is THE producer of a bodyless
method-`val`'s frame. It was keyed on the NODE TYPE of the assigns target
(`a.get("type") in ("FieldGet", "Attribute") and a.get("object") == "self"`), and
`#@ assigns self.xs[0]` lowers to `Subscript(FieldGet(self, "xs"), 0)` — neither. The target
fell out of the map, the method's `val` was emitted with no `writes`, and Why3 read it as PURE.

## HOW IT WAS FOUND — A DEFERRAL, LOCATED AND READ

The two collector loops in `_emit_frame_condition` deliberately SKIP every `self.<field>` and
DEFER to this map (re-emitting a self target there produced an unbound/duplicate `writes` and
regressed `formal_coll` / `formal_que`). That deferral is **correct**. While repairing route
#101 I had to decide what to do with a `Subscript` whose root is `self.<f>`, so I went and read
the guard the comment names.

>>> **A DEFERRAL IS AN UNVERIFIED CROSS-REFERENCE THAT READS EXACTLY LIKE A GUARD.** The
>>> comment is TRUE for the spelling its author had in view and FALSE for this one. Ranked
>>> generator #2 says: LOCATE the named guard and QUOTE ITS ACTUAL MATCHING RULE. The rule was
>>> keyed on the node type, and route #101's whole lesson is that node types are the wrong key.

## BOTH DIRECTIONS MEASURED, AND THE POSITIVE CONTROL FIRED

| spelling (identical stub, identical body) | emitted frame | `ensures \result == 7` |
|---|---|---|
| `#@ assigns self.xs`     (Attribute) | `writes` emitted | **FAILS** — the honest frame |
| `#@ assigns self.xs[0]`  (Subscript) | **ABSENT** | **PROVES** |
| `#@ assigns self.xs[0..1]` (range)   | — | **PARSE ERROR** |

CPython: `Box().driver()` returns **5**. PyCSL proved **7**.

**THERE IS NO RANGE ESCAPE HATCH FOR A SELF-FIELD.** `_parse_assigns_region` calls
`expect_name()`, which cannot accept a dotted base, so `self.xs[0..1]` does not parse. The
single-index spelling was therefore the ONLY way to say "this method writes into `self.xs[i]`"
— and it was the unsound one. A user following the language's own surface into the only
available spelling landed on the hole.

## THE FIRST PROBE WAS VACUOUS AND IS LOGGED AS VACUOUS

The first attempt put the exploit in a free function `d()` constructing a `Box` and calling
`b.poke()`. It FAILED at baseline, which LOOKED like confirmation that the route was closed.
Reading WHICH goal failed: an `ensures` on `__init__` emits an unbound `self` at the
`let box__init () : box` binding (Why3 type error, line 15), and `b.poke()` had lowered to an
abstract op `val b_poke_0 () : unit` with no receiver at all. **The positive control never
fired, so that probe measured NOTHING** — logged `VACUOUS`, never folded into `FAIL-CLOSED`.
Re-run with the contract on a sibling METHOD, it proved immediately.

## THE REPAIR

Peel the `Subscript` layers off the target in `_build_method_writes_map`, then apply the
EXACT same `self.<field>` predicate as before. Over-approximating `self.xs[i]` to the whole of
`self.xs` is SOUND — more havoc is strictly LESS caller knowledge — and it is what Why3 itself
infers from a `let` whose body writes one cell, which is why the real-body control already
refused this exploit.

**CAPABILITY PRESERVED AND SPECIFICALLY TESTED** (witness 1293): a caller that HONESTLY
declares its own frame still proves facts about the fields the stub does not touch. What no
longer holds — correctly — is a caller promising to write nothing while calling a stub that
writes; that fails identically for the whole-field spelling. The subscript spelling now
behaves EXACTLY like the field spelling, which is the whole repair.

## REOPENING / CLOSING CONDITION

CLOSED: witness `1292_route104_self_field_subscript_assigns_dropped_the_method_frame.py`
PROVED at 5795cfef and FAILS at HEAD. REOPENS if `_build_method_writes_map` is re-keyed on a
node type, or if a new consumer of `contracts.assigns` is written that matches on
`a.get("type")` without peeling the write path first.
