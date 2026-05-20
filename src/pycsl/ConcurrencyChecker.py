"""Lightweight static concurrency analysis pass for PyCSL.

Runs after Module4 (SemanticAnalyzer) and before Module5 (IREmitter).
Builds a shared-access map and emits ConcurrencyWarning objects for:
  - Shared variables declared without protected_by (unprotected shared state)
  - Shared variables accessed outside a critical section (informational, Module4 already errors on these)
  - queue.Queue, threading.Lock etc. are trusted thread-safe types (no warnings)

This pass does NOT raise exceptions — Module4 already enforces hard errors.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

# Thread-safe types that do not require mutex protection
_TRUSTED_CONCURRENT_TYPES = {
    "queue.Queue", "Queue",
    "threading.Lock", "Lock",
    "threading.RLock", "RLock",
    "threading.Semaphore", "Semaphore",
    "threading.Event", "Event",
    "threading.Condition", "Condition",
    "threading.Barrier", "Barrier",
}

# Keywords that indicate a thread-safe object access (don't warn on these)
_TRUSTED_ATTRIBUTES = {"put", "get", "acquire", "release", "wait", "set", "notify",
                        "notify_all", "is_set"}


@dataclass
class ConcurrencyWarning:
    kind: str          # "unprotected_shared" | "nested_without_order" | "info"
    message: str
    function: str = ""
    line: int = 0


class ConcurrencyChecker:
    """Walk the annotated AST and emit ConcurrencyWarning objects."""

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree
        self.warnings: List[ConcurrencyWarning] = []
        # Populated from module-level csl_* fields
        self._shared_vars: Dict[str, Optional[str]] = {}    # var → mutex (None = unprotected)
        self._lock_order: Optional[List[str]] = None
        self._thread_entries: Set[str] = set()

    def check(self) -> List[ConcurrencyWarning]:
        self.warnings = []
        module = self.tree

        # Read module-level concurrency declarations
        for decl in getattr(module, 'csl_shared_decls', []):
            self._shared_vars[decl.variable] = decl.mutex
            if decl.mutex is None:
                self.warnings.append(ConcurrencyWarning(
                    kind="unprotected_shared",
                    message=f"Variable '{decl.variable}' declared shared but has no protected_by mutex. "
                            "All accesses are potential data races.",
                ))

        lo = getattr(module, 'csl_lock_order', None)
        if lo is not None:
            self._lock_order = lo.order

        # Collect thread entry functions
        for node in ast.walk(module):
            if isinstance(node, ast.FunctionDef):
                if getattr(node, 'csl_thread_entry', False):
                    self._thread_entries.add(node.name)

        # Walk functions
        for node in ast.walk(module):
            if isinstance(node, ast.FunctionDef):
                self._check_function(node)

        return self.warnings

    def _check_function(self, func: ast.FunctionDef) -> None:
        if not self._shared_vars:
            return
        self._walk_body(func.body, held=set(), func_name=func.name)

    def _walk_body(self, stmts: list, held: Set[str], func_name: str) -> None:
        for stmt in stmts:
            self._walk_stmt(stmt, held, func_name)

    def _walk_stmt(self, node: ast.AST, held: Set[str], func_name: str) -> None:
        if isinstance(node, ast.With):
            mutex = (getattr(node, 'csl_critical_mutex', None) or
                     getattr(node, 'csl_acquires', None))
            inner_held = held | {mutex} if mutex else held
            self._walk_body(node.body, inner_held, func_name)
        elif isinstance(node, ast.If):
            self._walk_body(node.body, held, func_name)
            self._walk_body(node.orelse, held, func_name)
        elif isinstance(node, (ast.While, ast.For)):
            self._walk_body(node.body, held, func_name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._warn_if_unprotected(target.id, held, func_name,
                                              line=getattr(node, 'lineno', 0), write=True)
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                self._warn_if_unprotected(node.target.id, held, func_name,
                                          line=getattr(node, 'lineno', 0), write=True)

    def _warn_if_unprotected(self, var: str, held: Set[str], func_name: str,
                              line: int, write: bool) -> None:
        if var not in self._shared_vars:
            return
        req_mutex = self._shared_vars[var]
        if req_mutex is None:
            return  # already warned at declaration level
        if req_mutex not in held:
            action = "write to" if write else "read of"
            self.warnings.append(ConcurrencyWarning(
                kind="unprotected_shared",
                message=f"Unprotected {action} shared variable '{var}' (requires '{req_mutex}')",
                function=func_name,
                line=line,
            ))

    def summary(self) -> str:
        if not self.warnings:
            return ""
        lines = ["[*] ConcurrencyChecker warnings:"]
        for w in self.warnings:
            loc = f" [{w.function}:{w.line}]" if w.function else ""
            lines.append(f"    [{w.kind}]{loc} {w.message}")
        return "\n".join(lines)
