# OPEN ROUTES — exploited, reproduced, NOT closed

## run #3 (2026-10-31): #491-#495 REPAIRED (executor v1 off 0a6f9c153; one rewrite of route #489's judge, inline in `_run_pipeline`,
##   mirror twin `\trusted`, no new def, no axiom; annotations §7.400). Refuse by default: (a) every implicit position on a record of
##   a KNOWN class is EVERY dunder of its classes (unknown class: the position table, completed) (#491: `[1] * o`, `round(x, o)`, `isinstance(1, o)`, `iter(o, s)` need no table entry);
##   (b) the dunder set is the class NAMESPACE, aliases / chains / nested-block defs included (#492); (c) a bodyless val is
##   judged when its name / method name is read or its class is called, incl. `\trusted` / `\abstract` / imported `__init__` (no IR function) (#493); (d) a program / method /
##   builtin call, operator or rich comparison that may return the record continues the walk (#494); (e) purity is the woven
##   `assigns` and `\nothing` beside another clause is refused PYCSL-CONTRADICTORY-ASSIGNS for every function (#495).
##   113 witnesses (+ #495 x typed / store = 139 runs) REFUSED; corpus 7800-7817 / controls 7820-7826; over-refusal 0
##   (corpus / pyref / mirror byte-inert vs v19; rt41 17 + rt42 16 PASS controls and 7750-7754 not refused by the judge).
##   Residual by design: any non-pure dunder of a known record class refuses every implicit position of it in a bodyless
##   callee; named: unknown-class values use the completed table; dunder vals are reached via positions / name reads.

## run #3 (2026-10-31): #491-#495 OPENED (red team 42 on 77a3818d0: 818 probes + 715 mode re-proofs / 139 confirmed;
##   rt41's 237 all closed; #490 complements and new object-model surfaces held): #491 r489-dunder-position-table (23); #492 r489-dunder-alias-binding (21); #493 r489-bodyless-dunder-name-key (27); #494 r489-record-through-returning-call (29); #495 r489-contradictory-frame-text (13).
##   Diagnosis: all five are gaps of route #489's implicit-dunder judge (position table, alias-bound dunders, bodyless-name key,
##   record through a returning call, purity read from comment text).

## run #3 (2026-10-30): #489 REPAIRED (executor u1 off 394a1654a; inline in `_run_pipeline` after route #482's rule, mirror twin
##   `\trusted`, no new def, no axiom; new code PYCSL-R489-IMPLICIT-DUNDER; annotations §7.380). An implicit dunder position
##   (`len(o)`, truth test, `==` / order with reflection, `in`, BinOp / AugAssign, `str` / f-string / `%`, index, `o[0]`,
##   attribute fallback, iteration, `next`, `with`, container elements) of a non-scalar root in a bodyless `val` with no
##   `#@ assigns` (`\trusted` / `\abstract` / imported marked AND un-marked) is a CALL of the program dunder: admitted only when
##   the dunders reached on the value are `#@ assigns \nothing` (and, as an argument, verified self-only), else REFUSED.
##   100 witnesses x 3 models = 300 runs REFUSED; corpus 7730-7744 / controls 7750-7754; over-refusal 0 (corpus, pyref,
##   mirror byte-inert; rt41's 142 dunder probes: 98 refused, all CPython violations, d13006 / d13007 controls kept).
##   Verified callers probed: fail closed (Why3 typing). Residuals: class-attribute / metaclass dunders, auto-trusted bodies.

## run #3 (2026-10-30): #490 REPAIRED (executor u2 off 394a1654a; inline in `_run_pipeline` after route #486, mirror twin
##   `\trusted`, no new def, no axiom, emitter untouched; new code PYCSL-R490-LITERAL-INT-HASH; annotations.md 7.390). A
##   literal-kind judgement (number / str / None / tuple / containers, joined over ternary arms, and/or, local bindings and
##   container elements) refuses a value that may be a number AND a non-number at every arithmetic / ordering / augmented /
##   unary use, and a number-or-hashed-str/tuple at every other observation; numeric slot check for annotated bindings,
##   parameters (incl. omitted defaults), returns; a number-annotated function returning None is number-or-None at its
##   callers. 53/53 witnesses REFUSED; corpus 7770-7787 (FAIL) / 7790-7797 (PASS); siblings 7784 (truth test of a hashed '')
##   and 7787 (None from `-> int`) closed. Residuals named in route490-*.md (str-and-None join: Why3 type error; a mixed dict
##   passed whole).

## run #3 (2026-10-30): #489-#490 OPENED (red team 41 on 973a2755d: 634 probes + 556 re-runs + 2533 mode re-proofs / 237 confirmed;
##   rt40's 129 all closed): #489 implicit-dunder-callee-frame (100); #490 literal-int-hash-value-slot (53).
##   Diagnosis: implicit dunder calls are not calls for the callee frame (F1), and the int-hash coercion of str / None literals
##   in int value slots (F2).

## run #3 (2026-10-30): #483 / #484 REPAIRED (executor y2 off e3b3711a2; one rule, inline in `_run_pipeline` after route #466,
##   mirror twin `\trusted`, no new def, no axiom; new code PYCSL-R483-IMPORT-TIME-NAMESPACE-WRITER). Every module of the
##   import closure but the claimed one must run, AT IMPORT TIME (top level, decorators, defaults, class bodies, closed by name
##   through called functions / live classes' dunders and named methods / base hooks / metaclasses), only an allow-listed
##   fragment: allow-listed imports (never `__main__` / the claimed file), no exec / eval / compile / globals / vars / setattr /
##   getattr-of-a-computed-name / `__builtins__` / dunder or frame attributes / `.modules`, an imported module only as an
##   attribute-read receiver, no attribute store to a name bound at a module top level or in a class body (a write-only
##   `F(globals())` sink admitted: named residual for a computed key); else REFUSED.
##   Witnesses 22/22 (34 probe-mode pairs) REFUSED; corpus 7670-7678 (FAIL), controls 7680-7682. Over-refusal: 0 honest
##   corpus / pyref / mirror / red-team-control files (#474's NOT PROVED 7570-7572 move to REFUSED); route #466's run
##   claim-free (the alternative) refuses 14 mirror (pure_ast's `_build_nodes(globals())`) + 3 corpus files.
##   annotations 7.370. Gates (16d9d9d30): fidelity 0/0; byte-diff root 2677/2677 0 MOVED, 3 declared GONE (7570-7572,
##   NOT PROVED -> REFUSED), pyref 2186/2186 0/0/0; mirror 53/53 0/0/0; planes 61/61; ledgers green except
##   stdlib-modules-verify (json/__main__ refused: fixed in f3406e052, re-gated there); \trusted 436 unchanged.

## run #3 (2026-10-30): #482 REPAIRED (executor y1 off e3b3711a2; inline in `_run_pipeline`, mirror twin `\trusted`, no
##   Module 6 / mirror edit, no axiom). A bodyless `val` with no `#@ assigns` (explicit `\trusted` / `\abstract`) gets its
##   frame INFERRED; its body must keep every mutable root (non-scalar parameter, `self`) on the inference's allow-list
##   (access chain into a scalar position, `=` / `for` / unpack / walrus, store target cross-checked against the IR frame,
##   mutator / read-only / program-method receiver); `self` and dict / set parameters are read-only -- else
##   PYCSL-R482-TRUSTED-FRAME-UNTRACKED ("declare `#@ assigns`"). 34 list-parameter witnesses were already refused by
##   #468/#481 at base, the 16 others now are; new: a DIRECT `self` write in a `\trusted` method (7631). Over-refusal 0
##   (corpus, red-team controls, mirror). Residual #482-R1: AUTO-trusted / un-marked imported defs not judged. Plus D3 parity for #481's length rule (same SSA split as route #316: 7448 PASSES again).
##   Corpus 7630-7639 / 7653 (FAIL), controls 7650-7652 / 7654 / 7655. annotations 7.360.

## run #3 (2026-10-30): #485 / #486 / #487 REPAIRED (executor y3 off 0c61bfc3f; inline in `_run_pipeline` + `_handle_binop` /
##   `_to_bool`, all mirror twins `\trusted`, no new def / lambda in a mirrored file, no axiom). #485: a name LOADED but bound
##   nowhere in the file (implicit module globals `__file__` / `__cached__` / `__builtins__` ..., class implicit names) is an R325
##   origin; only `__debug__` stays a known int (10/10 REFUSED). #486: every augmented assignment of a verified function is
##   judged on its TARGET's static type (params, local-binding fixpoint, element / slot / field / return types): typed / store
##   admit only scalar targets, hoare-family models refuse what CPython rejects on the known type and leave the rest to Why3
##   typing (PYCSL-R486-NONSCALAR-AUGASSIGN-TARGET; 28/28 typed+store REFUSED, default 10 REFUSED + 4 Why3 type errors). #487:
##   an `and` / `or` over a non-bool / non-int operand is lowered inside a truth-only marker that every truth test strips; a
##   value use is refused (PYCSL-M6-BOOLOP-VALUE; 7/7 REFUSED). Corpus 7590-7596, 7600-7616, 7620-7629; annotations.md
##   7.350-7.352. Over-refusal 0: root 0 MOVED / 0 GONE (1 APPEARED: 1723, load-dependent, identical at base), pyref
##   2186/2186 and mirror 53/53 byte-inert; rt40 PASS controls 5/5 kept.

## run #3 (2026-10-30): #481 REPAIRED + #474 RESIDUAL closed (executor f2 off 8855b6b10; inline in `_run_pipeline`, mirror twin
##   `\trusted`, no new def, no axiom). #481: route #468's bodyless-`val` length allow-list now judges an EXPLICIT `\trusted` def
##   too (inferred or declared frame alike; one rule for imported / `\trusted` / `\abstract` / methods; verified callees stay
##   route #49's) -- PYCSL-R468-VAL-LIST-LENGTH; boundary-kind table in route481; corpus 7560-7564 (FAIL), controls 7565-7567.
##   #474 residual: a dependency constant stays folded only if NO module of the program's import closure (package `__init__`s
##   included) stores / deletes an attribute of its name or holds a namespace writer; else the fold is dropped (opaque, no
##   refusal); composes with x3's per-dependency guard. Corpus 7570-7572 (FAIL), controls 7573 / 7574. annotations 7.340 / 7.341.
##   Byte-diff root / pyref / mirror 0 MOVED / 0 GONE.

## run #3 (2026-10-30): #488 OPENED (dx1, Gate S of the cross-mixin-declaration-stubs wall; runtime-witnessed): ghost-handler-false-frames:
##   30 verified mirror ghost handlers prove `assigns \nothing` only because the trusted `_e` declarations they call understate
##   their definitions' frames; the live `_handle_has_key_expr` writes `self._abstract_ops`. Severity 2 (no consuming proof known).

## run #3 (2026-10-30): #482-#487 OPENED (red team 40 on dcf424f75: 624 probes + 1009 mode re-proofs / 129 confirmed;
##   rt39's 141 all closed): #482 trusted-callee-alias-frame (50); #483 dependency-builtins-mapping (12); #484 dependency-writes-main-or-peer (10); #485 implicit-module-globals-as-ints (10); #486 typed-store-subscript-augassign (14); #487 boolop-collection-truth-value (7).
##   Diagnosis: inferred frames of trusted callees (F1, with #481), dependency writes under ensures-only claims (F2 F3, #474's
##   residual class), and residues of #480 (F4), #478 (F5) and truth-value lowering of `or` / `and` (F6).

## run #3 (2026-10-30): #475 / #477 REPAIRED, #474 PARTIAL (executor x3 off 8aaa864ca; the FILE-BOUNDARY dependency reader:
##   every fact taken from a dependency comes from CPython's own reading of it; inline, mirror twins `\trusted`, no new def
##   in a mirrored file, no axiom). #475: route #465's decode gate at `_resolve_module_path` (the one place every frontend
##   reader gets a dependency path): bytes decoded by `tokenize.detect_encoding` must equal the UTF-8 text read, else
##   REFUSED (new code PYCSL-R475-DEPENDENCY-ENCODING). #474: a dependency constant folds into the importer only when
##   CPython's `ast.parse` of the dependency binds it at exactly ONE site of any form anywhere and the file has no
##   namespace writer, else opaque (no new refusal). #477: a from-import (any name, `*`) of a program module holding
##   `__getattr__`, and a claimed read `h.g` of a name it does not bind, are REFUSED inside route #466's run.
##   Witnesses 38/38 PROVED at base -> 34 REFUSED + 4 NOT PROVED; corpus 7450-7455, 7460-7462, 7470-7473 (FAIL),
##   controls 7457 7458 7463 7464 7474. #474 RESIDUAL: a constant mutated from ANOTHER program module (`h.K = 0` in a
##   peer, a package `__init__` writing `sub.K`) under an ensures-only claim still folds (PROVED at base and repair).

## run #3 (2026-10-30): #479 / #480 REPAIRED (executor o1 off 8aaa864ca; `_expr_to_whyml` + inline in `_run_pipeline`,
##   both mirror twins `\trusted`, no new def in a mirrored file, no axiom, no new diagnostic code). #479: route #40's
##   `py_ellipsis` marker is read on the `OpaqueExpr` carrier `expr_from_dict` makes of it inside a typed parent (ternary
##   test / `not` / `or` operand / arm), which the generic dispatch re-read as `NumberExpr(0)`: `...` is `pycsl_ellipsis`
##   in every position (7/7 witnesses NOT-PROVED). #480: a builtin name the file does not bind, `NotImplemented` and `...`
##   are R325 ORIGINS (only `__debug__` known int); an uncalled non-data attribute of an int value is an origin; bitwise /
##   shift / pow model ops are int uses; NotImplemented's truth value is refused; builtin-object identity stays reflexive;
##   #445 judges a chain rooted at a builtin name on the real object (58/58 witnesses REFUSED). Corpus 7490-7510
##   (FAIL), controls 7515-7522. Over-refusal: root 0 MOVED / 1 GONE (1039, an expected-FAIL route #40 witness, now
##   refused), pyref 2186/2186 and mirror 53/53 byte-inert; the stronger "every 0-ary fallback" polarity was measured
##   and dropped (it refused honest 0534 / 0546: emitter-internal pattern names).

## run #3 (2026-10-30): #476 / #478 REPAIRED (executor m2 off 8aaa864ca; inline in `_run_pipeline`, mirror twin `\trusted`, no
##   new def in a mirrored file, no axiom). #478: an augmented assignment on a formal parameter of a verified function is admitted
##   only when the DECLARED type is an immutable scalar (int / float / bool / complex / str / bytes / tuple / unannotated) -- judged
##   on the IR once for EVERY memory model (PYCSL-R478-COLLECTION-PARAM-AUGASSIGN); 15 witnesses x 3 models REFUSED (45/45).
##   #476: a module name a verified function reads (transitively through every def / class of the name), or its own name, bound
##   both before the call frontier and at / after it, is REFUSED (PYCSL-R476-REBOUND-AFTER-FRONTIER); 8/8 REFUSED. Over-refusal:
##   0 corpus / mirror / stdlib files by census; rt39 honest probe x2010 (typed / store) now refused. Model-gated refusal census:
##   of 2014 refusal witnesses 12 emit under typed / store only; 11 do not prove there, `0849` proves (route #289's gate keys on
##   the `subscript_set` emission; typed / store lower `a[i][k] = v` on `List[Dict]` to an effectful heap store) -- RESIDUAL: no
##   false proof found by 5 breach probes (len / frame / KeyError / read-back / neighbour), dict-as-heap-array left unrefused.
##   Witnesses 7530-7537, 7540-7545; controls 7538 7539 7546 7547 7548. annotations.md 7.330 / 7.331.

## run #3 (2026-10-30): #481 OPENED (executor d1's residual, driver-reproduced on d6abee90b): trusted-default-frame-list-length (1 +
##   control): a same-file `\trusted` function without `assigns` that appends to a list argument gets the inferred `writes { xs }`,
##   which keeps `Array.length xs`; the caller proves `\result == \old(len(xs))` while CPython returns 1 (route #49 / #468 class).

## run #3 (2026-10-29): #474-#480 OPENED (red team 39 on d6abee90b: 918 probes + 1064 mode re-proofs / 141 confirmed;
##   rt38's 142 counted all closed): #474 imported-constant-flow-insensitive (25); #475 dependency-encoding-cookie (10); #476 script-order-redefinition (8); #477 module-getattr-import (3); #478 typed-store-list-augassign (15); #479 ellipsis-ternary-test (7); #480 builtin-objects-as-ints (58).
##   Diagnosis: dependency analysis by a second, weaker reader (F1 F2 F4: constants, encoding, __getattr__), script-order
##   binding (F3), non-default memory models skipping a default-model refusal (F5), and opaque-int residues (F6 F7).

## run #3 (2026-10-29): #473 REPAIRED (executor e473 off 1f3aa3081; inline in `_run_pipeline`, mirror twin `\trusted`, no
##   new def in a mirrored file, no axiom, NO refusal): an empty list literal is the genuinely EMPTY `(Array.make 0 0)`
##   wherever the IR attributes the `(Array.make 1024 0)` text to it (a function with no real-1024-list producer: every
##   placeholder; otherwise each let / ref of a local only ever assigned `[]`, plus the rest when every producer is a
##   named real-list local). Census `systematic-soundness-r3/e473/placeholder-census.tsv` (54 probes, 11 PROVED at base:
##   call argument / alias / method / keyword / branch / bound result / mixed function / callee length / `list([])`);
##   corpus 7380-7389, 7396 (PROVED at base, FAIL now), controls 7391-7395; root 10 MOVED (exactly `1024` -> `0` in the
##   placeholder-route witnesses 1015 1016 1536 1538 1541 1588 1590 1595 1869 1870), pyref 0, mirror 0 (no OWED proof).

## run #3 (2026-10-29): #473 OPENED (found by executor lv5, driver-reproduced on a9eac4a08): a LOCAL empty list passed to a
##   callee is the 1024-element placeholder `Array.make 1024 0`, discharging the callee's `len(c) >= 1` (2 witnesses).

## run #3 (2026-10-29): #466 / #467 / #468 / #472 REPAIRED (executor x1 off daf5c3d1f; the FILE BOUNDARY of red team 38;
##   inline at the end of `_run_pipeline` after #461 / #462, mirror twin `\trusted`, no new def in a mirrored file, no
##   axiom, no emission change). #466 / #472: under any claim, imports are resolved on the TARGET's path (file dir,
##   `--import-path`, sys.path minus src/pycsl and src/; PYCSL-R472-IMPORT-NOT-ON-TARGET-PATH) and every PROGRAM module
##   (file dir / `--import-path`) is IMPORTED here in CPython's order with partial-module semantics -- compile(), top level
##   and class bodies run on real values (CPython `eval` behind a call allow-list, placeholders for defs, `types.new_class`
##   + real decorators), `from M import n` needs n bound at that moment (PYCSL-R466-IMPORTED-MODULE-RAISES). #467: a
##   reached function of a program module must claim `no_exception` covering the caller's claim, or be on an int-arithmetic
##   allow-list (PYCSL-R467-IMPORTED-UNCLAIMED). #468: a bodyless `val`'s list / bytearray parameter must be length-
##   preserved by its SOURCE body (PYCSL-R468-VAL-LIST-LENGTH). Corpus 7260-7289 minus 7266 (24 witnesses PROVED at base -> REFUSED;
##   5 controls PROVED at base and candidate); red-team witnesses 80/81 PROVED at base -> 81/81 refused (m260 by #161);
##   census +24 rows; 7 import-raising helpers named in check-corpus-executes' KNOWN_LOAD_FAILURES; advice audits R466 (2) / R467 / R468 FOLLOWABLE; docs annotations 7.280-7.282 / translational
##   T.6.290-T.6.292; REPAIR sections. Gates: fidelity rc=0; root 2604 -> 2609
##   0/0/0, pyref 2186 0/0/0, mirror 53 0/0/0; planes 61/61; ledgers rc=0; trusted 437. Over-refusal cost: 0 PASS
##   (corpus 6642 kept by the #467 allow-list; #468 narrowed after a wide cut refused 3382 + 11 mirror files).

## run #3 (2026-10-29): #465 / #469 / #470 / #471 REPAIRED (executor x2 off daf5c3d1f; inline in `_run_pipeline`: a new
##   compile gate just before m1's #461 block, the rest inside it; mirror twin `\trusted`, no new def, no axiom, no emission
##   change). #465: the claimed file's bytes are decoded by CPython's `tokenize.detect_encoding` (must equal the verified
##   text) and compiled by CPython's own `compile(...)`; any SyntaxError is REFUSED for every file (PYCSL-R465-COMPILE-ERROR).
##   #469: `__name__` / `__package__` / `__spec__` / `__loader__`, a class's `__module__` and strings exposing the private
##   module name are UNKNOWN to #461's run, except the canonical `if __name__ == "__main__":` (not judged). #470: reads of
##   `__annotations__` / `__annotate__`, of a placeholder def's unsynthesized dunders, and of a synthesized class's
##   `__doc__` / `__dict__` / ... are REFUSED. #471: every function-body class statement is a JOB created by
##   `types.new_class` on the final module bindings, function-local / `global`-ed / mutable values unknown, one narrow row
##   for an earlier class of the same def (PYCSL-R471-LOCAL-CLASS-RAISES). Corpus 7330-7368 + 7373 (40 witnesses, PROVED at base,
##   REFUSED; all 61 red-team files REFUSED), controls 7369-7372 PROVED at base and candidate; census +40 rows; advice
##   audit R465 FOLLOWABLE; docs annotations 7.290-7.293 / translational T.6.300-T.6.303. Over-refusal cost: 0 corpus PASS
##   (5590 kept by the narrow row), byte-diff root 2604 -> 2608 0/0/0, pyref 2186 0/0/0, mirror 53 / 53 0/0/0 (no OWED proof). Gates: see the
##   route REPAIR sections.

## run #3 (2026-10-29): #465-#472 OPENED (red team 38 on a9eac4a08: 688 probes / 155 proved / 142 confirmed; rt37's 83
##   all closed except #463 / #464): #465 compile-time-syntax-error (20); #466 imported-module-import-raises (18); #467 imported-callee-exceptions (17); #468 imported-callee-list-length (34); #469 module-dunders-script-view (16); #470 standin-lazy-annotations (7); #471 class-in-function-creation (18); #472 import-resolved-on-verifier-path (12).
##   Diagnosis: the FILE BOUNDARY (imported user modules not judged like local code: F2 F3 F4 F8) and #461's evaluation
##   boundary (F5 F6 F7), plus compile-time SyntaxErrors (F1).

## run #3 (2026-10-29): #463 / #464 REPAIRED (executor cc1 off a9eac4a08; inline in `Module1_Ingestor.process` /
##   `Module3_Weaver.process` / `_run_pipeline`, all mirror twins `\trusted`, no new def in a mirrored file, no axiom).
##   #463 CLAIM CONSERVATION: every own-line `#@` comment must land in an emitted slot -- an orphan footer (an indented
##   block above a less-indented statement: the F6 shape), an unconsumed module header, a dropped end-of-file line are
##   REFUSED; a `#@` after code and a near-miss spelling (`# @ensures`, `#\t@`, `##@`) are REFUSED; a module / class
##   name bound twice whose EARLIER binding is a claimed def / class is REFUSED (property / overload chains exempt);
##   a statement-level directive outside every function body (module level, class body, `__main__`) is REFUSED.
##   The mirror's own dead duplicate `def _contract_referenced_var_names` (frontend/ir_resolve, live + mirror) deleted.
##   #464 PRIVATE NAME MANGLING: `__x` inside class C is rewritten `_C__x` in the woven tree, in `_t341` and in the
##   claims, so the field / method / class-attribute tables and #445's admission see CPython's names. Corpus 7180-7207
##   (19 witnesses refused / FAIL, 7 controls PROVED); census +19 rows, 7 re-measured (5440 + six #374 slot witnesses);
##   advice audits R463 x6 FOLLOWABLE; docs annotations 7.240 / 7.241, translational T.6.250 / T.6.251. Byte-diff:
##   root 2604 -> 2613 2 MOVED (5091, 5465) / 0 GONE / 1 APPEARED (5440, expected FAIL, now FAILS on the claim),
##   pyref 2186 1 MOVED (0133) / 0 / 0, mirror 53 0 / 0 / 0. Over-refusal cost: 0 corpus / pyref / mirror files (the
##   one mirror hit, ir_resolve's dead duplicate def, was repaired in source). Gates: see route463 / route464 REPAIR.

## run #3 (2026-10-29): #463 / #464 OPENED (red team 37 families F5 / F6 / F8, still proving on the landed 33f7ac681 --
##   rt37's other 75 confirmed are refused / not proved there): #463 a written `#@` claim silently dropped (redefined def;
##   indented claim block) -- 'All contracts formally proven' for a file whose only claim is false (6); #464 private name
##   mangling ignored (2).

## run #3 (2026-10-29): #461 / #462 REPAIRED (executor m1 off b1611d192; inline at the end of `_run_pipeline`, mirror twin
##   `\trusted`, no new def in a mirrored file, no axiom, no emission change). #461: under any `no_exception` claim, the
##   module top level and every class body are RUN on a synthesized equivalent -- real values, only side-effect-free
##   stdlib calls, file code as placeholders (refused when CPython's machinery would call it), classes created by
##   `types.new_class` + their real decorators + `_mro363` -- and anything outside the allow-list is REFUSED
##   (PYCSL-R461-IMPORT-RAISES, CPython's own exception text). #462: an `__init__` returning a value / yielding / async
##   is REFUSED (PYCSL-R462-INIT-RETURNS-VALUE). Corpus 7130-7152 (21 witnesses: PROVED at base, REFUSED; controls 7151,
##   7152 PROVED at base and candidate); census +21 rows; advice audits R461 / R462 FOLLOWABLE; docs annotations 7.230 /
##   translational T.6.240. Over-refusal cost: 0 PASS (static screen of 1193 claimed corpus files; two narrow file-code
##   rows added after the first cut refused 1297 / 6330); byte-diff root 2592 -> 2594 0/0/0, pyref 2186 0/0/0, mirror 53
##   0/0/0. Gates: see route461 REPAIR.

## run #3 (2026-10-29): #461 / #462 OPENED (red team 37 on 370db7dc2, driver-salvaged: 641 census rows / 27 proved / 22
##   confirmed; rt36's 209 ALL closed): #461 a verified file whose IMPORT raises (20: class-creation errors, raising module
##   statements; Severity 2, arguable); #462 `__init__` returning a value (1). k002 (property getter KeyError) joins #460.

## run #3 (2026-10-29): #460 REPAIRED (executor c460 off 370db7dc2; census of 31 claim-gated sites
##   `getting-better/systematic-soundness-r3/c460/claim-gated-census.tsv`: 3 reached at base -> 20 now; corpus 7050-7056
##   (4 witnesses PROVED at base -> 2 REFUSED / 2 FAIL; 3 controls PROVED both), census +4 rows, docs annotations 7.210 /
##   translational T.6.220, REPAIR section). ONE reached-claim set (r1's `_rc444` closure): `_run_pipeline` hands Module 6
##   `reach_r460` (what callers' claims add to a def's own); `_reset_function_state` joins it into the BODY context (every
##   trigger assert, the #64 / #65 / #71 refusal walks: #66 / #72 / #160 / #161 / #173 / #207 / #178's walk); #434's site
##   census, #451, #459 count it; the SPEC (raises, #304 / #171 wrappers, call-site claims, #178's `_decl178`) keeps the
##   declared claim. Two #161 rows (`super()` in a plain method; `super().__str__/__repr__()` of a builtin-exception
##   subclass). Cost: corpus 0 GONE, 2 MOVED (0382 / 0383: a reached `256 // n` owes `no_div_zero`, M1 PROVED base and
##   candidate), pyref 0, mirror 0. Increment 2: the front-end #432-family claim `_cx432` reaches too (constructors keep
##   their own; a `super()` receiver under a reached-only claim is #450's): whole reach measured 12 corpus files refused,
##   0 after the rows; witnesses 7057 (rt37 k002 property getter) / 7059, controls 7058 / 7060.

## run #3 (2026-10-29): #460 OPENED (measured by executor r1, driver-reproduced on 8fe7204c3 and on the post-#444-#459
##   candidate): a caller's `no_exception` claim does not reach an UN-claimed callee's Module 6 obligations / #161
##   admission (`math.factorial(n)` in an un-claimed g called by a claimed f PROVES; CPython ValueError). Partial reach
##   exists (#178 summaries, `_rc444`, `_xf440`); the structural repair is one reached-claim set read by every claim-gated check.

## run #3 (2026-10-29): #447 / #451 / #452 / #454 / #456 / #459 REPAIRED (executor r3 off db6c57253; the MISSING-OBLIGATION
##   families of red team 36; corpus 7000-7046 (38 witnesses + 9 controls), census +38 rows / 3 re-measured (5066 5071 5072),
##   advice audits R447 / R451 / R452 / R454 / R459, docs annotations 7.200-7.205 / translational T.6.210-T.6.215, REPAIR
##   sections; no new def in a mirrored file, no axiom). #447: an augmented SHIFT on a name is lowered through the BinOp
##   path (its `non_neg_shift` row + #414's bound; emission of augmented shifts only, none outside the new files); `//=`
##   `%=` `/=` on a name REFUSED (were ill-formed WhyML). #451: #350's default-kind check also judges `None` defaults of
##   `@dataclass` / NamedTuple fields and annotated stores `self.f: T = v` (v None / an Optional parameter), for fields read
##   under a claim (NARROWED after the wide rule refused 33 corpus + 8 mirror files). #452: a byte search of a derived
##   `bytes` / `bytearray` admits only bytes-like / bool / an int literal in 0..255. #454: starred / double-starred values
##   must be derived iterables / mappings. #456: set-method arguments are hashed iterables (#349 / #394 rules). #459:
##   module-level definite assignment for names read by claimed functions. All 57 route witnesses PROVED at base 8fe7204c3
##   and now FAIL (13 shifts: obligation Unknown) or are REFUSED (44); 9 controls PROVED at base and candidate.
##   Gates: fidelity rc=0; root 2569 -> 2581 .mlw, 0 MOVED / 3 GONE (5066 5071 5072, expected-FAIL `*self` witnesses of
##   route #375: VERIFY-FAIL -> REFUSED by #454) / 0 APPEARED; pyref 2186 0/0/0; mirror 53/53 0/0/0 (no OWED proof);
##   planes 61/61; rwc 349 demonstrated / advice 176 audited / dropped-mutation / getattr / carriers / frame- / raises-honesty /
##   clause / assumed / trusted-reasons 413 / doc rc=0. Over-refusal cost: 0 PASS files (root, pyref, mirror).

## run #3 (2026-10-29): #448 / #449 / #450 / #455 REPAIRED (executor r2 off db6c57253; CALL BINDING inline in `_run_pipeline`,
##   in EVERY non-trusted function -- an unclaimed callee's TypeError reaches its caller's claim, measured; allow-list, refuse
##   by default; no new def in a mirrored file, no axiom, no emission change; annotations 7.190 / translational T.6.200).
##   #449 PYCSL-R449-CALL-SIGNATURE: calls of module defs bound once, own-scope defs, `C.m`, `self.m` (all file subclasses),
##   `p.m` (file-class-annotated parameters) bind by CPython's algorithm. #450 PYCSL-R450-SUPER-UNRESOLVED: `super().a`
##   resolved through every deriving class's file MRO (real `__mro__` for builtin / stdlib bases), call bound. #448: row
##   cross-constraints `_XC448` (max / min `default=` => 1 positional, ...; audit: only that one slipped) + real
##   `inspect.signature` of builtins (PYCSL-R448-BUILTIN-CROSS-CONSTRAINT). #455 PYCSL-R455-DECORATOR-SITE: property / accessors
##   / cached_property / classmethod only in a class body, no trailing `@overload`, no builtin decorator on a class. All 35
##   route witnesses refused; corpus 6950-6969 (20 witnesses, all PROVED at base; 3 found while repairing: `self.m(n, n)`,
##   `c.m(n, n)`, mismatches in UNCLAIMED callees) + 6980-6984 controls (PROVED base + candidate). Gates: fidelity rc=0; root
##   2569 -> 2574 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186 0/0/0; mirrors 53/53 0/0/0 (no OWED proof); planes 61/61; rwc 348 /
##   advice 175 / all ledgers rc=0. OVER-REFUSAL COST: 0 corpus / pyref / mirror / pycsl_lib files. Residual: class-code
##   mismatches of builtins in unclaimed callees (#441's table is claim-keyed), unresolved receivers, `*` / `**` calls.

## run #3 (2026-10-29): #444 / #445 / #446 / #453 / #457 / #458 REPAIRED (executor r1 off db6c57253; the OPAQUE-FALLBACK
##   families of red team 36, 117 witnesses, by ONE fail-closed rule inline in `_run_pipeline`; census of the Module 6
##   fallback sites `getting-better/systematic-soundness-r3/r1-opaque/census-fallback-sites.tsv` (436 rows, 14 now
##   FAIL-CLOSED); codes PYCSL-R444-UNBOUND-NAME / R445-ATTRIBUTE-NOT-DEFINED / R446-MATMUL-UNMODELLED /
##   R453-MODULE-ATTRIBUTE / R453-MODULE-FUNCTION-NOT-ADMITTED / R457-CLASS-SPEC-NOT-A-CLASS / R458-OPERAND-CLASSES;
##   corpus 6850-6867 witnesses + 6870-6874 controls, census +18 rows / 9 re-measured, 8 advice audits, annotations
##   §7.180 / translational §T.6.190, REPAIR sections; no def in a mirrored file, no axiom, no emission change).
##   The claim of a function now REACHES its callees for these rules (`_rc444`: #445's exemplar is a claimed `f`
##   calling an unclaimed method that reads `self.cout`). Allow-list rows judged on the REAL objects: bindings, file
##   MRO / #347 definitely-assigned fields, `hasattr` on the real builtin class / stdlib module, `isinstance(0, o)`,
##   `operator.<op>` on samples of the class pair, and three (module, function) rows (`os.path.join`, `copy.copy`,
##   `dataclasses.replace`). All 117 route witnesses refused. Cost: 0 PASS files, 0 mirror files; 5 expected-FAIL
##   witnesses (4491 / 4492 / 4494 / 4808 / 4815) now refused (GONE), 4 already-refused witnesses refused earlier.
##   Residual: non-stdlib modules, multi-class / underivable operands and receivers, non-file bases, dynamic attributes.
##   INCREMENT 2 (same rule, callee reach): #441's BUILTIN FUNCTION rows are also judged in an UNclaimed function called
##   by a claiming one (`def g(n: int): return len(n)` under a caller's `\all` PROVED on main: witness 6868, control 6875).
##   Extending the whole #432 / #440 claim instead refused 10 PASS corpus files (`super()` receivers, `list.pop` in
##   reached constructors) and was NOT landed. Open lead: #161 / Module 6 obligations still read a function's OWN
##   claim (`math.factorial(n)` in an unclaimed callee proves under the caller's `\all`).

## run #3 (2026-10-29): #444-#459 OPENED (red team 36, SYSTEMATIC census of operators / dunders / scoping / call
##   binding / modules on 8fe7204c3: 1723 probes / 240 proved / 209 confirmed; rt35's 175 all closed): #444 unbound-name-opaque (9); #445 missing-attribute-opaque (21); #446 unknown-operator-matmul (7); #447 augmented-shift-obligation (13); #448 builtin-arity-keyword (6); #449 user-call-signature (17); #450 super-call-opaque (6); #451 field-default-annotation (5); #452 bytes-int-argument-range (13); #453 module-function-by-name (56); #454 starred-non-iterable (3); #455 decorator-misuse (6); #456 set-method-arg-hash (14); #457 isinstance-class-spec (5); #458 operator-operand-classes (19); #459 conditional-module-binding (9).
##   Diagnosis: the dominant shape (F1 F2 F3 F10 F14 F15, 117 of 209) is an OPAQUE FALLBACK -- a construct the emitter
##   does not recognise is lowered to an opaque value instead of being refused; the rest are missing obligation rows.

## run #3 (2026-10-28): #440 / #441 REPAIRED (executor h440 off fa7cbb1aa; ONE signature table inline in `_run_pipeline`
##   after #432/#433/#437: `_FT440` 36 builtin rows + `_MT440` 100 (receiver class, method) rows, allow-list, refuse by
##   default; codes PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE; corpus 6650-6682 witnesses + 6690-6695
##   controls, census rows, advice audits, annotations 7.141 / translational T.6.152, REPAIR sections; no new def in a
##   mirrored file, no axiom, no emission change). All 150 route witnesses refused; a new A1 form through a MODULE receiver
##   (`math.factorial` beside a file `factorial`) found and closed. Cost: 0 PASS files; 4 VERIFY-FAIL witnesses refused
##   earlier. Residual: underivable receivers with a builtin method name (#443), `super()` / module calls (#161 by name).

## run #3 (2026-10-28): #442 / #443 REPAIRED (executor h442 off fa7cbb1aa; code inline in `_run_pipeline`'s route #432
##   judgement and narrowing leaves + one row of the `_ty383` type propagation; corpus 6750-6786, census +31 rows / 7
##   re-measured, advice audit R443, docs annotations 7.150 / translational T.6.160, REPAIR sections; no new def in a
##   mirrored file, no axiom, no emission change). #442: `isinstance(R, E)` narrows only when every class of E is a name
##   never bound in the file naming a real builtin class (metaclass `type`) that NoneType does not subclass; aliases,
##   attributes, imports (`Hashable`), tuple variables, PEP 604 unions and file classes do not narrow. #443 (ROOT: #432
##   admitted an EMPTY known-class set, so every underivable receiver passed): an attribute on a receiver whose classes are
##   empty / `#UND` / `#UNK` / `#UNKT` / `#UB` / `Any` / `object` / an unknown class name is REFUSED under an AttributeError
##   claim (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE); module objects and the DVW-R5-obligated `(N.get(k) or {}).get(k2, D)`
##   (own code) are not judged; a method on the `None` arm now derives bottom, not `#UND`. 25 red-team probes + h442's 6776 (a
##   `List[T]` element) PROVED at base -> REFUSED; 4 rule witnesses (not proved at base) REFUSED; 6 controls PROVED both; 6784 (narrowed Any element) admitted, FAIL on route #343.
##   Gates: fidelity rc=0; root 2563 -> 2566 0 MOVED / 4 GONE (3289 4812 4813 4825, expected FAIL: VERIFY-FAIL -> REFUSED) /
##   0 APPEARED; pyref 2186 0/0/0; mirrors 53/53 0/0/0 (no OWED proof); planes 61/61; rwc 342 / advice 169 / dropped-mutation /
##   getattr / clause / assumed / carriers / frame-honesty / raises-honesty / trusted-reasons / doc rc=0. Over-refusal cost:
##   0 PASS files (1054-file claim-bearing screen incl. the 13 claimed mirrors: only 8 expected-FAIL files change).

## run #3 (2026-10-28): #440-#443 OPENED (red team 35, SYSTEMATIC builtin-precondition census on daaf6ea78: 860 probes /
##   452 fully proved / 175 confirmed; rt34's 63 all closed): #440 route #161 admits a method by NAME, not (receiver class,
##   method) (43); #441 builtin call signatures unchecked -- arity and argument classes (107); #442 #432's isinstance narrowing
##   trusts superclasses of NoneType (Hashable, object aliases) (6); #443 Any-container element as method receiver (19,
##   inside #432's documented residual). Diagnosis: the central admission point (#161) has no (class, method, signature) table.

## run #3 (2026-10-28): #432 / #433 / #437 REPAIRED (executor g4 off 1c083dcbe; code inline in `_run_pipeline` after the
##   #349-#383 hashing pass, over its class derivation; corpus 6500-6549, census rows, advice audits R432 / R433 / R437, docs
##   annotations 7.133-7.135 / translational T.6.144-T.6.146, REPAIR sections; no new def in a mirrored file, no axiom, no
##   emission change). Each rule ENUMERATES what it admits under a claim covering the exception. #432: `R.a` admitted iff R's
##   classes at that point (Optional now derives `None`, a `= None` default holds `None`; FLOW NARROWING of names / attribute
##   paths by if / while / IfExp / and / or / assert / early-exit guards, stopped by rebinding, calls on attribute paths,
##   nested defs and generator expressions) are one non-None class or builtins all having `a`
##   (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE). #433: `S.join(it)` with S derived str (bytes) admits only derived str (bytes /
##   bytearray) elements (PYCSL-R433-JOIN-ELEMENT-CLASS). #437: sorted / list.sort / min / max admit only derived totally
##   ordered values -- numbers, str, bytes, parameterised tuples / lists of such, a mapping's `.items()` keys
##   (PYCSL-R437-UNORDERED-ELEMENTS). All 27 red-team probes + 3 g4 probes PROVED at base -> REFUSED; 6 rule witnesses (base-refused shapes) REFUSED; 13 controls PROVED both.
##   Gates: fidelity rc=0; root 2518 -> 2531 0 MOVED / 1 GONE (4810 expected FAIL, now REFUSED) / 0 APPEARED; pyref 2186 0/0/0;
##   mirrors 53/53 0/0/0 (no OWED proof); pycsl_lib identical; planes 61/61; rwc 334 / advice 162 / getattr / clause / assumed /
##   carriers / doc rc=0; census +37 rows, 4621 / 4810 re-measured. Over-refusal cost: 0 PASS files (claimed-corpus screen: only
##   4621 / 4810 change). Residuals: underivable / Any receivers and elements not judged; see each route's RESIDUALS.

## run #3 (2026-10-28): #434, #435, #436 REPAIRED (executor g5 off 1c083dcbe; ONE shared fail-closed mechanism, code inline in
##   `_handle_call_expr` / `_reset_function_state`'s route #178 summary / `_run_pipeline` (mirror twins `\trusted`), corpus
##   6550-6578 / 6580-6585, census rows, advice audit (5 entries), docs annotations 7.136-7.138 / translational T.6.147-T.6.149;
##   no new def in a mirrored file, no axiom). Under `no_exception \all`: #434 `ord(x)` owes `String.length x = 1` (s[i] / a
##   one-char literal owe nothing; a non-str argument is REFUSED, PYCSL-R434-ORD-LENGTH); #435 an unbound `T.m(x, ..)` of a
##   builtin type is admitted only when x's class is exactly T by its form (allow-list; PYCSL-R435-UNBOUND-DESCRIPTOR);
##   #436 the ENUMERATED C ssize_t / int method parameters (split / rsplit maxsplit, replace count, insert index, center /
##   ljust / rjust / zfill width, to_bytes length; expandtabs tabsize / hex bytes_per_sep: C int) owe their range, a non-pure
##   argument is REFUSED (PYCSL-R436-SSIZE-ARGUMENT). FAIL-CLOSED: the driver recounts every such site of every `\all` body
##   from the IR and REFUSES one whose check never reached the module (PYCSL-R434-UNCHECKED-SITE: comprehension / lambda /
##   `for` iterable); an un-claimed callee holding one makes a `\all` caller refused (PYCSL-R434-CALLEE-UNCHECKED-SITE).
##   Witnesses: all 20 red-team probes + 8 more, PROVED at base 78b519f63 (6574: FAILED at base by a type error) -> FAIL
##   on the new goal or REFUSED; controls 6580-6585 PROVED both. Root 2518 -> 2535 0 MOVED / 0
##   GONE / 0 APPEARED (17 new emitting sources), pyref 2186 0/0/0, mirrors 53/53 0/0/0 (vs v8/mb; none OWED); planes 61/61; census + advice audit
##   rc=0. OVER-REFUSAL COST 0 (no corpus / mirror / pycsl_lib file claims `\all` around such a site).
##   INCREMENT 2 (off 86f9efa51): the front end erases a `Path` annotation to `str`, so `ord(p)` / `ord(p[0])` / an alias
##   `q = p.parent; ord(q)` / `str.upper(p)` of a `p: Path` PROVED (base and 86f9efa51; CPython TypeError): a source (AST)
##   pass in `_run_pipeline` REFUSES them (PYCSL-R434-ORD-PATH); witnesses 6573 / 6579 / 6586 / 6588, control 6587.
##   Increment-2 gates: root 2518 -> 2536 0/0/0 (18 new emitting), 0/0/0 vs increment 1's sweep too; pyref 2186
##   0/0/0; mirrors 53/53 0/0/0 vs v8/mb; planes 61/61; coverage (338 demonstrated) / advice (165 audited) / doc /
##   trusted-reasons / getattr / clause / assumed / carriers rc=0; sync + mirror-check rc=0.

## run #3 (2026-10-28): #438 and #439 REPAIRED (executor g6 off 1c083dcbe; code inline in the #349-#383 hashing pass of
##   _run_pipeline (src/pycsl/pycsl.py, `\trusted` in the mirror), corpus 6600-6624 / 6640-6643 + multi_file_lib/r439_*.py,
##   census rows (+ the 9 R-gate rows re-measured: message edit), advice re-audit, docs annotations 7.139-7.140 /
##   translational T.6.150-T.6.151, REPAIR sections; no new def in a mirrored file, no axiom, no new refusal code).
##   #438: an un-parameterised `tuple` / `Tuple` (#UNKT) is UNDERIVABLE for route R-gate and #430 (refused hashed under a
##   TypeError claim; a `\all` caller of an un-claimed holder refused); not #UNK, which §7.47 measured refuses the
##   un-claimed mirror `pycsl.py` `_record_key -> Tuple` keys. #439: (1) a value declared by a structural type (file
##   `Protocol` class, typing Protocol, ABC with its own `__subclasshook__`: Callable / Hashable / Iterator ...) is #UNK;
##   (2) an un-claimed function of an imported USER module that may hash joins the #430 set; (3) a computed-name
##   `setattr` makes field / class-attribute reads #UND. All 16 red-team witnesses (+ 4 latents, 3 probes) REFUSED;
##   controls 6640-6643 PROVED both. Over-refusal cost MEASURED 0: root 2518 -> 2522 0 MOVED / 0 GONE / 0 APPEARED (4 new
##   controls emit), pyref 2186 0/0/0, mirrors 53/53 0/0/0 (no mirror refusal, no OWED proof), pycsl_lib --no-proof
##   screen identical (104 files, rc0 87).

## run #3 (2026-10-28): #432-#439 OPENED (red team 34 on 78b519f63, convergence measurement: 497 written / 474 fully proved /
##   63 confirmed; FINDINGS salvaged by the driver; rt33's 115/117 proofs now refused): #432 an optional / union receiver of an attribute or method access owes no attributeerror (8); #433 str.join / bytes.join over elements not derivably str / bytes owes no typeerror (9); #434 ord() of a string not of length 1 owes no typeerror (7); #435 an unbound str / bytes method descriptor applied to a wrong-type first argument owes no typeerror (8); #436 str.split / rsplit with maxsplit outside c ssize_t owes no overflowerror (5); #437 sorted() over elements not totally ordered owes no typeerror (10); #438 hashing a bare / unparameterised tuple (elements unknown) owes no typeerror (11); #439 a hashed value whose class comes through a protocol, a foreign user module, or setattr owes no typeerror (5).
##   Diagnosis: every family is a builtin whose TYPE-DEPENDENT precondition (receiver / element class, length, range,
##   orderability) has no admission rule under `no_exception \all` -- the operator forms (un00-un17) are all refused.

## run #3 (2026-10-28): #430 REPAIRED and route R-gate BUILT (executor h430 off 725a1c7e5 + #431; code inline in the
##   #349-#383 hashing pass of _run_pipeline and in route #178's callee summary; corpus 6460-6464 / 6470-6475 / 6480-6481,
##   census rows (+ 5069 re-measured), docs annotations 7.131-7.132 / translational T.6.142-T.6.143; no new def in a mirrored
##   file, no axiom). R-gate: an underivable (#UND / no-source) hashed value in a function claiming TypeError is REFUSED
##   (PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM); `list(x)` / `set(x)` now derive x's elements (6336's cost). #430: route
##   #178's summary carries "may raise TypeError by hashing #UND" (PYCSL-R430-CALLEE-UNDERIVABLE-HASH). Witnesses 6460-6462
##   and 6470-6475 PROVED at base -> REFUSED; controls 6463 / 6464 / 6480 / 6481 / 6336 PROVED both. Root 0 MOVED / 1 GONE
##   (5069, expected FAIL, now REFUSED) / 0 APPEARED; pyref 2186 0/0/0; mirrors 53/53 0/0/0 (no mirror refusal, no OWED).

## run #3 (2026-10-28): #431 REPAIRED (executor h430 off 725a1c7e5; code src/pycsl/pycsl.py next to route #156, corpus 6450-6457,
##   census rows, docs annotations 7.130 / translational T.6.141, route431 REPAIR; no new def in a mirrored file, no axiom).
##   A `return` anywhere in a `finally:` block, or a `break` / `continue` in it outside a loop nested in the block, is REFUSED
##   (PYCSL-R431-FINALLY-JUMP-SWALLOWS-EXCEPTION). Witnesses 6450-6452 / 6457 PROVED at base -> REFUSED, 6453 / 6454 FAIL ->
##   REFUSED; controls 6455 / 6456 PROVED both. Root 2512 -> 2514 0/0/0, pyref 2186 0/0/0, mirrors 53/53 0/0/0, pycsl_lib
##   identical: cost 0, as the AST census said. Other channels (user __exit__ True, except BaseException, except*, nested def
##   handlers, generators) measured REFUSED by #38/#39, #174, the desugar refusal, #271. rg's S0 re-run: every swallow REFUSED.

## run #3 (2026-10-28): #430 and #431 OPENED; route R-gate (claim-gated #UND hashing refusal) CERTIFIED-BOUNDARY (executor rg off
##   289fe6029, wall cycle #2 dict-value-model-r3, impl doc getting-better/dict-value-model-r3-impl.md; no src/bin/corpus change).
##   #431: a `return` in a `finally:` swallows an AMBIENT exception (un-claimed hash TypeError l3o / l3p, un-claimed KeyError l3n),
##   so an un-claimed function's proved `ensures` is false on a NORMAL return (rc=0 PROVED, CPython violates). That refutes R-gate's
##   premise that "ambient" means abnormal termination only; cost of the proposed refusal measured 0 (no jump in any finally in
##   root / pyref / mirror / pycsl_lib). #430: a `no_exception \all` caller of an un-claimed callee that hashes #UND PROVED
##   (route #178's TypeError-from-hashing gap). R-gate's gated cost measured: 0 mirrors, 0 pycsl_lib, 0 pyref, 1 root PASS
##   file (6336, 2 sites); it is reopened once #431 is repaired.

## run #3 (2026-10-27): #421-#428 REPAIRED, #429 NOT REPAIRED (executor g3 off ac28806be; code + corpus 6250-6322 / 6330-6337
##   + census 73 rows + advice audits R405(#423) / R424 / R425 + docs annotations 7.110-7.117 / translational T.6.121-T.6.128,
##   REPAIR sections; no new def in a mirrored file, no axiom, ledger unchanged). Method: each rule now enumerates what it ADMITS.
##   #421 global / class-body names UNKNOWN unless every binding is derived (union); #422 unbound str methods, str-row allow-list,
##   Enum .value, nested def -> T; #423 class-creating values (type, stdlib / file metaclasses, Enum functional calls) confined
##   to admitted positions; #424 `K[i]` with __class_getitem__ refused; #425 explicit __init__ outside chaining refused;
##   #426 f-string float / `c` specs owe DBL_MAX / range bounds; #427 UB-7.1 through generator expressions; #428 safe modules
##   vouch for resolved FUNCTIONS only. All 114 red-team probes of #421-#428 REFUSED / FAIL on the final candidate (73 kept as
##   witnesses, PROVED at base); 8 controls PROVED both. Root 2497 -> 2512 0/0/0, pyref 2186 0/0/0, mirrors 53/53 0/0/0,
##   pycsl_lib identical, planes 61/61. #429 lies inside the declared LATIN1-STR assumption (FAILS under --strict-latin1).

## run #3 (2026-10-27): #421-#429 OPENED (red team 33, convergence measurement: 653 screened / 385 fully proved / 116 confirmed;
##   9/9 sample driver-reproduced rc=0 on main 06ad8aa32): #421 global/class-body initializer derived narrower than a local (55),
##   #422 local derivation gaps (3), #423 metaclass calls other than type(..) create dynamic subclasses (12), #424 K[i] via
##   __class_getitem__ hashed (2), #425 explicit x.__init__(..) frame-less (4), #426 f-string format specs owe no OverflowError (13),
##   #427 mutation while iterating via a generator expression (6), #428 "safe module" list admits its classes' methods (19), #429
##   str.upper() leaves Latin-1 (2, arguable). Diagnosis: the repairs held head-on (58/65 of rt32's proofs now refused/fail); what
##   leaks is each allow-list's COMPLEMENT (neighbouring spellings).

## run #3 (2026-10-26): #403-#416 OPENED (red team 32 on 085ee3dcc: 63 confirmed / 345 screened / 157 fully proved; 11/11 sample
##   driver-reproduced rc=0): #403 verified __eq__ only for own-class `other`, #404 `type` base = metaclass unmodelled, #405 dynamic

##   subclasses escape the closed world, #406 GD misses stdlib attribute setters, #407 arithmetic/BoolOp/IfExp/slice over a container

##   global classed hashable, #408 read-only global test misses __main__ subscript store, #409 stdlib module attributes hashed

##   unclassified, #410 copy ignores __copy__/__replace__, #411 Latin-1 literal emitted as UTF-8 bytes, #412 float / by zero, #413 int

##   true-division overflow, #414 size limits, #415 `%` formatting, #416 dict mutation while iterating a view.

## run #3 (2026-10-27): #411 REPAIRED, candidate (u411 off 77b33f239; annotations 7.90 / translational T.6.101; corpus
##   6200-6209; route REPAIR section). WIDER than filed: Why3 1.8.2 prints every literal character outside printable ASCII,
##   and `"` / `\`, as `\xHH`, which Z3 4.13 reads as 4 characters, so `"\n"`, `"\t"`, `"a\"b"` had the wrong length too
##   (`requires s == "\n"; ensures len(s) == 4` PROVED). Final-text literal pass in `_run_pipeline` (twin `\trusted`):
##   such literals become `pystr_cat` / `pystr_chr N` (module PyCSL_StrLit: length 1, injective code, ground
##   disequality from the 93 printable one-char literals; no axiom, assumed-facts 88 -> 88); code points 128..255 are one
##   character. Root 10 / pyref 4 / mirror 18 MOVED (exactly the census of non-printable literals; diffs = re-encoding
##   only), 14/14 corpus verdicts kept, witnesses flip, controls prove; fidelity, planes 61/61, `\trusted` 442 -> 442.
##   Exposed a mirror proof that rested on the bug (audit_proof `_strip_lean_comments`; invariant strengthened, proves).
##   Whole-file mirror proofs: all 18 moved mirrors rc=0 at the candidate (incl. expressions, statements, stmt_control_flow,
##   functions); none OWED.

## run #3 (2026-10-27): #417 REPAIRED, candidate (r417 executor, completed and gated by r417b off 930d68ed5; code + corpus
##   6100-6125 + census + advice audit + docs, annotations 7.80-7.83 / translational T.6.91-T.6.94, route REPAIR section; no new

##   def in a mirrored file, no new axiom, ledger unchanged). Eight false proofs CONFIRMED at base (PROVED, CPython violates):

##   `[1, 2] * 3` as a length-3 list and `(0,) * 3` as the int 0 (REFUSED, PYCSL-R417-SEQUENCE-REPEAT); `[*range(n)]` as one

##   element (now an unconstrained list); contract `"\n"` kept raw (decoded as Python does); `list` / `sorted(range(10**20))`

##   and `float(10**400)` with no OverflowError obligation (obligations under `\all`; an obligation erased by a coercion is

##   REFUSED, counted per source occurrence; `float` of a non-int-read argument REFUSED); `setattr(o, "x", [1])` and

##   `shlex.split(..)` results hashed (UNKNOWN unless allow-listed). Root 2484 -> 2497, 3 MOVED (3570/3571/3575: one unused val

##   decl; verdicts kept), 0 GONE; pyref 0/0/0; mirrors 2 MOVED (Module3_Weaver 288/0 proved; Module5_IREmitter whole-file proof

##   OWED); planes 61/61; pycsl_lib identical. Residuals: a NON-constant `setattr(self, nm, [1])` still proves `{r.x}`; (h) the

##   `__eq__` isinstance narrowing not addressed.

## run #3 (2026-10-26): #226 POLARITY FLIP REPAIRED, candidate (c226 executor off main 8f4221371; code + corpus + docs on this
##   branch, annotations 7.58 / T.6.69, route #226 REPAIR section). A `#@ class invariant` of a class of the verified file is

##   ADMITTED only when its constructor goal `_check_class_inv_<c>` is emitted; otherwise REFUSED (NEW

##   PYCSL-R226-INVARIANT-GOAL-NOT-STATED; exemptions: a `\trusted` `__init__`, an imported class). NEW goal stage 2d states the

##   goal from `__init__`'s AST end state (int / bool literals and parameters, int expressions incl. `max` / `min`, `[c] * K`

##   element contents for element / quantifier terms, registry predicates). Census at HEAD: 336 invariant classes, 270 stated /

##   38 refused (#384) / 28 ASSUMED; after: 279 / 38 / 19 (10 refused witnesses, 7 trusted `__init__`, 1 imported, 1 expected-FAIL).

##   Gates: root 7 MOVED (goal line only, re-proved base + candidate), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED); fast planes

##   61/61 (trusted-raises-honesty now pairs a mirror def with its SAME-PATH live def first; ratchet tightened 61 -> 56).

##   Wholesale-refusal cost 8 PASS corpus + 3 mirrors + 2 pycsl_lib -> 0 / 0 / 0, at ONE new `\trusted` marker (mirror

##   `errors.py` `PyCSLError.__init__`: its `self.line >= 0` is not established and no raise site is modelled). Closed: carriers

##   #226 computed store and #384 element-term (rows assert REFUSED), rt29 a04/a05/a08/a10/a11/a24/a34/a46 (REFUSED). Corpus

##   0661/0662 source-repaired (`\valid(initial, 18)` is `>= 18`, invariant `== 18`). Residual: #385 unverified caller alias.

## gen #37 / run #3 (2026-10-27): #403 + #404 + #405 + #406 + #407 + #408 + #409 + #410 REPAIRED, candidate (g1 executor off 4431ef86f;
##   code + corpus + census + docs, annotations 7.60-7.64 / translational T.6.71-T.6.75, route REPAIR sections; inline in

##   `_run_pipeline`, refusals only, no emission change, ledger unchanged). Positive predicates tightened: a verified `__eq__` must be

##   `(self, o: object)` (#403); `type` is a base only for a metaclass that defines nothing, `metaclass=` only type / ABCMeta /

##   EnumMeta / a file class, closed over file subclasses of `type` (#404); `type(n, b, ns)` / `types.new_class` /

##   `make_dataclass(bases=)` refused anywhere, driver included (#405, new PYCSL-R405-DYNAMIC-SUBCLASS); a stdlib call outside an

##   attribute-safe module list (argparse, optparse, functools.update_wrapper, mock, object dunders, `"__dict__"`) makes GD and

##   field / class-attribute hash sources UNKNOWN (#406); container arithmetic / BoolOp / IfExp / slices stay containers (#407);

##   subscript stores are not bindings (#408); stdlib objects by real class, mutable / unhashable / method results UNKNOWN (#409);

##   copies UNKNOWN under `__copy__` / `__replace__` / `__deepcopy__` / `__reduce(_ex)__` (#410). Witnesses 5970-6014 (45, PROVED at

##   base -> REFUSED) + latents 6015 / 6016 / 6018 + #380 coverage 6017; controls 6020-6027 PROVED both. Root 2441 -> 2449 0/0/0,

##   pyref 2186 0/0/0, mirror 53/53 0/0/0, lib screen identical (104). Measured, not landed: #406 over the driver (GONE 5464) and over

##   every unread callee (6 mirrors GONE). Residuals: `isinstance` does not narrow an `object` `__eq__` parameter (field-wise eq

##   refused); #406 driver calls, user-module callees, `setattr` for hash sources; stdlib function results underivable.

## run #3 (2026-10-26): #420 (THE BESPOKE LOWERINGS DROP THE DECLARED CONTRACT: a recognized shape is replaced by a group with
##   `requires/ensures { true }`; `#@ ensures False` and a `no_exception` over a raising body PROVED, 15/15 probes + mirror `--fun`)

##   REPAIRED, candidate (rc1 off 42bc9c879): one predicate `generic_fold.bespoke_contract_ok` gating every `recognize_*`

##   (decorator; list recognizers re-run on conforming functions) and the 24 FunctionEmissionMixin-local branches. Witnesses

##   5920-5934 (5926: a dropped callee `requires`); mirror 53/53 0 MOVED; see route420-recognizer-drops-contract.md.

## run #3 (2026-10-26): #402 (a user `__hash__` on the static class itself is never called in the model: a raising `__hash__`
##   proves `{d}` under no_exception) OPENED (e1 residual of #395, driver-reproduced rc=0, CPython ValueError).

## gen #37 / run #3 (2026-10-26): #412 / #413 / #414 / #415 / #416 REPAIRED, candidate; #411 NOT REPAIRED (g2 executor off 4431ef86f;
##   code + corpus 6056-6076 + census + docs, annotations 7.70-7.74 / translational T.6.81-T.6.85, route REPAIR sections; no new

##   def, no new axiom, ledger unchanged). #412 float `/` and int TRUE `/` owe a zero-divisor obligation (int `a / b` was the one

##   int division path never wrapped). #413 int `a / b` owes |a| <= DBL_MAX * |b| under `\all` (FLOAT-FINITE judged NOT to

##   cover a raised OverflowError). #414 Py_ssize_t bounds (len(range), str / list repetition, `<<`) under `\all`; MemoryError

##   left unmodelled (a memory-cap assumption is a USER decision). #415 `%` formatting refused under `no_exception` unless

##   allow-listed (literal %s/%d/%i/%r, flags / width, matching operand count and static types; PYCSL-R415). #416 UB-7.1 matches

##   `d.keys()` / `.values()` / `.items()` (inline in `_run_pipeline`; the ir_scanner version left the recognised mirror model

##   stale, measured and moved). Root 2441 -> 2455, MOVED 1163 / 1164, GONE 3269 (expected FAIL); pyref 1 MOVED (0110, FAIL

##   both); mirrors 53/53 inert; pycsl_lib screen identical. #411: the encoder fix is necessary but NOT sufficient -- Why3

##   1.8.2 prints every non-printable / `"` / `\` string-literal character as `\xHH`, which Z3 4.13 (SMT-LIB 2.6) reads as

##   FOUR characters; a faithful repair moves 122 root / 4 pyref / 30 mirror emissions -- design decision for the user.

## gen #37 / run #3 (2026-10-26): #402 REPAIRED, candidate (e3 executor off 526d534de; code + corpus + census + docs, annotations 7.57 /
##   translational T.6.68, route REPAIR section; inline in `_run_pipeline`, no new def, no emission change, ledger unchanged). Option (b)

##   allow-list landed, option (a) faithful `__hash__` / `__eq__` call lowering measured and not taken (an emitter + mirror change for the

##   same 4 movers). A `__hash__` / `__eq__` counts only when ONE top-level `def` verified `no_exception \all`, no `requires`, `-> int` /

##   `-> bool`; an MRO-deciding unverified `def __hash__` makes the class unhashable (PYCSL-R349, message extended); EQ-RISKY classes (an

##   unverified `__eq__`, or dataclass / NamedTuple equality over a non-eq-safe field, closed over file subclasses) are refused at every

##   hashing site that may compare (all but `hash(x)` and one-element set / dict displays; new PYCSL-R402-UNVERIFIED-EQ). PASS controls

##   4694 / 4940 / 5043 given an honest `#@ no_exception \all` on their total `__hash__` (emission byte-identical, re-proved base +

##   candidate). Witnesses 5780-5789 PROVED at base -> REFUSED; controls 5800-5801 PROVED both. Root 2438 -> 2440 0/0/0, pyref 2192

##   0/0/0, mirror 53/53 0/0/0, lib screen identical (104). Residuals: cyclic values under field-wise `__eq__`; `__eq__` reached

##   through a stdlib container element; R252 already refuses `a in s` over an annotated `Set[D]` with a user `__eq__`.

## run #3 (2026-10-26): #401 (a `\trusted` stub's `assigns \nothing` over a body that mutates its PARAMETER in place:
##   pure_ast NodeTransformer.generic_visit; check-trusted-frame-honesty only sees self writes) OPENED (e2 side note, driver-confirmed).

## gen #37 / run #3 (2026-10-26): #393 + #396 + #397 + #398 + #399 + #400 REPAIRED, candidate (e2 executor off 3b2d2e763; code + corpus +
##   docs ffec1ac18 + follow-ups on this branch, annotations 7.52-7.56 / T.6.63-T.6.67, route REPAIR sections; inline in `_run_pipeline`,

##   no new def, no emission change, ledger unchanged). Allow-list polarity per model decision: #393 builtin exception bases admitted only

##   with a constructor model (any-arity `(self, *args)` no keyword via route #369; SyntaxError family by shape; ExceptionGroup /

##   Unicode*Error refused by S1); #396/#397 GD reads the closed-world SUBCLASS closure and binds every identifier a class-scope node

##   carries unless its kind is on a NON-binding allow-list, every Store/Del attribute in any target (self -> its class, else every

##   class); #398 functional TypedDict is a TC construct, body `.k` on a TypedDict refused, optional-key reads (NotRequired / total=False

##   / unknown) refused (new PYCSL-R398-TYPEDDICT-ACCESS); #399 builtins resolved through `from builtins import` / `builtins.` before SB;

##   #400 `.visit` / `.generic_visit` refused when a stdlib NodeVisitor subclass dispatches to `visit_*` (new PYCSL-R400-NODEVISITOR-

##   DISPATCH; the mirror's visitors use `pure_ast`, so the table keeps the bases). 27 red-team witnesses + 5 latents PROVED at base ->

##   REFUSED (corpus 5620-5646, 5650-5654); controls 5680-5686 PROVED both. Root 2424/2431 0/0/0, pyref 2186/2186 0/0/0, mirror 53/53

##   0/0/0 (first cut GONE'd mirror pure_ast + corpus 0889/0890: refined). Residuals: other-module subclasses / user-module bases (GD),

##   `cls(..)` constructions (#393), visit havoc model not built (#400).

## gen #37 / run #3 (2026-10-26): #392 + #394 + #395 REPAIRED, candidate (e1 executor off 3b2d2e763; code + corpus + census + docs
##   3445dc472, annotations 7.48-7.50 / translational T.6.59-T.6.61, route REPAIR sections). #392: ONE inline scope resolver for a base

##   head name (enclosing scope, enclosing functions, module, builtins, stdlib star import) read by S1, its star-import rule and the

##   hash MRO (shadowed import / builtin base = outside token); new latent 5554 (nested `class TypedDict`). #394: recognised SOURCES

##   for the hashed value's class (module globals / class attributes bound once, by initializer; read-only displays by element;

##   stdlib objects; copy.copy / deepcopy / dataclasses.replace; set / frozenset / Counter / fromkeys / dict over any iterable). The

##   full "unknown is refused" flip was MEASURED and NOT landed: 27/53 mirrors refused (679 sites; no-source-only variant: 7

##   mirrors), 7 root/pyref + 1 lib PASS file. #395: B unhashable when a file subclass is or defines an unverified `__hash__`.

##   Witnesses 5550-5580 PROVED at base -> REFUSED; controls 5590-5592 PROVED both. Root 2423->2426 0/0/0, pyref 2186 0/0/0, mirror

##   53/53 0/0/0, lib screen identical. Residuals: underivable (#UND) values still deny-list; own raising `__hash__` on the static

##   class still PROVES (requiring a verified one refuses PASS 4694/4940/5043); raising `__eq__` on collision unmodelled.

## gen #37 / run #3 (2026-10-26): #392 (nested class shadows a stdlib base for S1 / §7.46), #393 (builtin-exception subclass construction
##   unchecked), #394 (§7.47 hash allow-list misses module globals / class attributes / set()-frozenset() over dict views / copy), #395 (hash

##   check reads the static class only: unhashable subclass instance), #396 (GD folds getattr default when only a subclass binds), #397 (GD

##   census sees only `self.k = v` stores), #398 (TypedDict as an all-keys record), #399 (`from builtins import sorted` bypasses SB), #400

##   (ast.NodeVisitor admitted but `visit` has no effect) OPENED (red team 31: 59 confirmed / ~470 probes, 57 on these routes + 2 documented

##   residuals c23 / g24; 9/9 sample driver-reproduced rc=0 on 7859e8fb0).

## gen #37 (2026-10-26): #383 ALLOW-LIST ADDENDUM, candidate (rh1 executor off b62ff2e23; code 948b0ba72, corpus + census 6d4cac6a3,
##   docs annotations 7.47 / T.6.58, route383 REPAIR ADDENDUM). r381s "Variant A" landed: a hashed value of an UNKNOWN class

##   (declared Any / object / TypeVar, a non-stdlib module's class, a `Dict[str, Any]` subscript value) is refused unless known

##   hashable (PYCSL-R349-UNHASHABLE-RECORD, same message). Variant A alone GONEs 2/53 mirrors (root / pyref / lib 0): narrowed by

##   a PRECISE guarded re-hash (`if A in B:` then `B[A]`: module6_whyml/functions.py) and by keeping an UN-PARAMETERISED tuple

##   on the deny-list (pycsl.py `_record_key -> Tuple` of why3-JSON values: genuinely unknown-typed; residual). Witnesses

##   5500-5506 PROVED at base -> REFUSED; controls 5510-5511 PROVED. Root 2421/2421 0/0/0, pyref 2186/2186 0/0/0, mirror 53/53

##   0/0/0, lib identical, planes 61/61. Residuals: underivable (#UND) values unchecked; bare `tuple` holding a list PROVES; a

##   hashable class of a user module is over-refused (0 measured users).

## gen #37 (2026-10-26): #381 + #382 + #383 REPAIRED, candidate (r381s executor off 7bf752d4e; code 324907ddc / 9942dc760 (from the
##   r381 WIP, measured and narrowed), corpus + census b89ed1f91, docs ed1448bd4 (annotations 7.46 / T.6.57), route docs; inline, no

##   new def, no new refusal code, ledger 3). Sound refusals, no emission change, all PYCSL-R349-UNHASHABLE-RECORD. #381: outside bases

##   classified on the REAL stdlib class (`__hash__` None, contents-delegating hash: slice / memoryview / MappingProxyType /

##   weakref.ref; unknown = unhashable). #382: container mark at every depth of every hashing position; outside value classes by

##   their real class. #383: per-function type propagation (aliases, get / views / loops / comprehensions / slices / `*x` / `-> T`),

##   underivable = no class; declared Any / object / TypeVar checked against the file's unhashable classes. 47/47 red-team witnesses

##   + 9 NEW latents (deque `s.add` / dict key, MappingProxyType x2, memoryview, slice, weakref.ref, subclass-only field, star-import

##   base) PROVED at base -> REFUSED (corpus 5330-5385); controls 5390-5393 PROVED. The WIP's "#UNK for every underivable form"

##   refused 13/53 mirrors + 5 PROVED corpus files and was narrowed. Root 0 MOVED / 1 GONE (3601, expected-FAIL witness, now a sound

##   refusal) / 0; pyref 0/0/0; mirror 0/0/0 — no OWED proof; pycsl_lib identical. Planes fast 61/61. Residuals: still a DENY-list

##   (underivable values unchecked; Any / cross-module classes only vs the file's classes — driver probes a4 / a11 still PROVE).

## gen #37 (2026-10-25): #386 + #387 REPAIRED, candidate (r386 executor off 5addbdeef; code 13fbfa1ed / a1b4a8dd6 / 20ccfe42d, corpus
##   ebed9c6e7 / 20ccfe42d, docs 475527100 (annotations 7.41 / T.6.52), census d3fffd4f9, route docs; Module 3 only, inline, no new def,

##   no new raise site, ledger 3). Sound refusals, no emission change. #386: route #131's builtin-shadow arm now also covers a nested

##   `def` / `class` in a function or method, an import (local or module-level, not from `builtins`), a lambda parameter and a

##   comprehension target named like a builtin and read. #387: in every CLASS body, a `global` / `nonlocal` naming a member, and any

##   def / class / annotated member under a compound statement (except the body of a literal `if True:`, control 4940) are REFUSED.

##   10/10 red-team witnesses PROVED at base -> REFUSED, plus 5 NEW latents (lambda param, local / module `import .. as max`,

##   `for _ in range(0): def`, `if True: .. else: def`) PROVED at base -> REFUSED (corpus 5290-5310); controls 5320-5325 PROVED.

##   Root 0/0/0 (first sweep GONE'd 4940 -> `if True:` body admitted), pyref 0/0/0, mirror 0/0/0 — no OWED proof. Residuals:

##   over-refusal of always-true non-literal conditions (`if TYPE_CHECKING:`, 0 census users); no erasure model — see REPAIR.

## gen #37 (2026-10-25): #384 + #385 REPAIRED, candidate (r384 executor off 0a2d8019b; code 43ef55ea1 / 06912f666 / 80cb35620, corpus
##   06912f666, docs 06cf27dd5 (annotations 7.40 / T.6.51), clause-survival ledger 88896db0f, census + carriers 8c37ef315, route docs;

##   inline, no new def, no new field, ledger 3). Route #226's `\length` constructor goal now reads each list field's END state in

##   `__init__` (`_run_pipeline`'s `ctor_len_r384`: a fresh literal-length list — display, `[..] * K` with `[] * N` / K <= 0 EMPTY,

##   `bytearray(K)` incl. a once-bound module constant — followed by literal-effect `append` / `insert` / `extend([..])` / `pop` /

##   `clear` / `reverse` / `sort`; or a parameter named nowhere else with no call after the store). A `\length` class whose goal

##   stops only on a field state is REFUSED (NEW PYCSL-R384-INVARIANT-GOAL-UNSTATABLE, via an emission marker); a `super().__init__`

##   / `B.__init__(self, ..)` into a `#@ requires` over non-int parameters is REFUSED (NEW PYCSL-R385-DELEGATED-INIT-REQUIRES-UNCHECKED).

##   35/36 red-team witnesses PROVED at base -> 8 FAIL / 27 REFUSED (corpus 5240-5259); controls 5270-5275 PROVED. Census: 21

##   goal-less corpus `bytearray` classes (2c's computed-container residual) now get a goal and discharge; 0 corpus / mirror /

##   library refusals. Root 21 MOVED (goal line only, all re-proved to label) / 0 / 0; pyref 0/0/0; mirror 0/0/0 — no OWED proof.

##   Residuals (2 new registered carriers, SUCCESS): an element term masking a mutated length field (refusing it GONEs mirror

##   `Module2_Parser.py`), an unverified caller clearing an aliased list after construction (c34) — see REPAIR.

## gen #37 (2026-10-25): #384 (`\length` invariant with no statable goal assumed), #385 (`\length` goal binding / `[]*N` / super().__init__
##   requires), #386 (nested def shadowing a builtin), #387 (class-body defs never bound), #388 (getattr default vs imported base), #389 (getattr

##   default vs setattr / mangled store), #390 (`**` into builtins), #391 (Protocol / TypedDict construction) OPENED (red team 30: 60/233

##   confirmed; 8/8 sample driver-reproduced rc=0 on a064a298f).

## gen #37 (2026-10-25): #226 INCREMENT 2c (`\length` over array fields) REPAIRED, candidate (r226b executor off 919533395; code cabbeced2 +
##   40d416a0f, corpus + witnesses 40d416a0f / c4812834c, docs f0e1494c1 (annotations 7.37 / T.6.48), clause-survival ledger 2930c0af8,

##   census 31093ce1c, conformance golden 0595 c4812834c, route docs; Module 6 `_emit_type_decls` only, inline, no new def, ledger 3).

##   The constructor-invariant goal now admits `\length(self.f)` over an array field: `f` bound at its array type to the `__init__`

##   parameter it is stored from (quantified, premise-free for a synthesized dataclass `__init__`) or to its literal initial length

##   (`(Array.length f) = N`); `#@ requires` conjuncts with `len(p)` / `\length(p)` are premises. Census: 60 `\length` classes; 39 now

##   get a goal (16 discharge, 22 FAIL incl. the carrier, 1 refused file), 21 computed container stores stay goal-less. 13 PASS corpus constructors (0925-0929,

##   0933-0935, 1190, 1681, 1682, 1690, 2220; 2220 a latent false proof across the module boundary) gained `#@ requires len(toks) >= 1`

##   (callers satisfy it, labels unchanged, all re-proved). Registered carrier + witnesses 5100-5109 (incl. red team 29 a06 / a07)

##   PROVED at base -> FAIL; carrier row now asserts FAILED; controls 5110-5114 PROVED. Root 36 MOVED (goal line only, all re-proved

##   to label) / 0 / 0; pyref 0/0/0; mirror 1 MOVED (`proof2why3/parser`, whole-file proof SUCCESS, no OWED). Residuals: computed

##   container stores (`[Tok(0)] * 3`), element / quantifier / str terms, bool fields (rt29 a04/a05/a24), a08/a10/a11/a34/a46,

##   computed int stores (increment 3) — see REPAIR.

## gen #37 (2026-10-25): #377 + #378 + #379 + #380 REPAIRED, candidate (r377 executor off b815ee8d8; code 718bb669 / 13ee6e9e / 47fed51b,
##   corpus 91dc9137 / 7b794661 / 4f3a5cfc / 672aa0c5, docs 91dc9137 (annotations 7.38 / T.6.49), census 7b794661, route docs; no new def,

##   ledger 3). Sound refusals, no emission change. #377/#378: in every CLASS body a name bound twice where one binding is a `def` /

##   `class` / annotated member is REFUSED (Module 3's class-scope walk of #122/#130; property-accessor and `@overload` chains

##   exempt). #379: a `*` / `**` argument at a call of a file class / module `def` / file-class method is REFUSED

##   (PYCSL-R379-STARRED-CALL-ARGUMENT), except `*xs` landing wholly in an `*args` the contract does not read (mirror

##   `set_precedence`). #380: the constructor walk continues past `@dataclass(init=False)` to `object.__init__`; `super().__init__` /

##   `super(X, self).__init__` / `C.__init__(self, ..)` arity-checked (PYCSL-R369-CONSTRUCTOR-ARITY); construction through a metaclass

##   binding `__call__` (or unresolvable) REFUSED (PYCSL-R380-METACLASS-CALL). Witnesses 5140-5157 (18 red-team) + NEW latents

##   5158 / 5159 (`super().__init__(5)` over `__init__(self)` / `object`; PROVED at base) -> REFUSED; controls 5170-5174 PROVED at

##   base and after. Root 0/0/0 (5 new controls), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED). All gates rc=0 (planes fast 61/61).

##   Residuals: module scope, imported callees / `cls(..)`, diamond `super()` tails, inherited imported metaclasses (see REPAIRs).

## gen #37 (2026-10-25): #373 + #374 + #375 + #376 REPAIRED, candidate (r373 executor off dc378283c; code ada49f2d / 7a051eec /
##   34a579bb / 39d61190 / 9d029328, corpus e8488149 + 0c64cab1, census 98378213, getattr sites 51f0fbb1, docs f19c7b7a + c037431b

##   (annotations 7.36 / T.6.47), route docs; inline, no new def, ledger 3, one new refusal code). #373: the bare call of a def

##   nested in a METHOD (lifted to a method, lowered to the opaque int stub `g_0 ()`) is route #249-erased unless every method of

##   that name returns int / bool (names from the source). #374: `__slots__` entries mangled by their declaring class and attribute

##   stores by their lexical class before the #360 comparison (also fixes the `self._A__x` over-refusal). #375: a PyCSL-R375

##   failing assertion for an augmented assignment on an erased target / value under `no_exception`, and for a starred erased

##   element of a display (any context) or call (under `no_exception`). #376: NEW PYCSL-R376-GETATTR-CLASS-BINDING — `getattr` on

##   a known record of a non-field name bound in a class body of its file MRO (or a dunder / `object` name, or under a user

##   `__getattr__`) is refused instead of folding to the default. Witnesses 5050-5082 (22 route witnesses, 11 further shapes; 28 PROVED at

##   base, all CPython-violating) -> FAIL / REFUSED; controls 5090-5093 PROVED (5091 was an over-refusal at base). Root 0/0/0

##   (1723 GONE once = `--verify-imports` resource artefact, re-emitted identical), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED).

##   Residuals: outside-file bases not read (#376), starred call args outside `no_exception` (#375), nested `-> int` stubs (#373).

## gen #37 (2026-10-25): #377 (class-body name bound twice), #378 (dataclass default from first binding), #379 (`*`/`**` call args dropped),
##   #380 (constructor arity gaps: init=False / super().__init__ / metaclass __call__), #381 (stdlib bases skipped in hash MRO), #382 (container

##   set-display elements), #383 (hash element-class sources) OPENED (red team 29: 75/~270 confirmed; 7/7 sample driver-reproduced rc=0 on

##   919533395); 10 more live #226 not-covered shapes recorded under route #226 (witnesses-r226-rt29).

## gen #37 (2026-10-25): #369 + #370 + #371 + #372 REPAIRED, candidate (r369 executor off dc378283; code 88877615 / 6b575c0e /
##   38161b2e / 5a70413a / c2f46d20 / 710d3223, docs 2623c62a (annotations 7.35 / T.6.46), corpus c2f46d20 + 710d3223, census 001405cc +

##   710d3223, route docs; inline in the #346-#349 / #360-#363 and #339/#352 blocks of `_run_pipeline`, no new def, ledger 3). Sound

##   refusals, no emission change. #369: dataclass annotation heads / default callees RESOLVED through imports + module aliases

##   (PYCSL-R369-DATACLASS-SPECIFIER: an aliased InitVar / ClassVar / KW_ONLY / field, an unknown head or callee, a `def` default

##   callee, a member nested in class-body control flow, malformed `field(..)` keywords) and constructor ARITY checked against the

##   first C3-MRO `__init__` / the synthesized dataclass `__init__` / `object.__init__` (PYCSL-R369-CONSTRUCTOR-ARITY: d12 and d32 are

##   arity holes, and literal-spelling NEW latents 5008 / 5009 / 5037 / 5038 incl. a plain explicit `__init__(self, x)` with `D(1, 5)`).

##   #370: enum private test on the mangled key, member values only provably non-descriptor (literal / display / alias / auto() /

##   member()), any other value unknown-status, `C.X` of a non-member refused (except calling an own def / static / classmethod),

##   a read `_ignore_` refused. #371: `__hash__` looked up along the C3 MRO. #372: hashed element class from typed fields

##   (class-body / `self.f` stores), List / Dict / Tuple subscripts and loop elements of annotated names / fields. Witnesses

##   4990-5039 + 5045 (44 red-team + 7 new; all PROVED at base) -> REFUSED; controls 5040-5044 PROVED. Root 0/0/0 (5 new controls),

##   pyref 0/0/0, mirror 53/53 0/0/0 (no OWED). All gates rc=0 (planes fast 61/61). Residuals: `*`/`**`/super()/imported-class

##   constructions not arity-checked, non-descriptor computed enum values now over-refused, imported bases skipped (see REPAIRs).

## gen #37 (2026-10-25): #226 INCREMENT 2b (int-field projection) REPAIRED, candidate (r226 executor off c6d1156c; code 3633864b + 35fcdf9e,
##   corpus 09b5ef35 / 79cabed2, docs e29abd71 / e4dfb713 (annotations 7.34 / T.6.45), census 26f2fd53 / e4dfb713 + route docs; Module 6 goal + a `_run_pipeline` refusal, inline, no

##   new def, ledger 3). The constructor-invariant goal is now stated over the INT fields the invariant reads even when other

##   fields / `__init__` parameters are str / List / record / Optional (unconstrained in the goal); `#@ requires` conjuncts over the

##   bound int params are premises. NEW latent (increment 2's own goal): a param named like ANOTHER field conflated binders

##   (`self.x = y; self.y = x` PROVED `x == y`) -> REFUSED (NEW PYCSL-R226-INIT-PARAM-FIELD-NAME-CLASH). Witnesses q362str / q362list /

##   q362xinit = 4950-4952 + 4953/4955/4956 PROVED at base -> FAIL/REFUSED; controls 4960-4964 PROVED. Census: 227 invariant classes

##   reach emission, 147 had a goal, projection moves 4 (1 corpus file, 4573, re-proved); refusing the other 76 measured not inert

##   (NOT landed). Root 1 MOVED (4573) / 0 GONE / 0 APPEARED; pyref 0/0/0; mirror 53/53 0/0/0 (no OWED). Residuals: `\length` /

##   non-int-field invariants (59+11 classes; NEW registered carrier `route226-carrier-length-invariant-over-list-param.py`),

##   computed stores (increment 3), `field(init=False)` without default reads a fabricated 0 (see REPAIR).

## gen #37 (2026-10-25): #369 (dataclass specifier aliases), #370 (enum non-member bodies as members), #371 (hashability: first base only),
##   #372 (hashed element class from fields/subscripts), #373 (nested def in a method = opaque int), #374 (slots names unmangled), #375 (erased

##   augassign / star-unpack), #376 (getattr default vs class attribute) OPENED (red team 28: 67/360 confirmed; 8/8 sample driver-reproduced

##   rc=0 on 863a844aa). d08 = route #226 carrier (already recorded, r226 executor).

## gen #37 (2026-10-25): #364 + #365 + #366 + #367 REPAIRED, candidate (r364 executor off fcc2c822; code e78477a2 + 396b6ebb, corpus +
##   docs ece5f63b (annotations 7.33 / T.6.44), census 694d2e7c, route docs; inline in the #346-#349 and #339/#352 blocks of

##   `_run_pipeline`, no new def, ledger 3, no new refusal code). Sound refusals, no emission change. #364: every class-scope binding

##   (any statement / target / nesting) of `__eq__` defines it; a `__hash__` bound other than by top-level undecorated defs may be

##   None -> unhashable. #365: hashing positions decompose tuple displays (any depth, `:=`, if-expressions), tuple-bound locals and

##   `Tuple[...]` annotation arguments; a list / dict / set inside a hashed tuple is unhashable; annotation subtrees hash nothing.

##   #366: unhashability is a least fixpoint over all classes + functional namedtuples; field-hashed records (NamedTuple, frozen /

##   unsafe_hash dataclass) need every field provably hashable (int/str/float/bool/bytes/complex/None/Literal/frozenset/type, a

##   hashable file class, Optional/Union/Tuple of those; object / Any / unknown / other containers are not). #367: enum members as

##   `_EnumDict` builds them (drop `_ignore_` names, private `__x`, dunder / sunder, value-less annotations, descriptors,

##   `nonmember(..)`; `member(v)` counts); a non-literal `_ignore_` refused; enum dunders read from every class-scope binding.

##   Witnesses 4900-4933 (19 red-team + 15 new shapes, incl. NEW latents `{(xs, 1)}` with a list and enum `__eq__` under `if` /

##   in a tuple target; 30 PROVED at base, 29 of them CPython-violating) -> REFUSED; controls 4940-4943 PROVED (4943 was an over-refusal at base). Root 0/0/0

##   (4 new controls), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED). Residuals: `__hash__ = object.__hash__` over-refused, container-

##   element tuples, `field(hash=False)`, tuple-target enum members (see REPAIRs).

## gen #37 (2026-10-25): #360 + #361 + #362 + #363 REPAIRED, candidate (r360 executor off fcc2c822; code 6550de83, corpus eae6a9d8 +
##   dea007f9, census 69d1e9f2, docs 5be7bed4 (annotations 7.32 / T.6.43), route docs; inline in the #346-#349 `_run_pipeline` block,

##   no new def, ledger 3). Sound refusals + a sharper #347 summary, no emission change. #360 PYCSL-R360-SLOTS-STORE: a store (any

##   form, `setattr`) on a receiver whose class is FULLY SLOTTED (every C3-MRO class a file class with a literal `__slots__` /

##   `@dataclass(slots=True)`, or object / Generic / Protocol; no `__dict__` slot) of a name outside the slot union, and any

##   non-literal `__slots__`, refused. #361 PYCSL-R361-DATACLASS-PSEUDO-FIELD: InitVar / KW_ONLY (bare, dotted, string) leave #347's

##   field sets; any access of a pseudo-field name in a verified function refused (a defaulted InitVar reads the CLASS default).

##   #362 PYCSL-R362-INITVAR-INVARIANT: an invariant record whose dataclass closure declares a pseudo-field refused (route #226's goal

##   is dropped outside int fields / int-bool params). #363: #347 resolves `super(X, self)` through the C3 MRO (the class after X);

##   any other shape credits nothing. Witnesses 4850-4869 (18 PROVED at base, 2 FAILED) -> REFUSED; controls 4880-4886 PROVED.

##   Root 0/0/0 (7 new controls), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED); fast planes 61/61. NEW SUSPECTED (route #226 debt, not

##   repaired): an invariant class with a str / list field (dataclass or explicit `__init__`) gets no goal -> invariant assumed,

##   PROVED at base and after (q362str / q362list / q362xinit; 96 corpus classes out of that scope). Residuals: see REPAIRs.

## gen #37 (2026-10-25): #357 + #358 + #359 REPAIRED, candidate (r357 executor off 1a9cfa42; code 0bd03380 / fb898973 / 66f2f2ea /
##   acec0e22 / af97b85a, corpus + docs 570c626f (annotations 7.31 / T.6.42), census 66f2dd33 + route docs; inline, no new def,

##   ledger 3). #357: a `self.`-resolved method result annotated with a field-less class (string annotations too), every

##   `UnknownPyExpr` (`type(self)()`) and `e.__class__()` join route #249's erased set; `type(e)(..)` / `e.__class__(..)` is

##   REFUSED (NEW PYCSL-R357-DYNAMIC-CONSTRUCTOR) under any `no_exception` or with a non-literal argument (NEW latent: the dynamic

##   `__init__` mutating its argument PROVED). #358: under `no_exception` a failing `PyCSL-R358` assertion precedes iteration,

##   truth tests, attribute loads not known on the erased base (`dir(object)` + the declared file class's methods / self

##   stores) and str/list/dict/set/tuple methods handed an erased value. #359: R5's MRO walk counts every class-body binding;

##   a pair-independent pass refuses a non-`def` binding or an outside-file class (builtin classes by `__dict__`) before the

##   file definer. Witnesses 4800-4827 (27 PROVED at base, 5 new latent) -> FAIL/REFUSED; controls 4830-4832 PROVED. Root

##   0 MOVED / 2 GONE (1313, 1457: expected-FAIL files now REFUSED by these rules, census re-measured) / 0 APPEARED; pyref

##   0/0/0; mirror 53/53 0/0/0 (no OWED). Residuals: erased type still `int`, class-body constants of field-less classes not

##   known (FAIL), outside-file BASE classes still uncompared, dynamic constructors' global effects (see REPAIRs).

## gen #37 (2026-10-25): #360 (`__slots__` not modelled), #361 (InitVar / KW_ONLY counted as fields), #362 (InitVar drops the invariant
##   goal), #363 (`super(X, self)` misresolved), #364 (hash scan too narrow), #365 (unhashable inside a tuple), #366 (record field hashability),

##   #367 (enum `_ignore_` / private names as members) OPENED (red team 27: 31/~200 confirmed; 8/8 sample driver-reproduced rc=0 on ccdb07e6).

## gen #37 (2026-10-25): #352 + #353 + #354 + #355 + #356 REPAIRED, candidate (r352 executor off 1a9cfa42; code 46558356, corpus +
##   census 0855e796, docs 9a2cbb48 (annotations 7.30 / T.6.41), route docs; route #339's classifier rewritten in its inline

##   `_run_pipeline` block, no new def, ledger 3, no new refusal code). Sound refusals (PYCSL-SEM-ENUM-MEMBER-OPERATION), no emission

##   change. #352: bases resolved through imports / module aliases (`from enum import X as Y`, `import enum as e`); an attribute

##   tail enum of non-`enum` origin is opaque; a class over an unclassifiable import with a member-shaped body is a possible enum,

##   opaque with every dunder assumed. #353: dunders over every file class of the MRO; int-like only if the MRO is IntEnum / int /

##   Enum / ReprEnum / object / file enums; `hash` refused under any `__eq__`. #354: IntFlag / Flag (and `int`+Flag) opaque; a class

##   keyword makes an enum opaque. #355: `C(v)` admitted only for a same-type literal member value or a member. #356: `C.X` that is

##   neither a member nor bound in an MRO class body (`__members__`, `_value2member_map_`, ..) and stores through `C.X` refused.

##   Witnesses 4750-4766 (13 red-team + 4 new shapes incl. 1 new latent `class F(int, Flag)`; all PROVED at base) -> REFUSED;

##   controls 4770-4774 PROVED. Census: 0 non-witness users in any plane; mirror `_Precedence(_enum.IntEnum)` stays transparent.

##   Root 0/0/0 (5 new controls), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED). Residuals: possible-enum `C(v)`, class object via

##   `type(x)` / aliases, over-refusals (dunder-free mixins, IntFlag int ops, `C(v)` outside `no_exception`) (see REPAIRs).

## gen #37 (2026-10-25): #350 + #351 REPAIRED, candidate (r350 executor off 5c3b3413; code 2bfdb686 / b67bbe0f, corpus 24945d20,
##   census c40dd1dd, docs 656526be + route docs; two inline `_run_pipeline` blocks over a fresh source parse, no new def, ledger 3).

##   Sound refusals, no emission change. #350 PYCSL-SEM-DEFAULT-ANNOTATION-MISMATCH: every annotated parameter default of a lowered

##   def (function / method / nested; positional, positional-only, kw-only) must be admitted by one arm of its annotation (aliases,

##   Optional/Union/|, Annotated, string refs): `None` only for a None arm / Any / object / TypeVar, int <- int/bool, float <-

##   int/float/bool, str <- str, Literal <- a member, containers <- a display of their kind (elements checked), other heads <- a

##   non-literal; bare names resolve to once-bound module constants / same-annotated outer parameters; other non-literal scalar

##   defaults refused. 0698 (`sep: str = None` filled `""`) now refused; live + mirror `expect_name` default `None` -> `""`.

##   #351 PYCSL-SEM-READONLY-VIEW-ESCAPE: a Sequence / Mapping / tuple[T, ...] parameter, or an alias of one, may not be returned

##   under a non-view return annotation, stored into a field / subscript / mutably-annotated local, passed to a non-read-only call,

##   or stored into through an alias. Witnesses 4710-4720, 4722-4728 (12 PROVED at base) -> REFUSED; controls 4721/4729 PROVED.

##   Root 0 MOVED / 1 GONE (0698) / 0 APPEARED, pyref 0/0/0, mirror 1 MOVED (Module2_Parser, whole-file PROVED; no OWED); fast

##   planes 61/61. Residuals: \trusted defaults, dataclass field defaults, syntactic view names, over-refusals (see REPAIR).

## gen #37 (2026-10-25): #352 (enum base import alias), #353 (mixin dunders unseen by #339), #354 (IntFlag not int), #355 (`C(v)` no ValueError),
##   #356 (`__members__` members keep int laws), #357 (field-less values beyond self/params not erased), #358 (protocol ops on erased values

##   unchecked), #359 (R5 MRO walk: non-def bindings, imported MRO classes) OPENED (red team 26: 35/138 confirmed; 9/9 sample driver-reproduced

##   rc=0 on 3d937bdb, CPython violates).

## gen #37 (2026-10-25): #346 + #347 + #348 + #349 REPAIRED, candidate (r346 executor off b83a217b; code 2054301b, corpus + docs
##   ff6941ee (annotations 7.28 / T.6.39), census 44f8d480, route docs; one inline `_run_pipeline` block after #341/#342's, no new

##   def, ledger 3). Sound refusals, no emission change. #346 PYCSL-R346-POST-INIT-INVARIANT: an invariant-carrying record whose base

##   closure holds a `@dataclass` and a `__post_init__` (route #150's opacity dropped route #226's goal). #347

##   PYCSL-R347-FIELD-MAYBE-UNASSIGNED: definite assignment over each constructor (if/loop/try/with/early return/raise/super chain,

##   dataclass `field(init=False)`); a maybe-absent field read under an AttributeError-covering `no_exception`. #348

##   PYCSL-R348-IMMUTABLE-RECORD-STORE: attribute store / augmented / del / setattr / delattr on NamedTuple, namedtuple, frozen

##   dataclass (and subclasses). #349 PYCSL-R349-UNHASHABLE-RECORD: Python's hashability rule per class; an unhashable record as a

##   set element / dict key / subscript / `hash` / membership / set-method argument, or in a `Set[U]` / `Dict[U, ..]` annotation.

##   Witnesses 4660-4685 (8 red-team + 18 new shapes; 17 PROVED at base, 9 new latent) -> REFUSED; controls 4686-4696 PROVED. Census

##   screen 1286 class-bearing files: 0 hits. Root 0/0/0 (11 new controls), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED proof).

##   Residuals: ambient callees (#347), by-name receiver fallback, per-file analysis, underivable element classes (see REPAIRs).

## gen #37 (2026-10-24): #343 + #344 + #345 REPAIRED, candidate (r343 executor off b83a217b; code 9b8ee8b8 / e8f0cc77, corpus
##   3aa9c2b2, docs e1ea6c14 (annotations 7.27 / T.6.38) + route docs; inline, no new def, ledger 3, no new refusal code).

##   #343: a non-record class's method receiver `self` joins route #249's erased set (alias / walrus / element / builtin

##   propagation, laws off, route #252 flow refusal), its WhyML type stays `type c = int` (mirror unchanged; `self.f`,

##   `getattr(self, ..)`, `self.m()` are not uses of it); NEW latent closed with it: a dunder-dispatching builtin (`range`,

##   `abs`, `len`, `max`, ...) on an erased argument under `no_exception` gets a failing `PyCSL-R343` assertion (`range(x)`,

##   `x: Any` PROVED). #344: R5 resolves an inherited method through the C3 MRO. #345: an attribute base whose tail names a

##   file class is REFUSED (PYCSL-R341-CLASS-BASE-NOT-A-NAME) unless a self-import. Witnesses 4610-4625 (16 PROVED at base)

##   -> FAIL/REFUSED; controls 4630-4634 PROVED. Root 0/0/0, pyref 0/0/0, mirror 53/53 0/0/0 (no OWED). Residuals: alias

##   type kept, attribute-protocol builtins, imported MRO classes skipped, package self-import over-refused (see REPAIR).

## gen #37 (2026-10-24): #339 + #340 REPAIRED, candidate (r339 executor off 5e517ffc; code 148ebcaa / d336bd01, corpus adea2535, docs
##   0b3e2c03, census 9b14185e + route docs; inline `_run_pipeline` blocks, no new def, ledger 3). Sound refusals, no emission change.

##   #339 PYCSL-SEM-ENUM-MEMBER-OPERATION: a member of an OPAQUE enum (plain Enum/Flag/StrEnum, or any enum defining a dunder) may

##   only be bound, compared by `is` (`==`/`in`/`match` unless `__eq__`/`__ne__` is user-defined), truth-tested, read as

##   `.value`/`.name`, or passed/returned where annotated with the enum; arithmetic / ordering / index / builtins / int params

##   refused; a dunder-free IntEnum/IntFlag keeps int semantics. #340: a nested def/lambda bare-name default is admitted only when

##   the name is never rebound in the enclosing function nor global/nonlocal (PYCSL-SEM-DEF-TIME-EVALUATION). Witnesses 4590-4598,

##   4602-4605 + 1 new latent 4599 (enum into an `int` parameter) PROVED at base -> REFUSED; controls 4600/4601/4606 PROVED. Root

##   0/0/0, pyref 0/0/0, mirror 53/53 0/0/0 (no OWED); fast planes 61/61, stdlib-modules-verify OK. Residuals: contract-side enum arithmetic, untracked

##   enum flows, per-file enum resolution, over-refusals (see REPAIR).

## gen #37 (2026-10-24): #343 (field-less receiver aliases still int past R337), #344 (MRO-inherited override escapes R5), #345 (foreign
##   attribute base tail-resolved to a file class), #346 (`__post_init__` never verified), #347 (partial-init field assumed present), #348

##   (NamedTuple / namedtuple / frozen dataclass lowered mutable), #349 (unhashable record set element), #350 (default contradicts annotation),

##   #351 (read-only view escapes by return) OPENED (red team 25: 28/125 confirmed; 12/12 sample driver-reproduced rc=0, CPython violates).

## gen #37 (2026-10-24): #336 + #337 REPAIRED, candidate (r336b finishing executor off ebd6f814; r336 draft committed as found b48c7f0b,
##   code 49ff7298 / 28681a0d / a84af1ca / 834f9df4 / bba6e1b4 / 3a2ba7bc / 5a4e958c, corpus 4d5afb39, docs 45cac885 (annotations 7.23 / T.6.34),

##   census 231438aa; inline, no new def, ledger 3). Module 5 resolves module aliases (TypeAlias / type / TypeAliasType / plain),

##   Annotated, Sequence/tuple[T, ...] -> List, Mapping -> Dict, Literal[None] -> None before any type reader (emission byte-identical

##   to the direct spelling); a store / mutating call / non-builtin call on a read-only view param is REFUSED

##   (PYCSL-R336-READONLY-VIEW-STORE); Module 6 erases (route #249) any param / return tag outside the lowered set (Fraction, Decimal,

##   Real, SupportsFloat, type, None, Iterable/Collection/Deque, imported and FIELD-LESS classes); unmodelled element/key/value types

##   erased; a non-record class union arm erases the annotation; operators on `self` REFUSED (PYCSL-R337-SELF-OPERATOR). Witnesses

##   4480-4520, 4524, 4527: 40 base false proofs -> FAIL/REFUSED (3 view stores REFUSED at base too); controls 4521-4523, 4525, 4526,

##   4528, 4529 PROVED (6 FAILED at base). Root 9 MOVED (0892, 0962-0965, 1312, 2585, 2592, 3107 [edited `-> object`]) / 0 GONE /

##   0 APPEARED, all re-proved to labels; pyref 0/0/0; mirror 2 MOVED (crosscheck_ir, sertop: unused union decls) / 0 GONE, both

##   whole-file PROVED (no OWED). Residuals: function-local/class/imported aliases (erased, not resolved), Why3 type errors for

##   float `%` (pre-existing), syntactic view/self checks (no alias following), bare Sequence/Iterable/Mapping now erased.

## gen #37 (2026-10-24): #341 + #342 REPAIRED, candidate (r341 executor off 8984dce3; code 88a8a4c7 / 7be6e53a, corpus 0904473f /
##   ec7df9fe, census 41dddc52 / 768c1725, docs 83deebdc + route docs; one inline `_run_pipeline` block, no new def, ledger 3). Sound

##   refusals, no emission change. #341 PYCSL-R341-CLASS-BASE-NOT-A-NAME: a base that is not a class name (alias / annotated /

##   tuple-unpacked name, call, conditional, non-imported attribute, non-`Generic` subscript) — aliases refused rather than resolved

##   (~20 readers of `ClassDef.bases`, 0 users measured). #342 PYCSL-R342-CONSTRUCTOR-STORE-FORM: in the constructor of an

##   invariant-carrying class (or a class on its base closure) an invariant field stored other than by a top-level `self.f = e`, a

##   bare `self` (alias / argument), `self.m()`, a non-leading `super()`, a `return`; PYCSL-R342-CLASS-REASSIGNMENT (`__class__`

##   stores); PYCSL-R342-EXTERNAL-INVARIANT-STORE (NEW latent: module-level / `__main__` stores of invariant fields). Witnesses

##   4550-4571 + 3 new latent 4577-4579 (25 PROVED at base) -> REFUSED; controls 4572-4576 PROVED. Root 0/0/0, pyref 0/0/0, mirror

##   53/53 0/0/0 (no OWED); fast planes 61/61. Residuals: #226's computed straight-line store, per-file check, over-refusals (see REPAIR).

## gen #37 (2026-10-24): #339 (Enum members as ints), #340 (nested def bare-name default evaluated at call time), #341 (computed/aliased
##   class base drops inheritance), #342 (constructor-invariant goal reads only plain self.f stores; __class__ reassignment) OPENED

##   (red team 24; 10/10 sample driver-reproduced rc=0, CPython violates).

## gen #37 (2026-10-24): #338 REPAIRED, candidate (r338 executor off d175a70d; code e8c3d3e5 / 5d96d6e1 / ef4c3d57, corpus f8c6d9aa /
##   355942e6, census 88901d08, docs 2e529ccc + route docs; inline in `_run_pipeline`, no new def, ledger 3). (a) Override rule R5: an

##   override's return annotation must be a subtype of the base's and each base parameter annotation a subtype of the override's

##   (`bool` <: `int`, class <: ancestor, Union/Optional members, Any/object; `int` not <: `float`; absent = Any) — refused

##   PYCSL-SEM-OVERRIDE-REFINEMENT, off under `--assume-class-exact`. (b) #334's store census adds stores from ANY code (module level,

##   `__main__`, functions, other classes; `setattr` / `delattr` / `del` / `+=` / dict-value / `__dict__`), by receiver class when

##   typed, else to every class storing that field. (c) An unannotated-parameter initialiser is unknown when unverified module code

##   names the def / class (blunt version measured: mirror Module1_Ingestor GONE). Witnesses 4530-4540 (9 PROVED, 2 FAILED at base)

##   -> REFUSED; controls 4541-4544 PROVED. Root 0/0/0, pyref 0/0/0, mirror 53/53 0/0/0 (no OWED proof); fast planes 61/61. Residuals:

##   per-file census, imported-base overrides not compared, int-label only (see REPAIR).

## gen #37 (2026-10-24): #335 REPAIRED, candidate (r335 executor off 87b4eca6; commits abff40d6, 56aa4b8b, 2969cbf4 + route docs;
##   inline at the end of `apply_inheritance.merge_one` + a Module 5 side channel `nonrecord335`, no new def, ledger 3). Sound

##   refusal PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION: Python's constructor chain over the C3 MRO (walk through classes without

##   `__init__`, continue past one only via a leading `super().__init__(...)`) must store every inherited invariant field with the

##   merged literal, and no MRO class may define a method/property/non-constant binding of that name. Witnesses 4460-4468

##   (i33/i35/i36/i37/i38 + 4 new latent shapes p1-p4) PROVED -> REFUSED; controls 4469-4476 PROVED. Root 0/0/0, pyref 0/0/0,

##   mirror 1 MOVED (`raises` on `apply_inheritance`, frontend__ir_resolve PROVED rc=0, no OWED). Latent: corpus 0448 never ran its

##   imported base's `__init__` (invariant on unset `_depth`) — fixed in the corpus by `super().__init__()`, emission identical.

##   Residuals: over-refusal of `B.__init__(self)` / non-leading super; imported fieldless MRO classes end the chain.

## gen #37 (2026-10-24): #336 (unrecognised parameter/element annotations default to int: TypeAlias/Annotated/Fraction/Decimal/Real/
##   SupportsFloat/str-None aliases; parameterised containers drop element types), #337 (fieldless user class = int), #338 (override return

##   types not compared; external field stores not counted by #334) OPENED (red team 23; 5/5 combined files reproduced rc=0).

## gen #37 (2026-10-24): #334 REPAIRED, candidate (r334b finishing executor off 1b425056; r334 draft committed as found 43740172,
##   code 24b9295f / 7e75582d / 9bbf1701, census 41ac87f2, docs 054a4330 + route docs; inline in #325's block, no new def, ledger 3).

##   A field label is int only when EVERY value stored into it (class, bases, SUBCLASSES; tuple / starred / for / setattr / += / dict

##   value stores) is PROVABLY int by a type walk (locals, walrus, `**` by a non-negative literal, `-> int` callees ...); a value of

##   unknown type is carried only under an `int` field annotation (annotation trust, needed by 2 mirror files); an integral float is

##   int-modelled only as a direct comparison operand; dict-field values classified the same; bare `dict` params join the declared

##   BARE-CONTAINER-INT (+ strict flag; default-origin measured 3 root + 1 mirror GONE). Witnesses 4420-4439 (12 red-team, 7 scratch,

##   driver i01 = 4439) PROVED -> REFUSED; controls 4440-4442/4444/4445 + 1490 PROVED; 4443 assumption counterexample. Root 0 MOVED /

##   1 GONE (2132 `p.k + p.m`, a true claim, declared over-refusal, now FAIL-expected) / 0 APPEARED; pyref 0/0/0; mirror 53/53 0/0/0

##   (no OWED proof). Residuals: annotation trust, list-field elements, tuple-target record emitter gap (fail-closed), see REPAIR.

## gen #37 (2026-10-24): #335 (inherited class invariant assumes the base constructor's field values for subclasses that never ran it:
##   no super().__init__, class-attr/property shadowing, MRO) OPENED (red team 22; 4/4 sample reproduced). Red team 22 regression replay:

##   all 242 witnesses of #300-#333 still closed on main (j02 = documented #304 residual).

## gen #37 (2026-10-24): #333 REPAIRED, candidate (r333 executor off 0c2d49cc; commits 432e5fff, 0e8af983, 2448673c (code + corpus)
##   + census + route docs; inline in #327's `_run_pipeline` block, no new def, ledger 3). Refusal measured against a rename

##   (586 root / 12 pyref / 37 mirror re-emit): PYCSL-R327-IDENT-COLLISION now also refuses (a) a user exception class whose

##   underscore-stripped tag equals another source class, an imported name or a builtin exception (raises-tag spelling of the

##   own `_Y` and import aliases kept; exact builtin spelling stays #305's) and (b) a USER-SPELLED name in the censused

##   generated-binder namespace `_rsv333` (`_idx_*`, `_len_idx_*`, `_any_*`, `_tu_*`, `_pycsl_*`, `_inl_*`, ... see REPAIR).

##   Witnesses 4400-4403 PROVED -> REFUSED; controls 4404-4406 PROVED. Root 0/0/0, pyref 0/0/0, mirror 53/53 0/0/0 (no OWED

##   proof). Residuals: imported-module exception classes, census completeness, single-letter quantifier binders (probed FAIL).

## gen #37 (2026-10-24): #333 (#327 residuals: safe_exc_name merges user exceptions incl. with builtins; generated _idx_* etc shadow user names)
##   and #334 (#330/#331 field-origin gaps: locals/walrus/neg-pow initialisers, tuple-target __init__, integral floats, unknown dict values)

##   OPENED (red team 21; 12/12 sample driver-reproduced rc=0 on main).

## gen #37 (2026-10-24): #328, #330, #331 REPAIRED, candidate (r328 executor off aa1cf01c; commits 0edf93ea (code), 34f71ba4
##   (corpus/census/docs) + route docs; inline in #325's `_run_pipeline` check, no new def, ledger 3). #328: origins = every

##   module/class-level binding form at any nesting; tuple-pattern taint (component-precise); arm / for binders scoped

##   precisely; Map keys, writes-items, `Return_<ty>` admitted. #330: non-int instance fields (shown float/str/None/...

##   initialiser or annotation over an int label; integral float literals still carried), string-encoding model ops

##   (`repr_conv`, `str_of_int_hash`, ...; `==` kept), `complex` annotations refused; bare-container elements DECLARED as

##   BARE-CONTAINER-INT (90 corpus files rely on it) with `--strict-bare-containers`. #331: None/Optional fields refused

##   in arithmetic/ordering (`==` kept). Witnesses 4330-4353 PROVED -> REFUSED; controls 4354-4362 + assumption

##   counterexamples 4363-4364 PROVED. Root 0 MOVED / 8 GONE (1480, 1483-1485, 1851, 2112, 2113, 2392: expected-FAIL,

##   FAIL -> REFUSED), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED proof). Residuals: unannotated-parameter field

##   initialisers, integral-float fields, bare containers (declared), element-of-field containers.

## gen #37 (2026-10-24): #327 + #329 REPAIRED, candidate (r327 executor off aa1cf01c; commits 329d3a10, 2a1e8474 (code), edf5b05e
##   (corpus, census, docs) + route docs; inline, no new def/raise-site class, ledger 3; mirror twins `\trusted`). #327: an injective

##   encoding was measured out (~1962 root / ~48 pyref / ~48 mirror files re-emit); instead `_run_pipeline` refuses

##   PYCSL-R327-IDENT-COLLISION when two distinct names map to one `whyml_ident` in a scope (per function: params + Var reads incl.

##   globals + binding targets of body and contracts + `_tu_*`; module level: functions + module-level value bindings; classes

##   folding by `.lower()`); `c = C()` and the class operand of `isinstance` are not values. #329: the #42/#52 `is` refusals were

##   keyed on a wire dict and skipped every NESTED `is` (an `OpaqueExpr` under `not`, an if-expression test, `and`/`or`, filters);

##   they now read the opaque node's raw dict. Witnesses 4300-4306, 4315-4320, 4322, 4323 PROVED -> REFUSED; 4307/4308 FAIL ->

##   REFUSED; 4311 REFUSED(#325) -> REFUSED(#327); controls 4309, 4310, 4326, 4327 PROVED. Root 0 MOVED / 0 GONE (4260 refusal

##   message R325 -> R327, census row updated), pyref 0/0/0, mirror 53/53 0/0/0 (no OWED proof). Residuals: field-name folds

##   (Why3 rejects: fail-closed), `safe_exc_name` `_E`/`E`, erased `assert` under `no_exception \all` (new suspicion).

## gen #37 (2026-10-24): #332 (assert erased even under no_exception \all; CPython raises AssertionError) OPENED (r327 executor finding); driver-reproduced.
## gen #37 (2026-10-24): #332 REPAIRED, candidate (r332 executor off e9a499e6; commits bd0dc43e, 4ad3c60e, df884823 + route docs; inline in
##   `_stmts_to_whyml` (AssertStmt arm) + one local in `_reset_function_state`, no new def/field, ledger 3; mirror twins `\trusted`).

##   Under `no_exception \all` (or a named set holding AssertionError/Exception/BaseException — refused by Module 4 today) `assert c` lowers to

##   `if <c> then () else assert { [@expl:no_exception: AssertionError reachable] false }` (the if-test lowering: own triggers + truthiness;

##   message never evaluated on the proved branch); the #36/#301/#302 loop-target analyses count reads inside such an assert. Erasure

##   elsewhere byte-identical. Witness a01 + corpus 4380-4388 PROVED -> FAIL; controls 4389-4395 PROVED; 4396 REFUSED both. Population of

##   asserts under `\all` in root/pyref/mirror: 0 -> byte-diff 0/0/0 on all three planes, nothing OWED. Fast planes 61/61; all listed gates rc=0.

##   Residual: an assert over a havocked `for` target after its loop no longer proves under `\all` (sound, incomplete).

## gen #37 (2026-10-24): #326 REPAIRED, candidate (r326 executor off 0da66911; commits 61c98f12, d89ee890, 38757ff2, dfc5305d,
##   59b17e74, 7fb6adc8 + route docs; inline in `_resolve_module_path` / `resolve_imports`, no new def/field, ledger 3; mirror twins `\trusted`,

##   the `_resolve_module_path` stub now declares `raises`). Package before module in every root; a local file shadowing a

##   stdlib/built-in module name REFUSED (PYCSL-SEM-IMPORT-SHADOWS-STDLIB) unless byte-identical to the interpreter's own source

##   (the repo-root `json/` = CPython's Lib/json, 47 importers, admitted); `sys.path`/`sys.modules`/`meta_path`/`path_hooks`/

##   `path_importer_cache` references (any alias, `from sys import`, `sys` as a value; pure reads and the idempotent script-dir insert

##   exempt), dynamic-import machinery beside a local resolution, and a resolved dependency's top-level edits REFUSED

##   (PYCSL-SEM-IMPORT-STATE-MANIPULATED). Route witnesses sh01-sh04/k06 PROVED -> REFUSED, k04/k05 -> FAIL; corpus 4280-4283,

##   4287-4292 PROVED -> REFUSED, 4284/4285 -> FAIL; controls 4286 (FAIL -> PROVED), 4293-4295 PROVED. Root/pyref byte-diff 0/0/0;

##   mirror 1 MOVED (stub `raises` line; L3-tc ok, whole-file proof rc=0); sync/mirror-check/doc-coherency/assumed-facts/raises rc=0;

##   refusal-coverage rc=1 at base AND after (same 6 pre-existing sites; both new sites demonstrated); fast planes 60/61 (only that one); stdlib-modules-verify rc=0.

##   Residuals: dep-of-dep edits only under --deep; edits reached without `sys`/importlib names; cwd stays a search root.

## gen #37 (2026-10-24): #327-#331 OPENED (red team 20; 36 witnesses, 12/12 sample driver-reproduced rc=0): #327 identifier collisions
##   (whyml_ident case-fold/reserved prefix, N vs n, K vs k); #328 #325 taint bypasses (non-simple module bindings, tuple unpack,

##   generated binders R/V_); #329 is-refusals skipped in if-expression tests / under not; #330 fields/model-op results/bare+complex

##   annotations typed int; #331 no_exception over None/str field arithmetic.

## gen #37 (2026-10-24): #325 REPAIRED, candidate (r325 executor off 0da66911; commits f727109a, 4890e1d3, 6562aec2, 06382014,
##   da90b338 + route docs; inline in `_run_pipeline` on the EMITTED WhyML (mirror twin `\trusted`), no new def, ledger 3).

##   An opaque-int fallback standing for a module-level value (global, import / module alias, class, class-level attribute,

##   `getattr`, imported/builtin call) and everything derived from it (locals, getters, subscripts, containers, returns,

##   user-function parameters, receiver-dropped method stubs) may only be bound / passed / returned / discarded / compared

##   `==` against a different value; any int use is REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK); known-int values exempt.

##   Subsumes #322's bypasses (#322 kept as first layer). Witnesses 4230-4251, 4253-4263 PROVED -> REFUSED (13 of them new

##   shapes: alias chain, param flow, list store, nan, lambda case-fold, method return, abs, receiver), 4252 FAIL -> REFUSED;

##   controls 4264-4271 PROVED. Root 0 MOVED / 5 GONE (1066, 2702, 2706, 3432, 3433: expected-FAIL, FAIL -> REFUSED), pyref

##   0/0/0, mirror 53/53 0/0/0 (no OWED proof). Fast planes 61/61, getattr-erasure + stdlib-modules-verify, sync/mirror-check/

##   doc-coherency/assumed-facts/raises/refusal-coverage rc=0 (census +#322's owed rows). Residuals: attributes / subscripts /

##   method results over PARAMETERS, locals and instance attributes; int-encoded string/collection model ops; user-module int

##   attributes over-refused.

## gen #37 (2026-10-24): #325 (every unmodelled value falls back to an opaque int: int laws proved of floats/strings/lists; subsumes #322's
##   bypasses) and #326 (module resolution differs from CPython: stdlib shadowing, package vs module, sys.path) OPENED (red team 19);

##   10/10 sample driver-reproduced rc=0, CPython violates.

## gen #37 (2026-10-24): #322 + #324 REPAIRED, candidate (r322 executor off 67edf13c, finished by r322b; commits 6899062d, d9a53ce5,
##   2c457d4e + route docs; inline, no new def/field, ledger 3; #324 mirror twin verbatim). #322: abs()/sum()/known-element/dict/

##   NamedTuple/`__init__`/dataclass folds take INT literals only (9 `int()`-over-float sites censused); float constants of math/cmath

##   and sys.float_info REFUSED (PYCSL-R322-FLOAT-MODULE-CONSTANT; also via `from math import *` and `getattr(math, ...)`, two

##   bypasses found by r322b). #324: contract-side `s[a:b]` normalises any bound that is not a non-negative literal / omitted /

##   bare `len()` as CPython does. Witnesses 4190-4193 PROVED -> FAIL (L3-tc), 4194-4199 -> REFUSED, 4200-4202 -> FAIL; controls

##   4203-4207, 4209-4211 PROVED (4208 emission-identical, proof OWED). Root sweep 1-1000 0 MOVED (0767 identical); sync/mirror-check/

##   doc-coherency/raises rc=0. OWED (heavy queue saturated): root 1001-2991 + pyref byte-diff, mirror-emit-sweep (+ expressions mirror

##   whole-file proof), fast planes 61, assumed-facts, census rows 4190-4202.

## gen #37 (2026-10-23): #321 + #323 REPAIRED (r321 executor, off 67edf13c; inline in the seeded-map arm of `_call_named_builtins`,
##   `_iter_len_expr` and `_reset_function_state` (mirror twins `\trusted`; the two expression stubs now declare `#@ raises

##   PyCSLIRError`); no new def/field (scan result rides on `_r249_scope["r321_dd"]`); ledger 3). #321: Counter/OrderedDict/

##   defaultdict refuse keyword/starred/over-arity args and NON-LITERAL seeds (literal IR repr = value; Counter seeds keyed apart);

##   defaultdict factory only `int` / `lambda: 0`; a defaultdict local is admitted only when its key set is unobservable or every

##   read is fused into a same-key store (CPython's read inserts), else refused. #323: the itertools length model resolves the

##   callee through the import table (user/shadowed names fall through to the user's function; `chain as ch` now resolves);

##   keyword/starred operands refused. Witnesses 4150-4169, 4175 (15 PROVED -> REFUSED [4150-4160, 4163, 4164, 4167, 4168],

##   4 PROVED -> FAIL [4162, 4165, 4166, 4169], 2 FAIL -> REFUSED [4161, 4175]); controls 4170-4174 PASS. Root 1 MOVED (1076:

##   constant renamed by the Counter tag, FAIL -> FAIL), pyref 0/0/0; mirror 2 MOVED (`raises` clauses only, L3-tc OK, whole-file

##   proofs OWED, no call site); fast planes 61/61; sync/mirror-check/doc-coherency/assumed-facts/raises/refusal-coverage rc=0.

##   Residuals: syntactic per-function scan (closures unseen); dotted `collections.X(..)` and module-level defaultdicts not this

##   arm's (L3-tc FAIL today); islice negative stop outside `no_exception`; short-name oracles `_os_path_split_slot` /

##   `_IR_DISPATCHERS` censused, not changed.

## gen #37 (2026-10-23): #321-#324 OPENED (red team 18, stdlib/builtin model; 9/9 sample driver-reproduced rc=0): #321 Counter/
##   OrderedDict/defaultdict model (seed keyed on source text, kw seeds dropped, factory ignored, read does not insert); #322 float literals

##   truncated in abs()/sum() folds, float module constants as ints; #323 itertools length model (kwargs dropped, short-name match,

##   starred arg); #324 contract-side str slice uses raw substring.

## gen #37 (2026-10-23): #316 + #317 REPAIRED (r316 executor, off 6821931b; inline in `transpile` / `_handle_dotted_call` /
##   `_emit_function_block` (mirror twins `\trusted` or absent); no new def/field (result kept on each function IR dict, `func["_r316_frame"]`);

##   no frontend IR change; ledger 3). Every function's parameter WRITE SET is inferred from its body (store roots, in-place

##   mutators, argument mutators, two-level local aliasing, fixpoint over calls; dict/set params and string-keyed stores stay

##   with WL-05/#244) — the effect Why3 infers for a plain `let`. Method call stubs gain `writes { x_i }` per written array

##   position; a `\trusted`/imported `val` with no `assigns` gains `writes { p }` (#317). Refusals: PYCSL-METHOD-FRAME (declared

##   frame omits a written param), PYCSL-METHOD-GLOBAL-WRITE, PYCSL-OVERRIDE-FRAME (override writes a position its base does

##   not), PYCSL-METHOD-ARG-UNFRAMED / PYCSL-VAL-ARG-UNFRAMED (record argument written). Witnesses 4071-4077, 4079-4081 PROVED

##   -> FAIL; 4070, 4078, 4082, 4083, 4085 PROVED -> REFUSED; 4084 FAIL -> REFUSED; controls 4088-4091 PASS. Root 1 MOVED

##   (3195, expected FAIL, `assigns xs[0]` stub gains `writes { x0 }`, FAIL -> FAIL), pyref 0/0/0, mirror 0/0/0 (nothing OWED;

##   no latent false proof); fast planes 61/61 rc=0 (assigns-underdeclaration caught a first-cut `self.ir[..]` store, fixed);

##   sync/mirror-check/doc-coherency/assumed-facts/raises/refusal-coverage rc=0. Residuals: syntactic alias analysis; dict aliasing via elements (WL-05); record args refused not

##   framed; global writes from methods refused even if declared; element-precise `assigns` unchecked (as for plain functions).

## gen #37 (2026-10-23): #318 (range bound re-read every iteration), #319 (list parameter rebound in a nested block is lost after
##   the block; later writes hit the caller), #320 (literal rebind of a local list overwrites the same array in place) OPENED (red team 17);

##   6/6 sample driver-reproduced rc=0, CPython violates.

## gen #37 (2026-10-23): #318 + #319 + #320 REPAIRED (r318 executor, off 8610363c; inline; no new def/field; ledger 3; both new
##   raises in `_handle_assign_stmt` (`\trusted` twin already declares them); no IR change). #318: a `range` stop that the #29

##   hoist did not bind and that is not a literal / `!`-free name / `len` of one is captured once (`let _stop_<idx> = .. in`).

##   #319: a formal parameter whose first binding is nested -> `PYCSL-M6-PARAM-REBIND-NESTED-BLOCK` (a `ref` over an array

##   parameter is ill-typed in Why3, measured). #320: a literal rebind of an array local that may have another holder (value

##   use, non-literal binding, rebind inside a `for` over it) -> `PYCSL-M6-LIST-LITERAL-REBIND-ALIASED`. Witnesses 4110-4114

##   PROVED -> FAIL; 4117-4120, 4122-4124 PROVED -> REFUSED; 4125 FAIL -> REFUSED; controls 4115/4116 FAIL -> PASS,

##   4121/4126/4127 PASS both. Root 1 MOVED (0708, re-proved) / 3 GONE (r300 expected-FAIL 3578/3580/3582 -> REFUSED), pyref

##   0/0/0, mirror 1 MOVED (Module3_Weaver `_desugar_for`, L3-tc rc=0, `_desugar_for` re-proved, whole file OWED); fast planes 61/61. Residuals: `range(a,b,step)` /

##   `enumerate(range)` stay opaque; #320 is coarse (any user-callee argument refuses).

## gen #37 (2026-10-23): #316 (method writes to arguments / module objects invisible to callers: method stubs take writes only
##   from assigns on self; body checked only against a self frame) and #317 (imported function without contract assumed to write

##   nothing) OPENED (red team 16); 6/6 sample driver-reproduced rc=0, CPython violates.

## gen #37 (2026-10-23): #311-#315 OPENED (red team 15; 23 witnesses, 9 driver-reproduced rc=0 on main 65b22999, CPython violates):
##   #311 slice bounds evaluated right-to-left; #312 slice/sorted/list_new operand coerced to (any int) drops its calls;

##   #313 dict/set values lowered to (any_map ()) drop effects (display args, dict-returning calls, field stores);

##   #314 str-method keyword arguments dropped; #315 __init__ bodies never emitted/verified (argument mutations,

##   callee preconditions, explicit __init__ contracts all ignored).

## gen #37 (2026-10-23): #311 + #312 + #313 + #314 REPAIRED (r311 executor, off d4e39ef2; inline; no new def/field; ledger 3;
##   touched functions' mirror twins `\trusted`; no IR change). Route #310's choke point generalised from displays to EVERY

##   effectful operand: a non-display operand is PROBED (not marked: position-dependent lowerings keep their text), and an

##   operand absent from the node's lowering is evaluated first (`let _ = <op> in ..`) or REFUSED (arm / after an unbound

##   operand / re-derived call); operands whose calls are effect-free opaque `val`s / `(any T)` / literal records stay dropped

##   (byte-inert). `for` over any erased effectful iterable is materialised. #311: `SliceAccess` receiver/bounds join #307's

##   left-to-right sequencing. #314: builtin-type method keywords REFUSED in `_reset_function_state` (except `sort`;

##   string-literal `encoding`/`errors` of encode/decode rewritten positionally). Witnesses 3990, 3993-4001, 4003-4008

##   PROVED -> FAIL; 4009-4011 PROVED -> REFUSED; 4012-4014 FAIL -> REFUSED; 3991 near-miss FAIL -> FAIL; controls 4015-4020

##   FAIL -> PASS. Root 1 MOVED (0425, PASS -> PASS, positional decode), pyref 0/0/0, mirror 0/0/0 (nothing OWED);

##   fast planes 61/61 rc=0 (first run 59/61: control 4019 carried empty `gd/gs/gl` placeholders — vacuous-drivers and contract-truth; de-placeholdered). Residuals: sequenced slice then indexed is fail-closed L3-tc; statements ~3285 field-store

##   havoc text-keyed (census: unreachable with an effect); probe that raises out of position gives no verdict.

## gen #37 (2026-10-23): #315 REPAIRED (r315 executor, off d4e39ef2; sound refusal, inline in `_run_pipeline` (`\trusted` twin);
##   no new def/field; no IR change; ledger 3). A class whose constructor (`__init__`/`__post_init__`, else the base's) is not a

##   FIELD INITIALISER (only `self.<f>`/local stores, total-builtin / builtin-exception / `setattr(self)` / `super().__init__` /

##   modelled-ctor calls; no subscript read or store, non-`self` attribute store, in-place augmented store, non-literal

##   division/shift, `while`/`try`/`with`/`assert`/`global`), transitively, may not be constructed in a non-trusted function ->

##   `PYCSL-R315-UNMODELLED-CONSTRUCTOR`. Witnesses 4040-4058, 4063 PROVED -> REFUSED; controls 4059-4062 PASS both. Root 0

##   MOVED / 7 GONE (declared expected-FAIL #150/#154/#235 witnesses, FAIL -> REFUSED), pyref 0/0/0, mirror 0/0/0 (nothing

##   owed); fast planes 61/61. Residuals: undeclared/unresolved bases assumed modelled, `cls()`/alias constructions,

##   `default_factory`, `__init__` `requires` unchecked at the call site (#15), user dunders reached from initialisers.

## gen #37 (2026-10-23): #310 REPAIRED (r310 executor, off 09e2b7c9; inline; no new def/field; ledger 3; mirror twins `\trusted`;
##   no IR change). An erased value is still EVALUATED: an effectful display (route #307's predicate) bound to a tuple/set

##   local -> `(let _ = <display> in (any int))`; one coerced / `len`-folded / dropped inside an expression -> `let _ =

##   <display> in <node>` at its Python position (else REFUSED: a conditional arm); stores, dict-literal values,

##   `for` iterables (materialised), `append` arguments and `raise E(a)` evaluate it; a `raise` with a dropped 2nd/keyword

##   argument, `from` cause or computed exception containing a call -> `PYCSL-SEM-ERASED-EFFECT-R310`. Witnesses 3960-3980

##   PROVED -> FAIL (3970, 3978 REFUSED); controls 3981-3984 PASS both, 3985-3989 FAIL -> PASS. Root 0/0/0, pyref 0/0/0,

##   mirror 0/0/0 (nothing owed); fast planes 61/61. Residuals: unreachable statement-level unsafe hoist, newly fail-closed

##   L3-tc evaluations, `@mutable_state` dict displays, effectful user exception constructors.

## gen #37 (2026-10-23): #308 + #309 REPAIRED (r308 executor, off 35748ef0; inline; no new def; ledger 3). #308: Module 5
##   records (`aug_target_refused`, the #301 pattern) and Module 6 refuses (`PYCSL-SEM-AUGASSIGN-R308`) a `c[k] op= v` /

##   `p.f op= v` whose container/index has an effect, or reads mutable state while `v` has one; census 0 of 81 refused.

##   #309: a non-trivial getattr default is sequenced before the field read (ctor locals via the `c = C()` scan), IS the

##   answer for an absent attribute, REFUSED (`PYCSL-SEM-GETATTR-DEFAULT-R309`) for an unknown receiver / non-literal name;

##   an empty-collection default on an unknown receiver -> the receiver-keyed device (no shared constant). Witnesses

##   3930-3936 / 3940-3946 PROVED -> REFUSED/FAIL (3935/3944/3950 FAIL -> REFUSED); controls 3937-3939, 3947 PASS both,

##   3948/3949 FAIL -> PASS. Root 1 MOVED (2760, FAIL = label), pyref 0/0/0, mirror 3 MOVED (desugar, exec_splice,

##   functions; L3-tc ok; desugar/exec_splice whole-file PROVED, functions OWED); fast 61/61. Residuals: seeded-map constant (L3-tc-closed), `pycsl_nonempty_<name>`, load-vs-v order (#307).

##   functions; L3-tc ok). Residuals: seeded-map constant (L3-tc-closed), `pycsl_nonempty_<name>`, load-vs-v order (#307).

## gen #37 (2026-10-23): #307 REPAIRED (r307 executor, off f48adff0; inline at the `_expr_to_whyml` choke point (`\trusted` twin) + the
##   dict-literal folds (no twin); no new def/field; one new raise site; no IR change; ledger 3). Why3 1.8.2 measured RIGHT-TO-LEFT

##   for application args, infix operands, tuples, raise-vs-write. An n-ary program node whose later operand is effectful (walrus,

##   yield, or a call not known `assigns \nothing`/raise-free) let-binds its earlier non-inert operands left-to-right; container

##   operands stay inline (Python observes them late), effectful ones REFUSED; dict folds bind k0,v0,k1,...; range(start, stop)

##   header and re-derived operands REFUSED. Witnesses 3890-3903, 3907-3912 PROVED -> FAIL; 3904/3905 FAIL -> REFUSED; 3925 REFUSED;

##   controls 3913-3924 PASS (11 were FAIL). Root 18 MOVED (all explained by binder inlining, verdicts unchanged), pyref 0/0/0,

##   mirror 10 MOVED (L3-tc all; errors/struct_format proved; 8 long OWED); fast 61/61. New suspected false proof (not #307):

##   `t = (inc(xs), 0)` drops the call's effect (PROVED; repro in the route file).

## gen #37 (2026-10-23): #310 (a tuple assigned to a name is havocked to `(any ..)`, dropping the effects of calls inside it)
##   OPENED (r307 executor census); witness rc=0, CPython violates.

## gen #37 (2026-10-23): #306 REPAIRED (r306 executor, off 370e1875; inline; no new def/raise; no IR change; ledger 3; mirror twins
##   `\trusted` or absent). A non-atomic `.get` default (not a literal / name / empty collection) is let-bound BEFORE the lookup,

##   a non-atomic key before it (Python order): body/param dict, self-field dict, hval (plain + R5 + K7), module-const str dict

##   chained ITE (key no longer repeated); record/TypedDict `.get` evaluates the dropped default (`let _ = D in t.f`);

##   `max`/`min` `default=` non-atomic REFUSED (route #275 gate). Witnesses 3800-3813 PROVED -> FAIL/REFUSED (3804/3810 FAIL

##   both); controls 3814-3819 PASS, 3817 FAIL -> PASS. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (nothing owed); fast 61/61.

##   Residuals: mirror-only emit_ir `.get` projections drop a (so far always literal) default; walrus-rebinding default.

## gen #37 (2026-10-23): #307 (effectful operands evaluated right-to-left: nested WhyML applications, Why3 evaluates args RTL;
##   binops/calls/compare/walrus/literals/aug-assign) OPENED (red team 14); 20 witnesses, CPython violates.

## gen #37 (2026-10-23): #308 (`c[k] op= v` lowers the index twice) OPENED (red team 14); 5 witnesses.
## gen #37 (2026-10-23): #309 (getattr(o, name, call/collection default) -> shared hashed constant even when the attribute
##   exists: receiver and default effects ignored) OPENED (red team 14); 3 witnesses.

## gen #37 (2026-10-23): #305 REPAIRED (r305 executor, off 370e1875; inline in `_run_pipeline` (`\trusted` mirror twin); no new
##   def; no IR change; ledger 3). Any binding (class at any depth; def/import/store/param/except-as in a module or function

##   scope; main file + #181 dependency modules) of a name in EXCEPTION_BASES ∪ KNOWN_EXCEPTIONS ∪ {EnvironmentError, IOError}

##   is refused (PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED); `from builtins import N` accepted. Witnesses 3780-3784 PROVED ->

##   REFUSED, 3785/3786 FAIL -> REFUSED; controls 3787-3789 PASS both; #304 witnesses unchanged. Root 0/0/0, pyref 0/0/0,

##   mirror 0/0/0 (nothing owed); fast 61/61. Residual: refusal is by binding, not use.

## gen #37 (2026-10-23): #305 (user exception class named like a builtin is conflated with the builtin: shared WhyML tag + builtin
##   EXCEPTION_BASES, handler matching wrong under no_exception) OPENED (red team 13); 4 witnesses rc=0, CPython violates.

## gen #37 (2026-10-23): #306 (`d.get(k, default)` evaluates default lazily on the None arm: its writes and raises vanish when the
##   key is present) OPENED (red team 13); 5 witnesses rc=0 (2 without no_exception), CPython violates.

## gen #37 (2026-10-22): #304 REPAIRED (r304 executor, off 1d2401a5; inline; no new def; no IR change; ledger 3; no mirror twin touched).
##   `_emit_function_block` splits the body's escaping own raises against the DECLARED `no_exception` (`\all` = any class;

##   named = class or ancestor, builtin closure + class bases snapshotted by `_run_pipeline` before the inheritance merge;

##   unknown ancestry covered): covered classes are no longer inferred `raises`, the body is wrapped `try ... with E ->

##   assert false; absurd` (label `no_exception: own raise E reachable`). Witnesses 3720-3732 PROVED -> FAIL; controls 3733

##   FAIL(L3-tc) -> PASS; route witnesses 10/10 rc=0 -> rc=1. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (nothing owed); fast

##   61/61. Residuals: j02 (declared `raises` not exhaustive, by documented semantics); imported unrelated class under a

##   named set is a spurious FAIL.

## gen #37 (2026-10-22): #304 (a function's own explicit `raise` escapes its `#@ no_exception` claim: the emitter auto-adds
##   `raises { E }` and the contradiction check only reads declared raises) OPENED (red team 12); 7 witnesses rc=0, CPython raises.

## gen #37 (2026-10-22): #303 REPAIRED (r303 executor, off 388cd100; inline; no new def/field; ledger 3; mirror twins `\trusted`).
##   `_reset_function_state` refuses a mutation through any name a TupleUnpack slot aliases (literal elements, swaps,

##   call results with kind-filtered arguments, sub-collection reads; pure permutations exempt); r2c R1 treats unpack /

##   tuple-for / walrus bindings of the root as non-fresh; route #59 now also guards dict REBINDS (plain + chained

##   were PROVED false) and walks the whole body for a binding inside a loop (back-edge store was PROVED false).

##   Witnesses 3650-3654, 3661, 3662, 3664 PROVED -> REFUSED; 3655-3660 FAIL -> REFUSED; control 3663 PASS; route

##   witnesses rc=0 -> rc=1. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (nothing owed); fast 61/61. Residual: a callee

##   returning an element of a differently-kinded argument is not refused by construction (FAILS today).

## gen #37 (2026-10-22): #303 (dict aliased via tuple-unpacking assignment is a value copy; bypasses #59 and r2c-local root
##   freshness, incl. a parameter root) OPENED (red team 11); 4 witnesses rc=0, CPython violates.

## gen #37 (2026-10-22): #302 REPAIRED (r302 executor, off d117596a; inline; no new def/field/raise; ledger 3; mirror twins `\trusted`).
##   `_reset_function_state` marks every plain-name for target read STALE after a loop (the #301 path walk; a top-level

##   re-binding kills it) under the key "#302:<name>" of the existing `_loop_targets_read_outside`; the binder then writes

##   the element back for EVERY iteration lowering (exact when the types agree, L3-tc fail-closed otherwise) and, when

##   the body re-binds the target, binds the outer ref with no shadow. Witnesses 3630-3639 PROVED -> FAIL; controls 3640

##   PASS both; route witness rc=0 -> rc=1. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (nothing owed); fast 61/61.

##   Residual: a type-mismatched stale read fails at L3-tc instead of a refusal message.

## gen #37 (2026-10-22): #302 (plain-name for target over a non-index sequence read after the loop keeps its pre-loop value; route
##   #36 residue) OPENED (r301 executor).

## gen #37 (2026-10-22): #301 REPAIRED (r301 executor, off 25a03299; inline; no new def/field; ledger 3; mirror twins `\trusted`).
##   Module 5 records `unpack_target_refused` for every Assign/for/comprehension target outside {Name, flat tuple of

##   Names} (List, Starred, nested, attribute/subscript elements); Module 6 refuses it where the body is lowered

##   (imported/trusted bodies exempt). Also: a tuple for-target COMPONENT read outside its loop without a covering

##   re-binding is refused (never written back). Witnesses 3610, 3612-3617, 3622, 3623 PROVED -> REFUSED; 3611,

##   3618-3620 FAIL -> REFUSED; control 3621 PASS both; route witness rc=0 -> rc=1. Root 0/0/0, pyref 0/0/0, mirror

##   0/0/0 (nothing owed); fast 60/61 (the RED, refusal-witness UNWITNESSED 6 > 5, is RED at base). Residual: plain

##   Name for-target read after a non-index loop still PROVES stale (route #36 residue; witnesses-r301/residual_*.py).

## gen #37 (2026-10-22): #301 (starred assignment target dropped by the front end; [*h, t] = e keeps t) OPENED (found by r299);
##   rc=0 on main, CPython 5.

## gen #37 (2026-10-22): #299 + #300 REPAIRED (r299 executor, off f11bba0e; inline; `_pyval_wrap` unmirrored, `_reset_function_state`
##   mirror `\trusted`; no new def/field; ledger 3). #299: a list literal with a Starred element / dict literal with a `**`

##   entry stored as an hval is the opaque `(HArr (any hval_list))` / `(HMap (any hpairs))` (refused in a spec). #300: the

##   per-function pre-pass counts every static binding (params, with-as, Assign/AugAssign/For/walrus/comprehension

##   targets, TupleUnpack/tuple-For, except-as, match capture); a name bound twice is fold-unsafe whatever its first binding.

##   Witnesses 3570-3573, 3576-3580, 3582-3584 PROVED -> FAIL, 3574 FAIL -> FAIL (now well-typed), controls 3575/3581

##   PASS both; route witnesses 6/6 rc=0 -> rc=1. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (nothing owed); fast 61 green;

##   --slow 84/84 green. Residuals: see the two route files. NEW suspect: `[*h, t] = e` is dropped (false proof, route299 §residual 2).

## gen #37 (2026-10-22): #299 (starred element in an hval list literal wrapped as one element) and #300 (literal rebinding after a
##   non-literal first binding registers a fixed fold size; #297 residual) OPENED (red team 10); 6 witnesses rc=0, CPython violates.

## gen #37 (2026-10-22): #298 (hval model assumes nested dicts have str keys; isinstance(k, str) over .items() proves for {1: 2})
##   OPENED (found by r296); rc=0, CPython False.

## gen #37 (2026-10-22): #298 DECLARED (r298 executor, off 47f53c06; inline, mirror twins `\trusted`; no new def/field; ledger 3).
##   Decision (B) by measurement: the faithful key (A) breaks L3-tc in 3 mirrors (7 pyval `.items()` loops, 13 str

##   sinks of 7 kinds, 5 converted methods) and costs control 3497, so the assumption is DECLARED: HVAL-STR-KEYS in

##   `--soundness-report` (+ README, static-semantics C.1, translational T.10.5, check-assumed-facts), and

##   `--strict-hval-keys` binds a nested key to the uninterpreted `hval_keys_hget` (an unknown-carrier `hval`).

##   Witnesses 3550-3553 PROVED (declared counterexamples), strict twins 3554-3557 FAIL, controls 3558 PASS both

##   modes. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (nothing owed); fast 61 green. Residual: default still proves 3550.

## gen #37 (2026-10-22): #297 REPAIRED (r297 executor, off 2850cbbf; inline, mirror `\trusted`; no new def/field; ledger 3).
##   The literal fold answers only what the source decides: a Starred element (list/tuple/set), a non-literal set

##   element, a non-literal or non-integral-float dict key registers NO size and NO element map and blacklists the name;

##   inline `len(<literal>)` follows the same rule (distinct-counted); the indexed fold takes an int index only.

##   Witnesses 3510-3527 PROVED -> FAIL, controls 3528/3529 FAIL -> PASS; route witnesses 14/14 rc=0 -> rc=1. Root 0/0/0,

##   pyref 0/0/0, mirror 0/0/0; planes --slow 84/84 green. Residuals: see route297.

## gen #37 (2026-10-22): #297 (compile-time collection-literal fold ignores non-literal keys/elements and starred elements:
##   dict/set/tuple) OPENED (red team 9, ~262 probes; hval model + #286-#295 held); 7 witnesses rc=0, CPython violates.

## gen #37 (2026-10-22): #296 (hval local holding a list, iterated bare, is iterated as dict keys) OPENED (ch30); rc=0, CPython False.
## gen #37 (2026-10-22): #296 REPAIRED (r296 executor, off 9b84ec85; inline, mirror twins `\trusted`; no new def/field; ledger 3).
##   The bare `for x in <pyval local>` dict-KEY arm (and its "str" target typing) is removed; the R2b judgement admits a bare

##   pyval `Var` (same mutation guards), and its match iterates PER CARRIER: `HArr` real elements (exact length), `HMap` keys

##   as `HStr` (the `.items()` key over-approx), any other carrier the uninterpreted `hval_iter_*_other`; R2b declining ->

##   int fallback -> L3-tc (fail-closed). `startswith`/`endswith` with an `hval` argument reads `hstr_of` (not under

##   `no_exception`). Witnesses 3490-3494/3496 PROVED -> FAIL, 3499/3500 FAIL -> FAIL; controls 3495/3497 PASS, 3498 FAIL -> PASS.

##   Root 0/0/0, pyref 0/0/0, mirror 1 MOVED (stmt_control_flow `_maybe_inject_union_return`, intended; L3-tc ok, --fun

##   PROVED; whole-file proof OWED); fast 61 + --slow 84/84 green. Residual: nested-dict keys are modelled as strings (see route296).

## gen #37 (2026-10-20): #295 (dict returned by a may-alias call is a copy; store through it misses the original) OPENED; rc=0, CPython 2.

## gen #37 (2026-10-20): #294 (annotated dict local whose first assignment is not a dict literal lowered to the EMPTY map;
##   RHS discarded) OPENED (ch29); witnesses rc=0, CPython violates.

## gen #37 (2026-10-20): #287 (sorted key-lambda body raises dropped), #288 (element store through a list returned by a call),
##   #289 (tuple holding a list opaque; writes no-op), #290 (mutation via operator.i*/dunders/getattr/partial/methodcaller),

##   #291 (bool f-string rendered as int), #292 (cited struct axiom applied to '?' formats), #293 (os.path.relpath pure but

##   cwd-dependent) OPENED (red team 8, ~200 probes); 12 witnesses driver-reproduced rc=0, CPython violates each.

## gen #37 (2026-10-20): #287 + #291 + #292 + #293 REPAIRED (rA executor, off 7313506b; inline, mirror `\trusted`; no new
##   def/field; no axiom, no Rocq/Lean edit; ledger 3). #287: a `Lambda` body under an active no_exception context

##   (declared or handler-widened, #171) is censused by #285's `TRIGGER_EXPR_SHAPES` like a comprehension element and

##   refused on a hit (callable-taking builtins censused: only `sorted(key=lambda)` dropped a body; min/max key,

##   map/filter, reduce, named keys already refused or ill-typed). #291: the value-keyed renderers (`str_of_int_hash`,

##   `pycsl_format_<c>_i_*`) classify the int-model operand: shown bool -> `str_of_bool_hash` / `_b_` symbols; shown

##   exact int (literal, int-only builtin/operator, `int`-typed name — BUILTIN-EXACT) unchanged; else a program `val`

##   (fresh); a non-empty spec keeps `i` (CPython formats a bool as its int); unannotated locals classified from

##   their bindings (1706 kept). #292: `UnixFs.Struct.{i2,i18,i1a1}.round_trip` keyed on the exact documented format

##   (`>HH`/`>IHHHHHII10Ixx`/`>H30s`); other formats of that shape get `struct_*_<id>_h<hex>`; `--soundness-report`

##   lists cited lemmas as TCB entries. #293: `os.path.relpath` moved to the impure table (CPython reads the cwd);

##   the remaining pure list is lexical in posixpath. Witnesses 3340-3344/3346-3350/3352-3354/3356-3357 PROVED ->

##   REFUSED/FAIL, controls 3345/3351/3355/3358 PASS; 12 route witnesses rc 0 -> 1. Root 1 MOVED (1915, declared,

##   re-proved PASS), pyref 0; mirror 1 MOVED (`frontend__pure_ast` `Comment.__repr__` `!r` -> `_u_`, L3-tc ok,

##   whole-file proof OWED); fidelity green; planes --slow: 82/84 green, then 3358 made non-vacuous (vacuous-drivers

##   rc 0) and the hashed-literal-purity baseline re-keyed for the format-keyed struct symbols (rc 0); the remaining RED,

##   assigns-writes-survival TRAP 1447 > 1445, is identical at 7313506b (pre-existing, mirror emission, not this change).

##   Residual (suspected, not reproduced): legacy laws unguarded for out-of-range ints / `>H30s` name length != 30.

## gen #37 (2026-10-20): #288 + #289 + #290 REPAIRED (rB executor, off 7313506b; inline, mirror `\trusted`; no new def/field;
##   ledger 3). #288: #283's partner rule now runs for ANY list-valued target (seq-promoted, declared `list`, or an RHS

##   yielding an array) and its walk also refuses an element/slice store, `del`, or passing a live name to a user/

##   imported callee that may write it (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS; imported/`\trusted`/early-return

##   callees are "may alias"). #289: an emission GATE in `_run_pipeline` refuses every application of the no-effect

##   `val subscript_set` (a store through an element of an opaque tuple/container) (PYCSL-SEM-STORE-THROUGH-OPAQUE-

##   ELEMENT). #290: a source-AST rule in `_run_pipeline` refuses a computed callee (Module 5 erases the whole call,

##   effect included), an explicit in-place dunder, an unbound collection mutator, a mutator referenced as a VALUE,

##   and `getattr`/`methodcaller` naming a mutator (PYCSL-SEM-MUTATION-BY-ANOTHER-NAME); #162's denylist gains every

##   `operator.i<op>`. Witnesses 3370-3381/3383-3387/3389-3398 PROVED -> refused; controls 3382/3388/3399 PASS; all 14

##   route witnesses rc=0 -> rc=1. Root 0 MOVED / 4 GONE (0849, 1314, 1315, 1317: expected-FAIL witnesses now refused,

##   census rows re-measured), pyref 0/0/0, mirror 0/0/0; fast planes 61 green, --slow OWED. Residuals: see the three route files.

## gen #37 (2026-10-21): #295 REPAIRED (r295 executor, off ea7f5bcb = rB 4b67e24d; inline, mirror `\trusted`; no new def/field;
##   ledger 3). #283/#288's partner rule now also runs for a MAP-valued (dict/set) target bound from a may-alias RHS (call,

##   conditional, `or`): partners are the dict/set names in the RHS (parameters included) outside a fresh constructor, and the

##   same walk refuses stores/aug-stores/`del`/mutators/`|=`/writing callees through any live name

##   (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS). Witnesses 3450-3465 PROVED -> refused; control 3466 PASS; route witness

##   rc=0 -> rc=1. Root 0/0/0, pyref 0/0/0, mirror 0/0/0 (a first cut GONE'd mirror stmt_control_flow on a `-> str` target, fixed); fast planes 61 green, --slow 74/84 ok then capped (10 OWED).

##   Residuals: see route295.

## gen #37 (2026-10-20): #286 (one-arg `.get` on a non-map hval receiver under no_exception drops AttributeError) OPEN on main,
##   REPAIRED in the land27 stack (3cbcc895); witness 3289 PROVES on main, FAILS on land27. Closes when land27 lands.

## gen #37 (2026-10-20): #283 (list from a user-function return: append writes slot 0, len frozen, alias/frame lost), #284 (f-string
##   format specs: #281 digit-limit assert not emitted; invalid-spec ValueError unmodelled), #285 (comprehension raise check covers only

##   division/subscript) OPENED (red team 7, 237 probes); driver-reproduced rc=0 at HEAD, CPython violates each.

## gen #37 (2026-10-20): #284 + #285 REPAIRED (r284 executor, off 323066f9; inline, mirror `\trusted`; no new def/field;
##   ledger 3). #284: the literal-spec `FormattedValue` test read `_r231_ty` (the operand's WhyML type) instead of the

##   presentation type, so the #281 bound was never emitted for `:d`/`:5`/`:05d`/`:n`/`:,`/`:>10` — fixed; new row

##   `("call", "format_spec")` (`ValueError`, `false`) for a spec INVALID for the operand's type (decided at emit time

##   by CPython `format()` on a sample of the type; both int and str unless shown int), a COMPUTED spec, and an invalid

##   or non-literal `%` format (`"%q" % x` PROVED too — same gap, found auditing the siblings; `format(x, spec)` /

##   `str.format` verified refused by #161). #285: the #177 comprehension refusal is driven by the new

##   `exception_model.TRIGGER_EXPR_SHAPES` census of EVERY `TRIGGERS` row (shift, chr, int_str, format_spec newly

##   covered; an uncensused row refuses every comprehension — fail-closed for future rows). Corpus 3260-3270/3272-3278

##   PROVED -> FAIL/refused, controls 3271/3279 PASS; 19 route witnesses rc 0 -> 1. Root 1 MOVED (3118, its `:d` line;

##   docstring corrected), pyref 0, mirror 1 MOVED (`exception_model`, proved); fast planes 61 green; --slow OWED.

## gen #37 (2026-10-20): #283 REPAIRED (r283b executor, off 7be313fe; inline, mirror `\trusted`; no new def/field; ledger 3).
##   Two carriers. (A) the array-counter `.append` arm (`t[!t_len] <- v` with `t_len = ref 0` whatever `t` is bound

##   to) is REFUSED outright (PYCSL-WHYML-APPEND-UNTRACKED-LIST): measured population ZERO emissions in root/pyref/

##   mirror at 7be313fe — every appended local that type-checks is seq-promoted; it also closed the census-found

##   FRESH `b = [0] * 3; b.append(9); len(b) == 1`. (B) a SEQ-PROMOTED (annotated) local bound from a call/

##   conditional/`or` is a `snapshot` COPY: the list names inside the RHS (outside fresh constructors: literal,

##   comprehension, slice, `+`/`*`, list/sorted/bytes/bytearray, `.copy()`) join #279's live set, and a mutation

##   through target or partner refuses (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS; #279's text untouched).

##   Witnesses 3300-3309 PROVED -> refused; control 3310 PASS; route witnesses p003/p012/p017/p019/p130/p143 rc=0 ->

##   rc=1. root/pyref/mirror 0 MOVED / 0 GONE / 0 APPEARED; census +10 rows. Residuals: fresh-returning callee

##   refused under (B) (no freshness analysis; population 0); object-field partner (`c.get()` -> self.xs) ill-typed.

## gen #37 (2026-10-19): #282 (distinct parameters / list elements assumed non-aliasing, undeclared; R1 residue like FIELD-DISJOINT)
##   OPENED; witnesses p111/p112/p114 rc=0, CPython violates.

## gen #37 (2026-10-19): #282 RESOLVED as the DECLARED MODEL ASSUMPTION PARAM-DISJOINT (#256 FIELD-DISJOINT precedent):
##   two distinct mutable parameters (or a parameter and `self` / a module-level name it reads) and two distinct elements

##   of a container parameter hold distinct objects. Listed by `--soundness-report` (`model_assumptions`; relied_on_by =

##   every function writing through one handle while accessing another, or writing an element of a container handle;

##   types not matched, over-reported): root 112 files / 180 entries, mirror 33/53 files / 2731 entries (a refusal was

##   measured disproportionate). Probes: callee shapes (two lists/records/dicts/sets, self+param, param+self field,

##   param+nested element, forwarded) PROVE = assumed; every VERIFIED caller building the alias fails closed already

##   (illegal alias / ill-typed / route #254 refusal / R167) — no new false proof. Docs README, static-semantics

##   App. C.1, translational §T.10.1/§T.10.5, ownership discipline §5, check-assumed-facts. Corpus 3180-3186/3188

##   (assumed, PASS), 3189 control PASS, 3190-3196 verified-caller controls FAIL. Emission byte-inert; ledger 3.

## gen #37 (2026-10-19): #277 (user-class value assumed exact; override refinement opt-in only, undeclared), #278
##   (--check-behavioral-subtyping ignores raises and MRO-inherited overrides), #279 (list alias lost by += / chained

##   assignment), #280 (mutator on subscripted / call-result receiver dropped), #281 (int->str > 4300 digits ValueError

##   unmodelled) OPENED (red team 6, 273 probes); 17 witnesses driver-reproduced rc=0 at 78162575, CPython violates each.

## gen #37 (2026-10-19): #279 + #280 REPAIRED (inline, mirror `\trusted`; no new def/field; ledger 3).
##   #279: `_handle_assign_stmt` refuses a list (array/seq local, list param) or chained-assignment temporary bound to

##   a second name when the alias is MUTATED (mutator method, ANY augmented assignment, element store for a chained

##   temp) while LIVE — in-order walk of the rest of the block with kill-on-rebind, and a whole-function check when 2+

##   names escape the block (loop top, after an `if`) (PYCSL-M6-MUTATION-THROUGH-COLLECTION-ALIAS). #280:

##   `_handle_call_expr`'s computed-receiver fallback refuses a collection mutator name (list/dict/set/deque/

##   OrderedDict/in-place dunders) and any same-file method that may write its receiver (least fixpoint; `super()`

##   excludes the current class's override) (PYCSL-M6-MUTATOR-ON-COMPUTED-RECEIVER). Witnesses 3080-3087/3089-3096/

##   3098/3099 PROVED (3087 ill-typed) -> refused; controls 3088/3097 PASS; all 9 route witnesses rc=0 -> rc=1.

##   root/pyref/mirror 0 MOVED / 0 GONE / 0 APPEARED; census +18 rows. Residuals: dict/set re-bound alias, `x = d[0];

##   x.append` (fail-closed, ill-typed); parameter-aliasing p111/p112/p114 still prove (separation premise).

## gen #37 (2026-10-19): #277/#278/#281 REPAIRED (r277 executor, off 72ab1c57). #277 by MEASUREMENT option (A): the
##   override-refinement check is the DEFAULT (cost: 11 of 1791+2186 corpus files gain goals, 3 PASS -> FAIL — 0445, 1348,

##   pyref 0206, each a genuine Liskov violation; mirror 25 `true` goals); `--assume-class-exact` is the opt-out and is

##   then the declared assumption CLASS-EXACT (`--soundness-report`: every override pair + every method call). #278:

##   override pairs over the C3 MRO (mixin / fieldless-chain providers; a class-body binding is refused), raise

##   conditions in the goal, PYCSL-SEM-OVERRIDE-REFINEMENT for raises / no_exception / assigns / parameter position

##   (also caught: the mirror's `statements.py::_expr_to_whyml` stub under-declared its provider's frame, so two

##   verified mirror callers carried false frame claims — widened). #281: faithful `("call","int_str")` ValueError

##   trigger `|x| < 10**4300` at str/repr/format/print/f-string/% (cost 0). Witnesses 3100-3119 (base PROVED -> FAIL /

##   refused; controls 3103/3113/3119 PASS; 3107/3112 coverage). Root 9 MOVED (= base `--check-behavioral-subtyping`

##   emission) + 2 GONE (1343/1344, expected FAIL); pyref 0 MOVED; mirror 3 MOVED (type-check OK; proofs: see #278).

## gen #37 (2026-10-19): #276 RESOLVED as the DECLARED MODEL ASSUMPTION LATIN1-STR (#250/#253 precedent): every str
##   value consists of code points 0..255 (str = Why3 string of 8-bit `string.Char`); listed by `--soundness-report`

##   (`model_assumptions`, relied_on_by = every ord/chr site + per-function str values), stated in static-semantics

##   App. C.1 / translational §T.10.5 / README. Opt-in `--strict-latin1` (uninterpreted code point `pycsl_cp` clamped

##   to [0,0x10FFFF] by a definition, no axiom; `chr` not `Char.chr`): witnesses 3020-3023 PASS default, 3024-3027

##   FAIL strict, controls 3028 (default) / 3029 (strict) PASS. Strict cost (22 ord/chr root files) 3 of 12 PASS -> FAIL: 0702/0708/0712 (Char.code-keyed codec

##   lemmas; 0702 ord_range is FALSE). TypeError for ord(len != 1) is outside the no_exception universe (scope).

##   Default emission byte-inert (root/pyref/mirror 0 MOVED); ledger unchanged. Residual: 8-bit str sort (pigeonhole).


## gen #36 (2026-10-18): #273 (nested def/lambda defaults + nested class bodies not evaluated), #274 (effectful calls in
##   comprehensions vanish), #275 (sorted key/reverse dropped), #276 (ord < 256 / chr round-trip beyond 255) OPENED (red team 5).

##   #273/#274 REPAIRED 2026-10-18 (inline in `_run_pipeline`, mirror `\trusted`): inside a lowered function a nested

##   def/lambda/class whose defaults are not literals/names, whose decorators are calls, whose annotations/bases are not

##   type-shaped, or whose class body holds anything but defs/docstrings/literal bindings is refused

##   (PYCSL-SEM-DEF-TIME-EVALUATION); a call to a frame-carrying callee (declared `assigns`, or a body writing a

##   non-fresh base, transitively) or a receiver mutator inside an opaque comprehension/generator/lambda is refused

##   unless the function's own emission applies it as often as the IR calls it (PYCSL-SEM-VANISHED-CALL-EFFECT).

##   Witnesses 2960-2966/2970-2977 PROVED -> refused, controls 2967/2978 keep; root/pyref 0 MOVED / 0 GONE; mirror 1

##   MOVED (functions: `_build_param_list` genexp -> explicit loop, live+mirror, a genuine vanished stub write).

##   #275 REPAIRED 2026-10-18: `sorted(reverse=True)` -> descending `sorted_desc_1`, `sorted(key=<not None>)` -> length +

##   permutation only (`sorted_perm_1`); every other builtin keyword (the generic path DISCARDS them: `sum(start=)`,

##   `min/max(key=)`, `int(base=)`, `round(ndigits=)`, `enumerate(start=)`, `zip(strict=)`, `print(end=<non-literal>)`,

##   a calling `key` lambda) is REFUSED in `_reset_function_state` unless a lowering reads it (pow #259, max/min

##   default #160, print sep/end/flush/file=sys.std*). Witnesses 2980-2984 PROVED -> FAIL/refused, coverage 2985

##   FAIL -> PASS, controls 2986-2988 keep PASS; root/pyref/mirror 0 MOVED / 0 GONE / 0 APPEARED.

##   #276 stays OPEN with measurements: the `< 256` law is Why3 `Char.code`'s axiom on EVERY str value; the axiom-free

##   hidden-high-part ord model breaks the Char.code-keyed codec lemmas (0708/0712/0702, os stub dirent writes) and a

##   literal name cannot discharge a Latin-1 hypothesis; a `chr` obligation alone lands on mirror pure_ast.

## gen #36 (2026-10-18): #272 (a callee's undeclared raise is dropped at the call; no_exception \all proves) OPENED.
##   #272 REPAIRED 2026-10-18: a `no_exception` function may not call a method whose undeclared raise (or a declared one

##   through `C.m()`/`C().m()`, which the raises wrap does not resolve) is hidden behind the stub, directly or

##   transitively through methods/module functions (PYCSL-SEM-UNDECLARED-CALLEE-RAISE, inline in _run_pipeline).

##   Witnesses 2940-2950 PROVED -> refused, controls 2951-2953 keep; root/pyref/mirror 0 MOVED / 0 GONE.

##   Residual: an imported function whose raise arrives through a stub inside the dependency (documented, OPEN).

## gen #36 (2026-10-17): #270 (#264 analysis misses exception edges from calls; generators treated as no-return) and
##   #271 (calling a generator function runs its body eagerly) OPENED (red team 4, driver-reproduced).

##   #270/#271 REPAIRED 2026-10-18: inside a `try`/`with` region EVERY potentially-raising expression (call,

##   arithmetic, subscript, attribute, pattern, store target) adds a must-assign exception edge, and a generator /

##   coroutine is never no-return; a COUNTED generator (own `yield`, lowered, not the R-W2b `_walk_dicts` model) may

##   not carry `ensures` (other than True) / `raises` / NoReturn (G1), be a special method or non-CM-decorated (G3),

##   or be called / used as a value except as a `with` item (G2) — fail-closed. Witnesses 2900-2902/2905-2908 PROVED

##   -> REFUSED, controls 2904/2909-2912 PROVED both; root 0 MOVED/0 GONE (+5), pyref 0/0, mirror 53/53 0 MOVED.

## gen #36 (2026-10-17): #269 (residual divergence leaks after #263: C().m() stub drops diverges, comprehension-hidden
##   calls, diverges+no_exception RecursionError, Module5 bespoke dispatch stubs, cross-module cycles) OPENED.

##   #269 REPAIRED 2026-10-17 (inline in `_run_pipeline`, mirror `\trusted`): on the emission every plain `val` stub

##   spelling of a `\diverges` callee carries `diverges` (any producer: `C().m()`, `super().m()`, the Module 5

##   `self__py_expr_to_ir_1`) and every emitted `let`/`with` of a `\diverges` function does; a call VANISHED in an

##   opaque comprehension/generator/lambda applies an opaque diverging `val` (diverging callee) or is refused

##   (raising or precondition-carrying callee, `PYCSL-SEM-VANISHED-CALL-EFFECT`); `\diverges` + `no_exception \all`

##   reaching a call cycle is refused (`PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION`; RecursionError scope documented);

##   imported bodies' calls back into the unit join the #263 graph (`PYCSL-SEM-CROSS-MODULE-RECURSION`). Witnesses

##   2880-2887/2891/2892 PROVED -> FAIL, 2888/2889 FAIL -> PASS, control 2890 keeps; root/pyref 0 MOVED/0 GONE;

##   mirror 3 MOVED (Module5_IREmitter 14 + pure_ast 2 `\diverges` markers, pycsl import stubs), type-only clean.

## gen #36 (2026-10-17): #268 (cross-mixin `_stmts_to_whyml` stub under-declared its frame; 5 verified callers proved
##   false field-unchanged claims) OPENED + REPAIRED 487c4789 (found while fixing the slow survival plane).

## gen #36 (2026-10-17): #263 (method-call recursion never termination-checked), #264 (never-assigned local reads 0),
##   #265 (match True/False by equality), #266 (HAPPY region bypass via helper), #267 (vacuity gate misses one-branch

##   inconsistency) OPENED (red team 3, driver-reproduced).

##   #264/#265 REPAIRED 2026-10-17: a MUST-ASSIGN dataflow per lowered function (Python scoping: a name bound

##   anywhere is local; `del`/`except as` unbind) refuses a read not definitely assigned on every path

##   (`PYCSL-SEM-UNBOUND-LOCAL`); `case True/False` admitted only on a bool-BY-CONSTRUCTION subject (route #42's

##   whitelist), else refused (`PYCSL-SEM-MATCH-BOOL-SINGLETON`). Inline in `_run_pipeline`. Witnesses 2790-2796,

##   2799-2802 PROVED -> REFUSED, controls 2797/2798/2803 keep PASS; 24 concurrency drivers gain their missing

##   `global` (byte-identical); root 0 MOVED/0 GONE, pyref 0, mirror 0.

##   #266/#267 REPAIRED 2026-10-17: in every non-exempt body-verified function a non-scalar HAPPY-protected field

##   may appear only as `X.f[...]` / `len(X.f)` (no passing/aliasing/returning: a list goes by reference), and a

##   write/`del` reaching `.f` through any non-canonical spelling (other receiver, `poke(self)`, nested, tuple) or a

##   read-form read through a receiver other than `self` is refused — all region/protects/parametric/read forms.

##   The vacuity gate probes `check false` after/before each call to a body-less `val` (no raises/diverges) and

##   flags the function when only the AFTER point is unreachable. Witnesses 2810-2819/2825 and 2821/2822 PROVED ->

##   FAIL, controls 2820/2823/2824 keep; root/pyref/mirror 0 MOVED; `pycsl_lib_test/formal_happy_world.py` lists its

##   subsystem methods as owners (relied on 2818's shape); gate cost one goal per audited call site (538 root,

##   36 pyref; 0 false positives among non-failing files); big-mirror call-site measurement OWED.

##   #263 REPAIRED 2026-10-17: the unit's call graph now includes method/constructor calls (receivers resolved by

##   class hierarchy, unknown -> every same-named method), and a cycle with an edge the EMISSION shows as a stub (or a

##   vanished call) is refused unless every member is `#@ \diverges` (`_run_pipeline`, mirror `\trusted`); the stub of

##   a `\diverges` method carries `diverges` (`_handle_dotted_call`). Witnesses 2770-2779 PROVED -> FAIL, 2780 FAIL ->

##   PASS (honest marking now writable), control 2781 keeps; root 1 MOVED (0893 +`\diverges`), 0 GONE, pyref 0; mirror 3

##   MOVED (pure_ast 52 / Module3_Weaver 1 `\diverges` markers + pycsl import stub), type-only clean; planes 61/61 + slow 17 green (3 red at base).

##   Residuals R1-R5 in the route doc (receiver-form and bespoke-dispatch stubs to a `\diverges` callee, vanished calls).

## gen #36 (2026-10-17): #214 CLOSED (found by the slow `check-open-route-carriers` plane going red: its carrier no
##   longer proves). Driver bisect: closed by route #255 (323e857b; getattr over an erased receiver is erased, and #249's

##   `==` on erased values is uninterpreted). Corpus witness 2760; carrier row retired.

## gen #36 (2026-10-17): #259 (`**` always int; pow mod 0 no obligation), #260 (except LookupError misses KeyError),
##   #261 (self-call under a broken class invariant), #262 (symbolic negative index in contracts) OPENED (red team 2).

##   #260/#261 REPAIRED 2026-10-17: EXCEPTION_BASES carries the whole builtin hierarchy (handler arms per raised

##   subclass) + the vacuity gate flags a function whose only exit is an undeclared added `raises` arm; a

##   `self.<m>()` stub takes `self` under a class invariant (route #165 extended). Witnesses 2730/2733/2735/2736

##   PROVED -> FAIL, controls 2731/2732/2734/2737 keep verdicts; root 1 MOVED (0453, proves), pyref 0; mirror 2

##   MOVED (Module2_Parser, pure_ast: NoReturn error self-calls), type-only clean, changed-line goals Valid, OWED.

##   #259/#262 REPAIRED 2026-10-17: `**`/`x **= n`/`pow(b, e)` owe `exp >= 0` (`val function py_pow ... requires`),

##   keyword `pow` owes `false`, no negative-exponent fold; 3-arg `pow` under no_exception refused unless the modulus

##   is a nonzero literal (keywords folded in). Contract-side list/str/`\result`/field reads take Python's index

##   (`if e < 0 then a[len + e] else a[e]`, literal `-k` -> `len - k` on every arm). Witnesses 2700-2706/2710-2716/2720

##   PROVED -> FAIL, controls 2707-2709/2717-2719 keep, coverage 2721-2723 FAIL -> PASS; root 100 MOVED (all re-proved,

##   verdicts kept; 0708/0711/0714 gain declared `0 <= off` domain preconditions) / 0 GONE, pyref 0; mirror 2 MOVED

##   (Module2_Parser re-proved 868/0, pure_ast OWED); planes 61/61.

## gen #36 (2026-10-17): #258 (`Optional[Any]`/`Any | None` lowered with only the None arm) OPENED (residual of
##   #254/#255, driver-reproduced). REPAIRED 2026-10-17: a Union with an arm `_union_arm_tag` cannot type (`Any`,

##   `object`, unknown/lowercase name, nested `Optional`, unmodelled generic) lowers WHOLE to the erased `Any` value

##   (#249/#251/#252's treatment) instead of a variant with the arm dropped (inline in `_normalize_union_annotation`,

##   mirror `\trusted`). Witnesses 2580-2587 PROVED -> FAIL, coverage 2588-2589, controls 2590-2592 keep verdicts;

##   root/pyref 0 MOVED/GONE; mirror 3 MOVED (dead None-only types; one abstract `val` formal -> int), type-only

##   clean, `ir_schema`/`sertop` re-proved, `module6_whyml/expressions` OWED.

## gen #36 (2026-10-17): #257 (bare `with <cm>:` drops __enter__/__exit__ for an imported CM or a @contextmanager
##   method) OPENED (found by the ch18 census, driver-reproduced). REPAIRED 2026-10-17: outside `\trusted`, every

##   BARE `with` item must be provably inert -- a name bound only by `threading.Lock()`/`RLock()`, or an in-file

##   producer (per-class resolved `@contextmanager` with one top-level yield / `return <producer>()`) whose effects

##   land only in locals or a FIELD-LESS record -- else REFUSED (`PYCSL-R257-CONTEXT-MANAGER-NOT-INERT`, in

##   `_run_pipeline`); `async with` refused. Witnesses 2660-2666, pins 2667/2668, control 2670; root 0 MOVED/0 GONE,

##   pyref 0/0, mirror 53/53 0 MOVED.

## gen #36 (2026-10-16): #254 (one dict/set to a mutating AND a read slot of one call), #255 (erasure lost via walrus
##   / unannotated return), #256 (two list fields holding one list; alias built in unverified code) OPENED (red team).

##   2026-10-17: #254 REPAIRED (a mutating-slot argument may not reach another argument of the same call; WL-05b

##   by-ref slots joined the #243/#244 rule; witnesses 2540-2546, control 2548), #255 REPAIRED (walrus / tuple-

##   unpack / match / lambda bindings join the #249 fixpoint; missing/Any/TypeVar-return call results and

##   arg-passing builtins are erased; witnesses 2550-2562, control 2566), #256 RESOLVED as the DECLARED MODEL

##   ASSUMPTION FIELD-DISJOINT (ownership rule R1; corpus 2570). Residual: `Optional[Any]` drops its Any arm.

## gen #36 (2026-10-16): #250 and #253 RESOLVED as DECLARED MODEL ASSUMPTIONS (HASH-EQ-CONSISTENCY precedent):
##   FLOAT-FINITE (floats finite, non-NaN) and BUILTIN-EXACT (builtin-typed values are exact instances, no

##   dunder-overriding subclass), listed by `--soundness-report` (`model_assumptions`) when relied on, stated in

##   static-semantics App. C.1 / translational §T.10.5 / README. Opt-in `--strict-float-finite` (NaN sentinel

##   `1/3`, definition, no axiom) drops FLOAT-FINITE: witnesses 2500-2502 PASS by default, 2503-2505 FAIL strict,

##   controls 2507 PASS strict; strict cost 0517/1124 (true) + 0818/0847/1120 (false for NaN). BUILTIN-EXACT has

##   no strict mode (2506 PASS). Default emission byte-inert (root/pyref/mirror 0 MOVED); ledger 3.

## gen #36 (2026-10-16): #253 (a builtin-annotated value may be a subclass with overridden dunders: `x - x == 0`
##   proves for `x: int`) OPENED (design-level residual of #252).

## gen #36 (2026-10-16): #252 (an `Any` value flowing into an `int` param/field/local is trusted as an int;
##   `no_exception` over `Any` arithmetic) OPENED (residuals of #251, driver-reproduced). REPAIRED 2026-10-16:

##   (a) an erased value flowing into a builtin-declared slot (`int`/`float`/`str`/`bool`/`bytes` callee formal --

##   function, method, record constructor, class `__init__`, positional or keyword, body or contract -- record-field

##   store, or `return` from a builtin-annotated function) is REFUSED in `_reset_function_state` (route #249's own

##   fixpoint decides erasure via sentinel bindings; no new def); (b) under `no_exception` every erased `pycsl_py_*`

##   operation (arithmetic, ordering, unary, `==`/`!=`/`in`) carries `assert { [@expl:PyCSL-R252 ...] false }`.

##   Witnesses 2470-2482, controls 2490-2493; root 13 GONE (#249/#251 witnesses returning an erased value from

##   `-> int`, FAIL -> refused), pyref 0092 GONE (FAIL -> refused), 0 MOVED; mirror 53/53 0 MOVED. Residual:

##   an `int` SUBCLASS overriding `__sub__` passed to an `int` parameter (declared-type trust at the boundary).

## gen #36 (2026-10-16): #250 (`float` parameters may be NaN; the `real` model proves `x == x` etc.) and #251
##   (arithmetic on `Any` is int arithmetic; a user `__sub__` breaks `x - x == 0`) OPENED (residuals of #249). #251

##   REPAIRED 2026-10-16 (route #249's design: with an erased operand `+ - * // %` lower to the uninterpreted

##   `pycsl_py_add/_sub/_mul/_floordiv/_mod`, `< <= > >=` to `pycsl_py_lt/_le/_gt/_ge`, unary `- + ~` to

##   `pycsl_py_neg/_pos/_invert`, no law; #249's walk moved to `_handle_binop`'s head and shared via a probe op;

##   witnesses 2440-2458, controls 2460-2463; pyref 0059/0205 PASS -> FAIL, declared). Residuals: an `Any` passed to

##   an `int` parameter/field, `no_exception` over an erased op, `str`-typed operands. #250 MEASURED + SPIKED, stays

##   OPEN: NaN-as-`1/3` guard is sound but turns TRUE 0517/1124 FAIL; `ieee_float` needs exact literals.

## gen #36 (2026-10-16): #249 (`==` on `Any` is mathematical equality; an asymmetric user `__eq__` breaks
##   `requires x == y ensures y == x`) OPENED (design-level residual of #247/#248, driver-verified), REPAIRED

##   2026-10-16 (option (b): with an erased operand -- `Any`/`object`/unannotated/TypeVar param, a non-record class

##   defining `__eq__`, an `Any`-element container read, an `Any` field/return, a local bound from one -- `==`,

##   `!=`, `in` lower to the uninterpreted `pycsl_py_eq`/`pycsl_py_ne`/`pycsl_py_in`, no law, one symbol for

##   contract and body; `is` and builtin-typed pairs keep `=`; witnesses 2370-2393, controls 2395-2399; 1686/1851

##   PASS -> FAIL, declared). Residuals: float NaN (`real` has none: `x == x`, `x <= x` prove), `Any` arithmetic is

##   `int` arithmetic, bare `list`/`dict` read as `int` elements, dict keys are identity (`witnesses-r249/`).

## gen #36 (2026-10-16): #247 (`set`/`frozenset` share `dict`'s isinstance tag) and #248 (builtin-`==` assumption
##   on `Any` broken by a user `__eq__`) OPENED (residuals of the #246 repair, driver-verified), REPAIRED 2026-10-16

##   (#247: set/frozenset own tags 7/8, a declared type decides only when its tag names one class -- `object`/`float`

##   subjects and record/variant tags are undecided unless the same class; #248: str/list/dict on an undecided `Any`

##   subject join #246's arm, every contract-side hval test but `object` is refused; witnesses 2340-2348, 2350-2355,

##   controls 2360-2364; 2310-2313/2331/2332 PASS -> FAIL, declared). Residual: `==` on `Any` is builtin (`y == x`).

## gen #36 (2026-10-16): #246 (`isinstance(<Any>, int)` is a function of the stored int: 1 and 1.0 agree)
##   OPENED (driver-reproduced; residual of the #245 repair), REPAIRED 2026-10-16 (for a class whose builtin `==`

##   crosses types -- int/float/set/frozenset/user classes -- a contract-side test on an undecided subject is refused

##   at the WhyML type-check; a program-side test is keyed on an unrebound parameter's IDENTITY, else a fresh

##   `(any bool)`; str/list/dict keep the value application; witnesses 2320-2326, controls 2330-2333; 2212 PASS ->

##   FAIL, declared). Residuals: `isinstance(<dict>, set)` decided TRUE (shared tag); a user `__eq__` crosses `str`.

## gen #36 (2026-10-16): #245 (contract-side `isinstance(<hval>, bool)` cannot tell `True` from `1`) OPENED
##   (driver-reproduced; residual of the #242 repair), REPAIRED 2026-10-16 (a contract-side opaque `HInt` arm for a

##   class whose builtin values can be `==` to another type -- bool/int/float/set/bytes/user classes -- is refused at

##   the WhyML type-check; dict/str/list/tuple/NoneType keep it; witnesses 2300-2305, controls 2310-2314; corpus and

##   mirror byte-inert). Residual: an int-erased `Any` subject's `typeof_op x` is a function of the int (1 vs 1.0,

##   program side too).

## gen #36 (2026-10-16): #243 (a dict/set aliased through a second name/field is a COPY: `1 in self.g` stays
##   false after `self.d[1] = 5` with `self.g = self.d`, incl. cross-method) and #244 (`s.add` on a set

##   parameter is a no-op under @mutable_state) OPENED (driver-reproduced), REPAIRED (#244: the no-op arm is gone,

##   the mutated set/dict parameter is a faithful local shadow; #243/#244: fail-closed unit-wide rule — a dict/set

##   field store, an argument in an ESCAPING slot (stored into a field / dataclass init) and an argument in a MUTATING

##   slot must be fresh or single-use, the first two only when the unit mutates a shared dict/set in place; route #59

##   guard sees mutator calls and dict/set params; `__init__`/`__post_init__` scan; witnesses 2290-2299 + 2400-2409, controls

##   2410-2414 (renumbered from 2300-2314 at landing: collided with #245); corpus 0 GONE / 2 MOVED, mirror 0 GONE / 3 MOVED). Residual: an alias made in an IMPORTED method.

## gen #36 (2026-10-15): #242 (a `let function` with a nondeterministic body is one value per argument:
##   `h(True) == h(1)`, `r() == r()` for generators proved) OPENED (driver-reproduced), REPAIRED 2026-10-16 (a body

##   reading `any`, an unpinned program `val`, an unpinned `\trusted` callee or a nondeterministic function emits as a

##   plain `let`; witnesses 2270-2274, 2277, 2278, controls 2275-2276; 54 corpus + 11 mirror files moved header-only,

##   all verdicts kept). Residual: contract-side `hval_isinst_opaque` cannot tell `True` from `1`.

## gen #36 (2026-10-15): #240 (`isinstance(<int>, bool)` decided TRUE) and #241 (a generator actual to an `Any`
##   parameter emitted as the literal `0`) OPENED (driver-reproduced; residuals of the #239 repair), REPAIRED (a

##   `bool` test on any int-modelled subject — int, Any, even a `bool`-declared param — takes the unknown-class

##   receiver-carrying arm, `isinstance(<bool>, int)` stays TRUE; the GenExp value arm answers `(any int)` in every

##   position; witnesses 2240-2249, controls 2250-2252). Residual recorded: a `let function` body freezes its

##   fresh devices, so `h(True) == h(1)` / `r() == r()` still prove.

## gen #36 (2026-10-15): #239 (`isinstance(<Any>, T)` lowered to `typeof_op <name-hash>` — rebinding the name
##   kept the answer) OPENED (driver-written exploit), REPAIRED with its name-keyed siblings (`typeof_op` applied to

##   the VALUE in program and contract; `getattr` devices take the receiver; erased locals bind a fresh value and

##   read `!x`; witnesses 2200-2208, controls 2210-2215).

## gen #36 (2026-10-15): #237 (`isinstance(<hval>, dict)` lowered to the constant `true`) and #238 (`<hval> or []`
##   replaced a truthy non-map value with the empty map) OPENED (driver-reproduced), REPAIRED (hval constructor

##   discriminant + per-constructor truthiness + faithful `.get` defaults + `hint_of`/`hval_len` fixes;

##   witnesses 2140-2148, controls 2150-2157).

## gen #36 (2026-10-15): #236 (a `@dataclass` class-body `= None` default emitted as the definite `0`;
##   `P(c).k == 0` proved; also str-on-non-str and truncated-float class-body defaults, and an omitted

##   `Optional` `__init__` param) OPENED 3501dd72, REPAIRED (witnesses 2110-2132).

## gen #36 (2026-10-14): #235 (a record's collection field built from a supplied / bound / computed
##   initialiser took the DEFINITE empty default — pinned `Seq.empty`, `Array.make 0 0`, `const None`;

##   `len(e.items) == 0` proved for a 3-element actual) OPENED f403a3ec, REPAIRED (witnesses 2006-2018).

## gen #36 (2026-10-13/14): #232 (keyword-only / positional-only params dropped -> one shared opaque
##   constant) OPENED 3e758c0b, REPAIRED 1362a212 (witnesses 1974-1985); #233 (match capture read as an

##   opaque constant) + #234 (guarded constructor arm skipping its neighbour) OPENED+REPAIRED 558304b1

##   (witnesses 1986-1999).

## gen #36 (2026-10-12): #230 (None through a container, opened gen #35) REPAIRED 37e946d0 +
##   witnesses 1920-1931; #231 (f-string format spec / `!r` discarded at IR emission — `f"{s!r}"`

##   proved `== s`) OPENED 3ca32b8d and REPAIRED 985d570d, witnesses 1932-1940. Whole-file mirror

##   re-proofs for the movers queued (g36-logs qB/qC/qD). Still open from earlier: see below.

## CURRENTLY OPEN after gen #33 (2026-09-28): **THREE — #226, #214, #221.**
##   #228 was found AND CLOSED AND GATED in gen #33. Its carrier is the campaign's own

##   gate: `bin/check-hashed-literal-purity.py` had ALREADY found the `stable_hash`

##   collision (gen #30, the same pair, 185314078), had already named the pure-`val

##   function` discriminator, had already baselined the 22 struct rows — and ended that

##   baseline "searching for one is recorded as the follow-up rather than done here". The

##   deferral sat inside a GREEN gate for three generations; doing it took seconds and

##   PROVED a false postcondition (`struct.pack('<bb6x',1,2)` 8 bytes vs

##   `struct.pack('<xxxxxxxxhxLxxxxxxxx',1,2)` 23 bytes, one emitted term). Repaired by

##   making the "w.h.p." premise a per-emission CHECK, not a wider hash. Lessons (a5)/(b5).
##
## CURRENTLY OPEN after gen #32 (2026-09-27): **THREE — #226, #214, #221.**
##   #227 was found AND CLOSED AND FULLY GATED in the same generation (77/77 planes `--slow`,

##   4034/4052, both corpora inert). Its surviving CONTAINER arm is backlog #65, not an open route.
##
## (as first written, before the gate:) CURRENTLY OPEN after gen #32: **FOUR — #227 (NEW, SEV-1), #226, #214, #221.**
##
##   * **#227 — OPEN, SEV-1, found 2026-09-27, `route227-the-opaque-kept-the-type.md`.**

##     `v = None; return v - v + 3` PROVES `\result == 3` under `#@ no_exception \all`;

##     CPython raises `TypeError`. ORDER 2 — the carrier is the campaign's OWN repair:

##     routes #44/#184/#191 replaced a definite `0` with the opaque `pycsl_none : int`,

##     which killed every VALUE-dependent falsehood and left every consequence INVARIANT

##     under the value, because the opaque kept the TYPE `int`. Route #44's own witness

##     1060 is this shape with `x + 5` — value-DEPENDENT — one algebraic identity short.

##     Repair scoped in the file: use `_erased_truthy_locals` to REFUSE arithmetic and

##     strict order, which is what route #50's facts are already used for.
##
## (previous header, gen #31:) CURRENTLY OPEN after gen #31 (2026-09-24): **THREE — #226 (NEW, SEV-1), #214, #221.**
##
##   * **#226 — OPEN, SEV-1, found 2026-09-24.** A `#@ class invariant` the CONSTRUCTOR

##     never establishes is assumed by every method. `#@ class invariant self.n >= 5` with

##     `__init__` setting `self.n = 0`, and a method returning `self.n` under

##     `#@ ensures \result >= 5`, VERIFIES; CPython returns 0. The emitted record carries

##     `invariant { n >= 5 } by { n = 10 }` — the inhabitation witness is SYNTHESIZED FROM

##     THE INVARIANT — and `__init__` is not emitted at all, so nothing checks that the real

##     constructor establishes it. annotations.md says the invariant "must hold at every

##     method boundary"; the constructor's exit is one.

##     `route226-a-class-invariant-the-constructor-never-establishes.md`.
##
## (the previous line, kept because the correction is part of the record:)
## **TWO — #214 and #221.** (This line said
## "NONE" for four hours because I copied the shape of the gen-#30 header instead of
## checking; `check-open-route-carriers.py` holds the truth and it RUNS both of their
## carriers. Corrected on discovery, and recorded as corrected.)
##
##   * **#214 — OPEN.** The other arm of the `getattr` pair: one per-site constant answers

##     two DIFFERENT receivers. `route213-214-the-getattr-devices.md` §"ROUTE #214 STAYS

##     OPEN"; carrier `route214-carrier-two-unknown-receivers.py`.

##   * **#221 — PARTIALLY CLOSED, and its own title says the claim is still assumed.**

##     `--fun` assumes a frame nobody wrote and nothing checks.

##     `route221-fun-assumes-a-synthesized-frame.md`; three carriers/controls.
##
## **ROUTE #225 IS CLOSED** — a function returning `[]` CERTIFIED `\length(\result) == 1024` while the TRUE claim `== 0` was REFUSED. `[]` lowers to the placeholder `(Array.make 1024 0)` and a Why3 array's length is immutable, so the model of the empty list is 1024 long; `xs = []; return xs` behaved identically. Ordinary total Python — no `no_exception`, no opt-in, no `\trusted`. THIS IS THE THIRD POSITION OF ONE MECHANISM: route #159 repaired the INDEXING position (gen #29) and route #196 the ARGUMENT position (gen #30, substituting the genuinely empty `(Array.make 0 0)`); the RETURN carries the false length ACROSS a function boundary, where a caller ASSUMES it and `1024 = <the real length>` makes every downstream goal vacuously provable. Repaired in `_run_pipeline`'s post-emission pass beside #159's, with an IR-LEVEL FILTER — the text alone is not enough, because `[0] * 1024` and an append target's CAPACITY wear the same spelling, and the first version broke `return [0] * 1024`'s TRUE length claim (found by a CENSUS, invisible to a 0-MOVED byte-diff — wall-lesson (t4)). Witnesses 1869 (FAIL), 1870 (PASS, both spellings), 1871 (the append path, PASS and unmoved). STILL OPEN as the named capability: the same literal is the empty-list VALUE, a 1024-element literal, and a growable local's CAPACITY — splitting the three is what closes it at the source and unblocks the `or []` conversion family (74 `\trusted` stubs, re-censused this day). See `route225-a-returned-empty-list-has-length-1024.md`.
##

## CURRENTLY OPEN after gen #30 (2026-09-21, second entry): **NONE.**
##
## **ROUTE #197 IS CLOSED** — `getattr(o, "a", 0)` on an object of UNKNOWN static type ANSWERED THE DEFAULT, and the body read it: `peek(o: Any)` PROVED `\result == 1` (emitting `let v = ref 0 in v := 0;` with `o` UNUSED — Why3 says so) while CPython answers 2 for any object with `a = 7`. FOUND BY `bin/check-getattr-erasure.py`'s OWN RATCHET NOTE, which said the UNKNOWN default was "not demonstrated to be exploitable — a contract cannot name a field of an object whose type the model does not carry". THE CONTRACT DOES NOT HAVE TO NAME THE FIELD; the BODY reads it and the contract reads `\result`. Repaired with a PER-SITE opaque (route #47's own device, hashed on the call's IR so two reads of the same expression agree — `(any int)` was tried first and refuted by the emission census, because it is fresh at every evaluation). ABSENT keeps its faithful default. Witnesses 1691 (XFAIL), 1692 (PASS). See `route197-an-unknown-typed-getattr-was-its-default.md`.
##
## (previous header, same day:) **NONE.**
##
## **ROUTES #195 AND #196 ARE CLOSED — both found by SWEEPING `bin/check-argument-coercion.py`'s OWN BASELINE with one probe** (give the callee a contract TRUE of its own body that READS the substituted property; call it with the substituted-away shape; run CPython). #195: the EMPTY-LIST placeholder became the integer `0` at an int-erased param, so `self.f([])` PROVED `\result == 1` where CPython answers 2 — repaired with `(any int)`. #196: the SAME placeholder is 1024 ELEMENTS LONG at an `array int` param, so `self.g([])` with `ensures \result == \length(ns)` PROVED `\result == 1024` where CPython answers 0, AND CPython's own answer was REFUSED — repaired with the genuinely EMPTY array, which is FAITHFUL rather than merely opaque (witness 1690 now proves what the model could not). THREE of the plane's fourteen baseline entries fell to that one probe within nine hours of the plane landing, with no emitter line changed since gen #29. See `route195-196-the-empty-list-placeholder-at-a-call-boundary.md`.
##
## (previous header, 2026-09-20:) **NONE.**
##
## **ROUTE #194 IS CLOSED, AND THE PLANE THAT LANDED ONE HOUR EARLIER IS WHAT FOUND IT.** `_coerce_to_int` answered the LITERAL `0` for an array- or map-shaped actual reaching an INT-ERASED parameter. The argument-coercion plane's baseline justification for that arm said "the receiving param is int-erased, so no law reads it" — and A CONTRACT ON AN INT-ERASED PARAM IS A LAW THAT READS IT. A callee `def f(self, p)` (un-annotated, so the `val` declares `p: int`) with the TRUE contract `ensures p == 0 ==> \result == 1`, called as `self.f(sorted(xs))`, emitted `(p__f self 0)` — the array discarded, Why3 warning `unused variable xs` — and `\result == 1` PROVED while CPython answers 2. Repaired with Why3's `(any int)` (declaration-free, because the mirror's copy is a CONVERTED method with `assigns \nothing`). Witnesses 1685 (XFAIL), 1686 (PASS). See `route194-an-erased-collection-was-the-integer-zero.md`.
##
## (previous header, same day:) **NONE.**
##
## **ROUTE #193 IS CLOSED** — the PLACEHOLDER array for an iterable the IR cannot represent had a KNOWN LENGTH. `_array_coerce_arg` answered `(Array.make 1 0)` and `sorted_1` carries `ensures { Array.length result = Array.length a }`, so `len(sorted(x for x in [3, 1, 2]))` PROVED `== 1` while CPython answers 3; the true twin was refused. Its docstring's defence — "the abstract vals have no axioms about their input CONTENTS" — says nothing about LENGTH. The placeholder is now Why3's `any (array int)`. Witnesses 1683 (XFAIL), 1684 (PASS control). FOUND BY the census route #192's lesson demanded. See `route193-the-placeholder-array-had-a-known-length.md`.
##
## (previous header, gen #30 2026-09-19:) **NONE.**
##
## **ROUTE #192 IS CLOSED** — the candidate recorded below was reproduced SEV-1 on BOTH arms and repaired. A genuine integer `0` actual was handed to the callee as the Python `None` at an `Optional[<record>]` slot (`(parser__tag self (None: option tok))`) and at a synthesized-union slot (`(Arm_0_None : _union_expect_0)`); with the callee carrying the TRUE contract `ensures start == None ==> \result == 1`, `return self.tag(0)` PROVED `\result == 1` while CPython returns 2, and the TRUE twin was refused. The `"0"` spelling is dropped from both lifts; the omitted-optional and explicit-`None` actuals still lift (they arrive as `pycsl_none` after route #191) and an integer actual is now REFUSED at L3-tc. Witnesses 1679/1680 (XFAIL), 1681/1682 (PASS). Emission byte-inert in all three directions. See `route192-a-genuine-integer-zero-is-re-tagged-as-none.md`.
##
## (the candidate, as recorded before it was probed:) **the option/union LIFT's genuine-zero arm**.
##   `expressions.py::_option_record_param_upgrade`'s sibling lift turns an actual whose lowered text is `"0"` into `(None: option <R>)`, and the `_union_*` twin beside it substitutes the union's nullary `None` arm on the same test. Before route #191 that arm could not tell the Python `None` from a genuine integer `0`, because BOTH lowered to `"0"`. After #191 the `None` actual spells itself `pycsl_none`, so `"0"` can only be a real int — and an `f(0)` into an `Optional[<record>]` / union slot would make `start is None` decide True while CPython answers False. Reproduce it before repairing: the arm may be unreachable from ordinary Python.
##
## **ROUTE #56's `None`-as-zero family is CLOSED by gen #30's route #191** — the typed `NoneExpr` leaf answers route #44's opaque `pycsl_none` in every position, so the four recorded-open STORE carriers (`xs[0] = None`, `d["a"] = None`, `self.v = None` after construction, `xs.append(None)`) are UNDECIDED instead of decided-wrong. Witnesses 1673-1676 (XFAIL), 1677/1678 (PASS controls). The repair also exposed and fixed a LATENT defect in `Module6_WhyMLTranspiler._exprir_theory_symbols` — it scraped the deferred `emit_ir` ADT theory's declared names from text INCLUDING its own prose, capturing a symbol named `function`, so the theory was being spliced into nine corpus files and one mirror that never referenced it. See `route191-a-stored-none-reads-back-as-zero.md`.

## CURRENTLY OPEN after gen #29 (2026-09-18): **route #56's `None`-as-zero family** (SEV-1, reproduced, deliberately NOT fully repaired — the general fix is a distinguishable `None` in the value model, measured to move 16 mirror emissions).
##   #56 `route56-optional-union-local-read-sentinel.md` — an Optional LOCAL reads back as the carrier's zero. gen #29 measured the same mechanism on a FIELD (closed as #183), on a LIST ELEMENT and a DICT-LITERAL VALUE (closed as #184), and left the STORE positions open: `xs[0] = None`, `d["a"] = None`, `self.v = None` (after construction) and `xs.append(None)` still read back `== 0` (CPython False). The typed `NoneExpr` arm carries them; changing it is route #56's general repair, recorded in `route184-*.md`.

##   #57 `route57-dict-get-no-default-is-zero.md` — CLOSED for the scalar codomains; gen #29 measured the non-scalar ones (List/Dict/Set/str/bool/float values) and found no false proof.
##
## gen #29 (2026-09-16/18) CLOSED AND FULLY GATED **42 SEV-1 routes** — #143 #147 #148-#186 — plus #187-#190 drafted and batteried in the same run. FIVE of them are ONE QUESTION asked five ways — WHICH CALLEE DOES THIS CALL SITE GET? — and the battery had no plane for it, so gen #29 built one (`bin/check-callee-contract-attribution.py`, 16 cells, decisive against the pre-#189 tree):
##   #166 two call sites, one stub NAME (the clash kept the LONGER declaration); #185 a `self.<field>.<m>()` receiver mis-KEYED the callee so #167/#176 looked up nothing; #186 the same mis-keying on the `raises` wrap; #188 #166's disambiguating suffix is a 100000-bucket HASH and two declarations that collide share one contract again (`ensures \result == 123` and `== 441` both hash to `_c84185`); #189 one receiver NAME bound to two classes on two branches resolved to ONE of them.

##   #187 `#@ fresh_globals` ASSUMES the module-global's constructor post-state and the module body's own mutations are not in the IR at all (`counter = Counter(); counter.n = 7` then a driver returning `counter.n` PROVED `\result == 0`). gen #29 also built `bin/check-assumed-facts.py`, which classifies every emitted `assume`/`axiom` and immediately found a silent `hash_eq_consistent_<cls>` axiom the hand census had missed.

##   #190 an OPEN-ENDED or NEGATIVE string slice is decided as the EMPTY string: the omitted bound is a `None` node lowering to the integer 0 (so the length fallback the code already wrote was dead), and `str_sub_op`'s content `ensures` was unconditional while Why3's `String.substring` answers empty for `start < 0` or `len <= 0`. `"abc"[1:]` PROVED `len == 0`.
##
## (original gen #29 header:) CLOSED AND FULLY GATED **40 SEV-1 routes** — #143 #147 #148-#184 — in fourteen batteries (H..W), every leg predicted in `driver-progress.log` and hit. The exception model was the richest vein: #167 (a stubbed method call never checks the callee `requires`), #168/#169 (the global-method inliner dropped a discarded tail return, and let caller locals capture spliced names), #170-#174 (a CAUGHT implicit exception is a live path: missing-key reads, placeholder arrays, `int()`, tuple-unpack arity, handlers for unmodelled exceptions), #175/#181 (user exception subclasses vs base-class handlers, main file AND imports), #176 (stubbed method calls never raise), #178/#182 (implicit raises inside uncontracted/imported callees), #179 (raising constructors), #180 (a walrus inside a comprehension), #183/#184 (`None` fields and collection literals).
##
## gen #28 CLOSED AND FULLY GATED THREE SEV-1 routes in ONE battery — **#144** (a `@dataclass`'s `init_params` were this class's `AnnAssign`s only; `ClassVar`s entered it and base fields did not), **#145** (the CLASS-BODY default collector keyed on `isinstance(ast.Constant)` — gen #27's #139 one level up) and **#146** (a keyword-only `@dataclass` field stayed in the POSITIONAL binding list). Witnesses 1424-1443. Every leg of the battery was predicted in `driver-progress.log` and hit.
##
## gen #27 found AND CLOSED AND FULLY GATED FIVE SEV-1 routes in TWO batteries — #138, #139, #140 (battery-A, witnesses 1404-1419) and #141, #142 (battery-B, witnesses 1420-1423). WATCH items in the handoff.
##   #138 (carrier-rerun, order 2, EIGHT shapes) gen #26's own #136/#137 namespace fences were keyed on a receiver NAME (`_nb_imported` is file-wide, so `b = builtins; getattr(b, "set"+"attr")(...)` walks past), a syntactic SHAPE (`sa = getattr(builtins, "setattr"); sa(...)`), a token SPELLING (an eval text naming none of the eight), and a LOCATION (a bare in-function eval that mutates through a call). Plus the same namespace mapping reached by a mutating METHOD CALL, by the UNBOUND-method spelling (`dict.__setitem__(f.__globals__, ...)`) and as a CALL ARGUMENT (`operator.setitem(f.__globals__, ...)`).

##   #139 (deferral-audit, order 1) `construction_synth.py:83` defers a "Constant RHS" to `field_defaults`, whose rule is `isinstance(rhs, ast.Constant)`. PYTHON DOES NOT CONSTANT-FOLD: `self.start = -7` is `UnaryOp(USub, Constant)` and `self.start = 2 + 3` is a `BinOp`, so both were name-free, uncaptured, AND exempt from route #79's unknown-marking by the same premise, and fell to the definite witness 0.

##   #140 (deferral-audit, order 1) `Module6_WhyMLTranspiler.py:289` defers raises-condition propagation to `_wrap_call_with_callee_raises_assert`, whose substitution is a positional `zip(param_names, args)` and whose default fill is gated on a `self.` receiver. On `c.f()` and `c.f(k=-5)` the callee's parameter rendered IN THE CALLER'S SCOPE and a `no_exception ValueError` contract PROVED while CPython raises.

##   Generators: carrier-rerun (#138 — every one of the five drafts' widenings) and deferral-audit (#139 and #140 — LOCATE the named guard and QUOTE ITS ACTUAL MATCHING RULE; both of these deferrals named a guard that EXISTS and WORKS, on a narrower set than the word in the comment).
##
## (previous header, gen #26:)CURRENTLY OPEN: NONE (gen #26, 2026-09-15). gen #26 found AND CLOSED AND FULLY GATED two SEV-1 routes #136 and #137 in ONE battery (witnesses 1382-1397). WATCH items in the handoff.
##   #136 a DYNAMIC (non-constant) `exec`, and an `eval` that binds through a walrus, rebind a name whose value the model has already folded/resolved — the deferral in exec_splice.py names two real handlers (`\in_scope` havoc, typed-model frame taint) and NEITHER is about a value. Seven shapes, plus the alias/attribute/computed-getattr spellings.

##   #137 gen #25's OWN #135 module-executed walk `continue`d on Lambda and FunctionDef (so a called lambda body, a class-body lambda and a def DEFAULT ARGUMENT were never scanned), `_nb_fresh_ok` enumerated five binding forms (so a comprehension target counted as FRESH), and every namespace guard in the tree keys on a builtin's SPELLING (`sa = setattr`, `ex = exec`, `builtins.setattr`, `getattr(builtins, "set"+"attr")(...)`).

##   Generators: carrier-rerun (#137, and every widening of both repairs) and deferral-audit (#136 — LOCATE the named guard and ask WHICH PLANE it covers).
##
## (previous header, gen #25:) CURRENTLY OPEN: NONE (gen #25, 2026-09-15). gen #25 found AND CLOSED AND FULLY GATED six SEV-1 routes #130-#135 in two batteries (A: #130 #131 #132 #133 #134, commit 2313ded3; B: #135). WATCH items in the handoff.
##   #130 an imported name bound twice keeps the FIRST import. #131 a builtin rebound by an assignment is still the builtin.

##   #132 the constant folders' 'bound exactly once' premise (rebinding + mutation/alias arms). #133 a nested def in a method replaces a sibling method. #134 route #116's globals-lookup recognizer premise.

##   Generators: carrier-rerun (#130 #131 #133), witness-census (#132).
##
## (previous header, gen #24:) CURRENTLY OPEN: NONE (gen #24). gen #24 found AND CLOSED AND FULLY GATED nine SEV-1 routes #121-#129 in two batteries (A: #121 #123 #124 #125 #127 #128 + #122 compound arms, commit 629c80bb; B: #122 nested arm, #126, #129). WATCH items in the handoff.
##   #121 a user decorator is silently dropped (`@swap` returning `abs`).

##   #122 a def inside if/try, or nested in another function, is hoisted to module scope; textually last def wins.

##   #123 a subclass class-body binding (`m = lambda self: 2`) overriding an inherited method is ignored.

##   #124 `from m import *` after a def rebinds the name silently.

##   #125 multiple inheritance resolved depth-first, not by C3 MRO.

##   #127 namespace patching past #119: `__builtins__`, aliases, computed receivers, non-literal setattr on a cls parameter.

##   #128 the descriptor protocol (`__get__`/`__set__`) is ignored.

##   REPAIRS: #121 #122(module-compound arm) #123 #124 #125 #127 #128 drafted as ONE battery (battery-A); #122(nested arm) + #126 are battery-B (Module 6).

##   #129 a `global` write is dropped (fresh local) and reads of a non-constant module variable are one constant across it (OPEN, not scoped into a battery).

##   #126 a lifted nested def's closure variable becomes ONE global opaque constant (`f(1) - f(2) == 0` proves).

##   Generators: carrier-rerun (#121-#124, re-probing gen #23's VACUOUS function-as-value rows with values that

##   do not trip the duplicate-symbol fence, and the #118 rule (1) scope keys), hand (#125).
##
## (previous header, gen #23:) CURRENTLY OPEN: NONE — #109, #111–#120 all CLOSED AND FULLY GATED
##
##   >>> **gen #23 CLOSED AND FULLY GATED NINE SEV-1 ROUTES IN TWO BATTERIES: #111, #112, #113,

##   >>> #114, #115, #116, #117 (combined battery-2, e91bb786) and #109, #118 (battery-3).** #111/#112 were gen #21/#22's open items

##   >>> (dict value erased to the empty map in a field store / a dict literal argument);

##   >>> #113-#118 are NEW this generation:

##   >>>   #113 `_coerce_to_int` hashed the TEXT of any paren-wrapped term with a comma — a call

##   >>>        with `"a,b"` in a string argument, a tuple projection (corpus 0607 passed on it).

##   >>>   #114 a GENUINE tuple dict key was keyed by its text: `(y, 1)` same key after `y += 1`.

##   >>>   #115 an unrecognised Python expression (`(lambda y: y + 1)(x)`, `fs[0](x)`) lowered to 0.

##   >>>   #116 `F("name")(args)` lowered as a call to the function the string names (a pure_ast

##   >>>        recognizer applied to every program). Namespace-mutation carrier closed by #118.

##   >>>   #117 a list local returned early on the int Return path was the literal 0.

##   >>>   #118 a rebinding of a function/method name (`inc = dec`, class-body `m = n`, walrus,

##   >>>        `global`, `_g["inc"] = dec`) is ignored by call resolution. REFUSED now

##   >>>        (PYCSL-IR-FUNCTION-NAME-REBOUND); it also closed #116's last carrier.

##   >>>   #119 (order 2) every non-Name rebinding and instance-level shadowing survived #118 — closed in

##   >>>        batteries 4b+5.  #120 attribute-access hooks ignored — closed.

##   >>> Generators: substring-census (#113 #114), NEW witness-census (#115 #117), carve-out-census

##   >>> (#116), carrier-rerun (#118 — found on gen #23's OWN #116 fence).
##
##   **#110 was found AND CLOSED AND FULLY GATED in the same generation (gen #21).**
##
##   >>> **#110 and #111 are NEW THIS GENERATION**, both from the SUBSTRING-CENSUS generator,

##   >>> both SEV-1, both with BOTH DIRECTIONS MEASURED. **#110 is CLOSED AND GATED; #111 is

##   >>> NOT REPAIRED and is the highest-ranked item on the board.**

##   >>>   #110 CLOSED: `_coerce_to_int` replaced a call argument with the literal `0` when the

##   >>>        lowered text started with an internal op spelling — and SEVEN of those

##   >>>        spellings (`any_1`, `all_1`, `sorted_1`, `list_new_arr`, `array_slice`,

##   >>>        `map_update_some`, `map_update_none`) are ordinary Python identifiers.

##   >>>   #111 OPEN: a dict/set self-field is clobbered with the everywhere-empty map when the

##   >>>        lowered RHS is not alphanumeric. **NEEDS NO ADVERSARIAL NAMING** —

##   >>>        `self.b = self.a` is ordinary Python. This is the worst of the three.

##   >>> **#109** (`order = 2`) remains open and untouched by gen #21: the `_objstate_w`

##   >>> frame fallback exists in the `self.` arm only.
##
##   >>> **#107 and #108 are CLOSED AND GATED by gen #21 (2026-09-14)** — one structural

##   >>> repair for both directions (the `else:` is lowered as a SIBLING of the try behind a

##   >>> completion flag, never appended to the try body behind a substring test), an

##   >>> ELEVEN-LEG battery with ten exact predictions and one recorded miss, and corpus

##   >>> regression witnesses 1298–1302. Suite baseline moved to **3428/3446, 18 failures**.
##
##   >>> The gen #19 gate-status note that used to sit here (about #101–#106 being

##   >>> "REPAIRED BUT NOT YET GATED") is RESOLVED: gen #20 completed that battery on all

##   >>> nine legs. #101–#106 are repaired AND gated. Do not re-gate them.
##
##   **gen #18 (2026-09-13): #101 REPAIRED, and THREE MORE ROUTES FOUND INSIDE ITS OWN

##   CARRIER LIST — #102, #103, #104 — all SEV-1, all CLOSED AND GATED.** The whole family

##   is one sentence: **the frame collectors for a bodyless `val` were keyed on the NODE TYPE

##   carrying the write target, and the obligation is about the PATH BEING WRITTEN.** Four

##   spellings of "this stub writes through a parameter" existed and the guards covered one.
##
##   - **#101** `#@ assigns seq[idx]` (IR `Subscript`) — no `writes`, and it never reached

##     `_unframed_regions` either, so ROUTE #98's OWN REFUSAL COULD NOT FIRE. SHIPPED in

##     `src/pycsl_lib/oper/__init__.py:175`, reachable with no `\trusted` marker in sight.

##     File: `route101-subscript-assigns-on-bodyless-val-emits-no-frame.md`.

##   - **#102** a bare `#@ assigns g` (IR `Var`) — same hole, fourth spelling. Gen #17 NAMED

##     this carrier and said CHECK it rather than assume; checked, it was LIVE.

##     File: `route102-bare-var-assigns-on-a-bodyless-val-drops-the-frame.md`.

##   - **#103** a stray `#@ assigns \nothing` beside a real target — `nothings` non-empty

##     disarmed BOTH `if _val_targets and not nothings` AND `if _unframed_regions and not

##     nothings`, i.e. one clause switched off the frame AND route #98's refusal. ORDER 2:

##     that `and not nothings` is route #96's OWN repair. SURVIVED #101's repair.

##     File: `route103-a-stray-nothing-disarms-the-whole-frame-and-the-refusal.md`.

##   - **#104** `#@ assigns self.xs[0]` on a `\trusted` METHOD — `_build_method_writes_map`

##     keyed on the node type too, so the method's `val` got no frame. And there is NO range

##     escape hatch for a self-field (`self.xs[0..1]` is a PARSE ERROR), so the single-index

##     spelling was the ONLY way to say it and it was the unsound one.

##     File: `route104-self-field-subscript-assigns-drops-the-method-frame.md`.
##
##   >>> **A REFUSAL INSTALLED TO OBSERVE A RESIDUE IS KEYED ON THE SPELLING ITS AUTHOR WAS

##   >>> LOOKING AT.** #98 installed the observer and covered one spelling of four.
##
##   **AND THE SAME SHAPE IN THE `no_exception` CLAUSE — #105 and #106, also CLOSED:**

##   - **#105** route #100's repair covered ONE RECEIVER. `_module_func_raises` is keyed on

##     the IR name `<cls>__<m>`; every non-`self.` receiver was handed its SOURCE spelling

##     (`"c.f"`), the lookup missed, and the wrap returned `inner` untouched. The correct

##     key was already computed 600 lines above and never threaded.

##     File: `route105-raises-obligation-dropped-for-non-self-receivers.md`.

##   - **#106** a module-global receiver is INLINED before Module 6 ever looks, so there is

##     no call left to wrap — and the caller is emitted carrying `raises { ValueError }`

##     while its source says `#@ no_exception ValueError`. SURVIVED #105's repair.

##     File: `route106-inlining-deletes-the-call-and-with-it-the-obligation.md`.
##
##
##   **gen #20: #101-#106 ARE NOW FULLY GATED (all 9 battery legs green), AND THREE NEW SEV-1

##   ROUTES WERE FOUND. NONE OF THE THREE IS REPAIRED.**

##   - **#107** a try's `else:` block is SILENTLY DELETED when its lowered text merely CONTAINS

##     the substring `raise` — INCLUDING FROM AN ORDINARY IDENTIFIER'S NAME. A dead local named

##     `praiseworthy` deletes the whole block; `ensures \result == 1` then PROVES while CPython

##     returns 5. BOTH DIRECTIONS MEASURED. Route #37's fence tests four statement KINDS only.

##     File: `route107-a-substring-raise-in-an-identifier-deletes-the-else-block.md`.

##   - **#108** a callee's raise inside an `else:` is CAUGHT by that same try (Python never

##     does this) AND dropped from the function's `raises` summary, because `_callee_raised_in`

##     skips `orelse`. A `#@ no_exception` caller PROVES while CPython raises. SURVIVED the

##     #100 -> #105 chain: that chain fixed the receiver KEY; here the SET is empty.

##     File: `route108-a-callee-raise-in-an-else-block-is-caught-and-unreported.md`.

##     >>> #107 AND #108 ARE THE TWO DIRECTIONS OF THE SAME CODE — REPAIR THEM TOGETHER.

##   - **#109** the `_objstate_w` fail-closed FRAME fallback exists in the `self.` arm only;

##     a record-var / module-global receiver mints `val c_bump_0 () : unit` with NO frame and

##     NO receiver, so `#@ assigns \nothing` proves over a mutating call. `order = 2` — the

##     carrier IS the `#32 SPIKE` repair. Fourth link in #70 -> #100 -> #105 -> #109.

##     File: `route109-record-var-receiver-loses-the-objstate-frame-fallback.md`.
##
## (gen #16: #97, #98, #99 and #100 all CLOSED AND GATED.)
##
##   **#100 FOUND *AND* CLOSED 2026-09-13 (gen #16), SEV-1.** A `#@ no_exception E` on a

##   METHOD was proved with NO OBLIGATION AT ALL. `_wrap_call_with_callee_raises_assert` had

##   exactly ONE call site (the module-function path) and is keyed on the IR function name, so

##   a `self.<m>(...)` call never reached it: the callee's `#@ raises E when P` never produced

##   the `assert { not P }; try … with E -> absurd` the free-function path emits. Identical

##   contracts and bodies: as free functions REFUSED, as methods `Verification SUCCESS!`, while

##   CPython `Helper().caller(-1)` RAISES ValueError.

##   >>> **AN ABSTRACTION THAT IS CONSERVATIVE FOR WHAT A CALLER MAY *ASSUME* IS PERMISSIVE FOR

##   >>> WHAT A CALLER MUST *DISCHARGE*.** The val already carries the callee's `ensures`

##   >>> (measured), so the path VISIBLY carries a contract and reads as sound — the

##   >>> transmission set had been enumerated as "what the caller may assume", the half that

##   >>> HELPS. Losing a postcondition costs a proof; losing an effect obligation costs the CHECK.

##   Repair reuses the existing wrap, keyed on the resolved IR name. THE CAPABILITY ARM CHOSE IT:

##   the alternative (transmit `raises` onto the val) was spiked, closes the exploit, and emits an

##   UNCONDITIONAL `raises { E -> true }` that also breaks the guarded caller — refusing

##   everything instead of the wrong thing. Witnesses 1285-1287. This is the `no_exception`

##   sibling of route #70 (a dotted stub drops the callee PRECONDITION): the shape recurs once

##   per obligation kind, so sweep every consumer keyed on a callee name.
##
##   **#99 FOUND *AND* CLOSED 2026-09-13 (gen #16), SEV-1 — ON THE GATE ROUTE #94 BUILT.** A

##   `@cached_property` reading `self.a` PROVED `ensures \result == self.a` while `a` was

##   mutated by a free function taking the object as a parameter (`def bump(c: C): c.a = ...`).

##   CPython after one bump: `total=0, a=1`, so the proved postcondition is FALSE — the stale

##   cache (UB-7.7) that #94's gate exists to reject. Spell the identical mutation as a METHOD

##   and it was refused all along; only the RECEIVER differed.

##   **TWO INDEPENDENT NARROWINGS, AND ONLY BOTH FIXES CLOSED IT:** (1) the collector admitted a

##   `FieldAssign` only when `object == "self"` — fixing this ALONE left the exploit STILL

##   PROVING; (2) the check ran at the end of `visit_ClassDef`, whose comment claimed "by here

##   `generic_visit` has emitted every method of the class, SO THE SET IS COMPLETE" — true of

##   that CLASS, false of a module-level function defined after it. Moved to `visit_Module`.

##   >>> **#94 MOVED THIS CHECK ONE LEVEL (function -> class) WHEN IT NEEDED TO MOVE TWO

##   >>> (function -> class -> MODULE). Its own lesson — a check needing a whole-program fact

##   >>> cannot live in a per-node visitor — was right, and A CLASS IS STILL A NODE.**

##   Capability preserved against #94's own stated fear of a blanket ban: witness **1284 PROVES**.

##   Witnesses 1282-1284. Residue named, NOT smuggled: `mutated` is still a flat set of field

##   NAMES (20 of 72 names are shared across classes), a PRE-EXISTING over-refusal unchanged in

##   kind; keying on `(class, field)` is the right follow-up.
##
##   **#98 FOUND *AND* CLOSED 2026-09-13 (gen #16), SEV-1 — AND ITS CARRIER WAS #96's OWN

##   REPAIR.** Route #96's frame repair decided whether an array-region `assigns` becomes a

##   `writes` clause by testing `a.get("base")` — the **SOURCE** identifier — for membership in

##   `_current_array_param_names`, which is built by regexing the **ALREADY-EMITTED** signature

##   (post-`whyml_ident`, which lowercases a leading capital and prefixes WhyML reserved words

##   with `py_`). Two name spaces, one membership test, and the whole of #96 came back for every

##   renamed parameter. MEASURED: param `a` -> `writes { a }` -> exploit refused; param `model`

##   -> `val scramble (py_model: array int) ...` with NO writes -> **PROVED `\result == 7`**;

##   param `Buf` -> same, PROVED. CPython: `driver([7,7,7,7]) == 0`. `WHYML_RESERVED` is full of

##   ORDINARY parameter names — model, range, check, label, result, old, ref, float, to, by, type.
##
##   >>> **A CARRIER SURVIVING A REPAIR IS A SECOND ROUTE, NOT A FAILED REPAIR.**
##
##   **AND THE SKIP'S OWN COMMENT NAMED THE EXPLOIT AND CALLED IT SAFE** — "FAIL-CLOSED, and

##   deliberately so ... Any such residue stays visible as an un-framed val." Wrong twice, and

##   this is the transferable part: (1) **"FAIL-CLOSED" WAS A CLAIM ABOUT THE EMITTER, NOT THE

##   PROVER** — emitting nothing is fail-closed for the emitter (no ill-typed `writes`) and

##   fail-OPEN for the verifier, which is told the stub is PURE; dropping a frame clause is NEVER

##   conservative, since an un-framed `val` is the STRONGEST possible claim. (2) **"STAYS VISIBLE"

##   NAMED NO OBSERVER** — no gate, no plane, no ratchet counted that shape. Visible to whom?

##   Repair: compare in ONE name space, and GIVE THE RESIDUE AN OBSERVER

##   (`PYCSL-UNFRAMED-REGION-ASSIGNS`), negative-tested and with a demonstrably NON-EMPTY

##   population. Witnesses 1278-1281. Capability arm re-measured: 1271 still PROVES.
##
##   **#97 FOUND-AT-HEAD *AND* CLOSED 2026-09-13 (gen #16), SEV-2.**

##   `--check-behavioral-subtyping` emitted **NO refinement goal at all** when the base class had

##   no instance fields, and reported "All contracts formally proven." A class becomes a record

##   `type_decl` only `if fields or bases:`, so a STATELESS base — the interface / pure-behaviour

##   base — is absent from `records` in `ir_resolve.apply_inheritance`, whose `if base is None:

##   continue` skipped the ONLY place the Liskov override pair is ever recorded. **THE FAILURE IS

##   INVERTED WITH RESPECT TO GOOD PRACTICE: the cleaner the base class, the less checking it

##   received.** Minimal pair differing by ONE `__init__`: with a field, 1 goal and FAILED;

##   without it, 0 goals and SUCCESS. Repair splits the loop's two jobs — the MERGE stays gated on

##   the base carrying a record, the RECORDING goes unconditional (monotone: adds goals, removes

##   none). CO-LANDING FAIL-CLOSED HALF, not optional: `_emit_subtyping_goals`' `if sub_fn and

##   base_fn:` was a SECOND silent drop on the same obligation and now RAISES

##   `PYCSL-SUBTYPING-PAIR` — *a guard that stops being silent in one shape and stays silent in

##   the next has been NARROWED, not repaired.* Witnesses 1273-1277.
##
##   >>> **THE INDEX LAGS THE ROUTE FILES. TRUST THE FILES.** This header claimed

##   >>> "CURRENTLY OPEN: NONE" for the whole of gen #14's window while route #96 sat OPEN in

##   >>> its own file, and the window #6 supervisor had to carry the correction by hand. If you

##   >>> close or open a route, edit THIS BLOCK in the same increment.
##
##   **#96 CLOSED AND GATED 2026-09-13 (gen #15), FAIL-CLOSED, AND ITS DEFERRAL'S PREMISE WAS

##   REFUTED.** A bodyless `val` (`\trusted` / `\abstract` / imported) SILENTLY DROPPED an

##   array-region `assigns`: `_emit_frame_condition`'s val arm collected only `Attribute`/

##   `FieldGet` targets and `continue`d past every `AssignsRegion`, so the emitted val carried

##   NO `writes` clause and Why3 treated the stub as PURE. A caller kept `arr[0] == 7` across a

##   stub whose own contract says it writes `arr[0]` and PROVED `\result == 7`, while CPython

##   returns **0**. `\trusted` is the DECLARED TCB BOUNDARY, so the `assigns` a reviewer

##   certifies was exactly the part the emitter threw away.
##
##   Gen #14 found it and deliberately left it open, because the blast radius could not be

##   censused in its remaining window. **THE BLAST RADIUS WAS EMPTY** — an instrumented census

##   of the exact branch (probe positive- AND negative-tested first) found **0 val x region

##   sites across 3567 files**: 1193 pycsl-reference, 2217 python-reference, 104 `pycsl_lib`,

##   53 mirrors, with a planted positive control hitting through the same harness. 48 in-tree

##   functions carry a region `assigns` and not one is trusted/abstract.
##
##   >>> **THAT EMPTINESS IS WHY THE BUG SURVIVED, NOT WHY IT WAS HARMLESS.** The cell of the

##   >>> 2x2 nobody in-tree writes is the cell no test covered. And: **a deferral justified by

##   >>> an UN-MEASURED blast radius should be converted into a measurement before it is

##   >>> inherited as a cost** — the estimate was the only expensive thing about this route.
##
##   Both directions: exploit and `\abstract` arm now REFUSE; the capability twin (a trusted

##   stub with BOTH a region `assigns` and an array `ensures`) STILL PROVES. Soundness of the

##   whole-array over-approximation is EQUALITY with the verified-body baseline, not strictness:

##   a real body writing one cell already havocs the whole array, so 1269 (let) and 1270

##   (trusted twin) now agree where before exactly one of them proved. Fail-closed residue is

##   empty and each fence is quoted from an executed run (`_check_assigns_regions`

##   PYCSL-SEM-ASSIGNS for a global or non-list base; a Why3 TYPE REJECTION for `Any`).

##   Witnesses 1267-1272.
##
##   **#94 CLOSED AND GATED 2026-09-13 (gen #13), FAIL-CLOSED.** A `@cached_property` reading a

##   MUTABLE field passed the UB-7.7 referential-transparency gate, and **CPython contradicts

##   the proved postcondition** (`total = 0, self.a = 1` after one `bump()`, so `c.total == c.a`

##   is False while `ensures \result == self.a` was proved). Two reasons the gate missed it:

##   `_detect_purity` is about `assigns`, not reads; and `_reads_any` matches only

##   `type == "Var"`, so a `FieldGet` is invisible to the `#@ shared` clause. Repaired by

##   `_check_memoized_field_reads`, run from the POST-CLASS hook — **the first version, written

##   in the obvious place (`_check_memoization_soundness`, a per-function visitor), silently did

##   NOTHING, because the mutator is defined after the memoized reader and the mutated-field set

##   was empty. Only rule (l)'s negative test caught it.** Witnesses 1257 (exploit) / 1258 (a

##   construct-only field still proves, so it is not a blanket field-read ban). Confined: no

##   caller can consume the false postcondition (`cached_property` read across functions emits

##   an unbound symbol).
##
##   >>> PREVIOUSLY: the ledger was EMPTY at the start of gen #13, and THREE severity-1

##   >>> routes (#91, #92, #93) were sitting in ONE function. An empty ledger is a prompt to

##   >>> generate, not a floor — that is now five times over.
##
##   >>> AN EMPTY LEDGER IS A PROMPT TO GENERATE, NOT A FLOOR. It emptied three times in

##   >>> window #5 and a severity-1 route appeared after each of the first two; it emptied a

##   >>> fourth time at #89 and #90 appeared within the hour.
##
##   **#90 CLOSED AND FULLY GATED 2026-09-12 (gen #12), FAIL-CLOSED, COSTING EXACTLY ONE

##   CORPUS FILE.** `is True` was lowered to INTEGER EQUALITY on a `bool` annotation nothing

##   enforces: `if x is True:` emitted literally `if (x = 1)` with the param emitted as a

##   plain `int`, so under `requires x == 1` the guard was trivially true and `\result == 1`

##   PROVED while CPython returns 0 (`1 is True` is False; `True` is a distinct singleton

##   from the int 1, even though `1 == True`). **THE WHITELIST WAS ANTI-CORRELATED WITH

##   BOOL-NESS**: it ADMITTED the one source nothing enforces (an annotation — on a param

##   AND on a local) and REFUSED the two that are provable BY CONSTRUCTION. Three operators

##   lied (`is True`, `is not True`, `is False`), and the CROSS-CALL escalation reached it

##   from PyCSL source alone — the front-end accepts the int literal `1` for a `bool` param.

##   MECHANISM: a composition of TWO ROUTES THIS CAMPAIGN ALREADY CLOSED — #42's whitelist

##   admitted the arm because "the emitter can SHOW X is a Python bool" (it read a

##   DECLARATION) and #51 had ALREADY PROVED an annotation here is not a fact. **A CONTROL

##   THAT ADMITS AN ARM "BECAUSE WE CAN SHOW T" MUST CITE THE ENFORCEMENT OF T, NOT ITS

##   DECLARATION.** REPAIR: a four-line DELETION of that arm, plus a fix to the guard's own

##   error message, which closed with "Write `X == True`, **or annotate `X` as `bool`**" —

##   **THE REMEDIATION ADVICE WAS THE EXPLOIT.** GATES: 34/34 planes rc=0; pycsl-reference

##   byte-diff **0 MOVED, 1 GONE (exactly the predicted 1057), 0 APPEARED** with populations

##   asserted (1007 - 1 + 2 = 1008); python-reference 2203/2203 and MIRROR 53/53 fully inert;

##   zero-byte 0 on ALL SIX sides; conformance 38/38 + 38/38, determinism 10/10, no golden

##   re-blessed; fidelity rc=0 887 verbatim (the mirror's `_expr_to_whyml` is a stub, so no

##   mirror body owed); coverage 549 KEPT; **suite 3372/3390, ZERO XPASS, rc=1, failure set

##   18 vs 18 BYTE-IDENTICAL**, population 3390 = 3383 + exactly the seven new files;

##   value-differential grown 52 -> 56, rc=0. NEGATIVE-TESTED per rule (l): restoring the

##   deleted arm makes 1240/1243/1244 PROVE THE FALSE CLAIM AGAIN. Metric unchanged.

##   **COST, CENSUSED BY AST OVER AN ASSERTED 1179+2217+94+104+53 FILES AND RE-RUN

##   INDEPENDENTLY: of 92 `is`-against-bool sites, EXACTLY ONE took the deleted arm** —

##   corpus 1057, route #42's own "faithful" control, **whose claim is ITSELF FALSE** (its

##   `requires b == True` is met by `b = 1`, for which CPython returns 0, not 7). It is now

##   an expected-FAIL witness carrying its mechanism. Its old docstring warned "it fails if

##   the whitelist is ever narrowed to nothing" — **A CORPUS CONTROL WRITTEN TO PREVENT

##   OVER-NARROWING BECAME THE RATCHET THAT PROTECTED AN UNSOUND ARM FOR 48 ROUTES.**

##   AND MEASURING THE OVER-BREADTH CONTROL REVEALED WHAT #42's WHITELIST ACTUALLY WAS: its

##   comparison and `not` arms are ADMITTED THEN ILL-TYPED (`if ((a > b) = 1)` — a Why3

##   `bool` compared to an `int`), verified PRE-EXISTING at the pre-repair HEAD. So the

##   four-arm whitelist was **ONE TAUTOLOGY PLUS ONE UNSOUND ARM**, with the two arms meant

##   to carry the real capability dead and unrun for 48 routes. 1245 pins the literal arm

##   (PASSES); 1246 records the comparison arm as a CERTIFIED BOUNDARY with a REOPENING

##   CONDITION. See `route90-is-true-lowered-to-int-equality-on-an-unenforced-bool-annotation.md`.
##
##   **#89 CLOSED AND FULLY GATED 2026-09-12 (gen #12), FAIL-CLOSED IN ALL FOUR DIRECTIONS.**

##   The repair landed at e7a92460; gen #12 discharged the last owed gate and re-measured the

##   rest. **34/34 planes rc=0** at the repaired HEAD (that battery re-runs BOTH differential

##   corpora as planes, so value-differential 52 and no-exception-differential 45 are green at

##   HEAD too). pycsl-ref byte-diff **2 MOVED = EXACTLY the two expected-FAIL witnesses, ZERO

##   pre-existing files**, and the two CONTROL witnesses 1238/1239 BYTE-IDENTICAL — the

##   evidence that #85's and #87's completeness gains are untouched; python-ref 2203/2203 and

##   MIRROR 53/53 byte-identical; zero-byte 0/0 both sides. IR conformance **38/38 + 38/38

##   with NO golden moved DESPITE A NEW IR KEY**, and that key was NEGATIVE-TESTED per rule

##   (l): with preamble.py's hand-written `rec_info` copy line removed, witness 1236 PROVES

##   THE FALSE CLAIM AGAIN, so the documented Module-6 silent-no-op trap is real and the key

##   is load-bearing. fidelity rc=0 887 verbatim; mirror-coverage 549 KEPT; bespoke-model-drift

##   OK with no `--update`. **SUITE 3365/3383, ZERO XPASS, rc=1, failure set 18 vs 18

##   BYTE-IDENTICAL** with both populations asserted — and gen #12 PROVED BY MEASUREMENT that

##   this run exercised the REPAIRED tree (the log names 1236-1239, the count moved 3379 ->

##   3383 by exactly those four, and their verdicts XFAIL/XFAIL/PASS/PASS are producible only

##   with the repair in). PER-WITNESS: both false claims refused, both controls still faithful.

##   RULE (p) DISCHARGED LIVE: all four carriers re-run at HEAD are REFUSED (q4 and q5 flipped

##   from PROVED). **#89 closes FAIL-CLOSED, NOT FAITHFULLY** — unlike #85/#87/#88 — which is

##   the honest answer for a conditional store, since neither literal is the field's value.

##   Metric unchanged: markers 459 - grep 484 - offset 25 - unattached 0.
##
##   **#90 — `is True` IS LOWERED TO INTEGER EQUALITY ON A `bool` ANNOTATION NOTHING ENFORCES

##   — FOUND 2026-09-12 (gen #12).** `if x is True:` emits literally `if (x = 1)`, and the

##   `bool` parameter is emitted as a plain `int`. With `requires x == 1` the guard is

##   trivially true, so `\result == 1` PROVES while CPython returns 0 — `1 is True` is False,

##   because `True` is a distinct singleton from the int 1 even though `1 == True`. The TRUE

##   twin is refused, `is not True` lies the same way, and **the CROSS-CALL escalation proves

##   it from PyCSL source alone: the front-end accepts the int literal `1` as the actual for a

##   `bool` parameter.** MECHANISM — A COMPOSITION OF TWO ROUTES THIS CAMPAIGN ALREADY CLOSED:

##   route #42's `is` whitelist ADMITS this arm on the ground that "the emitter can SHOW X is a

##   Python bool", and route #51 ALREADY PROVED that an annotation in this codebase is not a

##   fact. **A CONTROL THAT ADMITS AN ARM "BECAUSE WE CAN SHOW T" MUST CITE THE ENFORCEMENT OF

##   T, NOT ITS DECLARATION.** See `route90-is-true-lowered-to-int-equality-on-an-unenforced-bool-annotation.md`.
##
##   **#88 CLOSED AND FULLY GATED 2026-09-12 (gen #11), FAITHFULLY ON THREE OF SIX CARRIERS.**

##   34/34 planes; pycsl-ref 7 MOVED = a subset of its own 8 witnesses with ZERO pre-existing

##   files (and the ONE witness that did NOT move is 1234, the single-store over-breadth

##   control — the census made executable); python-ref 2203/2203 and MIRROR 53/53 inert;

##   conformance 38/38 + 38/38 with no golden re-blessed; fidelity rc=0 887 verbatim; suite

##   **3361/3379, ZERO XPASS, rc=1, failure set 18 vs 18 BYTE-IDENTICAL** with both

##   populations asserted; value-differential grown **45 -> 50**, rc=0. Metric unchanged.
##
##   **#89 — A CONDITIONAL STORE TO A *COLLECTION* FIELD IS THE ARM ROUTE #83's REPAIR

##   FENCED OFF, AND ROUTES #85/#87 MADE IT DECIDABLE — FOUND 2026-09-12 (gen #11).**

##   `C(0).xs[0] == 7` PROVES where CPython returns 1: the model takes the CONDITIONAL

##   store's literal UNCONDITIONALLY (dict field identical). #83's `(any int)` override is

##   gated on `field_types not in _NONSCALAR`, i.e. SCALARS ONLY — correct when the

##   collection arms carried no decidable contents, and re-armed the moment #85/#87 made a

##   field literal's contents faithful. **A COMPLETENESS GAIN CAN RE-ARM A SOUNDNESS DEFECT

##   AN EARLIER REPAIR HAD FENCED OFF, WITHOUT TOUCHING EITHER OF THEM.** Repair scoped:

##   extend the override with #86's `any_map` and #87's `any_array`, both already built and

##   already spiked. See `route89-conditional-store-to-a-collection-field.md`.
##
##   **#88 — A SCALAR FIELD'S *LAST* STORE IN `__init__` LOSES TO ITS *FIRST*, AND AN

##   `AugAssign` TO A FIELD IS INVISIBLE — FOUND 2026-09-12 (gen #11).** Six carriers, both

##   directions, plus a CROSS-CALL escalation; four controls bound it (a single store is

##   faithful, `lit-then-param` is faithful, and BOTH collection arms — #85's dict and #87's

##   list — are ALREADY last-wins and faithful, so only the SCALAR `field_defaults` path is

##   affected). `_collect_class_fields` guards on `target.attr not in field_names_seen`

##   (first-wins) while `_collect_init_construction` APPENDS to `init_body` (so an earlier

##   param store beats a later literal, carrier c4 — the defect runs in BOTH directions).

##   Neither path reads `ast.AugAssign`, which also makes a NESTED `self.n += 5` a

##   **SURVIVOR OF ROUTE #83's REPAIR**. See `route88-init-field-last-store-loses-to-first.md`.

## **AN EMPTY OPEN LIST IS NOT A FLOOR. gen #10 EMPTIED IT THREE TIMES AND FOUND A NEW
## SEVERITY-1 ROUTE AFTER EACH OF THE FIRST TWO.** It means the hunt must GENERATE
## candidates rather than work a queue. What produced them, in order: re-probing a
## carve-out candidate an earlier generation had parked in the "LOW-VALUE TAIL" (#85);
## noticing a carrier that SURVIVED the repair that closed its siblings (#86); and probing
## a SECOND OPERATION on a carrier a control table had already called fail-closed (#87).
##
##   **#87 — A LIST FIELD'S LITERAL KEEPS ITS LENGTH AND LOSES EVERY ELEMENT TO A DEFINITE

##   `0` — FOUND AND CLOSED 2026-09-12 (gen #10), FAITHFULLY.** Gates: 34/34 planes;

##   conformance 38/38 + 38/38 (see below — it FAILED first and the REPAIR was narrowed, the

##   golden was NOT re-blessed); fidelity rc=0; python-ref 2203/2203 and MIRROR 53/53 inert;

##   pycsl-ref **4 MOVED, and the moved set ASSERTED MECHANICALLY to equal exactly this

##   route's own four witnesses — ZERO pre-existing corpus files moved**; suite **3350/3369,

##   ZERO XPASS, rc=1**, failure set 19 vs 19 byte-identical. Witnesses 1222-1225.

##   **THE IR CONFORMANCE GATE CAUGHT A REAL OVER-REACH.** The first build recorded EVERY

##   constant list literal, and golden 0595 gained an IR key while its EMISSION did not move

##   (core-only conformance stayed 38/38). Rule (k) forbids re-blessing, and the right answer

##   was to stop emitting information that carries none: an ALL-ZERO literal already lowered

##   faithfully. **The condition is "all elements ZERO", not "all EQUAL"** — `[7,7,7]` got

##   `Array.make 3 0` and must still be captured; witness 1225 is the negative test for

##   exactly that, without which the narrowing would close #87 for `[1,2,3]`, leave it open

##   for `[7,7,7]`, and pass every other test.

##   ORIGINALLY RECORDED AS:** `self.xs = [1,2,3]`

##   then `c.xs[0]` proved `\result == 0` where CPython returns 1; the true twin was refused;

##   and the zero-filled array DISCHARGED a callee's `#@ requires xs[0] == 0` that the program

##   violates. `_field_default` returned `(Array.make <len> 0)` — right about the shape, wrong

##   about the contents, and `Array.make` makes the wrong contents DECIDABLE.

##   **FOUND BY PROBING A SECOND OPERATION ON A CARRIER MY OWN ROUTE-#85 CONTROL TABLE HAD

##   DECLARED "fail-closed" AN HOUR EARLIER.** That control ran `len(c.xs)` only, and the

##   LENGTH is faithful. **A CONTROL IS A MEASUREMENT ABOUT THE OPERATION IT RAN, NEVER A

##   THEOREM ABOUT THE TYPE** — route #81's generator, and #87 is its mirror image (#81: length

##   wrong, elements right; #87: length right, elements wrong). For a collection, ALWAYS probe

##   BOTH the shape and the contents.

##   **THE FIRST REPAIR THIS GENERATION THAT MOVES CORPUS BYTES** (6 sites, all in the corpus).

##   The emission was designed so an ALL-EQUAL literal keeps the plain `(Array.make n v)` it

##   already emitted, so the three real affected files (all-zero literals) stay byte-identical.
##
## **AN EMPTY OPEN LIST IS NOT A FLOOR — gen #10 EMPTIED IT AND THEN FOUND TWO MORE ROUTES
## IN THE SAME SESSION.** It means the hunt must GENERATE candidates rather than work a
## queue. What produced #85 and #86 after the queue was empty: re-probing a carve-out census
## candidate that an earlier generation had ranked in the "LOW-VALUE TAIL" and left unprobed.
## The census's honest hit rate is now **3 hits in 7 probes**, and the "low-value" label is
## not evidence. FOUR candidates (6, 9, 10, and the residue of 5) remain.
##
##   **#85 and #86 — CLOSED AND FULLY GATED 2026-09-12 (gen #10), AT ZERO MEASURED COST.**

##   Gates (both repairs together): 34/34 planes rc=0; byte-inert pycsl-ref 983/983,

##   python-ref 2203/2203 AND the MIRROR 53/53, 0 MOVED/GONE/APPEARED, zero-byte checked on

##   every side; IR conformance 38/38 + 38/38, determinism 10/10; fidelity rc=0 with no mirror

##   sync and NO whole-file re-proof owed; mirror-coverage 549 KEPT; `check-bespoke-model-drift`

##   passed WITHOUT `--update`; **suite 3346/3365, ZERO XPASS, rc=1, failure set 19 vs 19

##   BYTE-IDENTICAL with its population asserted.** Witnesses 1216-1221.

##   **#85 WAS CLOSED FAITHFULLY** — the dict literal's contents are now carried to the

##   allocation site as the same `map_update_some` chain a LOCAL dict literal always got, so

##   the TRUE claim PROVES (witness 1219) and it is a completeness GAIN, the second such close

##   after #82. #86 could not be: its arm genuinely does not know the actual's contents, so it

##   gets a POLYMORPHIC unconstrained map. **BOTH HALVES OF "PREFER FAITHFUL WHERE THE

##   INFORMATION EXISTS" WERE MEASURED SIDE BY SIDE, IN ONE REPAIR.**
##
##   **#86 — A `map int (option int)` PARAMETER COERCION SUBSTITUTES THE EMPTY MAP FOR THE

##   ACTUAL — FOUND 2026-09-12 (gen #10), REPAIR BUILT, GATING.** This is carve-out census

##   candidate 5 PROPER. An actual that is neither a bare identifier nor an already-map

##   expression — a FIELD READ `c.d` — is replaced by `const None`, and the callee's contract

##   is then evaluated against it: a `#@ requires 1 not in d` was DISCHARGED while the program

##   passes a map containing 1, and a value carrier PROVED `\result == 0` where CPython gives

##   1. The carve-out justifies itself with "the abstract val has no axioms about its contents

##   anyway" — **a claim about the CALLEE BEING ABSTRACT, not about the lowering**, false as

##   soon as the callee is a real emitted function with a contract.

##   **IT ONLY BECAME VISIBLE BECAUSE #85 WAS FIXED FIRST.** Both erasures emitted the SAME

##   wrong constant, so one masked the other; with #85 repaired the emission reads

##   `let c = { d = (map_update_some ... 1 5) }` (correct) followed by `(g (const (None: option

##   int)))` (wrong) on the next line. **LESSON: AFTER LANDING A REPAIR, RE-RUN THE CARRIERS

##   AND LOOK FOR ONE THAT STILL PROVES — A SURVIVING CARRIER IS NOT A FAILED REPAIR, IT IS A

##   SECOND ROUTE THE FIRST WAS MASKING.**
##
##   **#85 — A NON-EMPTY DICT/SET LITERAL STORED TO A FIELD IN `__init__` IS MODELLED AS THE

##   EMPTY MAP — FOUND 2026-09-12 (gen #10), OPEN.** `self.d = {1: 5}` then `1 in c.d` proves

##   `\result == 0` where CPython returns 1, and the true twin is refused. The emitted WhyML

##   shows it directly: the allocation site is `{ d = (const (None: option int)) }`, the

##   TOTALLY EMPTY map, so `Map.get d 1` is decidably `None`. FOUR CARRIERS — membership, the

##   CONTENTS (`c.d.get(1, 0)` proves 0 where CPython gives 5, so the model is wrong about what

##   is IN the map, not merely about a present-guard), a SET field, and the serious one, a

##   CROSS-CALL carrier where the empty map DISCHARGES a callee's `#@ requires 1 not in d` that

##   the running program VIOLATES. THREE CONTROLS BOUND IT EXACTLY: a genuinely empty `{}` is

##   FAITHFUL, a field taken from a PARAMETER is fail-closed in both directions, and a LIST

##   field is fail-closed — which is why the blast radius is **ONE site, in `src/pycsl`, with

##   ZERO in the corpus and ZERO in the mirror**.

##   **FOUND FROM CARVE-OUT CENSUS CANDIDATE 5, WHICH GEN #9 RANKED AS LOW-VALUE TAIL.** The

##   candidate's own arm fired exactly as predicted and was NOT exploitable; the route was one

##   line above it in the same `--keep-mlw` dump. **READ THE WHOLE EMITTED FILE WHEN YOU DUMP

##   IT TO CHECK A CANDIDATE — a refuted candidate can still pay for itself in what its dump

##   shows.** The census's hit rate is therefore 3 in 7, not 2 in 6.
##
## **AN EMPTY OPEN LIST IS NOT A FLOOR.** It means every route the campaign has FOUND is
## closed and gated, and the hunt must now GENERATE candidates rather than work a queue.
## The generators that have paid, in order of yield, are recorded below and at the end of
## this file; the carve-out census still has FOUR unprobed candidates (5, 6, 9, 10) at a
## measured 2-hits-in-6 rate, and both differential corpora remain under-grown.
##
##   **#79 — AN `__init__` FIELD INITIALISER WHOSE RHS NAMES A NON-PARAMETER BECAME A

##   LITERAL `0` — FOUND 2026-09-11 (gen #8), CLOSED 2026-09-12 (gen #10), AT ZERO MEASURED

##   COST.** `self.n = len(items)` then `C([1,2,3]).n` proved `\result == 0` where CPython

##   returns 3, with the true twin refused. FOUR CARRIERS — a builtin, a module constant,

##   another `self` field, and **a PARAMETERLESS `__init__`, which gen #10 found and which no

##   earlier census could reach**: the function did `if not pset: break`, so a constructor

##   with no arguments never had a single initialiser examined. Route #79's own census is

##   defined as "the complement of the live capture rule" and therefore enumerated only

##   constructors that HAD parameters. **A GUARD'S EARLY EXIT IS PART OF THE GUARD.**

##   THE REPAIR IS AN UNCONSTRAINED CAPTURE, and a literal RHS is deliberately NOT marked

##   (`field_defaults` carries it faithfully — the #82 rule that faithful beats unconstrained

##   wherever the information exists). Gates: 34/34 planes; byte-inert pycsl-ref 979/979 and

##   python-ref 2203/2203, 0 MOVED/GONE/APPEARED, zero-byte checked BOTH sides; **mirror

##   emission 53/53 BYTE-IDENTICAL, so ZERO whole-file re-proofs were owed**; conformance

##   38/38 + 38/38; fidelity rc=0; mirror-coverage 549 KEPT; suite 3340/3359 ZERO XPASS with

##   the 19-failure set BYTE-IDENTICAL and its population asserted. Witnesses 1212-1215.

##   **ITS PRICE WAS CORRECTED THREE TIMES, DOWNWARD EVERY TIME** — gen #8 "70% completeness

##   regression, repair off the table"; gen #9 "133 defects, 17 mirror sites at ~56 min each";

##   gen #10 MEASURED: 40 scalar sites, zero corpus movement, zero mirror movement. Each

##   correction came from splitting a population by a distinction the previous count had

##   collapsed, and the last one from asking WHICH GUARD ALREADY STANDS between the

##   population and the change (Module 6's `_NONSCALAR` check fences the entire array arm).
##
##   **#84 — AN `assert` ERASES ITS TEST WHOLESALE, SIDE EFFECTS INCLUDED, AND IT LAUNDERS A

##   CONSTRUCT THE EMITTER OTHERWISE REFUSES — FOUND AND CLOSED 2026-09-12 (gen #9).**

##   Gates: byte-inert pycsl-ref 976/976, python-ref 1 intended GONE (0065); conformance

##   38/38 + 38/38; fidelity rc=0 with NO mirror work owed; mirror-coverage ratchet 549 KEPT

##   (the guard was inlined with ZERO new defs rather than re-baselined); 34/34 planes; suite

##   **3333/3352 ZERO XPASS with a byte-identical 19-failure set**. **COST: EXACTLY ONE CORPUS

##   FILE**, `python-reference/0065` (`buf.read()`), now a NEGATIVE WITNESS under the XPASS rule

##   rather than an untracked failure. **THE REPAIR WAS NARROWED 9x BY REFUTING MY OWN FIRST

##   DESIGN**: the byte-diff priced it at NINE files, and testing whether those passes were

##   HOLLOW showed they were NOT (hoisting `asyncio.run(...)` out of the assert still proves),

##   so refusing them was pure completeness loss.

##   `assert xs.pop() == 3` then `return len(xs)` proves `\result == 3` where CPython returns 2.

##   THE ASSERTION HOLDS, so CPython never aborts and the program is TOTAL. **THE CONTROL IS THE

##   POINT: the same `xs.pop()` OUTSIDE an assert is a PIPELINE ERROR** — this build refuses that

##   mutation outright, and wrapping it in a true assert launders it past its own guard. Escalates

##   to a `requires` discharge. The carve-out's two justifications are both about a FAILING

##   assert and correct about it; neither addresses a test that SUCCEEDS and MUTATES.

##   **BLAST RADIUS 21, not the 1450 the carve-out cites** — 1162 of 1212 asserts are in

##   `__main__` harnesses that are never lowered, and only 21 lowered asserts have a call in the

##   test. Repair priced: key on the EXISTING `_detect_purity` signal, NOT on syntax (a

##   mutator-name blocklist scored ZERO because `read` was not on it, and a

##   refuse-method-calls rule fails open on user functions — "a blocklist keyed on syntax fails

##   OPEN", three times in one route). Cost: a DELIBERATE completeness regression of ~9-11 corpus

##   files, moving the suite baseline from 19 failures to ~30 — to be justified file by file.
##
##   **#83 — A FIELD STORE INSIDE CONTROL FLOW IN `__init__` IS DROPPED — FOUND 2026-09-12

##   (gen #9) AND CLOSED 2026-09-12 (gen #10). FULLY GATED, AND IT COST NOTHING.**

##   Gates, all re-reproduced at HEAD rather than inherited: 34/34 planes; byte-inert over BOTH

##   corpora (pycsl-ref 976/976, python-ref 2203/2203, 0 MOVED / 0 GONE / 0 APPEARED, zero-byte

##   files checked on BOTH sides); IR conformance 38/38 core + 38/38 front-end, 0 MISMATCH;

##   mirror-coverage ratchet 549 KEPT (the guard was inlined with ZERO new defs, twice);

##   fidelity rc=0 with no mirror sync or whole-file re-proof owed; **suite 3336/3355, ZERO

##   XPASS, rc=1, failure set 19 vs 19 and BYTE-IDENTICAL to the baseline** — the diff's

##   population was asserted on both sides before it was believed. The specific risk watched for

##   was `src/pycsl_lib` fallout, since all five nested-store sites live there and the stdlib

##   demo drivers DO run in the suite even though they are in neither byte-diff corpus: NONE

##   moved. Witnesses 1209 (exploit), 1210 (the un-annotated control that refuted the predicted

##   mechanism) and 1211 (the BOUNDING control — a straight-line `__init__` must stay faithful,

##   or the repair would silently destroy the parametrized construction #76 and #82 depend on).

##   **THE REPAIR IS AN UNCONSTRAINED CAPTURE, NOT A FAITHFUL ONE, AND THAT IS CORRECT HERE:**

##   the model cannot know which branch ran, so neither `\result == 0` nor `\result == 7`

##   proves. Contrast #82, whose value WAS recoverable and so got a faithful capture.

##   ORIGINALLY RECORDED AS:** `self.v: int = 0` then `if n > 0: self.v = n`, and `C(7).v` proves

##   `\result == 0` where CPython returns 7. Cause: `for stmt in child.body:  # top-level only`.

##   **ITS CONTROL REFUTED THE MECHANISM THE CENSUS PREDICTED** — the annotation is irrelevant;

##   the un-annotated store is equally live — so the candidate's repair would have fixed the

##   annotated spelling, left the commoner one open, and passed every gate. Blast radius 5, all

##   in `src/pycsl_lib`, zero elsewhere.
##
##   **#82 — AN `__init__` KEYWORD-ONLY OR POSITIONAL-ONLY PARAMETER WAS DROPPED — FOUND AND

##   CLOSED 2026-09-12 (gen #9), AND CLOSED FAITHFULLY.** `P(v=7).v` proved `\result == 0` where

##   CPython returns 7, because `_collect_init_construction` read `child.args.args` and Python

##   keeps the other two parameter kinds in sibling fields. FIVE carriers; **the control was

##   exact** (same class, field, value and clause — only the parameter KIND differed — faithful in

##   both directions). **THE REPAIR IS A FAITHFUL CAPTURE, NOT A REFUSAL: every false claim is now

##   refused AND every true twin PROVES**, so it is a completeness GAIN. Gates: byte-inert both

##   corpora (971/971, 2204/2204), **IR conformance 38/38 + 38/38 WITH NEW IR KEYS ADDED** (the

##   additive-when-empty design held, so no frozen golden moved and no re-baselining was needed),

##   fidelity rc=0 with NO mirror sync owed, type-only 53/53, **34/34 planes**, suite **3333/3352

##   ZERO XPASS with a byte-identical 19-failure set**. Witnesses 1204-1208.

##   **FOUND BY RULE (o), NOT BY PROBING `__init__`:** re-verifying gen #8's inherited census

##   surfaced four rows that obviously should have been captured. **THE CENSUS WAS RIGHT AND THE

##   RULE WAS WRONG.** Generator banked: *when a census returns a member that obviously should not

##   be there, the bug is as likely to be in the RULE the census applies as in the census — read

##   the outlier ROWS, not just the totals.*
##
##   **#82 — AN `__init__` KEYWORD-ONLY OR POSITIONAL-ONLY PARAMETER IS DROPPED, AND EVERY

##   FIELD IT INITIALISES BECOMES A LITERAL `0` — FOUND 2026-09-12 (gen #9), OPEN.**

##   `_collect_init_construction` reads `child.args.args`, and Python keeps the other two

##   parameter kinds in the SIBLING fields `posonlyargs`/`kwonlyargs`, which are never read.

##   For a keyword-only `__init__` the parameter set is EMPTY, `if not pset: break` fires, and

##   every field falls to `_field_default`'s literal `0`. `class P` with

##   `def __init__(self, *, v: int = 0)` and `self.v = v`: **`P(v=7).v` PROVES `\result == 0`

##   where CPython returns 7.** FIVE carriers (keyword-only; keyword-only with RHS `b + 1`;

##   POSITIONAL-ONLY `(v, /)`; a keyword-only NONZERO default OMITTED at the call; and a

##   `requires` DISCHARGE), and **THE CONTROL IS EXACT** — the same class, field, argument

##   value and clause with an ORDINARY POSITIONAL parameter is FAITHFUL IN BOTH DIRECTIONS.

##   Only the parameter KIND changes. **WIDER THAN #79**: #79 needs an RHS outside the capture

##   shape, #82 needs nothing but `self.v = v`. Blast radius MEASURED: 8 constructors

##   repo-wide, **ZERO in the verified corpus**, 0 positional-only anywhere. Both edit sites

##   are OUTSIDE the mirror's verified surface (`construction_synth.py` is not mirrored;

##   `_call_record_constructor` is a `#@ \trusted` stub), so it is the CHEAP (#78) shape.
##
##   **#80 — `del obj.attr` IS ERASED AND A CLASS-ATTRIBUTE FALLBACK MAKES IT TOTAL — FOUND

##   BY gen #8, CLOSED AND FULLY GATED BY gen #9 (2026-09-12).** Proved `\result == 10` where

##   CPython returns 5; true twin refused. Gen #9 added TWO carriers gen #8 did not have, both

##   directions each: arithmetic on the stale field (`c.x - 5` proves the false 5, refuses the

##   true 0), and the stale value **DISCHARGING A CALLEE'S `requires v == 10`** where the

##   runtime value is 5 — the defect CROSSES THE CALL GRAPH. Blast radius **ZERO** (3636 files

##   parsed, 0 attribute deletes anywhere), so the guard is byte-inert BY CONSTRUCTION. Gates:

##   byte-inert both corpora (971/971, 2204/2204), mirror-sync rc=0, type-only 53/53,

##   conformance 38/38 + 38/38, **whole-file mirror re-proof w59a_m5ir rc=0 with 2111 goals

##   Valid and ZERO unproved**, **34/34 planes**, suite **3328/3347 ZERO XPASS with a

##   19-failure set BYTE-IDENTICAL to gen #8's**. Witnesses 1201-1203.
##
##   **THE LESSON #80 PAID FOR, RESTATED BECAUSE IT COST A GENERATION:** #80 was #77's OWN

##   RESIDUE, filed as out of scope *"because the program raises"*. That is TRUE of `del name`

##   and FALSE of `del obj.attr` — class-attribute fallback keeps the program total.

##   **"OUT OF SCOPE BECAUSE IT RAISES" IS ITSELF A CLAIM ABOUT PYTHON AND MUST BE PROBED,

##   NOT REASONED ABOUT.** `del name` is still a no-op today and is safe only for that same

##   unproven-looking reason — its reopening condition is now recorded explicitly.
##
##   **#81 — A LIST ALIAS TRACKS ELEMENT STORES BUT LOSES `append` — FOUND AND CLOSED

##   2026-09-11 (gen #8).** `a=[1,2]; b=a; b.append(3); return len(a)` proved `\result == 2`

##   where CPython returns 3; TRUE twin REFUSED; the ELEMENT read was a second and sharper

##   carrier (wrong about the CONTENTS, not just the length) and the REVERSE direction proved

##   identically. **IT REFUTED A SECTION HEADING IN ROUTE #59's OWN FILE** — "THE LIST CARRIER

##   IS CORRECT" — which was true of the ELEMENT STORE it measured and false one operation

##   over. MECHANISM: an appended-to list is SEQ-PROMOTED to `ref (seq int)` and the alias

##   COPIES it with its own length; Why3 prints `unused variable b_len` on the exploit run.

##   Closed by a guard at the TOP of `_handle_assign_stmt`. Gates: fidelity rc=0, byte-inert

##   both corpora under `--expect-gone`, conformance rc=0, **34/34 planes rc=0**, suite

##   **3325/3344 ZERO XPASS, failure set byte-identical**. Witness 1200; corpus 1131 (#59's

##   element-store control) still proves.
##
##   **THREE LESSONS FROM #81, ALL PAID FOR BY MEASUREMENT:**

##   1. **A CLOSED ROUTE'S "THIS CARRIER IS CORRECT" CONTROL IS EVIDENCE ABOUT THE OPERATION

##      IT RAN, NOT ABOUT THE TYPE.** Probe every OPERATION on a carrier declared safe, not

##      just every carrier. (Applied to #76's record control it found nothing — both outcomes

##      recorded.)

##   2. **THE SAME REPAIR IS CHEAP OR EXPENSIVE DEPENDING ON WHICH FUNCTION IT GOES IN.** A

##      guard in `_handle_seq_assign` (a CONVERTED mirror body) would owe a whole-file

##      statements.py re-proof; hoisted into `_handle_assign_stmt` (a `\trusted` STUB in the

##      mirror) it owes NOTHING — and is more correct, because the entry point sees both the

##      seq-promoted and unpromoted alias before the specialised handlers split them.

##      **A first attempt placed BELOW the `_seq_locals` dispatch never fired at all; one

##      debug print at the candidate site would have caught that in two minutes.**

##   3. **A BLAST-RADIUS CENSUS OVER AN UNTYPED LANGUAGE MUST NOT KEY ON TYPE ANNOTATIONS.**

##      Mine required `List[...]` and missed `a = []`, UNDER-counting — the dangerous

##      direction, since it makes a refusal look safer than it is. The byte-diff caught it.
##
##
##   **#78 — A SEEDED `deque(...)` WAS MODELLED AS EMPTY — FOUND AND CLOSED 2026-09-11

##   (gen #8).** `deque([1,2,3])` then `len` proved `\result == 0` where CPython returns 3;

##   the element read `dq[0]` was a second carrier and the stale length DISCHARGED a callee's

##   `requires`. The arm discarded EVERY argument under a comment calling it "a sound

##   under-approximation" — **it is not one: an EMPTY array is a DIFFERENT CONCRETE VALUE,

##   not a weaker fact, and a real under-approximation would be UNCONSTRAINED.** Closed by

##   refusing only the SEEDED form; the empty `deque()` is FAITHFUL and is the control that

##   bounds the guard (witness 1199; corpus 0501 still proves). Gates: fidelity rc=0,

##   byte-inert BOTH corpora (971/972 and 2204/2204), IR conformance rc=0, **all 34 planes

##   rc=0**, suite **3324/3343 ZERO XPASS with a byte-identical 19-failure set**.

##   **COST NIL — and the check that established that is the reusable part:** the mirror's

##   `_py_expr_call` is a `#@ \trusted` BODYLESS STUB, and the fidelity plane compares only

##   UN-trusted mirror methods, so the live body change owed NO mirror sync and NO re-proof.

##   Contrast #77, whose `_py_stmt_delete` was a VERIFIED body port and cost a 52-minute

##   whole-file proof. **BEFORE SCOPING ANY MODULE-5 REPAIR, GREP THE MIRROR FOR THE METHOD

##   AND CHECK FOR `#@ \trusted` — it is the difference between a ten-minute close and a

##   multi-hour one.**
##
##
##
##   **ALL THREE WERE FOUND BY ONE GENERATOR, AND THE GENERATOR IS #77's OWN LESSON:**

##   **A PROSE CARVE-OUT IN THE MODULE UPSTREAM OF A GUARD IS AN UNEXPLOITED ROUTE WITH A

##   SIGNPOST ON IT.** A census of comments admitting a construct is unmodelled / dropped /

##   "a sound under-approximation" / "stays a no-op", sitting next to code that then emits

##   nothing, returned ten ranked candidates; the top four were probed and THREE were live.

##   Every claim was re-measured independently before being believed (rule (o)).
##
##   **TWO OF THE THREE ARE GUARDED BY A SENTENCE ASSERTING THE ERASURE IS SOUND, AND BOTH

##   SENTENCES ARE FALSE.** #78's says "a sound under-approximation"; #79's says "sound, just

##   less precise". Neither is: each emits a definite literal (an EMPTY array, a literal 0),

##   and the emitter then proves definite facts from it. An under-approximation would be an

##   unconstrained value. **TREAT ANY COMMENT ASSERTING AN ERASURE IS SOUND AS AN UNPROVEN

##   LEMMA — it is checkable in one probe.**
##
##   * **#79 — AN `__init__` FIELD INITIALISER OUTSIDE THE CAPTURE SHAPE BECOMES A LITERAL 0**

##     (`route79-init-field-initialiser-falls-back-to-zero.md`). **THE WIDEST-REACHING ROUTE

##     THIS GENERATION**: it needs only `self.n = len(items)`. Three carriers proved

##     (`len(items)`, a module const, another `self` field); the params-only control is

##     FAITHFUL IN BOTH DIRECTIONS and bounds it exactly. **Blast radius NOT yet measured and

##     MUST be before building — this shape is idiomatic, so a blanket refusal may cost real

##     completeness; emitting an UNCONSTRAINED value (what the comment already claims) is

##     likely the better repair and should be priced first.**

##   * **#80 — `del obj.attr` IS ERASED AND A CLASS-ATTRIBUTE FALLBACK MAKES IT TOTAL**

##     (`route80-del-attribute-is-erased-class-fallback.md`). This is **#77's residue (a),

##     UPGRADED BY MEASUREMENT**: #77 filed `del obj.attr` as out of scope "because the

##     program raises", but Python falls back to the CLASS attribute, so it returns 5 where

##     PyCSL proves 10. **LESSON: "out of scope because it raises" IS ITSELF A CLAIM ABOUT

##     PYTHON AND MUST BE PROBED, NOT REASONED ABOUT.** One language feature turned a

##     written-off residue into a live route.
##
##   **#77 — A SLICE DELETE `del xs[i:j]` WAS ERASED TO `Pass` — FOUND AND CLOSED 2026-09-11

##   (gen #8).** File: `route77-slice-delete-is-an-erased-no-op.md`.
##
##       xs: List[int] = [1, 2, 3]

##       del xs[0:2]

##       return xs[0]          #@ ensures \result == 1   <-- CPython returns 3. PyCSL PROVED.
##
##   ROUTE #17's DEFECT ONE STEP OVER, WITH THE STEP CROSSING A MODULE BOUNDARY — #17's guard

##   is a Module-6 BLOCKLIST keyed on the emitted string (`code.strip() == "()"`), and

##   `Module5_IREmitter._py_stmt_delete` dropped the slice form to `{"stmt": "Pass"}` one

##   stage earlier, so the guard never saw it. Three carriers proved a false claim and the

##   TRUE TWIN OF EACH was refused; the stale value also DISCHARGED A CALLEE'S `requires`.

##   Closed by refusing at the site that ERASES it. Gates: mirror-sync 887/887 verbatim,

##   type-only 53/53, byte-inert over BOTH corpora against a pre-repair worktree baseline

##   (971/971 and 2204/2204, 0 MOVED/GONE/APPEARED), metric unchanged. Witnesses 1194-1197.
##
##   **#77 — A SLICE DELETE `del xs[i:j]` IS ERASED TO `Pass` AND THE READ IS THEN

##   CONSTANT-FOLDED — FOUND AND REPRODUCED 2026-09-11 (gen #8), BOTH DIRECTIONS

##   MEASURED, REPAIR SCOPED, NOT YET LANDED.** File:

##   `route77-slice-delete-is-an-erased-no-op.md`.
##
##       xs: List[int] = [1, 2, 3]

##       del xs[0:2]

##       return xs[0]          #@ ensures \result == 1   <-- CPython returns 3. PyCSL PROVES.
##
##   The #69 class, the serious one: a FALSE POSTCONDITION about ordinary TOTAL Python,

##   no `no_exception` and no opt-in. **IT IS ROUTE #17's DEFECT ONE STEP OVER, AND THE

##   STEP CROSSES A MODULE BOUNDARY** — #17 closed the ELEMENT delete with a blocklist in

##   Module 6 keyed on the emitted string (`code.strip() == "()"`), but

##   `Module5_IREmitter._py_stmt_delete` drops the SLICE form to `{"stmt": "Pass"}` one

##   stage earlier, so Module 6 never sees a delete to refuse. The guard and the hazard

##   ended up in different modules.
##
##   **THE NEW EDGE ON GEN #7's LESSON: THE ESCAPE HATCH WAS WRITTEN DOWN IN A COMMENT.**

##   Module 5's `else` branch names `del seq[i:j]` in prose, four lines under a docstring

##   that calls the blanket no-op "UNSOUND ... a severity-1 fail-OPEN". **A PROSE CARVE-OUT

##   IN THE MODULE UPSTREAM OF A GUARD IS AN UNEXPLOITED ROUTE WITH A SIGNPOST ON IT.**

##   That is a generator, not just a warning — grep for the next one.
##
##   Three carriers prove a false claim (element read, `len()` read, `del xs[:]`), and the

##   TRUE twin of each is REFUSED, which is what makes it a route rather than a gap.

##   Blast radius of a refusal measured at ZERO (no slice-delete in either corpus, the

##   mirror, `src/pycsl/` or `src/pycsl_lib/`). Repair owes a Module5 MIRROR re-proof —

##   the honest cost, stated in the route file with the re-usable `_csl_proj`

##   err-divergence pattern that pays step 2 of it.
##
##   **#59 IS CLOSED** — closed by gen #5 at `0bd9109e` (all seven carriers refuse),

##   witnesses `1125`-`1132` landed in the corpus by `3af2b851`. This file advertised it

##   as OPEN with "a partial repair staged" for four generations; that line was STALE and

##   is corrected here (gen #7, 2026-09-11). **RE-REPRODUCED AT HEAD BEFORE EDITING**, per

##   this file's own rule:

##     * local->local alias (`a={1:1}; b=a; b[1]=2; return a[1]`, `\result == 1`) — now an

##       EXPLICIT PIPELINE REFUSAL whose diagnostic names route #59 and explains the copy.

##     * the RETURN carrier (a getter handing out `self.d`, then mutating the handout) —

##       does not emit; fails closed.

##   `getting-better/staged-route59/` is EMPTY of live work: its witnesses moved into the

##   corpus at `3af2b851`. Do not rebuild the "partial repair" — the full one landed.
##
##   Routes #73, #74 and #75 (gen #6) are also CLOSED; so are #45-#58, #60-#72.
##
##   **#76 — `==` ON CLASS INSTANCES IS STRUCTURAL, PYTHON'S IS IDENTITY — FOUND AND

##   CLOSED 2026-09-11 (gen #7), `ecd41b8f`.** The DUAL of #42/#52: those found `is`

##   decided by VALUE equality (`is` too weak) and gave it its own IR operator; the `==`

##   side of that coin was never examined. `#@ ensures \result == x` PROVED for

##   `dup(x) = C(x.v)` where CPython answers False, and the false fact also discharged a

##   `requires` at a call site. Closed by a fail-closed ALLOWLIST — see the file for the

##   two blocklist designs that were REFUTED BY MEASUREMENT BEFORE LANDING, and for the

##   one-line lesson worth carrying: **an allowlist keyed on syntax fails CLOSED when the

##   hazard moves; a blocklist fails OPEN.** Three residues recorded with reopening

##   conditions (a `@dataclass` over-refusal, the record-FIELD carrier held only by a type

##   accident, and the value model's missing object identity).
##
## (the note below predates that find and is kept for its lesson)
## PREVIOUSLY: **NONE.** Every route in this ledger is CLOSED at `cf35437f`.
##
##   #46 was the last entry still advertised as open, and it had ALREADY been closed on

##   2026-09-08 by `5f57a95d` (witnesses 1089-1091); only this file was stale. Verified

##   at HEAD by re-reproducing both halves plus four variants — see its file.

##   THREE STALE ENTRIES WERE CORRECTED IN ONE WINDOW (#56, #57, #46). The rule that

##   catches them costs one command: RE-REPRODUCE AT HEAD BEFORE BUILDING, never inherit

##   a status line.
##
##   A THIRD GENERATOR, and the structural fact behind it (gen #4, 2026-09-10):

##   **PROBE THE ORACLES, NOT ONLY THE EMITTER.** The planes that decide whether a route

##   is closed are themselves programs with defects. Ten were found and fixed in one

##   window, two of them hiding live findings — a fidelity plane that a PROSE COMMENT

##   switched off for 46 functions (one genuinely divergent), and two gates testing the

##   same `# pycsl-expected: FAIL` marker differently, which left 13 drivers required to

##   prove AND exempt from the vacuity census.
##
##   **AND THE ONE ACCIDENT WORTH KNOWING BY NAME.** Carrier censuses of routes #44/#56

##   this window found the SAME mechanism confining three of them:
##
##       LOCAL   the carrier where the routes were FOUND (the sentinel type-checks)

##       PARAM   fails closed — `Optional[T]` becomes a generated `_union_f_0` and the

##               comparison dies with "has type PyCSL_Program._union_f_0"

##       RETURN  fails closed — identically, `_union_g_0`

##       FIELD   NOT a union at all: it lowers to a plain carrier read against the

##               opaque, `if (self.v = pycsl_none)`, i.e. genuinely COVERED by the repair
##
##   So the param and return carriers of the whole `None` family are guarded by ONE Why3

##   TYPE ACCIDENT, not by four independent decisions — and a `SAFE-TYPED` verdict is an

##   accident, never a guard. **REOPENING CAPABILITY, STATED ONCE FOR THE FAMILY:** any

##   change that makes a generated `Optional` union COMPARABLE to its carrier reopens the

##   param and return carriers of #44 and #56 SIMULTANEOUSLY. That is one condition to

##   watch rather than several, and it is cheap to check — re-run the carrier probes in

##   `route56-optional-union-local-read-sentinel.md`.
##
##   An empty OPEN list is NOT a floor — it means the hunt must now GENERATE candidates

##   rather than work a queue. The two productive generators this window: probe every

##   CARRIER of a closed route (that is how #56's bool carrier and #57 were found), and

##   probe every OTHER CODE PATH that reaches the same semantics as a repair just landed

##   (that is how #58 was found, one hour after #53 closed).

##   (#53, #56 and #57 were CLOSED AND LANDED by relaunch #51 on 2026-09-10; their

##    entries below are kept as the record of how, and are marked CLOSED in place.

##    #58 was found by probing #53's OWN REPAIR for the gap it leaves.)

  * **`route58-int-truediv-is-exact-real.md`** — **CLOSED, found AND closed 2026-09-10,
    while closing #53.** int/int TRUE DIVISION keeps its own bridge, `val float_truediv_op (a b: int)
    : real ensures { result = from_int a /. from_int b }`, on a different code path from
    float-operand arithmetic (that path tests that BOTH operands are floats, so it never
    fires for `1 / 3`). It still divides over the EXACT reals, so
    **`1 / 3 > 0.3333333333333333` PROVES** while Python answers False — the two are the
    same binary64 value. Same defect as #53, one costume over.  THE COST IS DIFFERENT AND
    THAT IS WHY IT IS ITS OWN ROUTE: the fix retires `5 / 2 == 2.5`, which two NORMATIVE
    surfaces use as the headline example of the WL-02 true-division fix. THAT COST DID NOT
    MATERIALISE: folding two int LITERALS to the binary64 quotient (rendered by the same
    `repr` normalization a float literal uses, which is injective and order-preserving on
    doubles) keeps ALL of 0813 while the unsound orderings fail closed — and it RECOVERED
    `1 / 3 == 0.3333333333333333`, true of the program, which the exact-real model could
    not prove. Witnesses 1121-1124.

  * **`route56-optional-union-local-read-sentinel.md`** — **CLOSED `b9217158`** (relaunch
    #51, 2026-09-10). Kept as the record of how. The route as found: a `None`
    Optional-union LOCAL reads back as the carrier's ZERO, so `x == 0` proves where Python
    answers False, and `x + 1` proves where Python RAISES. Bounded to the `int` carrier:
    `str`/`float` fail closed on a Why3 TYPE ACCIDENT, which is exactly why routes #50/#51
    probed this class at `str` and found nothing. REPAIR BUILT AND MEASURED (route #44's
    existing `pycsl_none` opaque in the non-Some arm; no new model, ledger stays 3); it
    moves ONE mirror emission. Witnesses + landing sequence: `getting-better/staged-route56/`.

  * **`route57-dict-get-no-default-is-zero.md`** — **CLOSED `d7796dbf`** (relaunch #51,
    2026-09-10). Kept as the record of how. The route as found: **the most reachable
    route in this ledger**: `d.get(k)` on a missing key is the codomain's ZERO, not `None`.
    #56 needs an `Optional` mutable local, a shape the corpus has ZERO of; this needs
    `d.get(k)`. Decides at BOTH the `int` and `str` codomains, because `.get` picks its
    sentinel FROM the codomain type and is therefore type-correct everywhere. The zero is
    borrowed from the SUBSCRIPT read's placeholder, justified as "proven dead under
    `#@ no_exception KeyError`" — coherent for `d[k]`, which RAISES, and inapplicable to
    `.get`, which never raises. REPAIR BUILT AND MEASURED SIX WAYS (all four shapes close,
    `d.get(k, v)` still proves, the subscript path deliberately untouched); it moves SEVEN
    mirror emissions, so it owes a re-proof battery. `getting-better/staged-route57/`.

  * **`route53-float-is-a-real.md`** — **CLOSED** (relaunch #51, 2026-09-10). Kept as the
    record of how. The route as found: `τ(float) = real`, so `0.1 + 0.2 == 0.3` proves.
    Closed by ONE uninterpreted DETERMINISTIC symbol for the float arithmetic bridge, used
    by the SPEC and BODY paths alike. MEASURED cost: 2 of 916 corpus emissions, 0 of 53
    mirrors (byte-inert), and exactly ONE clause — 0517's `\result >= 0.0`, a COMPLETENESS
    loss stated in its own docstring. Witnesses 1117-1120. Repair originally decided (make the float
    arithmetic bridge a deterministic opaque and route the SPEC path through the same
    symbol); measured cost is `0517`'s non-negativity clause. The tempting refinement
    (IEEE-true SIGN clauses) is REFUTED for `*`: the clauses meet at `a = 0.0` and decide
    `r = 0.0`, but Python's `0.0 * float("inf")` is `nan`.

  * **`route46-none-branch-join.md`** — **CLOSED `5f57a95d`** (relaunch #49, 2026-09-08;
    the ledger did not record it until 2026-09-10). The route as found: route #44's
    `None` record is flow-insensitive, so a `None` bound in ONE branch of an `if` and
    something else in the other walked past it, and route #45's NaN record leaked through
    the same join. Verified dead at HEAD across both halves and four variants, with the
    TRUE truthiness fact still provable — a fail-closed fix, not a refusal blanket.
    Witnesses 1089-1091.

### THE FAMILY #44 / #56 / #57 SHARE, AND THE RULE FOR TELLING IT FROM A HARMLESS TWIN

All three are **FAITHFUL STORAGE, ERASING READ**. The model really does carry a distinct
absent value — `map 'k (option 'v)` with a genuine `None`, a variant with a real
`Arm_*_None` — and a `match … | None -> <literal>` arm throws it away AT THE POINT OF USE.
An auditor who checks the REPRESENTATION finds it faithful and concludes the class is safe.
`bin/check-collapsed-option-reads.py` (the 31st plane) now enumerates every such arm.

The rule that separates the fatal ones from the nine benign ones, written after probing all
of them: **a ghost SPEC construct may DEFINE its absent-key answer** — `\map_get(d, k)`
returns 0 for an absent key and says so on two normative surfaces — **because it is a
spec-language primitive with no Python counterpart to contradict. A BODY lowering may not**,
because there the absent value is Python's `None`.


  * **`route46-none-branch-join.md`** — route #44's `None` record is flow-insensitive, so
    a `None` bound in ONE branch of an `if` and something else in the other walks past it.
    The obvious repair (a STICKY record) was BUILT and REFUTED TWICE, both times measured;
    read that section before re-attempting it. IT NOW CARRIES TWO ROUTES' FACTS — route
    #45's NaN record leaks through the same join (`if c > 0: x = float("nan") else: x = 1`
    then `x == x` PROVES), so ONE join build closes both.

CLOSED BY RELAUNCH #48, kept here as the record of how:

  * **#42** (`<int> is True`) — `is` was given its own IR operator and the bool-singleton
    test is whitelisted. Witnesses `pycsl-reference/1053`-`1057`. `bee3564c`.
  * **#44** (`None` was the integer 0, including the CONTRACT `ensures \result == None`
    proving for a function returning 0) — a shared opaque, faithful truthiness, and a
    return-annotation-gated faithful arm. Witnesses `1058`-`1064`. `c8a58cc9`.
  * **#45** (NaN breaks the reflexivity of `==`) — an EXACT lowering, because NaN's
    comparison semantics are totally determined. Witnesses `1065`-`1069`. `49a7334a`.
  * **#47** (a `getattr` default, and the no-default form Python answers with an
    `AttributeError`, were the integer 0) — an opaque keyed on the default's IR hash.
    Witnesses `1070`-`1073`. `5342bea1`.
  * **#48** (a SEEDED `Counter`/`OrderedDict`/`defaultdict` dropped its seed and the empty
    map's missing-key default was DECIDED on) — an opaque keyed on the seed's IR hash, with
    the FACTORY form deliberately untouched. Witnesses `1076`-`1079`. `5342bea1`.
  * **#49** (in-place growth of a list PARAMETER was modelled as ABSENT, in BOTH the
    `.append` and the `+=` shape) — refused, making the mutator family consistent.
    Witnesses `1080`-`1084`. `dfa01b0d`.



The ROUTE #36 RESIDUE (`x = 0; for x in a: pass; return x`) was closed later the same
window and its reproduction moved into the corpus as `pycsl-reference/1027`. The
obstacle — a general element write-back needs the outer ref's DECLARED TYPE, which the
binder does not have — was got round by pinning BOTH types instead of guessing one: the
target is in none of the non-int local classes (so its outer ref is the integer `ref 0`
pre-declaration) AND the iterable is a formal parameter whose symbol type is `list` (so
its element is an `int`). Zero mirror emissions moved, zero corpus emissions moved,
L3-tc 53/53.

WHAT IS STILL NOT COVERED, and it is narrower than the old residue: a loop over a
NON-int sequence, or one whose target carries a non-int type. There the two types can
genuinely disagree and the binder still has no way to compare them.

Everything in this directory is CLOSED and is kept as a record of how.

---

# The original heading and entries (relaunch #45)

Everything in this directory is a **live unsoundness with a working reproduction**.
Each file PROVES a contract that is FALSE of its own program, at HEAD, in the DEFAULT
`hoare` memory model, with no flags. They are kept HERE rather than in
`test-suite/corpus/pycsl-reference/` for one reason: a corpus witness for an open route
would be an **XPASS**, which the harness has counted as a failure since relaunch #44.
Move each file into the corpus in the SAME increment that closes its route.

## ROUTE #35 — CLOSED (relaunch #45, later the same window). Kept for the record.

The obstacle described below was real and the fix that overcame it is in
`module6_whyml/expressions.py`: separate PYTHON-BOOLISHNESS (does `1`/`0` already
encode the Python value faithfully?) from WHY3 TYPING (may this operand be selected
raw, or must it be wrapped back to an int?). `left_b == f"({left} <> 0)"` is the
precise second test. Mirror L3-tc came back 53/53, sixteen mirror emissions moved,
and their re-proofs were run. Witnesses are now `pycsl-reference/1023`-`1024`.

### The original entry, unedited:

## ROUTE #35 — `and`/`or` in a VALUE position return a boolean, not the operand

    x = 0 or 5      # Python: 5     model: 1
    x = 3 and 7     # Python: 7     model: 1

`module6_whyml/expressions.py`, the `raw_op in ("and","or")` branch, ends in
`return f"(if {left_b} {op} {right_b} then 1 else 0)"` under a comment that says "In
body context, Python's and/or return int". They return an OPERAND. The lowering is
CORRECT IN A CONDITION and WRONG IN A VALUE, and nothing at the emission site knows
which consumer it has. The string-operand and emit_ir-operand cases immediately above
it ALREADY select the operand — the general case never caught up.

REPRODUCTIONS: `route35-shortcircuit-value.py` (false, proves) and
`route35-shortcircuit-value-faithful.py` (true, does not prove).

### Why it is not closed here, MEASURED rather than guessed

* The value-preserving form
  `(let __or_l = <l> in if __or_l <> 0 then __or_l else <r>)` moves **19 of the 53
  mirror emissions**, including `expressions.py` (20125 goals, ~4h),
  `frontend/pure_ast`, `Module5_IREmitter`, `statements`, `stmt_control_flow`,
  `Module6_WhyMLTranspiler` and `preamble`. That is 19 whole-file re-proofs.
* AND THE NAIVE FORM IS ILL-TYPED. `_to_bool` returns a Why3 **bool** from many of its
  branches (a comparison, `Array.length … <> 0`, `hval_truthy …`, `py_isinstance_…_op`,
  an inductive predicate) and an **int** from exactly one (`({x} <> 0)`, its default).
  Selecting on the raw operand therefore emits `bool <> 0`: measured, the first version
  took mirror L3-tc from 53/53 to **40/53**, and the spike proof
  `frontend/module_collect` failed with "This expression has type bool, but is expected
  to have type int".
* PYTHON-BOOLISHNESS AND WHY3 TYPING ARE DIFFERENT QUESTIONS and the fix needs both:
  the first decides whether the `1`/`0` encoding is already faithful (it is, for a
  chain of comparisons — Python returns `True`/`False` there and `1`/`0` encodes it
  exactly, which is what keeps the ordinary `a == b or c == d` shape byte-inert); the
  second decides whether an operand may be selected raw or must be wrapped with
  `(if <bool> then 1 else 0)`. `left_b == f"({left} <> 0)"` is the precise test for the
  second. A THIRD trap is already documented in the code: the boolishness test must
  RECURSE through nested `and`/`or`, or `a == 0 and b == 3 and c == 1` looks like
  "int on the left, bool on the right" — the first version refused six real corpus
  files (0290, 0900, 0901, 0935, python-reference 0158/0161) because of it.

### The capability, named

Reconcile the two tests as above, then pay the 19 re-proofs. Estimated 8-12h wall at
two concurrent proofs. This is a COST/SCALE boundary in the §A.3 sense, not a
correctness one — every piece is expressible and the obstacles are enumerated here.

## ROUTE #36 — CLOSED for the index-valued loop (relaunch #45). Kept for the record.

The refusal described below was the wrong instrument and the entry stands as a record of
why. What landed instead is a WRITE-BACK in the binder: assign the OUTER ref immediately
before opening the inner `let`. It reproduces Python exactly, never-ran case included, it
is scoped to targets the function reads outside their loop AND to index-valued loops
(where the bound term is the counter and is int-typed like the outer ref), and it moves
**zero** mirror emissions and **zero** corpus emissions — so it cost no re-proofs at all,
against the fourteen the refusal implied. Witnesses `pycsl-reference/1025`-`1026`.

RESIDUE, recorded rather than hidden: `for x in <sequence>` followed by a read of `x`
still yields the pre-loop value. A general element write-back is NOT well-typed — the
outer ref takes its type from the FIRST assignment to that name, which need not be the
loop's element type. Measured: an unconditional write-back took mirror L3-tc to 51/53
(`expressions.py`, `functions.py`) and an `any int` havoc to 52/53 (`stmt_control_flow.py`,
whose loop target ref is `emit_ir`). Closing the residue needs the outer ref's declared
type at the binder, which it does not have.

### The original entry, unedited:

## ROUTE #36 — the `for` loop variable does not survive the loop

    i = 0
    for i in range(3):
        pass
    return i        # Python: 2      model: 0

The body opens `let i = ref (!_idx_i) in` INSIDE the loop, so the name is shadowed and
the OUTER `i` still holds its pre-loop value afterwards. Python leaves a loop variable
bound to its LAST value.

REPRODUCTIONS: `route36-loop-var-leak.py` (target pre-assigned) and
`route36-loop-var-leak-no-preassign.py` — BOTH prove. The second matters: a first guess
was that the exploit needs a stale pre-loop value, and it does not, because Module 6
declares the loop target as an outer `ref 0` regardless.

### Why it is not closed here, MEASURED rather than guessed

A pipeline-level REFUSAL of "the `for` target is read outside its loop" is written and
kept in `route36-refusal-that-broke-14-mirrors.py.txt`. It works, and it **breaks the
self-annotation mirror**: 14 of the 53 mirror files stop emitting, because reading a
loop variable after its loop is an ordinary Python idiom the emitter itself uses
throughout. A gate that makes the tool unable to verify itself is not shippable, and
exempting the mirror from its own soundness check is exactly the move this campaign
refuses.

One narrowing was tried and rejected on evidence: "refuse only when the target is
ASSIGNED before the loop" leaves `route36-loop-var-leak-no-preassign.py` exploitable.

One EXCLUSION in that refusal is worth keeping in any future version: a Python `assert`
is DROPPED by Module 6 (measured on `python-reference/0177`, whose `assert i == 5`
after a `break` loop emits nothing at all), so a read inside one is not a leak — and
counting it fails a PASSING corpus test for no soundness gain.

### The capability, named

Bind the OUTER ref in the loop body (`i := !_idx_i`, or `i := <elem_expr>` for a
non-range iterable) instead of shadowing it. That reproduces Python exactly INCLUDING
the never-ran case, where the variable keeps its previous value. It moves every
for-loop emission that reads its target afterwards — the same 14 mirror files — so it
carries the same 14 whole-file re-proofs. Do it in the same funded increment as #35;
the two overlap heavily in the files they touch.

---

## THE STRING MODEL'S BOUNDARY, MAPPED (gen #4, 2026-09-10) — PROBED, NO FINDING

Ten probes, every one run in BOTH directions, because "fails closed" without its true twin
does not distinguish a MODEL from a REFUSAL — the check route #53's file was caught having
skipped.

    MODELLED (false claim FAILS, true twin PROVES):
      len("abc") == 3          true -> PROVES        len("abc") == 4     false -> fails
      "abc" == "abc"           true -> PROVES        "abc" == "abd"      false -> fails

    OPAQUE — fails closed in BOTH directions, i.e. a COMPLETENESS GAP, not a guard:
      "a" < "b"                true -> FAILS         "b" < "a"           false -> fails
      "ab" + "cd" == "abcd"    true -> FAILS         ... == "abcd_"      false -> fails
      "abc"[0] == "a"          true -> FAILS         "abc"[0] == "b"     false -> fails

So string EQUALITY and LENGTH are genuinely decided, while string ORDERING, CONCATENATION
and INDEXING are uninterpreted. That is the safe configuration and there is no route here.
It also explains the previously recorded gap `"abc"[10:20] == ""` (true, does not prove):
slicing sits on the same opaque side as indexing, and is not a separate defect.

**REOPENING CAPABILITY — the thing to check if anyone makes these concrete.** Ordering,
concatenation and indexing are exactly the operations a completeness pass would want to
implement, and they are currently safe BECAUSE they are uninterpreted. Anyone giving them
a concrete model must re-run the FALSE column above in the same change: string ordering in
particular is where route #53's twin defect would live, since a concrete order on a hashed
or truncated string representation decides comparisons Python answers the other way.

**DO NOT RE-PROBE THESE TEN.**

---

## SIGNED `//` AND `%` ARE FAITHFUL IN ALL FOUR QUADRANTS (gen #4) — PROBED, NO FINDING

The highest-yield place to look for a route in any Python verifier, because Python FLOORS
toward negative infinity while C and most SMT integer theories TRUNCATE toward zero, and
`%` takes the sign of the DIVISOR rather than the dividend. Nine probes, both directions.

    python: -7//2 = -4   -7%2 = 1   7//-2 = -4   7%-2 = -1

      -7 // 2 == -4   (Python, true)  -> PROVES      -7 // 2 == -3  (C, false)  -> fails
      -7 %  2 ==  1   (Python, true)  -> PROVES      -7 %  2 == -1  (C, false)  -> fails
       7 // -2 == -4  (Python, true)  -> PROVES       7 // -2 == -3 (C, false)  -> fails
       7 %  -2 == -1  (Python, true)  -> PROVES       7 %  -2 ==  1 (C, false)  -> fails

**MODELLED, not merely refused, in every quadrant** — each C-semantics claim fails AND each
Python-semantics twin proves. This is a genuinely reassuring result rather than an absence
of evidence, and it is only meaningful because both columns were run.

Gen #3 had probed `5 // 0` and `5 % 0` (both fail closed). NEGATIVE OPERANDS were not
covered by that, which is why this was worth doing: division by zero and division by a
negative are different code paths reaching the same operator, and "a repair covers the PATH
it edits" cuts both ways when deciding what has actually been checked.

One completeness gap alongside it, recorded rather than left loose:

      (-2) ** 3 == -8   TRUE of the program  ->  does not prove

which sits with the already-recorded `2 ** -1 == 0`: exponentiation is opaque outside the
simple positive cases. Safe direction, no route.

**DO NOT RE-PROBE THESE NINE.**

---

## TYPE-CONFUSION AND KEY-HASHING PROBES (gen #4) — PROBED, NO FINDING

PyCSL coerces string literals to ints via `stable_hash` in several lowering paths, so
type confusion and key collision are the natural places to look for a route. Both
directions on each.

    1 == "1"                       FALSE of the program  ->  fails closed
    len({"a": 1, "b": 2}) == 2     TRUE                  ->  **PROVES**
    len({"a": 1, "b": 2}) == 1     FALSE                 ->  fails
    {"a": 1, "b": 2}["a"] == 2     FALSE (it is 1)       ->  fails

**Two distinct string keys are genuinely DISTINCT in the model** — the true twin proves, so
this is modelled rather than merely refused, and there is no hash-collision route here.
Cross-type `int == str` fails closed.

**DO NOT RE-PROBE THESE FOUR.**

---

## THE MISSING-KEY SUBSCRIPT LOOKS EXACTLY LIKE A ROUTE AND IS NOT ONE (gen #4)

Recorded because it presents with every symptom of a route and would cost a future
generation an afternoon.

    d: Dict[int,int] = {1: 1};  return d[5]
    `\result == 0`  ->  **PROVES**.  CPython RAISES KeyError.
    `\result == 1`  ->  fails.

A claim false of the program proving is the exact signature this campaign hunts. But it is
**DOCUMENTED, INTENTIONAL AND OPT-IN**, so it is a CERTIFIED BOUNDARY:

`docs/pycsl-static-semantics-reference.md` §2.1.13 defines the obligation set as
`active(f) = no_exception_set(f) ∪ (no_exception_all(f) ? KNOWN_EXCEPTIONS : ∅)`. With no
`#@ no_exception` directive, `active(f) = ∅` and **no implicit-exception obligation is
imposed at all** — "ambient mode, preserving backward compatibility ... The CLI flag is off
by default and treated as opt-in; ambient mode is the default per workplan §11.3."

**AND THE MACHINERY IS CORRECT WHEN ASKED.** Measured:

    return d[5]  with  `#@ no_exception KeyError`   ->  FAILS   (it cannot prove 5 is present)
    return d[1]  with  `#@ no_exception KeyError`   ->  PROVES

So the placeholder is not a modelling error; it is the value of a read whose
exception-freedom the author did not ask to be checked. This is also exactly what route
#57's docstring meant by "proven dead under `#@ no_exception KeyError`, the ambient default
otherwise", and it is why #57 deliberately left the SUBSCRIPT path untouched while fixing
`.get`: `.get` never raises, so there is no directive that could ever discharge it.

**THE STRENGTHENING ALREADY EXISTS**: `--strict-no-exception-propagation`. The boundary
closes if that becomes the default, and the cost of doing so is the interesting open
question — not the placeholder itself.

**DO NOT FILE THIS AS A ROUTE.**

---

## INTEGER BIT OPERATIONS AND ARBITRARY PRECISION (gen #4) — PROBED, NO FINDING

The soundness risk in this area is FIXED-WIDTH WRAPAROUND: Python ints are unbounded, and a
model that silently truncates to 64 bits would decide overflow comparisons the other way.
Nine probes, both directions where a false twin exists.

    MODELLED (true claim proves):
      (1 << 70) > 0    -> PROVES     ** no wraparound; arbitrary precision preserved **
      (1 << 3) == 8    -> PROVES
      (6 & 3) == 2     -> PROVES
      (6 | 1) == 7     -> PROVES
      ~5 == -6         -> PROVES     (and `~5 == -5`, false, fails)

    OPAQUE — fails closed in BOTH directions (a completeness gap, not a guard):
      -8 >> 1 == -4    TRUE  -> fails       -8 >> 1 == 4   FALSE -> fails

So the only gap is ARITHMETIC RIGHT SHIFT ON A NEGATIVE operand, and it is undecided rather
than wrong. `(1 << 70) <= 0` — the wraparound signature — fails, which is the result that
mattered: a 64-bit truncation would have proved it.

**REOPENING CAPABILITY:** if a bounded-int mode is ever made the default (the emitter
already carries a `self._bounded_int` notion and a `bounded_int` first-assign kind), re-run
`(1 << 70) > 0` and `(1 << 70) <= 0` FIRST — that pair is the cheapest wraparound detector
in the corpus.

**DO NOT RE-PROBE THESE NINE.**

---

## THE CORE MACHINERY: FRAME ENFORCEMENT AND `\old` (gen #4) — PROBED, NO FINDING

Probed because everything else in this campaign leans on it. The `\trusted` ledger, the
frame-honesty planes and every "the mirror proves its own frame" argument are worth nothing
if `assigns` is not actually enforced on a VERIFIED method.

    FRAME, write OUTSIDE the declared assigns:
      `#@ assigns self.x` with a body writing self.x AND self.y   ->  **FAILS**  (caught)
      `#@ assigns self.x, self.y` with the same body              ->  **PROVES** (control)

    `\old`, in a postcondition:
      `#@ ensures \old(self.x) == self.x`  after  self.x = self.x + 1   ->  **FAILS**
      `#@ ensures \old(self.x) + 1 == self.x`  after the same           ->  **PROVES**

**Both are MODELLED, not merely refusing** — each false claim fails AND its true twin
proves, which is the only pair that distinguishes a working check from a check that always
says no. A frame lie is caught, and `\old` genuinely captures the PRE-state rather than
aliasing the post-state.

    CLASS INVARIANTS (`#@ class invariant self.x >= 0`), all three directions:
      body sets `self.x = -1`, breaking it                    ->  **FAILS**  (CHECKED at exit)
      body sets `self.x = 5`, preserving it                   ->  **PROVES**
      `#@ ensures \result >= 0` for `return self.x`,
        which can only hold if the invariant is ASSUMED       ->  **PROVES** (ASSUMED at entry)

So the invariant is both ASSUMED on entry and CHECKED on exit — the correct discipline, and
the assume half is confirmed by a postcondition that is unprovable without it rather than by
inspection.

This is the reassuring result the campaign's own structure depends on, and it is recorded
here so that "is `assigns` actually enforced?" never has to be re-asked from scratch.

    INTER-PROCEDURAL CONTRACTS:
      `g` requires x > 0, caller does `g(-1)`     ->  **FAILS**  (precondition discharged
                                                                  AT THE CALL SITE)
      the same caller doing `g(5)`                ->  **PROVES**
      caller's `\result == 5` proved only from
        the callee's `ensures \result == x`       ->  **PROVES** (the postcondition FLOWS)

**DO NOT RE-PROBE THESE TEN.**

### THE STRUCTURAL CONCLUSION, WHICH IS WORTH MORE THAN ANY ONE OF THEM

Frames, `\old`, class invariants, precondition discharge and postcondition flow are ALL
sound, each verified in both directions. **So every route this campaign has found lives in
the VALUE MODEL — how a Python value is represented — and none of them live in the Hoare
logic.** #44/#50/#51/#56/#57 are `None` and sentinels; #53/#58 are floats as exact reals;
#54 is dict-literal key collapse; #59 is reference vs value semantics for collections.

That is a useful place to point the next generation: **probe representations, not the
proof engine.** The engine has now been measured and it holds.

---

## NESTED CONTAINERS AND TUPLES (gen #4) — PROBED, NO FINDING

Closing out the "still unprobed" list rather than leaving it to look like an opportunity.

    NESTED CONTAINERS — a list inside a list, mutated through the inner binding:
      a = [1];  outer = [a];  a[0] = 9;  return outer[0][0]      CPython: 9
      -> emission TYPE ERROR, both directions.

    Consistent with the boundary already recorded on route #57: a container whose ELEMENT
    or VALUE type is itself a container does not lower. Fails closed, by the same TYPE
    ACCIDENT, and it inherits the same reopening capability — if nested containers are ever
    given a lowering, the R1 "storing a list in a dict and keeping the original" case from
    `docs/pycsl-ownership-discipline.md` §2 becomes reachable and must be re-probed.

    TUPLES:
      `a, b = (1, 2);  return a + b`  with `#@ ensures \result == 3`   ->  **PROVES**

    **AND A CORRECTION TO MY OWN FIRST ATTEMPT**, recorded because the failure mode is
    easy to misread as a finding: annotating the tuple LOCAL (`t: Tuple[int, int] = (1, 2)`)
    produces a type error. That is an unsupported LOCAL ANNOTATION, not a tuple defect —
    unpacking itself is fine. A probe that dies on emission has to be re-run in a second
    spelling before its failure means anything about the semantics.

**DO NOT RE-PROBE THESE.**

## ALSO OPEN after gen #31 (2026-09-24) — THREE DIAGNOSTIC FINDINGS, NOT ROUTES
##
## 1. **A NAME THAT RESOLVES TO NOTHING IS DROPPED IN SILENCE** — **CLOSED the same day,
##    all four** (witness/control pairs 1877/1878, 1880/1881, 1882/1883, 1884/1885). Kept

##    here because the SHAPE is the finding and the next one will look the same. It was:

##    `Callable[[Rekt], int]` silently becomes `int`; `#@ uses no_such_lemma` verifies;

##    `#@ reveal no_such_function` verifies (this generation's OWN new feature, eight hours

##    old when the audit found it); `#@ footprint no_such_prop(k)` verifies in a file with

##    no `#@ happy` — its guard exists, its comment calls a typo "a soundness hole", and it

##    sits two lines below an early return. Six other directives DO refuse, which is what

##    makes this a defect rather than a policy. Four patches + eight witnesses drafted.

##    `finding-a-name-that-resolves-to-nothing-is-dropped-in-silence.md`
##
## 2. **THE RECORD DECL DRIVES THE IMPORTS, AND TWO DISJUNCTIONS SAY SO WHILE IMPLEMENTING
##    IT FOR ONE WITNESS EACH** — a class whose only array is a list FIELD dies on

##    `unbound type symbol 'array'`; a dict FIELD whose values are lists dies on `unbound

##    type symbol 'seq'`. Fail-closed, so never a false green — but a whole shape of program

##    cannot be verified at all, and the message names a Why3 symbol rather than anything

##    the user wrote.

##    `finding-array-import-missing-for-a-list-field-only-program.md`
##
## 2b. **A `List[T]` TAKEN OUT OF A `Dict[K, List[T]]` CANNOT BE PASSED TO ANYTHING** — and
##    this is the measured answer to "why has the `\trusted` count not moved in thirty

##    generations". The cheapest stub in the mirror is FIVE LINES

##    (`PyCSLWeaver.visit_FunctionDef`); built on an offline copy of the tree and put

##    through the real whole-file proof, it needs two patches AND a modelling decision —

##    a `List[T]` PARAMETER is `array T`, a `Dict[K, List[T]]` VALUE is `seq T`, and

##    nothing converts between them. A 2x2 locates the nearest half of it in one conjunct:

##    `statements.py` ~5900 promotes a single-assign list local to `_seq_locals` only when

##    its element type is `string`, so `len(fp)` on a `seq int` mistypes — the THIRD

##    instance this generation of a rule implemented for the element type the first witness

##    happened to have. Fail-closed throughout.

##    `finding-a-list-out-of-a-dict-cannot-be-passed-anywhere.md`
##
## 2c. **A MUTEX NAME THAT RESOLVES TO NOTHING** — `#@ critical` / `#@ acquires` /
##    `#@ releases` never validate the name. All three verify silently when the `with`

##    block touches nothing shared, and `#@ releases` is never caught by anything in any

##    program because nothing downstream reads `csl_releases`. **This one also CORRECTS

##    this session's own silent-name sweep**, which listed `#@ critical` among the

##    directives that refuse an unknown name: that verdict came from a file whose block

##    WROTE a protected shared variable, so the refusal was the protection analysis, not a

##    name check. Two of seven "controls" were the same mechanism in a name check's

##    clothes. `finding-a-mutex-name-that-resolves-to-nothing.md`
##
## 2d. **`struct.unpack` RETURNS A TUPLE, AND TWO PROOF-CITED DRIVERS CERTIFY
##    `\result == x`** — `0753.py` and `0778.py`, five functions, both

##    `# pycsl-expected: PASS`, both carrying audited `#@ proof rocq` and `#@ proof lean`

##    citations. CPython answers `(x,)`. Deleting the citations makes 0753 FAIL, so the

##    discharge is the audited-external-proof opt-in and this is a finding rather than a

##    SEV-1 route — but it is a defect in a CHECKED surface: the registered axiom is a true

##    theorem about a byte codec returning an INT, and nothing in the 3-way cross-check

##    compares the Rocq result TYPE with the Python return type.

##    **It was hidden by an exclusion list.** `check-corpus-contract-truth-args` had

##    `\nothing` among "CSL tokens this oracle cannot evaluate" — a token that can only

##    appear in `#@ assigns \nothing`, a clause it never reads — and tested the whole

##    annotation block, so every empty-frame function was skipped: 416 -> 519 functions,

##    4367 -> 5750 evaluations. `finding-struct-unpack-returns-a-tuple.md`, wall-lesson (o5).
##
## 3. **THE `#@ datatype` MATCH-EXHAUSTIVENESS REFUSAL IS WITHDRAWN** — its census came out
##    zero and it was written up as ready; then one constructed counter-program refuted it

##    (`#@ requires c != Blue()` makes a partial match legitimate and Why3 DISCHARGES the

##    `absurd`). Recorded because the near-miss is the lesson: a census measures the blast

##    radius over the EXISTING population; a rule applies to every program that COULD be

##    written. `finding-hard-error-claims-audited.md`, wall-lesson (u4).
