"""Project a sertop Coq Constr s-expression into the shared IR
(proof2why3 Phase A v1 — sticky-02.md).

The driver in `sertop.py` returns a parsed s-expression (nested
Python tuples) representing the elaborated `Constr.t` of a cited
theorem. This module walks that tree and produces a
`proof2why3.ir.Term`.

Schema (Coq 8.20 via coq-serapi 8.20.0+0.20.0; see
~/.opam/coq-4.14/.opam-switch/sources/coq-serapi.../serlib_8_20/ser_constr.ml):

  Constr ::= ('Rel', N)
           | ('Var', ID)
           | ('Sort', _)
           | ('Cast', body, _, ty)
           | ('Prod', binder_annot, ty, body)
           | ('Lambda', binder_annot, ty, body)
           | ('LetIn', binder_annot, val, ty, body)
           | ('App', head, args_tuple)
           | ('Const', ((Constant ker_name)...))
           | ('Ind', (((MutInd ker_name) ind_idx) ...))
           | ('Construct', ((((MutInd ker_name) ind_idx) ctor_idx) ...))
           | ('Case', ...) | ('Fix', ...) | ('CoFix', ...)
           | ('Proj', _, body)
           | ('Int', n)
           | ('Float', n)
           | ('Array', _, _, _, _)

  binder_annot ::= (('binder_name', ('Name', ('Id', NAME)))
                   ('binder_relevance', _))
                | (('binder_name', 'Anonymous')
                   ('binder_relevance', _))

  ker_name ::= (KerName (MPfile (DirPath ((Id seg) ...))) (Id NAME))
             | (KerName (MPdot ... (Id MOD)) (Id NAME))      (* nested module *)
             | etc.

Mapping rules:
  - Prod with Named binder of base type (nat/Nat/int) → Forall.
  - Prod with Anonymous binder → BinOp("->", ty, body).
  - Rel N → Var via de Bruijn lookup against `ctx` (the binder stack
    populated by enclosing Prods).
  - App with head Const(... gcd ...) → App("gcd", [a, b])
  - App with head Const(... modulo ...) → App("mod", [a, b])
  - App with head Ind(... eq ...) → BinOp("=", a, b) (skipping type arg)
  - App with head Const(... gt ...) → BinOp(">", a, b)
  - App with head Const(... ge ...) → BinOp(">=", a, b)
  - App with head Ind(... or ...) → BinOp("\\/", a, b)
  - Construct(nat, 1) → IntLit(0)  (O constructor)
  - Construct(nat, 2) applied to argument → recurse, S applied to k → IntLit(k+1)
  - Const lookup table strips library prefixes.

Anything else falls through to `Unsupported`.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple

from proof2why3.ir import (
    App, BinOp, BoolLit, Forall, IntLit, Term, UnaryOp, Unsupported, Var,
)


# ---------------------------------------------------------------------------
# Constr head-name extraction
# ---------------------------------------------------------------------------


def _walk_kername(kn: Any) -> List[str]:
    """Walk a (KerName MPfile/MPdot ... (Id NAME)) tree and return the
    full dotted-path components as a list of strings."""
    out: List[str] = []
    if not isinstance(kn, tuple):
        return out
    if kn and kn[0] == "KerName":
        if len(kn) >= 3:
            mp = kn[1]
            iid = kn[2]
            out.extend(_walk_modpath(mp))
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out


def _walk_modpath(mp: Any) -> List[str]:
    """Walk a MPfile / MPdot / MPbound tree to extract module path
    components in left-to-right order."""
    out: List[str] = []
    if not isinstance(mp, tuple):
        return out
    if mp and mp[0] == "MPfile":
        # (MPfile (DirPath ((Id NAME) ...)))
        if len(mp) >= 2:
            dp = mp[1]
            if isinstance(dp, tuple) and dp[0] == "DirPath" and len(dp) >= 2:
                segments = dp[1]
                # DirPath stores components in REVERSE order; reverse to
                # get logical left-to-right.
                segs_reversed: List[str] = []
                if isinstance(segments, tuple):
                    for seg in segments:
                        if (isinstance(seg, tuple) and seg[0] == "Id"
                                and len(seg) >= 2):
                            segs_reversed.append(seg[1])
                out.extend(reversed(segs_reversed))
    elif mp and mp[0] == "MPdot":
        # (MPdot <parent_mp> (Id NAME))
        if len(mp) >= 3:
            out.extend(_walk_modpath(mp[1]))
            iid = mp[2]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out


def _const_name(const_node: Any) -> Optional[str]:
    """Extract the short name (last Id) of a Const node.

    Shape: ('Const', ((Constant ker_name) (Instance ...))) — but
    note sertop wraps as ((Constant ker_name) other_kername).
    """
    if not isinstance(const_node, tuple) or len(const_node) < 2:
        return None
    payload = const_node[1]
    # payload is typically (((Constant (KerName ...)) ...) (Instance ...))
    # We dig for the first KerName-style nested tuple.
    parts = _find_kername_components(payload)
    return parts[-1] if parts else None


def _full_const_path(const_node: Any) -> List[str]:
    """Return the full dotted path of a Const node."""
    if not isinstance(const_node, tuple) or len(const_node) < 2:
        return []
    return _find_kername_components(const_node[1])


def _find_kername_components(payload: Any) -> List[str]:
    """Recursively search the payload for the first KerName subtree
    and return its components."""
    if isinstance(payload, tuple):
        if payload and payload[0] == "KerName":
            return _walk_kername(payload)
        for sub in payload:
            r = _find_kername_components(sub)
            if r:
                return r
    return []


def _ind_short_name(ind_node: Any) -> Optional[str]:
    """Extract the type name from an Ind node.

    Shape: ('Ind', ((((MutInd (KerName ... (Id NAME)) _) IND_IDX) ...) (Instance ...)))
    """
    if not isinstance(ind_node, tuple) or len(ind_node) < 2:
        return None
    parts = _find_kername_components(ind_node[1])
    return parts[-1] if parts else None


def _construct_indices(construct_node: Any) -> Optional[Tuple[str, int]]:
    """Return (inductive_short_name, constructor_index_1based) for a
    Construct node, or None if shape unrecognized.

    Shape: ('Construct', ((((((MutInd kn) IND_IDX) CTOR_IDX) ...) (Instance ...)))
    """
    if not isinstance(construct_node, tuple) or len(construct_node) < 2:
        return None
    payload = construct_node[1]
    # Walk to find the constructor index — it's nestled in the structure.
    # We look for a pattern (((MutInd ...) "<n>") "<m>") where m is the
    # constructor index.
    parts = _find_kername_components(payload)
    type_name = parts[-1] if parts else None
    # Search the structure for an integer-string at the right depth.
    ctor_idx = _find_construct_idx(payload)
    if type_name is not None and ctor_idx is not None:
        return type_name, ctor_idx
    return None


def _find_construct_idx(payload: Any) -> Optional[int]:
    """Heuristic: walk the payload looking for an integer-string at
    depth-2 inside a tuple following a tuple containing a MutInd."""
    if not isinstance(payload, tuple):
        return None
    # Pattern: (((MutInd ...) IND_IDX) CTOR_IDX) — the outermost tuple
    # has the CTOR_IDX as its second element.
    for elem in payload:
        if isinstance(elem, tuple) and len(elem) == 2:
            head = elem[0]
            tail = elem[1]
            if isinstance(head, tuple) and any(
                isinstance(x, tuple) and x and x[0] == "MutInd"
                for x in _flatten_tuples(head)
            ):
                try:
                    return int(tail)
                except (ValueError, TypeError):
                    pass
        # Recurse
        r = _find_construct_idx(elem)
        if r is not None:
            return r
    return None


def _flatten_tuples(t: Any) -> List[Any]:
    """Helper: yield all sub-tuples of t at any depth."""
    out: List[Any] = []
    if isinstance(t, tuple):
        out.append(t)
        for sub in t:
            out.extend(_flatten_tuples(sub))
    return out


# ---------------------------------------------------------------------------
# Binder name extraction
# ---------------------------------------------------------------------------


def _binder_name(binder_annot: Any) -> Optional[str]:
    """Extract the variable name from a binder_annot tuple, or None
    if the binder is Anonymous (arrow hypothesis)."""
    if not isinstance(binder_annot, tuple):
        return None
    for field in binder_annot:
        if (isinstance(field, tuple) and len(field) >= 2
                and field[0] == "binder_name"):
            val = field[1]
            if val == "Anonymous":
                return None
            if isinstance(val, tuple) and val[0] == "Name" and len(val) >= 2:
                inner = val[1]
                if (isinstance(inner, tuple) and inner[0] == "Id"
                        and len(inner) >= 2):
                    return inner[1]
    return None


# ---------------------------------------------------------------------------
# Library-prefix strip for Const head names
# ---------------------------------------------------------------------------


_CONST_STRIP_TABLE = {
    "gcd":    "gcd",
    "modulo": "mod",
    "add":    "add",
    "mul":    "mul",
    "sub":    "sub",
    "gt":     ">",
    "lt":     "<",
    "ge":     ">=",
    "le":     "<=",
}


_INDUCTIVE_TYPE_AS_BASE = {"nat", "Nat", "Int", "Bool"}


# ---------------------------------------------------------------------------
# App-head dispatcher
# ---------------------------------------------------------------------------


def _project_app(head: Any, args: List[Any],
                 ctx: List[str]) -> Term:
    """Project an App whose head is `head` (a Constr sub-tree) and
    `args` is a Python list of Constr sub-trees."""
    # Const head: dispatch on the short name.
    if isinstance(head, tuple) and head and head[0] == "Const":
        sname = _const_name(head)
        if sname in _CONST_STRIP_TABLE:
            op = _CONST_STRIP_TABLE[sname]
            if op in (">", "<", ">=", "<=") and len(args) >= 2:
                return BinOp(op, project_constr(args[-2], ctx),
                              project_constr(args[-1], ctx))
            # Numeric function call — project all args.
            arg_terms = [project_constr(a, ctx) for a in args]
            return App(head=op, args=tuple(arg_terms))
        # Unknown Const — emit as App with raw short name.
        if sname:
            arg_terms = [project_constr(a, ctx) for a in args]
            return App(head=sname, args=tuple(arg_terms))
    # Ind head: equality, conjunction, etc.
    if isinstance(head, tuple) and head and head[0] == "Ind":
        iname = _ind_short_name(head)
        if iname == "eq" and len(args) >= 3:
            # (Ind eq) [type, lhs, rhs] — drop the type ascription.
            return BinOp("=", project_constr(args[1], ctx),
                          project_constr(args[2], ctx))
        if iname == "or" and len(args) >= 2:
            return BinOp(r"\/", project_constr(args[0], ctx),
                          project_constr(args[1], ctx))
        if iname == "and" and len(args) >= 2:
            return BinOp(r"/\\", project_constr(args[0], ctx),
                          project_constr(args[1], ctx))
        if iname == "not" and len(args) >= 1:
            return UnaryOp("not", project_constr(args[0], ctx))
        # Inductive comparison predicates on nat: le, lt, ge, gt
        # — Coq's `Peano.le` is an inductive `Inductive le : nat → nat → Prop`.
        # Same for `lt`. (`ge` and `gt` are defined by le/lt.)
        if iname in ("le", "lt") and len(args) >= 2:
            op = "<=" if iname == "le" else "<"
            return BinOp(op, project_constr(args[0], ctx),
                          project_constr(args[1], ctx))
        # Inductive applied to args (e.g., list nat) — emit as App.
        if iname:
            return App(head=iname,
                       args=tuple(project_constr(a, ctx) for a in args))
    # Construct head — for S applied to k, recurse to recognize a literal.
    if isinstance(head, tuple) and head and head[0] == "Construct":
        info = _construct_indices(head)
        if info is not None and info[0] == "nat" and info[1] == 2 and args:
            # S applied to k.
            inner = project_constr(args[0], ctx)
            if isinstance(inner, IntLit):
                return IntLit(inner.value + 1)
        # Otherwise fall through.
    head_term = project_constr(head, ctx)
    arg_terms = [project_constr(a, ctx) for a in args]
    if isinstance(head_term, Var):
        return App(head=head_term.name, args=tuple(arg_terms))
    return Unsupported(reason=f"non-trivial app head {type(head_term).__name__}",
                        raw=str(head)[:120])


# ---------------------------------------------------------------------------
# Main recursive projector
# ---------------------------------------------------------------------------


def project_constr(constr: Any, ctx: Optional[List[str]] = None) -> Term:
    """Recursively project a Coq Constr s-expression into the IR.

    `ctx` is the de Bruijn binder stack (innermost binder at the end).
    Rel N references ctx[len(ctx) - N] (1-indexed from the top).
    """
    if ctx is None:
        ctx = []
    if not isinstance(constr, tuple) or not constr:
        return Unsupported(reason="non-tuple constr", raw=str(constr)[:100])
    head = constr[0]
    if head == "Rel":
        try:
            n = int(constr[1])
        except (ValueError, TypeError, IndexError):
            return Unsupported(reason="bad Rel", raw=str(constr))
        if n <= 0 or n > len(ctx):
            return Unsupported(reason=f"Rel {n} out of context ({len(ctx)})",
                                raw=str(constr))
        return Var(ctx[len(ctx) - n])
    if head == "Var":
        if len(constr) >= 2:
            iid = constr[1]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                return Var(iid[1])
        return Unsupported(reason="bad Var", raw=str(constr)[:100])
    if head == "Sort":
        # (Sort Prop), (Sort SProp), (Sort (Type _)), (Sort Set), etc.
        # We collapse them to canonical strings; for cross-prover
        # comparison only the distinction Prop / Type matters in
        # practice (everyone normalizes universe levels).
        if len(constr) >= 2:
            inner = constr[1]
            if inner == "Prop":
                return Var("Prop")
            if inner == "SProp":
                return Var("Prop")  # collapse to Prop for IR purposes
            if inner == "Set":
                return Var("Type")
            if isinstance(inner, tuple) and inner and inner[0] == "Type":
                return Var("Type")
        return Var("Sort")
    if head == "Cast":
        # (Cast body _ ty) — strip the cast.
        if len(constr) >= 2:
            return project_constr(constr[1], ctx)
        return Unsupported(reason="bad Cast", raw=str(constr)[:100])
    if head == "Prod":
        if len(constr) < 4:
            return Unsupported(reason="short Prod", raw=str(constr)[:100])
        binder = _binder_name(constr[1])
        ty = constr[2]
        body = constr[3]
        ty_term = project_constr(ty, ctx)
        # Phase C v1: emit Forall for ANY Named binder. The type can
        # be a simple Var (base-type case: nat, Nat, stmt, exec_state)
        # or a function/predicate type (e.g. `exec_state -> Prop` for
        # continuations) — in the latter case we serialize the type
        # via its pp() form so structural equality on the canonical
        # IR still works across rocq/lean.
        if binder is None:
            # Anonymous binder = arrow hypothesis. Push placeholder
            # into ctx so de Bruijn indices in body still resolve.
            body_term = project_constr(body, ctx + ["_hyp"])
            return BinOp("->", ty_term, body_term)
        # Named binder — emit Forall. Type string is the Var name
        # when ty is a simple inductive (most cases); otherwise it's
        # the pp() of the type term (higher-order quantification).
        ty_str = (ty_term.name if isinstance(ty_term, Var) else ty_term.pp())
        body_term = project_constr(body, ctx + [binder])
        return Forall(binders=(binder,), ty=ty_str, body=body_term)
    if head == "App":
        if len(constr) < 3:
            return Unsupported(reason="short App", raw=str(constr)[:100])
        head_constr = constr[1]
        args_tuple = constr[2]
        args = list(args_tuple) if isinstance(args_tuple, tuple) else []
        return _project_app(head_constr, args, ctx)
    if head == "Const":
        sname = _const_name(constr)
        if sname in _CONST_STRIP_TABLE:
            return Var(_CONST_STRIP_TABLE[sname])
        if sname:
            return Var(sname)
        return Unsupported(reason="empty Const name", raw=str(constr)[:100])
    if head == "Ind":
        sname = _ind_short_name(constr)
        if sname:
            return Var(sname)
        return Unsupported(reason="empty Ind name", raw=str(constr)[:100])
    if head == "Construct":
        info = _construct_indices(constr)
        if info is not None:
            type_name, idx = info
            if type_name == "nat" and idx == 1:
                return IntLit(0)
        return Unsupported(reason=f"unrecognized Construct {info}",
                            raw=str(constr)[:120])
    if head == "Int":
        if len(constr) >= 2:
            try:
                return IntLit(int(constr[1]))
            except (ValueError, TypeError):
                pass
        return Unsupported(reason="bad Int", raw=str(constr)[:100])
    return Unsupported(reason=f"unhandled head {head}",
                        raw=str(constr)[:120])
