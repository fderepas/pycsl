"""#33 — THE MODULE-5 INPUT NORMALIZATION PASS (Python-AST -> Python-AST).

Every rewrite here exists because a Module 5 handler SILENTLY DROPS part of the node it is
given — a fail-OPEN erasure, invisible to every gate plane because the dropped construct
simply is not in the IR to be checked. Normalizing the INPUT is deliberate: the handlers
(`_py_expr_compare`, `_py_stmt_annassign`) are CONVERTED mirror methods whose models are
HAND-SYNTHESIZED bespoke lowerings keyed on the method name, so editing their bodies would
leave mirror-sync, L3-tc and the whole-file proof all GREEN while the model silently
stopped being the body. Rewriting the input instead leaves every such body byte-identical
and makes its bespoke model TRUE, because the shape it cannot express no longer reaches it.


## 1. CHAINED COMPARISONS

Python's `a < b < c` means `a < b and b < c`, with the middle operand evaluated EXACTLY
ONCE. Module 5's expression walker (`_py_expr_compare`) lowers a `Compare` node by reading
`ops[0]` and `comparators[0]` and DISCARDING the rest, so before this pass every chain lost
its tail: `if 2 <= a <= 3:` became `if (2 <= a)`.

That is not a harmless over-approximation. A guard that is TRUE MORE OFTEN than Python's
over-approximates the THEN branch (more states, still sound) but UNDER-approximates the
ELSE: every state with `a >= 2` and `a > 3` takes Python's else and the model's then, so
the else branch was proved over a strict SUBSET of the reachable states.

It was also an internal disagreement. The `#@` ANNOTATION grammar has always expanded
chains correctly (`#@ ensures 0 <= \\result < 256` emits `0 <= result && result < 256`), so
the two halves of the same file meant different things by `a <= b <= c`.

WHY A PRE-PASS AND NOT A FIX INSIDE `_py_expr_compare`. That method is CONVERTED in the
self-annotation mirror and its model is a HAND-SYNTHESIZED whole-body lowering
(`module6_whyml/functions.py::_emit_py_expr_compare_bespoke`) keyed on the METHOD NAME,
which emits the head comparison and nothing else. Changing the live body would leave
mirror-sync GREEN (the bodies would still match), L3-tc green and the proof green, while
the model silently stopped being the body — the exact faithfulness trap this campaign
exists to close. Normalizing the input instead leaves `_py_expr_compare` byte-identical and
makes its bespoke model's claim — "the head comparison is the whole node" — TRUE, because
after this pass no multi-operator `Compare` reaches Module 5 at all.

WHERE IT RUNS: `Module5_IREmitter.generate_json`, immediately before the walk. That is the
single choke point both Module 5 entry paths go through (`pycsl.py`'s main pipeline and
`ir_resolve.resolve`'s dependency sub-pipeline), so no caller can forget it.

EVALUATION ORDER IS THE SOUNDNESS ARGUMENT, AND NOTHING IS REFUSED. The naive expansion
mentions the middle operand TWICE while Python evaluates it once, so it is
semantics-preserving only when re-evaluating that operand is observationally identical.
Names, constants, attribute and subscript reads and arithmetic over them qualify (a
subscript that raises raises identically both times), as does a call to a pure, total,
deterministic builtin — `len`, `ord`, `abs`, `chr`, the spellings that actually occur in a
chain's middle (`2 <= len(xs) <= 3`, `32 <= ord(ch) <= 126`). `_chain_operand_repeatable`
decides exactly that, from a literal allow-list rather than a heuristic.

When the middle operand is NOT repeatable — `0 <= enc_range() < 256`, four of which are in
the reference corpus — it is NOT mentioned twice and it is NOT refused. It is bound by a
WALRUS on its first and only evaluation and read back in the next link:

    a <= f() <= b      ->      a <= (_pycsl_cmp_1 := f())  and  _pycsl_cmp_1 <= b

which is Python's own rule for a chain, written in Python. No purity assumption is needed
and no idiom is rejected. The temporary is numbered from a per-pass counter, never from
`id(...)`, because the emitted `.mlw` must be byte-reproducible across runs.


## 2. ANNOTATED STORES THROUGH A NON-NAME TARGET

`_py_stmt_annassign` is

    if isinstance(stmt.target, ast.Name) and stmt.value is not None:
        ir_stmts.append({"stmt": "Assign", ...})

so `self.x: int = 0` and `a[i]: int = v` — an AnnAssign whose target is an ATTRIBUTE or a
SUBSCRIPT — produce NO IR AT ALL. The store vanishes. `_py_stmt_assign` handles exactly
these targets, and handles them carefully: `self.f = v` becomes a `FieldAssign`, `p.f = v`
on a record-typed parameter becomes a caller-visible `FieldAssign`, `a[i].f = v` is
REFUSED with a diagnostic — its own comment records that the earlier silent drop was "an
UNSOUND fail-OPEN: a caller/body could prove the field UNCHANGED after a real mutation".
The annotated form is the same store with a type written on it, and it had the very bug
`_py_stmt_assign` was fixed for.

So `_normalize_annotated_stores` rewrites `<non-Name target>: T = v` into `<target> = v`
and lets `_py_stmt_assign` decide. `T` is a DECLARATION, not part of the store, and no
consumer reads it here — with ONE exception, which is why `__init__` is excluded: Module 5
`_collect_class_fields` and `module5/construction_synth` scan `__init__` bodies for
`self.x: T = ...` to recover the FIELD TYPE (that is how the mirror's own
`self._final_registry: List[Dict[str, PyVal]] = []` declares its type). Rewriting those
would erase the type, so they are left exactly as they are. Every other AnnAssign consumer
in the tree already filters on `isinstance(target, ast.Name)` and is unaffected.

CENSUS AT THE TIME OF WRITING: 0 in the reference corpus, 0 in the mirror, 0 in
`pycsl_lib`, 51 in the live emitter (`functions._reset_function_state`,
`Module6_WhyMLTranspiler.transpile`, `Module5_IREmitter.visit_Module`, ...). So this is
byte-inert today and it UNBLOCKS those state-reset methods for conversion.


## 3. MULTI-TARGET ASSIGNMENT `a = b = v`

`_py_stmt_assign` opens with `target = stmt.targets[0]` and never looks at the rest, so in
`a = b = 5` the binding of `b` DOES NOT EXIST in the model. When no other statement
assigns `b` the file at least fails L3-tc with `unbound function or predicate symbol 'b'`;
when another statement DOES assign it, the initialisation is silently lost and the local
keeps its declaration DEFAULT. That is not a theoretical hazard — it PROVES FALSE
POSTCONDITIONS. Measured, before the fix:

    def f(n: int) -> int:          #@ ensures n <= 0 ==> \result == 0
        a = b = 5
        if n > 0:
            b = 7
        return a * 0 + b

reported `Verification SUCCESS`, while `f(0)` returns 5 in Python. The model had `b`
declared `ref 0` and assigned only inside the `if`.

`normalize_stores` expands the statement into one assignment per target. The RHS is
re-mentioned only when it is a `Constant` or a `Name` — both SHARE their object, so the
aliasing Python guarantees (`a = b = []` binds ONE list to both names) is preserved; for
every other RHS a fresh temporary is bound first, so the value is computed exactly once.


## 4. `for ... else` / `while ... else`, AND THE EXTENDED SLICE, ARE REFUSED NOT DROPPED

`_process_for` and `_process_while` read `target`/`iter`/`body` and `test`/`body`; neither
reads `orelse`. A loop `else` runs exactly when the loop finished WITHOUT `break`, and
dropping it removes a whole reachable path from the model while leaving the program's
behaviour unchanged — fail-OPEN in the same way as the two above. Modelling it needs a
break-flag lowering, which is a feature, not a normalization. Until that exists the honest
answer is a loud refusal: `_reject_loop_else` raises. CENSUS: 0 in the corpus, 0 in the
mirror, 0 in `pycsl_lib`, 2 in the live emitter (both inside `\trusted` mirror stubs, whose
bodies are never parsed by this pipeline). `try ... else` is NOT affected —
`_py_stmt_try` does carry `orelse` and `finalbody`.

An EXTENDED SLICE `x[lo:hi:step]` lowers to `Array.sub x lo (hi - lo)` — the step is
dropped and the model carries a sequence of a DIFFERENT LENGTH with DIFFERENT ELEMENTS.
Measured, before the refusal:

    #@ ensures \result == xs[1] + xs[2]        <-- FALSE OF THE PROGRAM
    def f(xs: list) -> int:
        ys = xs[1:4:2]
        return ys[0] + ys[1]

    [+] Verification SUCCESS! All contracts formally proven.

`f` returns `xs[1] + xs[3]` in Python. Modelling a strided copy is a value-model feature,
not a normalization, so the honest answer is again a refusal. CENSUS: 0 in the corpus, 0 in
the mirror, 0 in `pycsl_lib`, 0 in the live emitter — the refusal is completely inert and
closes a demonstrated unsoundness.
"""
from __future__ import annotations

from frontend import pure_ast as ast
from errors import PyCSLParseError

# Calls that may be mentioned twice by the expansion: pure, total, deterministic
# projections of their argument, with no state and no I/O. A literal tuple, not a
# heuristic — widening it is a deliberate soundness decision.
_REPEATABLE_CALLS = ("len", "ord", "abs", "chr")

# Node kinds that are never safe to re-evaluate: they bind, suspend, or build.
_NON_REPEATABLE = (ast.Await, ast.NamedExpr, ast.Yield, ast.YieldFrom,
                   ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _chain_operand_repeatable(node: object) -> bool:
    """Is `node` safe to EVALUATE TWICE, as the chain expansion does?"""
    for sub in ast.walk(node):
        if isinstance(sub, _NON_REPEATABLE):
            return False
        if isinstance(sub, ast.Call):
            if not (isinstance(getattr(sub, "func", None), ast.Name)
                    and sub.func.id in _REPEATABLE_CALLS
                    and not getattr(sub, "keywords", [])):
                return False
    return True


class _ChainDesugarer(ast.NodeTransformer):
    def __init__(self) -> None:
        # A DETERMINISTIC counter, not `id(node)`: the emitted `.mlw` must be reproducible
        # byte-for-byte across runs, and an object address is not.
        self._n = 0

    def visit_Compare(self, node):
        self.generic_visit(node)
        ops = getattr(node, "ops", [])
        comparators = getattr(node, "comparators", [])
        if len(ops) <= 1:
            return node
        links = []
        left = node.left
        for k in range(len(ops)):
            right = comparators[k]
            if k + 1 < len(ops) and not _chain_operand_repeatable(right):
                # NOT SAFE TO MENTION TWICE — so DO NOT mention it twice. Bind it with a
                # walrus on its FIRST (and only) evaluation and read the binding in the
                # next link: `a <= (_t := f()) and _t <= b`. That is exactly Python's own
                # rule for a chain — the middle operand is evaluated once — expressed in
                # Python itself, so no purity assumption is needed and no idiom is refused.
                self._n += 1
                tmp = "_pycsl_cmp_%d" % (self._n,)
                bind = ast.NamedExpr(target=ast.Name(id=tmp, ctx=ast.Store()), value=right)
                ast.copy_location(bind, node)
                ast.fix_missing_locations(bind)
                link = ast.Compare(left=left, ops=[ops[k]], comparators=[bind])
                nxt_left = ast.Name(id=tmp, ctx=ast.Load())
                ast.copy_location(nxt_left, node)
                ast.fix_missing_locations(nxt_left)
            else:
                link = ast.Compare(left=left, ops=[ops[k]], comparators=[right])
                nxt_left = right
            ast.copy_location(link, node)
            ast.fix_missing_locations(link)
            links.append(link)
            left = nxt_left
        out = ast.BoolOp(op=ast.And(), values=links)
        ast.copy_location(out, node)
        ast.fix_missing_locations(out)
        return out


def _try_reaches_assert(tree: ast.AST, node: ast.AST) -> bool:
    """Route #16: can a Python `assert` execute inside this `try`, with a handler that
    catches `AssertionError`? True when a handler is bare / names `AssertionError` /
    `Exception` / `BaseException`, AND the body either contains an `assert` lexically or
    calls a same-module function that transitively contains one — an `assert` in a CALLEE
    is exactly as invisible to the model as one written in the body (MEASURED: the
    interprocedural form proved `\\result == 1` while Python returned 2).

    ONE helper returning a BOOL rather than two returning a set and a bool: the mirror
    models it as a single `\trusted` stub, and a set-returning stub has no value-model
    type here (measured — `unbound function or predicate symbol`, then
    `This expression has type (), but is expected to have type int`)."""
    _catchers = ("AssertionError", "Exception", "BaseException")
    _catching = False
    for _h in node.handlers:
        if _h.type is None:
            _catching = True
        elif isinstance(_h.type, ast.Tuple):
            for _e in _h.type.elts:
                if isinstance(_e, ast.Name) and _e.id in _catchers:
                    _catching = True
                if isinstance(_e, ast.Attribute) and _e.attr in _catchers:
                    _catching = True
        elif isinstance(_h.type, ast.Name) and _h.type.id in _catchers:
            _catching = True
        elif isinstance(_h.type, ast.Attribute) and _h.type.attr in _catchers:
            _catching = True
    if not _catching:
        return False
    _funcs = {}
    for _n in ast.walk(tree):
        if isinstance(_n, ast.FunctionDef):
            _funcs[_n.name] = _n
    _has = {}
    for _k in _funcs:
        _flag = False
        for _x in ast.walk(_funcs[_k]):
            if isinstance(_x, ast.Assert):
                _flag = True
        _has[_k] = _flag
    _changed = True
    while _changed:
        _changed = False
        for _k in _funcs:
            if _has[_k]:
                continue
            for _c in ast.walk(_funcs[_k]):
                if isinstance(_c, ast.Call):
                    _f = _c.func
                    _nm = None
                    if isinstance(_f, ast.Name):
                        _nm = _f.id
                    elif isinstance(_f, ast.Attribute):
                        _nm = _f.attr
                    if _nm is not None and _nm in _has and _has[_nm]:
                        _has[_k] = True
                        _changed = True
    for _stmt in node.body:
        for _n in ast.walk(_stmt):
            if isinstance(_n, ast.Assert):
                return True
            if isinstance(_n, ast.Call):
                _f = _n.func
                _nm = None
                if isinstance(_f, ast.Name):
                    _nm = _f.id
                elif isinstance(_f, ast.Attribute):
                    _nm = _f.attr
                if _nm is not None and _nm in _has and _has[_nm]:
                    return True
    return False


def reject_unmodelled(tree: ast.AST) -> None:
    """Refuse the shapes Module 5 would SILENTLY DROP and that have no sound rewrite."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)) and node.orelse:
            raise PyCSLParseError(
                "`for ... else` / `while ... else` is not modelled: the `else` clause runs "
                "exactly when the loop finished without `break`, and the IR emitter reads "
                "only the loop body, so the clause would be silently DROPPED from the "
                "model. Rewrite it with an explicit flag.")
        if isinstance(node, ast.TryStar):
            raise PyCSLParseError(
                "`try ... except*` (an exception-GROUP handler) is not modelled: "
                "`_PY_STMT_HANDLERS` has no `TryStar` entry and `_py_stmts_to_ir` falls "
                "through with no `else`, so the WHOLE statement — body, handlers, "
                "`else` and `finally` — is silently DROPPED from the model. Measured "
                "before this refusal: `try: x = 2 except* ValueError: x = 3` under "
                "`ensures \\result == 1` proved SUCCESS while Python returns 2. "
                "Rewrite with a plain `except`.")
        # (#43) ROUTE #16 — A PYTHON `assert` IS LOWERED TO `()`, AND INSIDE A CATCHING
        # `try` THAT IS UNSOUND. The emitted body of `def f(n): assert n > 0; return n`
        # is `(); n` — the assertion is neither checked nor assumed. OUTSIDE a handler
        # that is CONSERVATIVE and sound: the model must discharge the postcondition on
        # the path Python aborts, which is strictly harder, so 1450 asserts across this
        # tree stay exactly as they are. INSIDE a `try` whose handlers can catch
        # `AssertionError`, the handler branch is DEAD in the model and is the branch
        # Python takes. MEASURED, before this refusal (corpus 0984):
        #     try:
        #         assert 1 == 2
        #         return 1
        #     except AssertionError:
        #         return 2
        #     #@ ensures \result == 1     <-- FALSE OF THE PROGRAM (Python returns 2)
        #     [+] Verification SUCCESS! All contracts formally proven.
        # `AssertionError` is deliberately absent from `exception_model.KNOWN_EXCEPTIONS`
        # (it has no mathematical implicit trigger), so `#@ no_exception \all` does not
        # cover it and no existing plane sees this.
        # CENSUS: 0 across pycsl-reference, python-reference, the mirror, `src/pycsl_lib`,
        # the live emitter and `tests/` — of 1450 `assert` statements, NONE sits inside a
        # catching `try`. Byte-inert.
        # REOPENING CAPABILITY: model `assert P` as `if not P: raise AssertionError`, i.e.
        # add `AssertionError` to the exception model with an explicit (not implicit)
        # trigger. Then the handler becomes reachable and the refusal can go.
        # An explicit loop, NOT `any(<genexp>)`: the `any`/`all` bounded-fold lowering
        # needs the predicate as a PURE function symbol and rejects a call to a `\trusted`
        # helper there (`unbound function or predicate symbol`), which is an L3-tc failure
        # in the mirror. Measured while syncing this refusal into the mirror.
        if isinstance(node, ast.Try) and _try_reaches_assert(tree, node):
            raise PyCSLParseError(
                "a Python `assert` inside a `try` whose handler can catch "
                "`AssertionError` is not modelled: the `assert` is lowered to a NO-OP, so "
                "the handler branch is DEAD in the model while it is the branch Python "
                "takes, and the run would still report 'All contracts formally proven'. "
                "Measured: `try: assert 1 == 2; return 1 / except AssertionError: "
                "return 2` proved `\\result == 1` while Python returns 2. The same holds "
                "when the `assert` is in a CALLEE reached from the `try` body — measured "
                "too. Use an explicit `if not <cond>: raise AssertionError(...)`, or move "
                "the `assert` out of the `try`.")
        if isinstance(node, ast.Slice) and node.step is not None:
            raise PyCSLParseError(
                "an EXTENDED slice `x[lo:hi:step]` is not modelled: the lowering is "
                "`Array.sub x lo (hi - lo)`, which ignores the step entirely, so the "
                "model would carry a DIFFERENT sequence — different length and different "
                "elements — from the one Python builds. Use an explicit strided loop.")


def normalize_stores(tree: ast.AST) -> None:
    """Rewrite the two ASSIGNMENT shapes Module 5 drops, in every statement list.

    1. `<attribute-or-subscript>: T = v`  ->  `<target> = v`
       `__init__` is EXCLUDED: its annotated `self.x: T = ...` statements are where the
       record field TYPES are read from.
    2. `t1 = t2 = ... = v`  ->  `t1 = v` followed by one assignment per remaining target.
       `_py_stmt_assign` reads `stmt.targets[0]` ONLY. The value is re-mentioned only when
       it is a `Constant` or a `Name` — both share their object, so the aliasing Python
       guarantees (`a = b = []` binds ONE list) is preserved. For anything else a fresh
       temporary is bound first, so the RHS is evaluated exactly once, as Python does."""
    # (#46) ROUTE #40's RESIDUE — THE BUILTIN NAME `Ellipsis` IS THE SAME SINGLETON AS
    # THE `...` LITERAL, and Module 5 lowered the NAME to a bare `{"type":"Number",
    # "value":0}` with none of the `py_ellipsis` marker the literal carries. So the
    # opaque-value fix that closed `...` did not reach `x is Ellipsis`, and the model
    # still answered `0 = 0`:
    #     x = 0;   if x is Ellipsis: return 7   ->  `\result == 7` PROVED. Python: 0.
    #     x = ...; if x is Ellipsis: return 0   ->  the TRUE contract stopped proving
    #                                              once the literal half became opaque
    #                                              (`python-reference/0041`).
    # Rewriting the NAME into the LITERAL here is SEMANTICALLY EXACT — `Ellipsis` and
    # `...` denote the same object — and it is the CHOKE POINT: one AST rewrite in a
    # `\trusted` front-end pass, instead of editing `_py_expr_name`, which is a
    # CONVERTED mirror method whose body change would owe a mirror sync and a
    # 2109-goal re-proof to say the same thing.
    # SKIPPED ENTIRELY if the module binds the name itself (an assignment, a parameter,
    # an import or a def/class called `Ellipsis`), so a program that shadows the builtin
    # keeps its own meaning.
    _ell_bound = False
    for _n in ast.walk(tree):
        if isinstance(_n, ast.Name) and isinstance(_n.ctx, (ast.Store, ast.Del)) \
                and _n.id == "Ellipsis":
            _ell_bound = True
        elif isinstance(_n, ast.arg) and _n.arg == "Ellipsis":
            _ell_bound = True
        elif isinstance(_n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and _n.name == "Ellipsis":
            _ell_bound = True
        elif isinstance(_n, ast.alias) and (_n.asname or _n.name) == "Ellipsis":
            _ell_bound = True
    if not _ell_bound:
        for _n in ast.walk(tree):
            for _f, _v in list(ast.iter_fields(_n)):
                if isinstance(_v, ast.Name) and isinstance(_v.ctx, ast.Load) \
                        and _v.id == "Ellipsis":
                    _c = ast.Constant(value=Ellipsis, kind=None)
                    ast.copy_location(_c, _v)
                    ast.fix_missing_locations(_c)
                    setattr(_n, _f, _c)
                elif isinstance(_v, list):
                    for _i, _e in enumerate(_v):
                        if isinstance(_e, ast.Name) and isinstance(_e.ctx, ast.Load) \
                                and _e.id == "Ellipsis":
                            _c = ast.Constant(value=Ellipsis, kind=None)
                            ast.copy_location(_c, _e)
                            ast.fix_missing_locations(_c)
                            _v[_i] = _c
    protected = set()
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == "__init__"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.AnnAssign):
                    protected.add(id(sub))
    counter = [0]
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if not isinstance(stmts, list):
                continue
            out = []
            for st in stmts:
                if (isinstance(st, ast.AnnAssign) and st.value is not None
                        and not isinstance(st.target, ast.Name)
                        and id(st) not in protected):
                    rewritten = ast.Assign(targets=[st.target], value=st.value)
                    ast.copy_location(rewritten, st)
                    ast.fix_missing_locations(rewritten)
                    out.append(rewritten)
                elif isinstance(st, ast.Assign) and len(st.targets) > 1:
                    if isinstance(st.value, (ast.Constant, ast.Name)):
                        source = st.value
                        pre = []
                    else:
                        counter[0] += 1
                        tmp = "_pycsl_multi_%d" % (counter[0],)
                        hold = ast.Assign(targets=[ast.Name(id=tmp, ctx=ast.Store())],
                                          value=st.value)
                        ast.copy_location(hold, st)
                        ast.fix_missing_locations(hold)
                        pre = [hold]
                        source = ast.Name(id=tmp, ctx=ast.Load())
                        ast.copy_location(source, st)
                        ast.fix_missing_locations(source)
                    out.extend(pre)
                    for tgt in st.targets:
                        one = ast.Assign(targets=[tgt], value=source)
                        ast.copy_location(one, st)
                        ast.fix_missing_locations(one)
                        out.append(one)
                else:
                    out.append(st)
            stmts[:] = out


def desugar_chained_comparisons(tree: ast.AST) -> ast.AST:
    """Rewrite every multi-operator `Compare` into the `and`-chain Python means by it.
    No-op (byte-identical emission) for any file that contains no chained comparison."""
    return _ChainDesugarer().visit(tree)
