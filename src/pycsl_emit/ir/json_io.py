"""JSON encoder + decoder for pycsl_emit.ir nodes.

Used by the bridge in §3.3 to round-trip contracts through disk
without re-running the converters. The format is structural — each
node serializes to `{"type": "NodeName", ...fields...}` — and the
schema is the public surface contract for any tool that consumes
rocq2pycsl / lean2pycsl `--ir-dump` output.

The encoder is total over the IR. `Unsupported` round-trips
faithfully so the reconciler can show what was missed.
"""

from __future__ import annotations

import json
from typing import Any

from .nodes import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    Lit,
    Node,
    Result,
    UnaryOp,
    Unsupported,
    Var,
    Length,
    Nth,
    Tuple,
    Proj,
    MapGet,
    MapSet,
    MapEmpty,
    HasKey,
    StrConcat,
    StrLength,
    StrSub,
    StrLit,
    FieldGet,
    ListNil,
    ListCons,
    ListLen,
    ListAppend,
    ListNthAt,
    SetEmpty,
    SetAdd,
    SetRemove,
    SetMem,
    SetUnion,
    SetInter,
    SetDiff,
    SetSubset,
    SetEq,
)


# ──────────────────────────────────────────────────────────────────────
# Encode
# ──────────────────────────────────────────────────────────────────────


def to_dict(node: Node) -> dict[str, Any]:
    """Serialize one IR node to a JSON-ready dict."""
    if isinstance(node, Var):
        return {"type": "Var", "name": node.name}
    if isinstance(node, Lit):
        return {"type": "Lit", "value": node.value}
    if isinstance(node, Result):
        return {"type": "Result"}
    if isinstance(node, App):
        return {
            "type": "App",
            "fn": node.fn,
            "args": [to_dict(a) for a in node.args],
        }
    if isinstance(node, BinOp):
        return {
            "type": "BinOp",
            "op": node.op,
            "lhs": to_dict(node.lhs),
            "rhs": to_dict(node.rhs),
        }
    if isinstance(node, UnaryOp):
        return {"type": "UnaryOp", "op": node.op, "arg": to_dict(node.arg)}
    if isinstance(node, Forall):
        return {
            "type": "Forall",
            "var": node.var,
            "ty": node.ty,
            "body": to_dict(node.body),
        }
    if isinstance(node, Exists):
        return {
            "type": "Exists",
            "var": node.var,
            "ty": node.ty,
            "body": to_dict(node.body),
        }
    if isinstance(node, Divides):
        return {"type": "Divides", "d": to_dict(node.d), "n": to_dict(node.n)}
    if isinstance(node, Unsupported):
        return {"type": "Unsupported", "reason": node.reason, "raw": node.raw}

    # Lists / arrays / tuples / dicts / strings
    if isinstance(node, Length):
        return {"type": "Length", "arr": to_dict(node.arr)}
    if isinstance(node, Nth):
        return {"type": "Nth", "arr": to_dict(node.arr), "i": to_dict(node.i)}
    if isinstance(node, Tuple):
        return {"type": "Tuple", "args": [to_dict(a) for a in node.args]}
    if isinstance(node, Proj):
        return {"type": "Proj", "t": to_dict(node.t), "i": node.i}
    if isinstance(node, MapGet):
        return {"type": "MapGet", "d": to_dict(node.d), "k": to_dict(node.k)}
    if isinstance(node, MapSet):
        return {
            "type": "MapSet",
            "d": to_dict(node.d),
            "k": to_dict(node.k),
            "v": to_dict(node.v),
        }
    if isinstance(node, MapEmpty):
        return {"type": "MapEmpty"}
    if isinstance(node, HasKey):
        return {"type": "HasKey", "d": to_dict(node.d), "k": to_dict(node.k)}
    if isinstance(node, StrConcat):
        return {"type": "StrConcat", "a": to_dict(node.a), "b": to_dict(node.b)}
    if isinstance(node, StrLength):
        return {"type": "StrLength", "s": to_dict(node.s)}
    if isinstance(node, StrSub):
        return {
            "type": "StrSub",
            "s": to_dict(node.s),
            "lo": to_dict(node.lo),
            "hi": to_dict(node.hi),
        }
    if isinstance(node, StrLit):
        return {"type": "StrLit", "value": node.value}

    # Class instances
    if isinstance(node, FieldGet):
        return {"type": "FieldGet", "obj": to_dict(node.obj), "name": node.name}

    # ghost_list
    if isinstance(node, ListNil):
        return {"type": "ListNil"}
    if isinstance(node, ListCons):
        return {
            "type": "ListCons",
            "head": to_dict(node.head),
            "tail": to_dict(node.tail),
        }
    if isinstance(node, ListLen):
        return {"type": "ListLen", "l": to_dict(node.l)}
    if isinstance(node, ListAppend):
        return {"type": "ListAppend", "l1": to_dict(node.l1), "l2": to_dict(node.l2)}
    if isinstance(node, ListNthAt):
        return {"type": "ListNthAt", "l": to_dict(node.l), "i": to_dict(node.i)}

    # ghost_set
    if isinstance(node, SetEmpty):
        return {"type": "SetEmpty"}
    if isinstance(node, SetAdd):
        return {"type": "SetAdd", "s": to_dict(node.s), "x": to_dict(node.x)}
    if isinstance(node, SetRemove):
        return {"type": "SetRemove", "s": to_dict(node.s), "x": to_dict(node.x)}
    if isinstance(node, SetMem):
        return {"type": "SetMem", "x": to_dict(node.x), "s": to_dict(node.s)}
    if isinstance(node, SetUnion):
        return {"type": "SetUnion", "a": to_dict(node.a), "b": to_dict(node.b)}
    if isinstance(node, SetInter):
        return {"type": "SetInter", "a": to_dict(node.a), "b": to_dict(node.b)}
    if isinstance(node, SetDiff):
        return {"type": "SetDiff", "a": to_dict(node.a), "b": to_dict(node.b)}
    if isinstance(node, SetSubset):
        return {"type": "SetSubset", "a": to_dict(node.a), "b": to_dict(node.b)}
    if isinstance(node, SetEq):
        return {"type": "SetEq", "a": to_dict(node.a), "b": to_dict(node.b)}

    raise TypeError(f"to_dict: unknown IR node {type(node).__name__}")


def to_json(node: Node, *, indent: int | None = 2) -> str:
    return json.dumps(to_dict(node), indent=indent, sort_keys=False)


# ──────────────────────────────────────────────────────────────────────
# Decode
# ──────────────────────────────────────────────────────────────────────


def from_dict(data: dict[str, Any]) -> Node:
    """Deserialize one IR node from a JSON-decoded dict."""
    kind = data.get("type")
    if kind == "Var":
        return Var(name=data["name"])
    if kind == "Lit":
        return Lit(value=data["value"])
    if kind == "Result":
        return Result()
    if kind == "App":
        return App(fn=data["fn"], args=tuple(from_dict(a) for a in data["args"]))
    if kind == "BinOp":
        return BinOp(
            op=data["op"], lhs=from_dict(data["lhs"]), rhs=from_dict(data["rhs"])
        )
    if kind == "UnaryOp":
        return UnaryOp(op=data["op"], arg=from_dict(data["arg"]))
    if kind == "Forall":
        return Forall(var=data["var"], ty=data["ty"], body=from_dict(data["body"]))
    if kind == "Exists":
        return Exists(var=data["var"], ty=data["ty"], body=from_dict(data["body"]))
    if kind == "Divides":
        return Divides(d=from_dict(data["d"]), n=from_dict(data["n"]))
    if kind == "Unsupported":
        return Unsupported(reason=data["reason"], raw=data["raw"])

    # Lists / arrays / tuples / dicts / strings
    if kind == "Length":
        return Length(arr=from_dict(data["arr"]))
    if kind == "Nth":
        return Nth(arr=from_dict(data["arr"]), i=from_dict(data["i"]))
    if kind == "Tuple":
        return Tuple(args=tuple(from_dict(a) for a in data["args"]))
    if kind == "Proj":
        return Proj(t=from_dict(data["t"]), i=data["i"])
    if kind == "MapGet":
        return MapGet(d=from_dict(data["d"]), k=from_dict(data["k"]))
    if kind == "MapSet":
        return MapSet(
            d=from_dict(data["d"]),
            k=from_dict(data["k"]),
            v=from_dict(data["v"]),
        )
    if kind == "MapEmpty":
        return MapEmpty()
    if kind == "HasKey":
        return HasKey(d=from_dict(data["d"]), k=from_dict(data["k"]))
    if kind == "StrConcat":
        return StrConcat(a=from_dict(data["a"]), b=from_dict(data["b"]))
    if kind == "StrLength":
        return StrLength(s=from_dict(data["s"]))
    if kind == "StrSub":
        return StrSub(
            s=from_dict(data["s"]),
            lo=from_dict(data["lo"]),
            hi=from_dict(data["hi"]),
        )
    if kind == "StrLit":
        return StrLit(value=data["value"])

    # Class instances
    if kind == "FieldGet":
        return FieldGet(obj=from_dict(data["obj"]), name=data["name"])

    # ghost_list
    if kind == "ListNil":
        return ListNil()
    if kind == "ListCons":
        return ListCons(head=from_dict(data["head"]), tail=from_dict(data["tail"]))
    if kind == "ListLen":
        return ListLen(l=from_dict(data["l"]))
    if kind == "ListAppend":
        return ListAppend(l1=from_dict(data["l1"]), l2=from_dict(data["l2"]))
    if kind == "ListNthAt":
        return ListNthAt(l=from_dict(data["l"]), i=from_dict(data["i"]))

    # ghost_set
    if kind == "SetEmpty":
        return SetEmpty()
    if kind == "SetAdd":
        return SetAdd(s=from_dict(data["s"]), x=from_dict(data["x"]))
    if kind == "SetRemove":
        return SetRemove(s=from_dict(data["s"]), x=from_dict(data["x"]))
    if kind == "SetMem":
        return SetMem(x=from_dict(data["x"]), s=from_dict(data["s"]))
    if kind == "SetUnion":
        return SetUnion(a=from_dict(data["a"]), b=from_dict(data["b"]))
    if kind == "SetInter":
        return SetInter(a=from_dict(data["a"]), b=from_dict(data["b"]))
    if kind == "SetDiff":
        return SetDiff(a=from_dict(data["a"]), b=from_dict(data["b"]))
    if kind == "SetSubset":
        return SetSubset(a=from_dict(data["a"]), b=from_dict(data["b"]))
    if kind == "SetEq":
        return SetEq(a=from_dict(data["a"]), b=from_dict(data["b"]))

    raise ValueError(f"from_dict: unknown node type {kind!r}")


def from_json(text: str) -> Node:
    return from_dict(json.loads(text))
