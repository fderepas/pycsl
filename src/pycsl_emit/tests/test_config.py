"""Config loader tests."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from pycsl_emit.config import load_config
from pycsl_emit.config.load import ConfigError
from pycsl_emit.translator import DividesStyle


def test_minimal_dict_loads():
    cfg = load_config({"input": {"python": "src/euclid.py"}})
    assert cfg.python == "src/euclid.py"
    assert cfg.output == "src/euclid.annotated.py"
    assert cfg.functions == {}
    assert cfg.pycsl.extra_flags == ()
    assert cfg.pycsl.prover is None


def test_default_output_for_non_py_input():
    cfg = load_config({"input": {"python": "weird"}})
    assert cfg.output == "weird.annotated"


def test_explicit_output_path_honored():
    cfg = load_config({"input": {"python": "a.py", "output": "/tmp/b.py"}})
    assert cfg.output == "/tmp/b.py"


def test_missing_input_section_raises():
    with pytest.raises(ConfigError, match=r"missing required section \[input\]"):
        load_config({})


def test_missing_python_field_raises():
    with pytest.raises(ConfigError, match=r"missing required field input\.python"):
        load_config({"input": {}})


def test_function_with_full_options():
    cfg = load_config({
        "input": {"python": "src/euclid.py"},
        "functions": {
            "gcd": {
                "python_name": "compute_gcd",
                "arg_map": {"a": "x", "b": "y"},
                "divides_style": "existential",
                "spec_theorems": ["gcd_divides", "gcd_greatest"],  # tool-specific
            },
        },
    })
    fn = cfg.functions["gcd"]
    assert fn.qualname == "gcd"
    assert fn.python_name == "compute_gcd"
    assert fn.arg_map.apply("a") == "x"
    assert fn.arg_map.apply("b") == "y"
    assert fn.arg_map.apply("c") == "c"  # identity for unmapped
    assert fn.divides_style is DividesStyle.EXISTENTIAL
    # Tool-specific keys round-trip via .raw
    assert fn.raw["spec_theorems"] == ["gcd_divides", "gcd_greatest"]


def test_function_with_defaults_only():
    cfg = load_config({
        "input": {"python": "src/x.py"},
        "functions": {"foo": {}},
    })
    fn = cfg.functions["foo"]
    assert fn.python_name == "foo"
    assert fn.arg_map.mapping == {}
    assert fn.divides_style is DividesStyle.OPERATIONAL


def test_invalid_divides_style_raises():
    with pytest.raises(ConfigError, match="divides_style: unknown value"):
        load_config({
            "input": {"python": "x.py"},
            "functions": {"f": {"divides_style": "bogus"}},
        })


def test_arg_map_type_error():
    with pytest.raises(ConfigError, match="arg_map entries must be string"):
        load_config({
            "input": {"python": "x.py"},
            "functions": {"f": {"arg_map": {"a": 42}}},
        })


def test_pycsl_settings_round_trip():
    cfg = load_config({
        "input": {"python": "x.py"},
        "pycsl": {
            "extra_flags": ["--memory-model", "hoare"],
            "prover": "Alt-Ergo,2.6.2,",
            "timeout": 60.0,
        },
    })
    assert cfg.pycsl.extra_flags == ("--memory-model", "hoare")
    assert cfg.pycsl.prover == "Alt-Ergo,2.6.2,"
    assert cfg.pycsl.timeout == 60.0
    args = cfg.pycsl.cli_args()
    assert "--memory-model" in args and "hoare" in args
    assert "-p" in args and "Alt-Ergo,2.6.2," in args


def test_pycsl_extra_flags_type_error():
    with pytest.raises(ConfigError, match="extra_flags"):
        load_config({"input": {"python": "x.py"}, "pycsl": {"extra_flags": "no"}})


def test_pycsl_timeout_type_error():
    with pytest.raises(ConfigError, match="timeout"):
        load_config({"input": {"python": "x.py"}, "pycsl": {"timeout": "fast"}})


def test_load_from_file(tmp_path: Path):
    cfg_path = tmp_path / "cfg.toml"
    cfg_path.write_text(textwrap.dedent("""
        [input]
        python = "src/euclid.py"
        output = "/tmp/out.py"

        [pycsl]
        extra_flags = ["--memory-model", "hoare"]

        [functions.gcd]
        python_name = "gcd"
        divides_style = "guarded"
    """))
    cfg = load_config(cfg_path)
    assert cfg.python == "src/euclid.py"
    assert cfg.output == "/tmp/out.py"
    assert cfg.functions["gcd"].divides_style is DividesStyle.GUARDED
    assert cfg.pycsl.extra_flags == ("--memory-model", "hoare")
