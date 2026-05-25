"""TOML loader for the shared schema.

Reads a TOML file (or a pre-parsed dict) and produces a `Config`. The
loader is *permissive on unknown keys* (they round-trip into `.raw`) but
strict on type errors and missing required fields — those raise
`ConfigError` with a path-prefixed message.

Python 3.11+ ships `tomllib`; this module uses it directly.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any, Mapping

from ..translator import DividesStyle, NameMap
from .schema import Config, FunctionSpec, PycslSettings


class ConfigError(ValueError):
    """Raised on schema validation failure."""


def load_config(source: str | os.PathLike | Mapping[str, Any]) -> Config:
    """Load a Config from a TOML file path or a dict.

    Pass a path-like object to read TOML from disk; pass a Mapping to
    skip the parse step (useful for tests).
    """
    if isinstance(source, Mapping):
        data: Mapping[str, Any] = source
    else:
        path = Path(source)
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    return _parse(data)


# ──────────────────────────────────────────────────────────────────────


def _parse(data: Mapping[str, Any]) -> Config:
    input_section = _get_section(data, "input")
    python = _get_str(input_section, "python", path="input.python")

    output = input_section.get("output")
    if output is None:
        # Default: foo.py → foo.annotated.py
        if python.endswith(".py"):
            output = python[:-3] + ".annotated.py"
        else:
            output = python + ".annotated"
    if not isinstance(output, str):
        raise ConfigError("input.output must be a string")

    functions = _parse_functions(data.get("functions", {}))
    pycsl = _parse_pycsl(data.get("pycsl", {}))

    return Config(
        python=python,
        output=output,
        functions=functions,
        pycsl=pycsl,
        raw=dict(data),
    )


def _parse_functions(
    funcs: Mapping[str, Any],
) -> Mapping[str, FunctionSpec]:
    if not isinstance(funcs, Mapping):
        raise ConfigError("[functions] must be a table")
    out: dict[str, FunctionSpec] = {}
    for qualname, entry in funcs.items():
        if not isinstance(entry, Mapping):
            raise ConfigError(f"[functions.{qualname}] must be a table")
        python_name = entry.get("python_name", qualname)
        if not isinstance(python_name, str):
            raise ConfigError(f"functions.{qualname}.python_name must be a string")

        raw_argmap = entry.get("arg_map", {})
        if not isinstance(raw_argmap, Mapping):
            raise ConfigError(f"functions.{qualname}.arg_map must be a table")
        for k, v in raw_argmap.items():
            if not (isinstance(k, str) and isinstance(v, str)):
                raise ConfigError(
                    f"functions.{qualname}.arg_map entries must be string → string"
                )

        divides_raw = entry.get("divides_style", "operational")
        try:
            divides = DividesStyle(divides_raw)
        except ValueError as exc:
            raise ConfigError(
                f"functions.{qualname}.divides_style: unknown value {divides_raw!r}; "
                f"valid: {[s.value for s in DividesStyle]}"
            ) from exc

        out[qualname] = FunctionSpec(
            qualname=qualname,
            python_name=python_name,
            arg_map=NameMap(mapping=dict(raw_argmap)),
            divides_style=divides,
            raw=dict(entry),
        )
    return out


def _parse_pycsl(section: Mapping[str, Any]) -> PycslSettings:
    if not isinstance(section, Mapping):
        raise ConfigError("[pycsl] must be a table")
    flags = section.get("extra_flags", ())
    if not isinstance(flags, (list, tuple)) or not all(isinstance(f, str) for f in flags):
        raise ConfigError("pycsl.extra_flags must be a list of strings")
    prover = section.get("prover")
    if prover is not None and not isinstance(prover, str):
        raise ConfigError("pycsl.prover must be a string")
    timeout = section.get("timeout", 120.0)
    if not isinstance(timeout, (int, float)):
        raise ConfigError("pycsl.timeout must be a number")
    return PycslSettings(
        extra_flags=tuple(flags),
        prover=prover,
        timeout=float(timeout),
    )


def _get_section(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    section = data.get(key)
    if section is None:
        raise ConfigError(f"missing required section [{key}]")
    if not isinstance(section, Mapping):
        raise ConfigError(f"[{key}] must be a table")
    return section


def _get_str(section: Mapping[str, Any], key: str, *, path: str) -> str:
    value = section.get(key)
    if value is None:
        raise ConfigError(f"missing required field {path}")
    if not isinstance(value, str):
        raise ConfigError(f"{path} must be a string")
    return value
