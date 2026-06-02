"""Shared `--ir-dump` schema for rocq2pycsl and lean2pycsl.

The bridge consumes JSON files in this format (one per converter run)
to reconcile contracts before they ever reach the Python source. The
schema is intentionally small — just enough to round-trip the
FunctionContract shape that both converters produce — and language-
agnostic so the bridge can compare them by canonicalizing the IR
nodes.

Schema:

  {
    "schema": "pycsl-ir-dump",
    "version": 1,
    "provenance": "rocq2pycsl" | "lean2pycsl",
    "source": "path/to/spec.v" | "path/to/Spec.lean",
    "functions": {
      "<python.qualname>": {
        "python_name": "<def name>",
        "theorems":    ["<source-side theorem name>", ...],
        "divides_style": "operational" | "existential" | "guarded",
        "contract": {
          "requires": [<IR JSON>, ...],
          "ensures":  [<IR JSON>, ...],
          "assigns":  "\\nothing",
          "variant":  <IR JSON> | null,
          "diverges": bool,
          "unsupported": [["<thm>", "<reason>", "<raw>"], ...]
        }
      },
      ...
    }
  }

`FunctionContract` is *intentionally not imported here* because both
converters define their own (structurally identical) versions. This
module's helpers take dicts so they can serve both.
"""

from __future__ import annotations

from typing import Any, Iterable

from .ir import Node, from_dict, to_dict


SCHEMA_NAME = "pycsl-ir-dump"
SCHEMA_VERSION = 1


def encode_contract(
    *,
    python_name: str,
    theorems: Iterable[str],
    divides_style: str,
    requires: Iterable[Node],
    ensures: Iterable[Node],
    assigns: str,
    variant: Node | None,
    diverges: bool,
    unsupported: Iterable[tuple[str, str, str]],
    arg_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build one function's entry for an --ir-dump file.

    `arg_map` carries the proof-side → Python-side identifier rewrite
    so the bridge can re-apply it during emission (needed for class
    methods where the proof models the receiver as a parameter that
    becomes `self.<field>` on the Python side).
    """
    return {
        "python_name": python_name,
        "theorems": list(theorems),
        "divides_style": divides_style,
        "arg_map": dict(arg_map or {}),
        "contract": {
            "requires": [to_dict(r) for r in requires],
            "ensures": [to_dict(e) for e in ensures],
            "assigns": assigns,
            "variant": to_dict(variant) if variant is not None else None,
            "diverges": diverges,
            "unsupported": [list(u) for u in unsupported],
        },
    }


def build_envelope(
    *,
    provenance: str,
    source: str,
    functions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Wrap per-function entries in the dump envelope."""
    return {
        "schema": SCHEMA_NAME,
        "version": SCHEMA_VERSION,
        "provenance": provenance,
        "source": source,
        "functions": functions,
    }


def decode_envelope(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the schema/version on a loaded dump and return it.

    Raises ValueError if the schema is unknown — guards against feeding
    arbitrary JSON to the reconciler.
    """
    if data.get("schema") != SCHEMA_NAME:
        raise ValueError(
            f"not a pycsl-ir-dump file (schema={data.get('schema')!r})"
        )
    if data.get("version") != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported pycsl-ir-dump version {data.get('version')!r} "
            f"(this build understands version {SCHEMA_VERSION})"
        )
    return data


def decode_contract_clauses(entry: dict[str, Any]) -> dict[str, Any]:
    """Helper used by the bridge: decode the IR nodes inside one
    function entry back to live `pycsl_emit.ir` objects."""
    c = entry["contract"]
    return {
        "python_name": entry["python_name"],
        "theorems": list(entry.get("theorems", [])),
        "divides_style": entry.get("divides_style", "operational"),
        "arg_map": dict(entry.get("arg_map") or {}),
        "requires": [from_dict(r) for r in c.get("requires", [])],
        "ensures": [from_dict(e) for e in c.get("ensures", [])],
        "assigns": c.get("assigns", "\\nothing"),
        "variant": from_dict(c["variant"]) if c.get("variant") else None,
        "diverges": bool(c.get("diverges", False)),
        "unsupported": [tuple(u) for u in c.get("unsupported", [])],
    }
