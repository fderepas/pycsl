# FINDING (gen #7, 2026-09-11) — THE `_add_abstract_op` ENSURES AUDIT IS NOW FINISHED

The gen-#6 ladder left item 2 open: *"the `_add_abstract_op` audit is NOT finished, and
#73/#74 show where the yield is — the HAND-ADDED ORACLES keyed on a literal string, a
method NAME, or a domain convention."* This closes the ENSURES half of it.

**AN `ensures` ON AN ABSTRACT `val` IS AN AXIOM** — that is the whole reason this audit
exists, and it is how routes #73 and #74 were found (`val get_arity_field ... ensures
{ result >= 0 }`, `val self_isdigit_0 () : int ensures { result = 0 || result = 1 }`).

**RESULT: ACROSS THE WHOLE EMITTER THERE ARE EXACTLY TWO SITES THAT ATTACH AN `ensures`
TO AN ABSTRACT `val`, AND THEY ARE THE SAME SITE** — `expressions.py:7249` and `:7254`,
the zero-arity and n-arity arms of the ONE generic abstract-op fallback. Both take their
clause from `_dotted_ensures_suffix`.

**AND THAT SUFFIX IS NOT A HAND-ADDED ORACLE — IT IS CALLEE-CONTRACT PROPAGATION.** It
renders the callee's own declared `#@ ensures` (`_module_method_result_ensures` and its
field/param siblings). **MEASURED, not assumed:** a method whose declared
`#@ ensures \result == 7` is FALSE of its body (`return 3`) does NOT yield a caller-side
axiom — the callee's own VC `c__m'vc` is emitted and FAILS, so the file fails closed. The
propagated postcondition is backed by a real proof obligation.

**SO THE ORACLES THE GEN-#6 LADDER FLAGGED AS "STILL UNGUARDED" CARRY NO AXIOM.** The
dotted and class-name-keyed recognizers — `.to_dict`, `.copy`, `.findall`, `.split`,
`.get`, `IRScanner.find_*`/`collect_*`, `self.ir.get` — attach NO `ensures` anywhere. The
gen-#6 handoff's standing warning is therefore CONFIRMED and can be restated precisely:
**they are not axiom-carriers today, and the moment one gains an `ensures` it becomes
route #73/#74 again.** That is a one-line grep to re-check
(`grep -rn "_add_abstract_op(" src/pycsl/module6_whyml/ | grep -i ensures`) and it should
return exactly the two lines above. A THIRD line is a live route until proven otherwise.

**WHAT REMAINS OF THE AUDIT, AND IT IS A DIFFERENT SHAPE.** Those recognizers can still be
unsound by MIS-MODELLING a call rather than by asserting a fact — `IRScanner.find_*` /
`.split` are consulted by `ir_scanner.py:148,195-197` to CLASSIFY a variable as an
array/dict, and a misclassification changes how the value is modelled without ever
emitting a clause. That is a classification audit, not an axiom audit, and it is NOT
covered by the grep above.

**ALSO CLEARED THIS GENERATION (gen-#6 ladder item 2b): `axiom hash_eq_consistent_<cls>`
IS UNREACHABLE, NOT MERELY SWITCHABLE.** `preamble.py:9081` emits it over two abstract
`val function`s `<cls>_hash_` / `<cls>_eq_`. **MEASURED: both are DEAD SYMBOLS.** `hash(a)`
on a class instance does NOT lower to `<cls>_hash_` — it lowers to an unrelated
`val hash_1 (x0: int) : int` and then Why3 TYPE-REJECTS the class argument; `a == b` does
not lower to `<cls>_eq_` either (it lowered to the record `=` — which is ROUTE #76, found
from exactly this reading). So the axiom is attached to functions nothing uses and no
false claim is reachable through it. REOPENING CONDITION: the day `hash()` or `==` on a
class instance is routed through `<cls>_hash_`/`<cls>_eq_`, this axiom becomes live and
says something Python does NOT enforce.
