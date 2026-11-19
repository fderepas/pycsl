# Run #7 dict-value requirements census (cv13)

Executor cv13, branch `run7-cv13` (base c15a2afed). This census follows the driver redirect of 2026-11-13 (log
838), which reopened the Dict[str, Any] / Any-IR boundary. It measures what a mixed-type value model must
support to convert the governing `\trusted` stubs that touch mixed values.
- Census only: no `src/pycsl` edit and no proof.
- Every emission is either a QUICK `--no-proof --keep-mlw` heavy.sh job (20 s gap) or a `why3 prove --type-only`
  of a hand-patched `.mlw` (`scratchpad/cv13/mlwx/`, via `tcx.sh`).
- The slice oom_kill was 0 at the start and 0 at the end (no proof was run).

**STATUS: FINAL (2026-11-13T16:45Z).**
- All **127** stubs of the population reached L1 (`d<sid>_1`).
- 14 stubs got further links (L2..L5, source-level and emission-level).
- 4 chains CLOSE.

## Method

- **Population** (`scratchpad/cv13/dpop.json`, 127 governing `\trusted` stubs; defined in `pop.py`/`desk.json`):
  - cv12's 48 BOUND chains (`run7-capability-census.md` §2-§3);
  - r3's rows 398 / 400 / 034 / 001 / 250, which are s362 `_record_key`, s374 `_synthesize_block`, s030
    `_namedtuple_check_call`, s001 `_build_callee_no_exception_summary` and s253 `_handle_sum_call`;
  - every cv11 `merged11.json` row whose need-list names cap-vm-unerase-dict / -irnode / -union / -list /
    -any-tree or an R325 dict-value capability.
- **The stand-in for the mixed-value model is the certified `hval` view** (`Dict[str, PyVal]`). It is already
  emitted, with the `Phase2f_PyVal.v` / `PyVal.lean` certificate.
  - `gen_l1.py` ports the verbatim body (`bin/port-one-mirror-body.py --convert`).
  - It then retypes to the hval view every parameter whose LIVE annotation is `Dict[str, Any]` / `dict` / `Any` /
    `List[Dict..]` and whose mirror annotation is not an IR type (`spec/d<sid>_1.json`).
  - The next links are:
    - [R] behaviour-identical respellings;
    - [T] mirror retypes;
    - [S] stand-in helpers for a missing op;
    - emission-level hand patches of the blocker (law-free `val`s, new hval tags), checked with
      `why3 prove --type-only`.
- **Raw data:**
  - `probe/results.tsv` (rows `d*`) and `probe/d*.{log,mlw,src.py,patchlog}`;
  - `dnotes.tsv`, the per-stub record of §3;
  - `matrix.py`, the operation x stub tags of §2 (it renders `matrix.md`);
  - `wclass.py`, the automatic wall class of every probe;
  - `dops.py` -> `dops.json`, a syntactic op census of the 127 live bodies;
  - `mlwx/d*_x*.mlw/.log`.

## 0. Headline

**4 of 127 chains close (honest TC-OK, input-reading). All four are in pycsl.py (mirror proof ~0.5 h).**

| stub | closes with | evidence |
|---|---|---|
| s375 `_synthesize_legacy_text` | **no new capability**: [T] `records: List[Dict[str, PyVal]]`, [T] the trusted callee `_synthesize_block(rec: Dict[str, PyVal])`, [R] the genexp join becomes for/append + join | `probe/d375_3` TC-OK. The existing `hval_to_map` bridge is used |
| s356 `_json_goal_records` | **O7**: an hval-element comprehension `[r for r in xs if "k" in r]` | `mlwx/d356_x1` rc 0. [T] `-> List[Dict[str, PyVal]]` on it and on the trusted `_parse_why3_json` is SELECTED today (`seq hval`). The stand-in comp has a length law only; a content law is needed for useful specs |
| s363 `_residual_selectors_from_records` | **O19** (f-string / str() of an hval) + an **Optional[List[str]] union-arm typing fix** (the arm is emitted `Arm_3_0 int`) + **O3** (None tag, for the R521 proof) | `mlwx/d363_x1` rc 0, after [T] hval sigs, [R] split unpack and [T] unquoted local annotations |
| s362 `_record_key` | **O6** a `Tuple[PyVal, ..]` return codomain + **O7** `tuple()` over an hval + **O3** a None tag | `mlwx/d362_x1` rc 0. HEAD now emits an R521 `assert false` that only a None tag the codomain admits can discharge. For a faithful dict KEY (its caller `_merge_records_best_of_n` hashes it), the tuple needs its own tag (HTuple) |

**Minimal operation set:**
- {O3, O6, O7, O19} + the union-arm typing fix closes all 4: s375, s356, s363, s362.
- Without O6 it closes 3.
- Without O19 it closes 2.

**The r3 reopening test is NOT met.** That test needs >= 2 of rows 398 / 400 / 034 / 001 / 250 at TC-OK with a
Tuple[PyVal] codomain plus one hval builtin. Only 398 (s362) closes.
- 400 (s374) needs O7 join + O19 + O18 + O9 (`mlwx/d374_x1`).
- 034 (s030) needs O4 + O17 + O16 + raises propagation into its VERIFIED generic-fold caller (`mlwx/d030_x2`).
- 001 needs a dict-of-SET field model.
- 250 (s253) needs O2 / O7 / O18.

**The dict model is the FIRST wall of only 48 of 117 in-scope stubs.**
- 69 stop first on a non-value capability:
  - nested-closure lift (11);
  - in-place mutators on local / param lists, sets and dicts (12);
  - R252 / R301 / R319 / R325 / R542 / #381 / #303;
  - CSL record vs `emit_ir` (8);
  - byref param frames;
  - method recursion; kwarg drops.
- 10 are out of scope (external lvQ, or lvR typed-locals rows).

**Mutation and aliasing are the largest requirement.**
- O11 (in-place store / setdefault / pop / insert on dict values, nested path write-back) is the top measured
  op: 18 stubs; next are O5 hval at builtin-typed call arguments (10) and O13 hashing an hval (8).
- O12 (by-reference dicts: `self.ir` / `self.program_ir`-style FIELDS, IR dicts passed to callees that write
  them, e.g. `_reset_function_state(func)`) adds 5 more.
- A pure immutable `hval` cannot close these. The model must be a mutable, aliased dict value with writes
  frames, or those stubs need value-returning live refactors.

**Adding tags is cheap to type and costly to certify.** `mlwx/d362_x2.mlw` adds `HNone | HBool bool | HFloat
real | HTuple hval_list` to the emitted `hval`.
- Why3 accepts the type.
- But 5 emitted consumers become non-exhaustive (`absurd` VCs): `hval_truthy`, the `or`-default template and the
  isinstance arms.
- Every consumer template, and the Phase2f / PyVal.lean certificates, gains arms.
- Today the absent key is `HInt pycsl_none`. That is why `isinstance(v, str)` has an `HInt _ -> (any bool)` arm
  (`d030_1`): an `HNone` tag removes that imprecision.

**Model-seam findings (selection defects, each fail-closed):**
- `Dict[str, PyVal]`, `Tuple[..]` and bare `PyVal` RETURNS are not selected (`d027_2`, `d164_T`), while
  `List[Dict[str, PyVal]]` returns are (`d356_2`).
- A bare `PyVal` PARAMETER lowers to `int` (`d374_3`).
- `x or []` passed to a PyVal slot gets a spurious `hstr_of` (`d374_3`).
- An isinstance-narrowed hval stays hval at a `str` annotated local (`d030_2`).
- hval truthiness in an IfExp condition is lowered as `str_eq_op .. ""` (`d253_2`).
- A typed dict of tuples must use `seq` payloads (Why3 rejects mutable `array` map payloads, `d030_x1`).
- The VERIFIED generic-fold caller passes `any map string (option hval)`, i.e. the pyval -> hval bridge is
  input-blind (`d030_x2`).

## 1. Recommended build (smallest set with measured closures)

| step | capability | closes (cumulative) | home + proof | risk |
|---:|---|---|---|---|
| 0 | none: the [T]/[R] links of s375 | s375 | pycsl.py ~0.5 h | none new |
| 1 | O7a hval-element comprehension (filter/map over `seq hval`, with a content law) | + s356 | pycsl.py | low (law-free, deterministic) |
| 2 | O19 hval formatting (`str(h)` / f-string: `HStr s -> s`, `HInt i -> decimal`, others opaque) + the Optional[List[str]] union-arm typing fix + O3 HNone tag | + s363 | pycsl.py + Phase2f/PyVal.lean (new tag) | med (new constructor: every hval consumer template gains an arm) |
| 3 | O6 Tuple[PyVal..] return codomain + O7b hval `tuple()` (HTuple tag for hashability) | + s362 | pycsl.py | med (r3: Alt-Ergo proves rk_hval_chain, Z3 times out: pairs_get E-matching) |

**Make-or-break spike:** convert s375 + s356 + s363 + s362 in pycsl.py with steps 0-3, then run one pycsl.py
whole-file proof, plus the mirror-emit sweep and the byte-diff sweep. The HNone tag moves every emission that
uses hval: re-measure the r3 cost of `stmt_control_flow` (~2,400 s after one hval field retype) before
committing to it.

**Next ring.** These stubs have only one more measured op (or none beyond the bundle) at their first value wall.
None of them was walked past L1/L2, so each could still hide later walls:

| stub | measured ops beyond {O1 O2 O3 O6 O7 O19} | status |
|---|---|---|
| s140 | (none beyond the bundle measured; chain not walked past L1) | open (5-tuple unpack of an Any element of an IR import list) |
| s158 | (none beyond the bundle measured; chain not walked past L1) | open |
| s250 | (none beyond the bundle measured; chain not walked past L1) | open (R487 `or` value over IR reads) |
| s036 | O5 | open (R252) |
| s067 | O17 | open (typed dict-of-list values) |
| s077 | O5 | open (R252) |
| s092 | O17 | open (typed Dict[int, List[...]] field value) |
| s096 | O5 | open (R252) |
| s108 | O11 | open |
| s139 | O11 | open |
| s145 | O5 | open |
| s147 | O5 | open |
| s149 | O5 | open (R252) |
| s152 | O13 | open (#381 hashing an IR dict value) |
| s159 | O5 | open (R252) |
| s163 | O11 | open (element store through a non-list: nested write-back) |
| s166 | O11 | open (`spec.pop` on an IR dict) |
| s167 | O11 | open (`spec.pop`) |
| s225 | O8 | open (str.split of an hval / erased str) |
| s236 | O11 | open (worklist pop over IR dicts) |
| s268 | O12 | open |
| s269 | O13 | open |
| s271 | O11 | open (mutator) |
| s273 | O12 | open |
| s282 | O9 | open (flags dict: bool/set payloads, sorted() over a set payload, O19) |
| s311 | O13 | open (#381) |
| s322 | O20 | open (`pycsl_py_eq a b` on Any values in a union return) |
| s329 | O16 | open |
| s330 | O11 | open (local list/dict mutator) |
| s349 | O13 | open (#381) |
| s001 | O17 O4 | open (L1: dict-of-set field) |
| s027 | O10 O9 | open (L2: return codomain not selected; record list field erased) |
| s118 | O11 O12 | open |
| s142 | O11 O13 | open |
| s253 | O18 O4 | open (L2) |
| s374 | O18 O9 | open (L3: needs O7 join + O19 + O18 + O9) |
| s003 | O11 O16 O9 | open |
| s006 | O11 O16 O9 | open |
| s030 | O16 O17 O4 | open (4 links + raises propagation into the verified fold caller) |
| s160 | O10 O11 O14 | open |
| s162 | O11 O14 O4 | open |
| s164 | O14 O15 O4 | open (stTP) |
| s287 | O12 O16 O5 | open |
| s270 | O10 O13 O5 O8 | open (L2) |

## 2. Operation x stub matrix (all 127, measured links; `matrix.py`)

| op | meaning | stubs needing it |
|---|---|---:|
| O1 | get / get-default / nested get (exists: pairs_get) | 9 |
| O2 | truthiness incl. `or`-default and IfExp conditions | 7 |
| O3 | None / absent tag (HNone; today absent = HInt pycsl_none) | 7 |
| O4 | isinstance / type test + narrowing projection to str/int (keys, slots) | 6 |
| O5 | hval at a builtin-typed CALL ARGUMENT (R252 projection with a tag obligation) | 10 |
| O6 | PyVal RETURN codomain (Tuple[PyVal..] / Dict[str,PyVal] / List[Dict..] / PyVal) | 4 |
| O7 | hval-polymorphic builtins (tuple, join, set, list, bool, int, str, sum, all, [i]) | 8 |
| O8 | str methods on an hval (split, lower, ...) | 3 |
| O9 | bool / float payload tags (HBool, HFloat) | 7 |
| O10 | mixed-payload dict / list LITERAL construction | 5 |
| O11 | in-place store / setdefault / pop / update / insert on a dict value (incl. nested path write-back) | 18 |
| O12 | by-REFERENCE dicts: Dict[str,Any] FIELDS, dicts passed to mutating callees | 5 |
| O13 | HASHING an hval (set element / dict key; hashability tag, HTuple) | 8 |
| O14 | items() / keys() / values() iteration | 3 |
| O15 | recursion over a json-like tree (structural hval measure) | 4 |
| O16 | bridges between value models (hval<->emit_ir, hval<->pyval, PyVal through trusted callee signatures) | 5 |
| O17 | typed dicts with container values (Dict[str, Set/Tuple/List]; seq payloads) | 4 |
| O18 | hval-typed locals (hoisted / re-bound) | 3 |
| O19 | f-string / str() formatting of an hval | 3 |
| O20 | equality / ordering between two Any values (pycsl_py_eq today) | 1 |

| stub | ops | non-value first wall | closes? |
|---|---|---|---|
| s362 | O1 O2 O3 O6 O7 O13 | - | CLOSES (mlwx/d362_x1: O6 + O7 tuple + O3) |
| s374 | O1 O2 O7 O9 O18 O19 | - | open (L3: needs O7 join + O19 + O18 + O9) |
| s030 | O1 O3 O4 O16 O17 | - | open (4 links + raises propagation into the verified fold caller) |
| s001 | O1 O2 O4 O7 O17 | - | open (L1: dict-of-set field) |
| s027 | O6 O9 O10 | - | open (L2: return codomain not selected; record list field erased) |
| s253 | O1 O2 O4 O7 O18 | - | open (L2) |
| s270 | O1 O2 O3 O5 O6 O8 O10 O13 | - | open (L2) |
| s279 | O1 O5 O8 | byref Set param .add | open |
| s142 | O11 O13 | - | open |
| s162 | O4 O11 O14 | - | open |
| s164 | O4 O6 O14 O15 | - | open (stTP) |
| s006 | O9 O11 O16 | - | open |
| s003 | O9 O11 O16 | - | open |
| s160 | O10 O11 O14 | - | open |
| s287 | O1 O5 O12 O16 | - | open |
| s357 | O13 | needs s362 | open |
| s329 | O16 | - | open |
| s158 | O7 | - | open |
| s147 | O5 | - | open |
| s145 | O5 | - | open |
| s150 | O11 | R319 param rebind | open |
| s139 | O11 | - | open |
| s108 | O11 | - | open |
| s118 | O11 O12 | - | open |
| s269 | O13 | - | open |
| s273 | O12 | - | open |
| s268 | O12 | - | open |
| s137 | O11 | local dict .update | open |
| s011 | O11 | local set .update | open |
| s257 | O4 | R301 nested unpack | open |
| s258 | O18 | R274 (free [R]) | open |
| s175 | - | Optional record param / emit_ir field write | out of dict scope |
| s230 | - | R563 method arg kind | open |
| s135 | - | byref List param extend | open |
| s292 | O15 | closure lift | open |
| s031 | O15 | closure lift | open |
| s229 | - | closure lift | open |
| s277 | - | closure lift | open |
| s267 | - | closure lift | open |
| s138 | - | closure lift | open |
| s074 | - | array-local rebind | open |
| s136 | O12 | R316 frame | open |
| s294 | - | non-growable append | open |
| s356 | O7 | - | CLOSES (mlwx/d356_x1: O7 hval-element comprehension; [T] List[Dict[str,PyVal]] return IS selected) |
| s375 | - | - | CLOSES with free [T]/[R] only (d375_3) |
| s363 | O1 O2 O3 O19 | - | CLOSES (mlwx/d363_x1: O19 + Optional[List[str]] union-arm typing + O3 for the R521 proof) |
| s163 | O11 | - | open (element store through a non-list: nested write-back) |
| s166 | O11 | - | open (`spec.pop` on an IR dict) |
| s167 | O11 | - | open (`spec.pop`) |
| s330 | O11 | - | open (local list/dict mutator) |
| s322 | O20 | - | open (`pycsl_py_eq a b` on Any values in a union return) |
| s225 | O8 | - | open (str.split of an hval / erased str) |
| s092 | O17 | - | open (typed Dict[int, List[...]] field value) |
| s067 | O17 | - | open (typed dict-of-list values) |
| s140 | O7 | - | open (5-tuple unpack of an Any element of an IR import list) |
| s165 | O15 | R542 on the Any tree | open |
| s036 | O5 | - | open (R252) |
| s077 | O5 | - | open (R252) |
| s149 | O5 | - | open (R252) |
| s159 | O5 | - | open (R252) |
| s060 | O3 | R252 / Optional record fields | open |
| s059 | O3 | Optional/List record fields | open |
| s282 | O7 O9 O19 | - | open (flags dict: bool/set payloads, sorted() over a set payload, O19) |
| s055 | - | R325 constant model | open |
| s033 | - | R325 | open |
| s086 | - | R325 | open |
| s052 | - | R551 CSL constructor arg kind | open |
| s058 | - | CSL record vs emit_ir | open |
| s078 | - | CSL record vs emit_ir | open |
| s051 | - | CSL clause union | open |
| s083 | - | CSL record vs emit_ir | open |
| s103 | - | CSL record vs emit_ir | open |
| s063 | - | R567 emit_ir attr on non-IR | open |
| s192 | - | pyast attribute write-back | open |
| s110 | - | pyast node typing | open |
| s232 | - | erased str receiver | open |
| s112 | O3 | Optional[ExprIR] codomain | open |
| s042 | - | method recursion | open |
| s241 | - | method recursion (families rank 3) | open |
| s309 | - | method recursion | open |
| s345 | - | generator (family d) | open |
| s342 | O11 | pop on byref param + sexp value model | open |
| s353 | - | EXT | out of scope |
| s347 | - | EXT | out of scope |
| s344 | - | EXT | out of scope |
| s014 | - | EXT fs | out of scope |
| s143 | - | EXT with/fs | out of scope |
| s019 | O9 | float->str | open |
| s045 | - | lvR typed locals | lvR |
| s289 | - | lvR rank-0 | lvR |
| s354 | - | lvR + re | lvR |
| s359 | - | lvR | lvR |
| s314 | - | lvR rank-0 | lvR |
| s066 | - | re lastgroup (families rank 1) | open |
| s231 | - | R563 | open |
| s262 | - | R301 | open |
| s146 | - | R301 | open |
| s280 | - | non-growable append | open |
| s116 | - | field append | open |
| s336 | - | sorted(key=) kwarg | open |
| s319 | - | kwarg dropped | open |
| s324 | - | kwarg dropped | open |
| s056 | - | except SyntaxError hierarchy | open |
| s238 | - | proof wall (cv12) | open |
| s227 | O9 O10 | R350 Optional dict default | open |
| s249 | - | R350 | open |
| s007 | - | R319 | open |
| s296 | - | R319 | open |
| s331 | - | R319 | open |
| s256 | - | closure lift | open |
| s284 | - | #303 | open |
| s126 | - | array rebind | open |
| s002 | - | #303 | open |
| s054 | - | CSL record vs emit_ir | open |
| s096 | O5 | - | open (R252) |
| s152 | O13 | - | open (#381 hashing an IR dict value) |
| s154 | - | #303 | open |
| s234 | - | closure lift | open |
| s236 | O11 | - | open (worklist pop over IR dicts) |
| s239 | - | kwarg dropped | open |
| s248 | O10 | dict(..., k=v) kwargs | open |
| s250 | O2 | - | open (R487 `or` value over IR reads) |
| s271 | O11 | - | open (mutator) |
| s297 | - | R325 | open |
| s300 | - | definite assignment | open |
| s311 | O13 | - | open (#381) |
| s349 | O13 | - | open (#381) |

Syntactic upper bound over all 127 live bodies (`dops.py`; counts any value, not only dict values):

| syntactic op (live body, any value: an UPPER bound) | stubs of 127 |
|---|---:|
| truthiness_if | 108 |
| subscript_varkey | 101 |
| get_nodefault | 68 |
| get_default | 67 |
| in_test | 66 |
| dict_literal | 62 |
| truthiness_or | 62 |
| eq_literal | 60 |
| isinstance_test | 52 |
| hash_value | 49 |
| list_payload_iter | 47 |
| subscript_strkey | 46 |
| item_store | 41 |
| len | 39 |
| items_iter | 33 |
| str_payload | 30 |
| nested_get | 20 |
| pop | 14 |
| self_recursion | 13 |
| setdefault | 13 |
| values_iter | 10 |
| int_payload | 7 |
| update | 5 |
| bool_payload | 3 |
| type_test | 3 |
| keys_iter | 3 |
| copy | 1 |
| float_payload | 1 |

## 3. Per-stub record of the walked chains (`dnotes.tsv`)

| sid | stub | probe | verdict | receiver shapes | value operations needed (measured link) | wall past the model | closes? |
|---|---|---|---|---|---|---|---|
| s362 | _record_key | d362_1 | L3-TC | Dict param (rec), nested Dict via .get or {} | get-default(or {}), nested get, truthiness(or), None payload (absent keys inside returned tuple: R521 needs an HNone/HAbsent tag), Tuple[PyVal..] return codomain, tuple(<hval list>) | tuple_1 int-typed builtin over hval; return codomain (int,int,int) | r3 rk_hval_chain.mlw: closes with {Tuple[PyVal] codomain, hval tuple} (Alt-Ergo proves, Z3 times out); now also R521 needs a None tag |
| s374 | _synthesize_block | d374_1 | REFUSED | Dict param (rec), nested Dict via .get or {} | get-default (str/int/float defaults), nested get, str `or` as value, join over hval list, f-string of hval str/int, float payload (`{t:.2f}`), hval==str | R487 boolop value (`", ".join(..) or "goal"`) | - |
| s030 | _namedtuple_check_call | d030_1 | L3-TC | Dict param (call), typed Dict[str, Tuple] param | get, isinstance(v, str) test on a value + narrowing to str at a dict-key position, HInt arm of isinstance is `(any bool)` (absent conflated with int: needs HAbsent) | hval used as a map string key | - |
| s030 | _namedtuple_check_call | d030_2/mlwx d030_x1,x2 | L3-TC | Dict param + typed Dict[str,Tuple] param; verified generic-fold caller (pyval model) | isinstance narrowing -> hstr_of at key; typed tuple-valued dict (payload must be seq, not array: Why3 forbids mutable map payloads); pyval->hval bridge at the verified caller (today `any map string (option hval)`: input-blind); raises propagation into the fold caller | x2: verified caller `_namedtuple_walk_construction` lacks `raises PyCSLSemanticError` | NO (4 links, chain open) |
| s374 | _synthesize_block | d374_2 | L3-TC | Dict param + nested | join over an HArr of HStr (`join_1` int-typed); a FLOAT payload (`get("time", 0.0)` emits `HInt 0.0`: needs HFloat); re-binding an hval local (`ans = ""` after `if not ans`, emitted as `ans := ""` on a non-ref hval let); f-string of hval int/str/float incl. `{t:.2f}`; hval==str (ok: `match HStr`); a branch-assigned str local `tok` is scoped per branch | join_1 over hval | NO (>=4 more links) |
| s001 | _build_callee_no_exception_summary | d001_1 | REFUSED | List[Dict] param element; typed self dict fields Dict[str, Set[str]] / Dict[str, bool] / Dict[str, List[str]] | iterate List[hval-dict]; get no-default + truthiness skip; nested get with {} default; set(<hval list> or []), bool(<hval>), list(<hval> or []) conversions; hval (truthy, NOT isinstance-narrowed) used as a str key of typed fields | R325: typed dict field with SET values (`Dict[str, Set[str]]`) has no value model | NO |
| s027 | _to_cache_payload | d027_1 | L3-TC | Returned heterogeneous dict literal (mirror `-> dict`), record fields bool/str/float + list-of-lists | dict LITERAL with mixed payloads: bool, str, float, list of [str, bool, list] triples (needs HBool, HFloat, nested HArr), list comprehension building hval rows | str record field stored into `map int (option int)` (return codomain not hval) | - |
| s027 | _to_cache_payload | d027_2 | L3-TC | (same) | + a `Dict[str, PyVal]` RETURN codomain: not selected today (r3 backlog #69, re-measured: the literal is still `map int (option int)`) | same clash | NO |
| s175 | _Parser._fin | d175_1 | L3-TC | Optional[_tok] param (`end_tok=None`), attribute writes on an emit_ir node | not a dict value: Optional record param vs pycsl_none; then emit_ir in-place field write (CORRECTNESS boundary per cv12) | Optional record | NO (out of dict scope) |
| s279 | _emit_opaque_class_aliases | d279_1 | REFUSED | List[Dict] param element; Set[str] param mutated | get eq-literal, truthiness, [k] str read, str method on an hval (`.lower()`), whyml_ident(<hval>) (hval->str at a str slot) | Set PARAM `.add` (byref mutator, not dict) | NO |
| s142 | _inject_functions | d142_1 | REFUSED | List[Dict] param; Dict param with nested list | set comprehension of hval names (HASHING an hval: #UND), `in` on a set of hval, nested-list INSERT through a dict value (path write-back `ir_data["functions"].insert(0, f)`), set.add of hval | computed-receiver mutator (nested container write-back) | NO |
| s253 | _handle_sum_call | d253_2 | L3-TC | Any-IR param (`expr`, hval stand-in) + typed self fields Dict[str,int] / Dict[str, Dict[int, Any]] via getattr default | get with list-of-dict default `[{}]` (ok: HArr(HCons(HMap PNil))); TRUTHINESS of an hval in an IfExp condition (lowered as str_eq_op .. "": wrong type); hval list index `[0]`; isinstance(<hval>, int); all(genexp over hval list); sum/int(<hval>); str(<Any>) of a typed-dict value | hval truthiness in IfExp | NO |
| s162 | _rewrite_annotations | d162_1 | REFUSED | Dict param (ir_data); its list elements are dicts | iterate list value of a dict; get with `or {}`; items() iteration; build a fresh dict from hval values; ITEM STORE into a dict that is an element of a list inside the param (path write-back); isinstance(<hval>, str) | element store through a non-list value | NO |
| s230 | _handle_ctor_payload_expr | d230_1 | REFUSED | Any-IR node | (not a dict wall first) R563 method argument kind (set-typed param of a sibling) | R563 | NO |
| s164 | _rewrite_subscript_calls_in_stmt | d164_T (stTP) | L3-TC | Any param (json-like IR tree), returns Any | isinstance(<v>, dict/list) dispatch; items() iteration; build a fresh dict / list of rewritten children; RECURSION over the tree (needs a structural measure over hval: hval is an ADT, so a size exists in principle); a `PyVal` RETURN codomain (not selected: `raise (Return !new)` of a map into an int return) | Any/PyVal return codomain | NO |
| s006 | _shared_use_lines | d006_1 | REFUSED | local from a trusted callee returning the heterogeneous flags Dict[str, Any] (bool/set/int values) | ITEM STORE of a bool into a mixed dict obtained from a call; pass the dict on; get of bool/set payloads | element store through a non-list value (the callee result is an int) | NO |
| s135 | _hoist_calls_in_expr | d135_1 | REFUSED | Any param (IR tree) + List param mutated | isinstance list/dict dispatch, {**node, ...} dict rebuild, recursion; first wall is the List PARAM `pre.extend` (byref mutator, not dict) | byref list param extend | NO |
| s160 | _record_classification | d160_1 | REFUSED | Dict param (ir_data), Dict[str, Dict] param | items() iteration of a dict-of-dict; set of tuples; list of str-valued dict LITERALS; `setdefault(k, {})[k2] = v` (setdefault + nested item store = path write-back into the param) | setdefault on an hval dict | NO |
| s287 | _fresh_globals_facts | d287_1 | L3-TC | self.ir (Dict[str, Any] FIELD), self._record_types field, rec dict values | get with list default on the IR field; [k] str; get-or-[] on a field-dict value; whyml_ident(<hval>) (str slot); an hval passed to an `ExprIR` parameter (`_expr_to_whyml(retargeted)`: hval <-> emit_ir BRIDGE between the two IR models) | receiver-less `rec_get_2`: the field value is erased | NO |
| s357 | _merge_records_best_of_n | d357_1 | L3-TC | List[List[dict]] param (quoted; the L1 generator did not retype it) | depends on s362 _record_key (an hval-tuple KEY of `occ: Dict[Tuple, int]`: hashing an hval tuple), nested list-of-list-of-dict iteration, get of int/float payload for "best" selection | erased record passed to the hval-typed _record_key | NO (needs s362 first) |
| s329 | _is_ofnat_lit | d329_1 | L3-TC | Dict param (Lean JSON AST) | hval passed to a TRUSTED callee whose mirror sig is int (`_linearize_app`): PyVal must propagate through callee signatures; tuple unpack of the callee result (head, args); get/eq on nested JSON | hval vs int at a trusted-callee argument | NO |
| s158 | _collect_instantiations | d158_1 | REFUSED | Dict param + local dict-of-dict | `set(<dict>)` (key set of a dict-of-dict local), recursion/iteration over IR | R542 set() argument | NO |
| s292 | _subst_self_in_expr | d292_1 | REFUSED | Any IR tree | nested recursive closure `rec` (closure lift wall first) | closure lift | NO |
| s074 | _field_write_site | d074_1 | REFUSED | Any IR | array local rebind first (not dict) | array-local rebind | NO |
| s138 | _recursive_methods | d138_1 | REFUSED | List[Dict] param | nested closure reaches_self first | closure lift | NO |
| s147 | _resolve_module_imports | d147_1 | REFUSED | Dict params (ir_data, cache) | hval passed to builtin-typed slots of a callee (`level: int`, `module_dotted: str` of `_resolve_module_path`): R252 needs hval->int / hval->str PROJECTIONS at call arguments (with a tag obligation) | R252 hval into int/str slot | NO |
| s150 | _strip_dir_scan_proofs | d150_1 | REFUSED | Dict param (func) | parameter rebind in a nested block first (`func = dict(func)`: a COPY of an hval dict = dict(hval) op), then item store / pop on the copy | R319 param rebind | NO |
| s031 | _returns_literal_none | d031_1 | REFUSED | Any IR tree | nested recursive closure `walk` first | closure lift | NO |
| s229 | _should_auto_trust_tuple_return | d229_1 | REFUSED | List[Dict] param | nested closure first | closure lift | NO |
| s139 | apply_inline_globals | d139_1 | REFUSED | Dict param | `.pop(k, default)` on an hval dict (an element of a list value), item store, del | dict pop on hval | NO |
| s257 | _linear_form | d257_1 | REFUSED | Any IR (hval stand-in) | nested tuple unpack of an Optional[Tuple[int, Dict[str,int]]] recursive result; get/eq-literal/isinstance int on hval; dict of int coefficients | R301 nested unpack | NO |
| s277 | _emit_inductive_decls | d277_1 | REFUSED | List[Dict] param | nested closure first | closure lift | NO |
| s270 | _mixin_dep_pseudo_functions | d270_1 + mlwx/d270_x1 | L3-TC | List[Dict] param; returns List[Dict] | get-or-[] + truthiness skip (ok); hval->str PROJECTION at a trusted str argument (x1 repairs it); then: str METHODS on an hval (`name.split("__")[0]`, `"__" in name` ok via hval_in), f-string mixing hval/str, set comprehension of hval names (HASHING an hval: #UND), dict comprehension from a trusted tuple list, mixed-payload dict LITERAL (str, list, nested dict, None, bool False) appended to a `List[Dict[str, PyVal]]` RETURN (codomain not selected), R521 None in the returned container (needs a None tag) | x1: `str_concat` of an erased `name.split(..)[0]` (int) with a str | NO (>=4 more links) |
| s108 | _emit_protocol_interface | d108_1 | REFUSED | self fields holding IR dicts | append on a COMPUTED receiver (a list value inside a dict: path write-back) | computed-receiver mutator | NO |
| s258 | _match_pattern_cond | d258_1 | REFUSED | Any-IR pattern dict | writing self-call in a comprehension first ([R] for-loop is free; then the pattern dict reads, see families c900_M2: the recursive stub is int-typed because the element `a` of `pat.get("alternatives", [])` is erased) | R274 | NO |
| s267 | _emit_narrowing_vc | d267_1 | REFUSED | Dict params | nested closure first | closure lift | NO |
| s136 | inline_stmts | d136_1 | REFUSED | List param of IR stmts | method frame: the List param is written (byref), not declared | R316 frame | NO |
| s145 | _resolve_imported_base_classes | d145_1 | REFUSED | Dict params | R252: hval into int/str slots of `_resolve_module_path` (as s147) | R252 hval into builtin slot | NO |
| s003 | _emit_prefunctions_infra | d003_1 | REFUSED | List[Dict] params; flags Dict[str, Any] from a trusted callee | item store of a bool into the heterogeneous flags dict from a call (as s006) | element store through a non-list value | NO |
| s273 | _render_refinement_goal | d273_1 | REFUSED | Dict params (ov, sub_fn, base_fn) | passing an IR dict to a callee that MUTATES it (`_reset_function_state(func)` writes `func`): needs a by-REFERENCE (aliased, mutable) dict value with a writes frame, not a pure hval | R316 method arg unframed | NO |
| s268 | _emit_subtyping_goals | d268_1 | REFUSED | List[Dict] param | the List[Dict] param is written via callees (byref mutation of an IR list param) | R316 method frame | NO |
| s294 | sort_functions_by_scc | d294_1 | REFUSED | List[Dict] param | non-growable list append first (list bound from a call result) | growable-list local | NO |
| s118 | _populate_protocol_conformance | d118_1 | REFUSED | self.program_ir (Dict[str, Any] FIELD) | `setdefault` on a Dict[str, Any] field (nested path write-back into object state) | setdefault on a dict field | NO |
| s269 | _emit_union_arm_vc | d269_1 | REFUSED | Dict param (symbol_table) values | HASHING an hval (`symtype not in variant_types`: a dict value used as a key: #UND) - needs a hashability tag (HStr hashable, HMap/HArr not) | #381 hash of an hval | NO |
| s137 | _inline_calls | d137_1 | REFUSED | List[Dict] param | `.update` on a local dict (mutator) first | local dict update | NO |
| s356 | _json_goal_records | d356_2 + mlwx/d356_x1 | TC-OK (stand-in) | List[Dict] returned by a trusted callee (`_parse_why3_json`, json-facing) | [T] both sigs `-> List[Dict[str, PyVal]]` (SELECTED today: `seq hval`); comprehension filtering hval elements by `"k" in r` (the comp op is int-typed: stand-in `list_content_comp_0 : seq hval -> seq hval`, length law only; a content law is needed for a useful spec) | - | CLOSES with {O7 hval-element comprehension} (+[T]) |
| s345 | parse_sexp | d345_1 | L3-TC | sexp (generator tokens) | not a dict value: `list(_sexp_tokens(s))` generator result (family d) then the sexp tuple value model | generator | NO (out of dict scope) |
| s353 | _find_coqc | d353_1 | L3-TC | - | external `shutil.which` (lvQ) | EXT | NO (out of scope) |
| s375 | _synthesize_legacy_text | d375_3 | TC-OK | List[Dict] param passed elementwise to a trusted Dict callee | [T] `records: List[Dict[str, PyVal]]` + [T] trusted callee `_synthesize_block(rec: Dict[str, PyVal])`; [R] the genexp join -> for/append + join (behaviour-identical); hval->map bridge `hval_to_map` exists | - | CLOSES with NO new capability (free [T]/[R] links on the existing hval model) |
| s363 | _residual_selectors_from_records | d363_2 | REFUSED | List[Dict] param, nested get via `or {}` | [T] hval sigs + [R] split tuple unpack; then F-STRING / str() of hval values (`f"{fn}:{ln}"`, HStr and HInt payloads) is opaque (R325 str_concat); `fn is None` on an hval (needs the None tag); a verified callee `_record_is_valid(rec)` already takes Dict[str, PyVal] | R325 f-string of an hval | NO (1 op: hval formatting; + None tag) |
| s363 | _residual_selectors_from_records | d363_3..5 + mlwx/d363_x1 | TC-OK (stand-in) | List[Dict] param, nested get via `or {}` | [T] hval sigs, [R] split unpack, [T] unquote `sels`/`seen` annotations (quoted locals lower to int maps); O19 hval FORMATTING (stand-in helper `_cv13_hval_fmt(a: PyVal, b: PyVal) -> str`; a bare `PyVal` param IS hval, a Dict-typed one clashes: d363_3); OPTIONAL[List[str]] return: the union arm is typed `int` (`Arm_3_0 int`): a typing fix; the R521 obligation on `fn` needs the None tag to be provable from the `fn is None` guard | - | CLOSES with {O19, Optional-list union arm typing, O3 (proof)} |
| s374 | _synthesize_block | d374_3 + mlwx/d374_x1 | L3-TC | (same) | with stand-ins for O7 join (`_cv13_hval_join`) and O19 formatting (`_cv13_hval_fmt7`): (i) the `x or []` template passed to a PyVal-typed slot wraps an hstr_of (emitter selection defect), (ii) a bare `PyVal` PARAM of a helper lowers to int (not hval), (iii) next wall O18: `if not ans: ans = ""` re-binds an hval let (needs hval refs), then O9 (`HInt 0.0`: float default) | O18 hval local rebinding | NO (needs O7 + O19 + O18 + O9) |
| s282 | _emit_preamble_exceptions | d282_1 | REFUSED | the heterogeneous preamble FLAGS dict `needs` (bool / set / int payloads; shared by s003 s006 s280 s283) | [k] truthiness of bool payloads (needs HBool), get with a set() default, sorted() over a SET payload (needs a set tag, or a typed flags record), element projection to int, f-string of the element (O19) | R325 str_concat over an erased `sorted(..)` element | NO |

## 4. Reproduction

- Probe: `HEAVY_QUICK=1 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh bash scratchpad/cv13/probe.sh <rel>
  <Qualified.fn> <tag> <spec.json>`, drained by `scratchpad/cv13/chunk.sh` from `queue.list` (20 s gap).
- Scratch trees: `st` (HEAD) and `stTP` (HEAD + `scratchpad/lvC/typepos.patch`, for `d164_T`). Each one is a
  copy of `bin/ src/`.
- L1 specs come from `python3 scratchpad/cv13/gen_l1.py <sid..>`. Emission stand-ins are checked with
  `scratchpad/cv13/tcx.sh mlwx/<f>.mlw` (`heavy.sh why3 prove --type-only`).
- Tables: `python3 matrix.py`, `python3 notes2md.py` and `python3 wclass.py`, all run in `scratchpad/cv13`.
- The cv13 families census (pre-redirect) is in `getting-better/run7-capability-census-2.md` (PARTIAL).
