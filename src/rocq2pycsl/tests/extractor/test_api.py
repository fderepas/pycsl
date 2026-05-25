"""Backend dispatcher tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from rocq2pycsl.extractor import Backend, extract
from rocq2pycsl.extractor.serapi_backend import (
    parse_module as serapi_parse,
    sertop_available,
)


def test_extract_lark_default(tmp_path: Path):
    v = tmp_path / "tiny.v"
    v.write_text("Theorem trivial : forall a : nat, a = a.")
    mod = extract(v)
    assert [t.name for t in mod.theorems] == ["trivial"]


def test_extract_lark_explicit(tmp_path: Path):
    v = tmp_path / "tiny.v"
    v.write_text("Theorem trivial : forall a : nat, a = a.")
    mod = extract(v, backend=Backend.LARK)
    assert mod.theorems[0].name == "trivial"


def test_extract_unknown_path_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        extract(tmp_path / "does-not-exist.v")


def test_serapi_backend_is_stub():
    with pytest.raises(NotImplementedError, match="opam install coq-serapi"):
        serapi_parse("Theorem foo : True.")


def test_sertop_available_returns_bool():
    # We don't care what it returns — just that it doesn't crash.
    assert isinstance(sertop_available(), bool)
