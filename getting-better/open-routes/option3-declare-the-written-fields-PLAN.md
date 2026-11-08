# OPTION 3 — DECLARE THE WRITTEN FIELDS ON THEIR CLASSES

**STATUS: LANDED by gen #34 (commit `016a93d2`), gated in battery #1.** This file is now the RECORD
of what the change actually is, because gen #33's plan (preserved in the history of this file) was
wrong in three measurable ways and each one matters to whoever touches the frame planes next.

## WHAT LANDED

    check-assigns-underdeclaration     TRAP  18 -> 5    HOLE   0   (ceiling lowered 18 -> 5)
    check-assigns-underdeclaration -t  TRAP-T 148 -> 116 HOLE-T 0
    check-assigns-writes-survival      TRAP  2989 (unchanged, NOT raised)  HOLE 0

Thirty-two `#@ assigns` clause repairs (13 direct + 19 transitive) and **seven** class-level /
`__init__` field declarations. Mirror movers: **four** — `Module6_WhyMLTranspiler`,
`frontend__Module5_IREmitter`, `module6_whyml__statements`, `module6_whyml__types`. Corpus and
python-reference emissions **byte-inert in all three directions** (1381/1381 and 2199/2199, 0 MOVED).

## THE THREE THINGS THE ORIGINAL PLAN GOT WRONG

### 1. THE CLAUSE AND THE DECLARATION ARE TWO DIFFERENT REPAIRS

The plan paired them one-for-one, and that pairing is what made gen #33's patch raise
`check-assigns-writes-survival` 2989 -> 3000.

  * **The CLAUSE is what `check-assigns-underdeclaration` measures**, and — measured, see below — it
    is also what every CALLER consumes as a frame assumption. Repairing it is a soundness repair.
  * **The DECLARATION is what `check-assigns-writes-survival` needs**, and it is worth making ONLY
    where it actually reaches the emitted RECORD. Where it does not, it is emission-inert AND it
    switches ON the HOLE / HOLE-T arms for that field — pure liability for zero frame honesty.

Measured, per class:

| class | does a class-level declaration reach the record? |
|---|---|
| `TypeInferenceMixin` (types.py) | **YES** |
| `StatementEmissionMixin` (statements.py) | **YES** |
| `FunctionEmissionMixin` (functions.py) | **NO** — it emits `type functionemissionmixin` with no fields at all |
| `PyCSLWeaver` (Module3_Weaver.py) | **NO** — its record is built from `__init__` |
| `PyCSLToJSONEmitter` (Module5_IREmitter.py) | **NO at class level** — see 2 |

So the six `FunctionEmissionMixin` fields and the two `PyCSLWeaver` fields got **the clause and no
declaration**. Gen #33's patch declared all fourteen.

### 2. A CLASS-LEVEL ANNOTATION ON `PyCSLToJSONEmitter` IS COLLECTED FOR A `@dataclass` AND FOR NOTHING ELSE

`Module5_IREmitter.py::_collect_class_fields` builds that class's record from the
`self.<f>: T = ...` AnnAssigns of `__init__` only; the class-body path (`:3494`) is gated
`if not fields and self._is_dataclass_decorated(node)`. The class-level spelling was therefore
SILENTLY INERT and left survival at **2990** — one row, `_collect_class_fields` + `_m5_dc_unknown`.
The declaration was moved into the `\trusted` `__init__` stub, which is the idiom that file's own
comment already documents (*"scanned by Module5 `_collect_class_fields` (a static AST walk) for the
field TYPE only"*), the `writes` clause gained the field, and TRAP came back to 2989.

### 3. `_emitted_record_field_types` IS `Dict[str, Dict[str, str]]`, NOT `Dict[str, str]`

`preamble.py:9123` maps `type_name -> {label -> whyml type}`. The plan's type — and the half-landed
patch's — was the inner map's. That makes it a **fifth** deferred field, not one of the clear
fourteen: a guessed container type is the fabricated-witness shape the campaign already has a lesson
about. (Nested dicts DO model: `_known_collection_elements: Dict[str, Dict[int, str]]` emits
`map string (option (map int (option string)))` and `why3 --type-only` accepts it. So the objection
is to GUESSING the type, not to the shape.)

## THE THING NOBODY HAD MEASURED: THE TWO RATCHETS ARE A CHAIN OF THREE

Lesson (f5) said two planes bracket the frame from opposite sides. There is a THIRD side, and it is
ratcheted:

    declared-but-not-EMITTED   <-- class declaration -->   written-but-not-DECLARED (DIRECT)
      (survival, TRAP 2989)                                  (underdeclaration, TRAP)
                                                                     ^
                                                                  clause
                                                                     v
                                              written-THROUGH-A-CALLEE (HOLE-T, ceiling 0)

Declaring a field makes every OTHER clause that omits it a **HOLE-T**, and `HOLE-T`'s ceiling is 0.
Measured BEFORE touching a line: **32** of the 148 TRAP-T rows carry one of the 13 fields and only 13
are direct, so **19 would have fired**. They are now declared too — `_emit_function`,
`_emit_subtyping_goals`, `_render_refinement_goal` (the six fields `_reset_function_state` writes) and
`visit_ClassDef` (`_m5_dc_unknown`).

>>> **A FRAME INVARIANT BRACKETED FROM N SIDES NEEDS THE STATE THAT SATISFIES ALL N, AND N WAS NOT 2.**

## THE POPULATION HOLE IN `check-assigns-writes-survival`, MEASURED

One rise during the build was not a regression: declaring `_rebound_collections` gave
`_track_collection_metadata` its FIRST `writes` clause, which ADMITTED it to the plane's population —
and with it the three other fields its clause declares and the record still dropped (+6, two files).
The plane does `w = re.search(r"writes\s*\{...\}", seg); if not w: continue`, so:

>>> **A CLAUSE THAT IS 100% DROPPED EMITS NO `writes` AND IS INVISIBLE. THE WORST CASE IS THE ONE THE
>>> PLANE CANNOT SEE — AND ITS TRAP IS THEREFORE NOT MONOTONE UNDER AN HONEST REPAIR.**

Paid for honestly by declaring all four of that method's fields (types read off the live
initialisers). The size of the blind spot, measured at HEAD by widening the population to every
emitted symbol with a non-empty clause: **1515 symbols, 1060 of which emit NO `writes` clause,
TRAP 5427, HOLE 327** — against the shipped plane's 455 symbols / TRAP 2989 / HOLE 0.

**The 327 are FAIL-CLOSED, and that took two probes to establish** (`probes.tsv`, gen #34): a
bodyless `val` with no `writes` is a DEAD DECLARATION — every call to a `\trusted` method, intra-class
`self.m()` and cross-object `c.m()` alike, is lowered to an ABSTRACT OP and never to that `val`. So
widening the population would report a large number about declarations nothing consumes. **Widening
it anyway is still worth doing as an AUDIT measure, but it must not be confused with the soundness
arm, and it cannot reuse `MAX_TRAP`.**

## AND THE FINDING THAT CHANGES WHAT THIS ITEM WAS FOR

The abstract op that replaces the call is built FROM THE CLAUSE:

    #@ assigns self.x    ->  val c_bump_0 (self: c) : unit  writes { self.x }   caller's `\result == 0`  **Unknown**
    #@ assigns \nothing  ->  val c_bump_0 () : unit                             the same `\result == 0`  **Valid, 104 steps**

>>> **A `\trusted` STUB'S DECLARED FRAME IS EXACTLY THE CALLER-SIDE ASSUMPTION, VERBATIM.** An
>>> under-declared clause is a false assumption consumed by every caller, so the eighteen clauses were
>>> SOUNDNESS debt, not audit debt — and TRAP-T is the identical defect one call deeper.

## WHAT IS LEFT, FOR THE NEXT GENERATION

1. **TRAP-T 116 across 66 methods** — the same defect one call deeper. 55 trusted / 61 converted.
   Mechanical, and measured survival-free for the 19 already done. **This is the top frame item.**
2. **The five judgement fields**, each needing a decision and not a type: `expressions.py::ir` (a
   container mutation of the whole IR mapping — decide first whether it is a record field at all),
   `_r188_stub_names` (initialised from another map), `_r55_subsumed_name` (an `Optional`, route #227
   territory), `preamble.py::_formal_params` (`= list(params)`), and
   `preamble.py::_emitted_record_field_types` (the nested dict above).
3. **The survival SHRINK seam is real and ranked**: 629 of the 2989 dropped occurrences are fields
   whose LIVE initialiser carries an unambiguous simple annotation (`Set[str]`, `Dict[str,str]`,
   `Dict[str,int]`, `List[str]`, `int`, `str`, `bool`) that agrees across every site. Biggest:
   `ExpressionEmissionMixin.frame_trigger_active` (88), `.abstract_ops` (49), `.dict_locals` (44),
   `StatementEmissionMixin.current_params` / `.frame_trigger_active` / `.func_return_type` (44 each).
   Each declaration widens a record, so price it with `bin/mirror-emit-sweep.sh` FIRST — **it is 53
   files in 52 SECONDS, which makes it the cheapest instrument in the campaign** and the right way to
   iterate this whole family.
4. **Widen the survival plane's population** as a SECOND, separately-ratcheted arm (do NOT move
   `MAX_TRAP`), so a 100%-dropped clause stops being invisible.
