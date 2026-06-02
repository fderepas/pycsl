"""Normalize Rocq, Lean, and WhyML axiom strings to a comparable form
(proof2why3 v0).

The normalization is intentionally simple — Unicode → ASCII, strip
known type-qualifier prefixes (PeanoNat.Nat.gcd → gcd, Nat.gcd → gcd),
unfold Lean's dot notation (a.gcd b → gcd a b), normalize binders
and arrow operators. Sufficient for the gcd theorem family in 0342.

This is NOT a full first-order canonicalizer — that's Phase 3 in
sticky-01.md. The v0 normalizer is a regex pipeline that handles
the immediate set of constructs the gcd theorems use:

    forall / ∀          → forall
    ->    / →           → ->
    >=    / ≥           → >=
    <=    / ≤           → <=
    \\/   / ∨           → \\/
    /\\   / ∧           → /\\
    a.gcd b             → gcd a b      (Lean dot notation)
    PeanoNat.Nat.gcd    → gcd          (Coq library prefix)
    Nat.gcd             → gcd          (Lean library prefix)
    PeanoNat.Nat.modulo → mod          (Coq)
    %                   → mod          (Lean operator)
    BinNat.N.gcd        → gcd          (alt Coq)
    (a b : nat)         → (a b : int)  (nat → int with side conditions)

Bound variables are also alpha-renamed to v0, v1, … for stable diffing.
"""
from __future__ import annotations

import re
from typing import List, Tuple


# Unicode → ASCII operator map.
_UNICODE_OPS = {
    "∀":   "forall",
    "→":   "->",
    "≥":   ">=",
    "≤":   "<=",
    "∨":   r"\/",
    "∧":   r"/\\",
    "≠":   "<>",
    "¬":   "not",
    "≡":   "=",
}

# Library-prefix strips: applied in order, longest first.
_PREFIX_STRIPS: List[Tuple[str, str]] = [
    ("PeanoNat.Nat.gcd",    "gcd"),
    ("PeanoNat.Nat.modulo", "mod"),
    ("PeanoNat.Nat.add",    "add"),
    ("PeanoNat.Nat.mul",    "mul"),
    ("PeanoNat.Nat.sub",    "sub"),
    ("Nat.gcd",             "gcd"),
    ("Nat.modulo",          "mod"),
    ("Nat.mod",             "mod"),
    ("Nat.add",             "add"),
    ("Nat.mul",             "mul"),
    ("Nat.sub",             "sub"),
    ("BinNat.N.gcd",        "gcd"),
    ("BinNat.N.modulo",     "mod"),
    ("Init.Nat.gcd",        "gcd"),
]


def normalize_prover_output(s: str) -> str:
    """Apply the Unicode + library-prefix + dot-notation normalization
    pipeline to a Rocq or Lean type string."""
    out = s.strip()
    # 1. Unicode → ASCII operators
    for u, a in _UNICODE_OPS.items():
        out = out.replace(u, a)
    # 2. Library-prefix strips
    for src, dst in _PREFIX_STRIPS:
        out = out.replace(src, dst)
    # 3. Lean dot notation: a.gcd b → (gcd a b), a.mod b → (mod a b).
    #    Pattern: `<var>.<fn>` becomes `(fn <var>` then one argument
    #    is consumed via a balanced lookahead; we approximate by
    #    inserting an opening paren before fn and a closing paren
    #    after the next token (which is the second arg).
    for fn in ("gcd", "mod", "add", "mul", "sub"):
        # `a.fn b` → `(fn a b)` — preserve grouping for downstream
        # infix rewrites (e.g., `%`) and for paren-aware comparison
        # with Coq's pretty-printer output.
        out = re.sub(
            rf"\b([a-zA-Z_][a-zA-Z0-9_]*)\.{fn}\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            rf"({fn} \1 \2)", out,
        )
        # Same with paren'd second arg: `a.fn (X)` → `(fn a (X))`.
        out = re.sub(
            rf"\b([a-zA-Z_][a-zA-Z0-9_]*)\.{fn}\s+(\([^()]+\))",
            rf"({fn} \1 \2)", out,
        )
    # 4. Lean's `%` infix operator → `mod` prefix.
    #    `a % b` → `mod a b` for simple operands; `a % (E)` → `mod a (E)`.
    out = re.sub(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*%\s*(\([^()]+\))",
        r"(mod \1 \2)", out,
    )
    out = re.sub(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*%\s*([a-zA-Z_][a-zA-Z0-9_]*)",
        r"(mod \1 \2)", out,
    )
    # 5a. Expand anonymous-binder arrows (forall ... (_ : H), → H ->).
    out = _expand_anon_binders(out)
    # 5b. Normalize parens/spaces in binders: `forall (a b : nat),` → `forall a b : nat,`.
    out = re.sub(
        r"forall\s*\(\s*([^()]+?)\s*\)\s*,",
        r"forall \1,",
        out,
    )
    # 6. nat → int with side conditions:
    #    `forall a : nat, P(a)` → `forall a : int, a >= 0 -> P(a)`.
    #    `forall a b : nat, P(a, b)` → `forall a b : int, a >= 0 -> b >= 0 -> P(a, b)`.
    out = _nat_to_int_with_sidecond(out)
    # 7a. Strip redundant parens around top-level disjunctions/conjunctions
    #     appearing as an `->` hypothesis: `... -> (P \/ Q) -> ...` →
    #     `... -> P \/ Q -> ...`.
    out = re.sub(
        r"->\s*\(\s*([^()]+?(?:\s*[\\/]+\s*[^()]+?)+)\s*\)\s*->",
        r"-> \1 ->",
        out,
    )
    # 7b. Normalize comparison direction: `0 <= x` → `x >= 0`,
    #     `0 < x` → `x > 0`. Two-arg version only.
    out = re.sub(
        r"\b(\w+(?:\s+\w+)*)\s*<=\s*(\w+(?:\s+\w+)*)",
        lambda m: f"{m.group(2)} >= {m.group(1)}"
                  if not re.search(r"\b(forall|exists)\b", m.group(1))
                  else m.group(0),
        out, count=1,
    )
    # 7c. Lean's `a.gcd 0` case where second token is a literal.
    out = re.sub(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.gcd\s+(\d+)",
        r"(gcd \1 \2)", out,
    )
    # 7d. Paren strip BEFORE the <= rewrite so `k <= (gcd a b)` collapses
    #     to `k <= gcd a b` and the <= rule below can fire.
    out = _strip_all_parens(out)
    # 7e. <= rewrite (re-applied post-paren-strip with broader RHS).
    out = re.sub(
        r"\b(\w+)\s*<=\s*(\w+(?:\s+\w+)*)",
        r"\2 >= \1",
        out, count=1,
    )
    # 8. Whitespace collapse + alpha rename.
    out = re.sub(r"\s+", " ", out).strip()
    out = _alpha_rename(out)
    return out


def _strip_all_parens(s: str) -> str:
    """v0 lossy unification: drop all parentheses from a normalized
    string. Sufficient for the gcd-family where structural ambiguity
    is benign (all applications are flat). Phase 3's IR-based
    canonicalization will replace this with structural equality."""
    s = s.replace("(", "").replace(")", "")
    return re.sub(r"\s+", " ", s).strip()


def _nat_to_int_with_sidecond(s: str) -> str:
    """Rewrite `forall <vars> : nat, P` into
    `forall <vars> : int, v0 >= 0 -> v1 >= 0 -> ... -> P`.

    The Rocq/Lean theorems are over `nat` (Coq) / `Nat` (Lean); the
    WhyML registry is over `int` with `>= 0` side conditions. This
    normalizer applies the same expansion both ways so they compare
    equal. Matches both lowercase `nat` and capitalized `Nat`.
    """
    def repl(m: re.Match) -> str:
        vars_str = m.group(1).strip()
        names = vars_str.split()
        side = " ".join(f"{n} >= 0 ->" for n in names)
        return f"forall {vars_str} : int, {side}"
    pattern = re.compile(r"forall\s+([a-zA-Z_ ][a-zA-Z0-9_ ]*?)\s*:\s*[nN]at\s*,")
    return pattern.sub(repl, s)


def _expand_anon_binders(s: str) -> str:
    """Rocq prints curried hypotheses as anonymous binders:
        forall a b : nat, b > 0 -> P
    can also appear as
        forall (a b : nat) (_ : b > 0), P
    Coq's default pretty-printer uses the arrow form for hypotheses
    when possible, but with `Unset Printing Notations` or in some
    versions the `(_ : H)` form leaks through. Rewrite the latter
    into arrow form: `(_ : H) , P` → `H -> P`.

    Repeats until fixed-point (multiple anonymous binders).
    """
    pattern = re.compile(
        r"\(\s*_\s*:\s*([^()]+(?:\([^()]*\)[^()]*)*)\)\s*"
    )
    while True:
        new = pattern.sub(lambda m: f"{m.group(1).strip()} -> ", s, count=1)
        if new == s:
            return s
        s = new


def _alpha_rename(s: str) -> str:
    """Rename bound variables in `forall <vars> : <ty>,` headers to
    v0, v1, ...  Applied left-to-right, no scope-aware shadowing.

    Best effort — works for first-order quantifier prefixes the gcd
    theorems use; would need proper scope tracking for nested binders.
    """
    binders_match = re.match(r"forall\s+([a-zA-Z_0-9 ]+?)\s*:", s)
    if not binders_match:
        return s
    names = binders_match.group(1).split()
    if not names:
        return s
    rename_map = {n: f"v{i}" for i, n in enumerate(names)}
    out = s
    for orig, new in sorted(rename_map.items(), key=lambda kv: -len(kv[0])):
        out = re.sub(rf"\b{re.escape(orig)}\b", new, out)
    return out


def normalize_whyml_axiom(body: str) -> str:
    """Normalize a WhyML axiom-body string to the same canonical form.

    The registry already uses ASCII operators and the `forall ... : int,
    <sidecond> -> <body>` shape. We strip redundant parens around
    top-level disjunctions, normalize `<=` direction, alpha-rename,
    and collapse whitespace — same pipeline as the prover side so
    the canonical forms compare equal.
    """
    out = body.strip()
    # Collapse Why3 `forall x y : int.` (dot) to `forall x y : int,` (comma).
    out = out.replace(" : int.", " : int,")
    # Strip redundant parens around top-level disjunctions appearing
    # as -> hypotheses (mirror prover-side rule 7a).
    out = re.sub(
        r"->\s*\(\s*([^()]+?(?:\s*[\\/]+\s*[^()]+?)+)\s*\)\s*->",
        r"-> \1 ->",
        out,
    )
    # Normalize `0 <= x` → `x >= 0` to match the prover side.
    out = re.sub(
        r"\b(\w+(?:\s+\w+)*)\s*<=\s*(\w+(?:\s+\w+)*)",
        lambda m: f"{m.group(2)} >= {m.group(1)}"
                  if not re.search(r"\b(forall|exists)\b", m.group(1))
                  else m.group(0),
        out, count=1,
    )
    out = re.sub(r"\s+", " ", out)
    out = _strip_all_parens(out)
    out = _alpha_rename(out)
    return out
