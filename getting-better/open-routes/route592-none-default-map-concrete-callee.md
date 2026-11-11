# OPEN ROUTE #592 — AN OMITTED `None` DEFAULT OF AN `Optional[Dict]` PARAMETER IS FILLED WITH THE OPAQUE MAP `pycsl_none_map`, SO A VERIFIED CALLEE'S CONTRACT (PROVED FOR EVERY MAP) IS APPLIED WHERE CPYTHON PASSES `None`
**Status: REPAIRED (driver run #6, executor u40, branch run6-u40 off run6-int56 fe057a6c1; annotations §7.592). Mechanism (front end, `pycsl.py::_run_pipeline`, twin `\trusted`; inline, no new def, no axiom): every `pycsl_none_map` fill Module 6 makes is observed together with its callee, and REFUSED, new `PYCSL-R592-NONE-DEFAULT-MAP-CONCRETE`, unless every binding of the callee has no verified body (`\abstract`, `\trusted`, or a mirror `#@ declared_in` whose definition is `\trusted` / `\abstract`).** Opened as: Status OPEN, Severity 1, INTRODUCED BY RUN #6 (capability cap-none-default-map-param, lvN, c9ef6badd, landed in L5); red team rt56 probe `hc1762_cl_isinstance_dict.py` (copied to `witnesses-r592/`).

## The defect

lvN changed the fill of an omitted `None` default of a map-typed parameter (`Optional[Dict[K, V]] = None`, WhyML
`map K (option V)`) from the int `0` (ill-typed: the file was refused at L3-tc) to the opaque constant
`val function pycsl_none_map : map 'k (option 'v)`. The constant itself decides nothing, but a VERIFIED callee body
reads the parameter AS A MAP, so its contract is proved for every map, and the caller inherits it at a call where
CPython passes `None`:

    #@ ensures \result == 1
    def g(x: int, d: Optional[Dict[str, str]] = None) -> int:
        return 1 if isinstance(d, dict) else 0      # true of every map
    #@ ensures \result == 1
    def h() -> int: return g(3)                     # PROVED; CPython returns 0

Measured by the driver: on the pre-run-#6 base (pycsl-base6) an L3 type error (not proved); on run6-int56 PROVED.

## The repair

RULE (annotations §7.592). The two fill sites are `ExpressionEmissionMixin._handle_dotted_call` (`self.m(..)`, key
`_dk`) and `_handle_call_expr` (module function, key `func_name`; the keyword-bound path included); both mirror twins
are `\trusted`, and they are the only `_add_abstract_op` calls of that `val`. `_run_pipeline` installs an
instance-attribute observer over `transpiler._add_abstract_op` (route #506's device: no emitter source change, emission
byte-identical) that, on the `pycsl_none_map` declaration, reads the filling frame's callee key and parameter name.
After `transpile()` each fill is judged: the callee's IR bindings (by name or `whyml_ident` name) must all be
`abstract`, or `trusted` without a `declared_in:` reviewer, or `declared_in:<relpath>::<Class.m>` whose definition in
`src/self-annotate/src/<relpath>` carries `#@ \trusted` / `#@ \abstract` in the `#@` block directly above its `def`.
Anything else (a verified body, no visible binding, an unresolvable declaration) is REFUSED. The refusal is at the
CALL SITE, so it covers every use the callee makes of the parameter (in its body or contracts).

Advice (audited FOLLOWABLE, see below): pass the argument explicitly; make the parameter required; or mark the callee
`#@ \trusted` only if its contract holds for `None`.

## Witnesses and measurements

RESULTS_PLACEHOLDER
