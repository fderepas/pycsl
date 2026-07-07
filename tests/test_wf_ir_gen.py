"""test_wf_ir_gen.py — fixture for the wall-plan-v2 `wf_ir` generator (Phase 1 §D3).

`module6_whyml/wf_ir_gen.py` derives the per-(shape,key) `wf_val` typing predicate
from `ir_schema.py` (the schema is code).  This fixture pins two things:

  1. The schema-derived shape map is correct for the interned keys — `left`/`right`
     are node references (`PDict`), `op`/`type`/`target`/`func`/`name` are strings
     (`PStr`), and heterogeneous keys (`value`, `body`) stay unconstrained
     (fail-open, never a false typing claim).
  2. The GENERATED `wf_val` is well-typed WhyML and the E4 compositionality lemma
     `wf_ir_binds` (a well-formed dict projected at a bound key satisfies that
     key's typing) still discharges over it — proved by Why3 (skipped if absent).

This is the deliverable-3 gate: the generator is a real tool, not a stub.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src", "pycsl"))

from module6_whyml.wf_ir_gen import (  # noqa: E402
    field_shape_map,
    generate_wf_val,
)

_SCHEMA = os.path.join(_ROOT, "src", "pycsl", "ir_schema.py")


def test_shape_map_interned_keys():
    smap = field_shape_map(_SCHEMA)
    # node-reference fields -> PDict
    assert smap["left"] == "PDict"
    assert smap["right"] == "PDict"
    # string-valued fields -> PStr
    assert smap["type"] == "PStr"
    assert smap["op"] == "PStr"
    assert smap["target"] == "PStr"
    assert smap["func"] == "PStr"
    assert smap["name"] == "PStr"
    # heterogeneous fields (scalar in one node, sub-node/list in another) -> unconstrained
    assert smap["value"] is None
    assert smap["body"] is None


def test_generated_predicate_shape():
    src = generate_wf_val(_SCHEMA)
    assert "predicate wf_val (k: irkey) (v: pyval)" in src
    assert "| K_op -> (match v with PStr _ -> true | _ -> false end)" in src
    assert "| K_left -> (match v with PDict _ -> true | _ -> false end)" in src
    assert "| K_value -> true" in src  # heterogeneous key stays open
    assert "| K_dyn _ -> true" in src


_THEORY_HEAD = """module WfIrGen
  use int.Int
  use list.List
  use option.Option
  use string.String

  type irkey =
    | K_type | K_left | K_right | K_op | K_z
    | K_value | K_target | K_body | K_orelse | K_func | K_name
    | K_dyn string

  type pyval =
    | PInt int | PStr string | PBool bool | PNone
    | PList (list pyval) | PDict pydict
  with pydict = DNil | DCons irkey pyval pydict

  function get (d: pydict) (k: irkey) : option pyval
  = match d with
    | DNil -> None
    | DCons k' v rest -> if k = k' then Some v else get rest k
    end

"""

_THEORY_TAIL = """
  predicate wf_dict (d: pydict)
  = match d with
    | DNil -> true
    | DCons k v rest -> wf_val k v /\\ wf_dict rest
    end

  predicate wf_ir (v: pyval)
  = match v with PDict d -> wf_dict d | _ -> true end

  let rec lemma wf_ir_binds (k: irkey) (d: pydict) : unit
    requires { wf_dict d }
    ensures  { forall v: pyval. get d k = Some v -> wf_val k v }
    variant  { d }
  = match d with
    | DNil -> ()
    | DCons _ _ rest -> wf_ir_binds k rest
    end
end
"""


@pytest.mark.skipif(shutil.which("why3") is None, reason="why3 not installed")
def test_generated_predicate_proves():
    """The generated wf_val is well-typed WhyML and the E4 compositionality lemma
    discharges over it (Valid on Alt-Ergo)."""
    module = _THEORY_HEAD + generate_wf_val(_SCHEMA) + _THEORY_TAIL
    with tempfile.NamedTemporaryFile("w", suffix=".mlw", delete=False) as fh:
        fh.write(module)
        path = fh.name
    try:
        # discover an Alt-Ergo prover id: prefer the plain `Alt-Ergo <ver>` variant
        # (no parenthetical), formatted as the `Name,Version` id why3 -P expects.
        listp = subprocess.run(["why3", "config", "list-provers"],
                               capture_output=True, text=True)
        prover = "Alt-Ergo"
        import re as _re
        for line in listp.stdout.splitlines():
            m = _re.match(r"^\s*(Alt-Ergo)\s+([0-9.]+)\s*$", line)
            if m:
                prover = f"{m.group(1)},{m.group(2)}"
                break
        res = subprocess.run(
            ["why3", "prove", "-P", prover, "-t", "20", path],
            capture_output=True, text=True,
        )
        out = res.stdout + res.stderr
        assert "Error" not in out and "error" not in out, f"WhyML type error:\n{out}"
        assert "wf_ir_binds'vc" in out, f"lemma VC missing:\n{out}"
        # the wf_ir_binds VC must be Valid (the generated table is consistent)
        assert "Valid" in out, f"generated wf_val did not prove:\n{out}"
        assert "Timeout" not in out and "Unknown" not in out, f"non-Valid goal:\n{out}"
    finally:
        os.unlink(path)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
