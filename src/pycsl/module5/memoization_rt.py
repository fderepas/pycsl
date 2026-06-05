from __future__ import annotations

import pure_ast as ast
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
