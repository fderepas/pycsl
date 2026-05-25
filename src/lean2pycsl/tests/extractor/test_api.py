"""Backend dispatcher tests for lean2pycsl."""

from __future__ import annotations

from pathlib import Path

import pytest

from lean2pycsl.extractor import Backend, extract
from lean2pycsl.extractor.lean_script_backend import (
    parse_module as lean_script_parse,
    lake_available,
)


def test_extract_lark_default(tmp_path: Path):
    v = tmp_path / "tiny.lean"
    v.write_text("theorem trivial : forall (a : Nat), a = a := sorry")
    mod = extract(v)
    assert [t.name for t in mod.theorems] == ["trivial"]


def test_extract_lark_explicit(tmp_path: Path):
    v = tmp_path / "tiny.lean"
    v.write_text("theorem trivial : forall (a : Nat), a = a := sorry")
    mod = extract(v, backend=Backend.LARK)
    assert mod.theorems[0].name == "trivial"


def test_extract_unknown_path_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        extract(tmp_path / "does-not-exist.lean")


def test_lean_script_backend_is_stub():
    with pytest.raises(NotImplementedError, match="lake"):
        lean_script_parse("theorem t : True := trivial")


def test_lake_available_returns_bool():
    assert isinstance(lake_available(), bool)
