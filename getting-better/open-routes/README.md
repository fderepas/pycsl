# OPEN ROUTES — exploited, reproduced, NOT closed

## CURRENTLY OPEN after gen #31 (2026-09-24): **NONE.**
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
## 1. **A NAME THAT RESOLVES TO NOTHING IS DROPPED IN SILENCE** — four directives:
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
## 3. **THE `#@ datatype` MATCH-EXHAUSTIVENESS REFUSAL IS WITHDRAWN** — its census came out
##    zero and it was written up as ready; then one constructed counter-program refuted it
##    (`#@ requires c != Blue()` makes a partial match legitimate and Why3 DISCHARGES the
##    `absurd`). Recorded because the near-miss is the lesson: a census measures the blast
##    radius over the EXISTING population; a rule applies to every program that COULD be
##    written. `finding-hard-error-claims-audited.md`, wall-lesson (u4).
