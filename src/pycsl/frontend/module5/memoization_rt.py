from __future__ import annotations

from frontend import pure_ast as ast
from typing import Any, Dict, List, Set

from errors import PyCSLIRError


class MemoizationRTMixin:
    """Referential-transparency detection and the sound-`lru_cache` (UB-7.7)
    gate — no-more-int Stage F.

    Extracted verbatim from `Module5_IREmitter.PyCSLToJSONEmitter` as a sibling
    mixin under `module5/` (Part B move 3, mirroring `module6_whyml/`). Composed
    into `PyCSLToJSONEmitter`, which supplies `self.program_ir`; the methods are
    invoked from `visit_FunctionDef` / `_build_function_ir`."""

    _MEMOIZING_DECORATORS = {"lru_cache", "cache", "cached_property"}

    @staticmethod
    def _is_memoized(node: ast.FunctionDef) -> bool:
        """True if the function carries a memoizing decorator — `@lru_cache`,
        `@lru_cache(maxsize=…)`, `@cache`, `@cached_property` (bare, dotted, or called)."""
        memo = MemoizationRTMixin._MEMOIZING_DECORATORS
        for d in node.decorator_list:
            if isinstance(d, ast.Name) and d.id in memo:
                return True
            if isinstance(d, ast.Attribute) and d.attr in memo:
                return True
            if isinstance(d, ast.Call):
                f = d.func
                if isinstance(f, ast.Name) and f.id in memo:
                    return True
                if isinstance(f, ast.Attribute) and f.attr in memo:
                    return True
        return False

    def _reads_any(self, ir: Any, names: Set[str]) -> bool:
        """True if the IR reads a `Var` whose name is in `names` (used to detect a
        memoized function reading a mutable global)."""
        if isinstance(ir, dict):
            if ir.get("type") == "Var" and ir.get("name") in names:
                return True
            return any(self._reads_any(v, names) for v in ir.values())
        if isinstance(ir, list):
            return any(self._reads_any(x, names) for x in ir)
        return False

    def _detect_purity(self, func_ir: Dict[str, Any]) -> None:
        """Mark function as pure if it assigns nothing, doesn't diverge, and isn't trusted."""
        assigns = func_ir["contracts"]["assigns"]
        is_pure = (len(assigns) == 1 and isinstance(assigns[0], dict)
                   and assigns[0].get("type") == "Nothing"
                   and not func_ir["diverges"]
                   and not func_ir["trusted"])
        if is_pure:
            func_ir["pure"] = True

    def _check_memoized_field_reads(self) -> None:
        """ROUTE #94. The mutable-state half of `_check_memoization_soundness`, run where it
        can actually see the answer.

        `_check_memoization_soundness` runs per-function inside `visit_FunctionDef`, so when a
        memoized method is checked the methods DEFINED AFTER IT are not yet in
        `program_ir["functions"]` — and the mutator usually is one of them. This pass is called
        from the post-`generic_visit` hook of `visit_ClassDef`, where every method of the class
        has been emitted, so the set of mutated fields is complete.

        WHAT IT REJECTS. A memoized function (`@lru_cache` / `@cache` / `@cached_property`)
        whose body READS `self.<f>` where `<f>` is assigned somewhere other than `__init__`.
        MEASURED: a `@cached_property` returning `self.a`, with `#@ assigns \nothing` and
        `#@ ensures \result == self.a`, PROVED — while running the same program under CPython
        gives `total = 0, self.a = 1` after one `bump()`, so the proved postcondition is FALSE
        in the real language. That is UB-7.7, exactly what this gate exists to reject.

        WHY THE RULE IS NOT "READS ANY FIELD". A `cached_property` inherently reads `self`, and
        one over a construct-only field is genuinely referentially transparent — measured: it
        PROVES and CPython AGREES with it. A blanket field-read ban would delete that real
        capability (the corpus-1057 mistake). The `__init__` carve-out is the same one routes
        #91 and #92 needed: the constructor establishes the object rather than mutating it.

        WHY THE EXISTING CLAUSES COULD NOT SEE IT: `_detect_purity` is about `assigns`, not
        reads, so a method that reads a mutable field and writes nothing counts as pure; and
        `_reads_any` matches only `type == "Var"`, so a field read (a `FieldGet`) is invisible
        to the `#@ shared` clause whatever is declared.
        """
        funcs = self.program_ir.get("functions", []) or []
        if not any(f.get("memoized") for f in funcs):
            return
        mutated: Set[str] = set()
        for g in funcs:
            if str(g.get("name", "")).rsplit("__", 1)[-1] == "__init__":
                continue
            stack: List[Any] = [g.get("body", [])]
            while stack:
                cur = stack.pop()
                if isinstance(cur, dict):
                    # (#49) ROUTE #99 — THIS TEST USED TO READ `and cur.get("object") ==
                    # "self"`, AND THAT SPELLING-KEYED FILTER REOPENED THE WHOLE OF ROUTE
                    # #94 FOR ANY MUTATION THROUGH A FOREIGN RECEIVER.
                    #
                    # `mutated` is the population this gate's refusal iterates. A write
                    # spelled `c.<f> = ...` — the ordinary way a FREE FUNCTION mutates an
                    # object it was handed — is a `FieldAssign` whose `object` is `"c"`,
                    # so it was skipped, `mutated` stayed EMPTY, and the `if not mutated:
                    # return` below DISARMED THE GATE ENTIRELY before its consumer ran.
                    # MEASURED on a pair differing ONLY in the receiver of the write:
                    #     def bump(self): self.a = self.a + 1   -> REFUSED (this gate)
                    #     def bump(c: C):  c.a   = c.a + 1      -> Verification SUCCESS,
                    #                                              `c__total'vc` Valid
                    # and CPython on the second: before `total=0 a=0`, after `total=0
                    # a=1` — so the PROVED `ensures \result == self.a` is FALSE in the
                    # running language. The cached value is stale exactly as UB-7.7
                    # describes; the gate simply never saw the mutation.
                    #
                    # >>> STALENESS IS A PROPERTY OF **THE FIELD**, NOT OF WHO WROTE IT.
                    # >>> The cache does not care which receiver dirtied the value, so the
                    # >>> collection must be keyed on the FIELD BEING WRITTEN and never on
                    # >>> the syntactic shape of the receiver. A check keyed on the shape
                    # >>> of a write target enumerates the shapes its author pictured.
                    #
                    # WHY THIS SURVIVED ROUTE #94's OWN REVIEW, WHICH WAS CAREFUL: #94 had
                    # ALREADY learned that its first repair sat in a per-function visitor
                    # and silently did nothing, and moved it to the post-class hook so it
                    # could see every function (see the docstring above). The author was
                    # therefore thinking hard about WHEN the population is assembled — and
                    # not about HOW WIDE it is. Getting a population's TIMING right and its
                    # BREADTH wrong produces a gate that passes every test its author
                    # wrote: witnesses 1257 and 1258 are both still correct and neither can
                    # see this hole, because both spell the mutation with `self`.
                    #
                    # SOUNDNESS AND COST OF THE WIDENING, MEASURED RATHER THAN ASSUMED:
                    # admitting every receiver can only ADD refusals, so it cannot make a
                    # false claim provable. It can over-refuse, because `mutated` is a flat
                    # set of field NAMES — but THAT HAZARD IS PRE-EXISTING AND UNCHANGED IN
                    # KIND: the set was already global and name-keyed, so an unrelated
                    # class's `self.x = ...` already poisoned a memoized `self.x` reader
                    # before this change. Census: 72 distinct field names across the
                    # corpora, 20 of them owned by more than one class — and only FOUR
                    # pycsl-reference files use a memoizing decorator at all (0515, 0516,
                    # 1257, 1258), so the exposed population is enumerable and each of the
                    # four is measured individually. Narrowing `mutated` to (class, field)
                    # pairs would fix the over-refusal in BOTH directions and is the right
                    # follow-up, but it is a widening of scope, not of soundness, and is
                    # recorded in the route file rather than smuggled in here.
                    if cur.get("stmt") in ("FieldAssign", "FieldAugAssign"):
                        mutated.add(cur.get("field"))
                    stack.extend(cur.values())
                elif isinstance(cur, list):
                    stack.extend(cur)
        if not mutated:
            return
        for f in funcs:
            if not f.get("memoized"):
                continue
            hit = None
            stack = [f.get("body", [])]
            while stack and hit is None:
                cur = stack.pop()
                if isinstance(cur, dict):
                    if (cur.get("type") == "FieldGet" and cur.get("object") == "self"
                            and cur.get("field") in mutated):
                        hit = cur.get("field")
                        break
                    stack.extend(cur.values())
                elif isinstance(cur, list):
                    stack.extend(cur)
            if hit is not None:
                raise PyCSLIRError(
                    f"Function '{f['name']}': a memoizing decorator (lru_cache / cache / "
                    f"cached_property) requires a referentially transparent function, but it "
                    f"reads `self.{hit}`, a field assigned outside `__init__`. The cached value "
                    f"goes stale the first time that field changes, so the verified (uncached) "
                    f"body no longer describes the running program — unsound (UB-7.7). Read "
                    f"only fields written by the constructor, or drop the decorator. See "
                    f"config/skills/pycsl-ub-catalog/SKILL.md §7.7.")

    def _check_memoization_soundness(self, func_ir: Dict[str, Any]) -> None:
        """no-more-int Stage F: a memoizing decorator (lru_cache/cache/cached_property)
        is sound only on a **referentially transparent** function — one that is pure
        (effect-free) AND reads no mutable global state. Otherwise the cache returns
        results inconsistent with the verified (uncached) body — unsound. Reject (UB-7.7).

        (Why3 logic functions are referentially transparent by construction, and PyCSL
        already emits a pure non-method function as a `let function`; so for an RT
        function the cache is observationally transparent and ignoring the decorator is
        sound — no extra emission is needed, only this gate on the unsound case.)"""
        if not func_ir.get("memoized"):
            return
        reasons: List[str] = []
        if not func_ir.get("pure"):
            reasons.append("it is not pure (requires `#@ assigns \\nothing`, and no "
                           "`\\trusted` / `\\diverges`)")
        shared = {sv["name"] for sv in self.program_ir.get("shared_vars", [])}
        if shared and self._reads_any(func_ir["body"], shared):
            reasons.append("it reads a `#@ shared` mutable global (non-deterministic)")
        if reasons:
            raise PyCSLIRError(
                f"Function '{func_ir['name']}': a memoizing decorator (lru_cache / cache "
                f"/ cached_property) requires a referentially transparent function, but "
                f"{' and '.join(reasons)}. Memoizing it is unsound — the cache would "
                f"return values inconsistent with the verified body (UB-7.7). See "
                f"config/skills/pycsl-ub-catalog/SKILL.md §7.7.")
