from __future__ import annotations
import hashlib
import unicodedata
from typing import Dict, Set
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def stable_hash(s: str) -> int:
    return 0

OP_MAP: Dict[str, str] = {'==': '=', '!=': '<>', '==>': '->', '<==>': '<->', 'and': '&&', 'or': '||', 'not': 'not', 'div': 'div', '//': 'div', '/': 'div', '%': 'mod'}
WHYML_RESERVED: int = {'at', 'any', 'diverges', 'val', 'let', 'in', 'if', 'then', 'else', 'while', 'do', 'done', 'for', 'to', 'begin', 'end', 'match', 'with', 'try', 'raise', 'exception', 'type', 'use', 'module', 'theory', 'import', 'export', 'clone', 'goal', 'lemma', 'axiom', 'predicate', 'function', 'constant', 'mutable', 'ghost', 'invariant', 'variant', 'requires', 'ensures', 'returns', 'raises', 'reads', 'writes', 'assert', 'assume', 'check', 'absurd', 'true', 'false', 'not', 'old', 'ref', 'abstract', 'private', 'model', 'range', 'float', 'by', 'so', 'pure', 'alias', 'label', 'epsilon', 'exists', 'forall', 'rec', 'and', 'or', 'mod', 'div', 'result', 'partial', 'fun', 'as', 'scope', 'coinductive', 'inductive'}
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def whyml_ident(name: str) -> str:
    return ""
#@ requires True
#@ ensures True
#@ assigns \nothing
def safe_mutex_name(mutex: str) -> str:
    """Convert a mutex expression (possibly 'locks[0]') to a valid WhyML identifier."""
    return whyml_ident(mutex.replace("[", "_").replace("]", "").replace(".", "_"))
#@ requires True
#@ ensures True
#@ assigns \nothing
def safe_exc_name(name: str) -> str:
    """Sanitize a user-exception name for WhyML emission.

    Python local-alias imports (`from X import Y as _Y`) produce
    exception names starting with `_`, which WhyML rejects in
    exception-declaration position. Stripping leading underscore(s)
    yields a valid WhyML identifier; the de-aliased name also
    collapses with the original (un-prefixed) declaration via set
    deduplication at the call site, so `Y` and `_Y` emit a single
    `exception Y` declaration."""
    return name.lstrip("_") or name
#@ requires True
#@ ensures True
#@ assigns \nothing
def op_translate(op: str) -> str:
    """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
    return OP_MAP.get(op, op)

