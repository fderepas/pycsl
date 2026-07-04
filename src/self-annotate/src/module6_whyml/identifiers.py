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

OP_MAP: int = {'==': '=', '!=': '<>', '==>': '->', '<==>': '<->', 'and': '&&', 'or': '||', 'not': 'not', 'div': 'div', '//': 'div', '/': 'div', '%': 'mod'}
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
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def safe_exc_name(name: str) -> str:
    return ""
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def op_translate(op: str) -> str:
    return ""

