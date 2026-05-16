"""Static oracle — runs PyCSL/Why3 and parses per-goal verification results."""

import subprocess
import sys
import os
import re
import tempfile
from dataclasses import dataclass, field
from typing import List

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')


@dataclass
class GoalResult:
    """A single Why3 sub-goal verification result."""
    name: str
    status: str  # "Valid", "Unknown", "Timeout", "Invalid", "Error"
    prover: str = ""


@dataclass
class StaticResult:
    """Aggregated static verification result for one file."""
    filepath: str
    goals: List[GoalResult] = field(default_factory=list)
    overall: str = "UNKNOWN"  # "PASS", "FAIL", "ERROR", "SKIP"
    error_msg: str = ""
    raw_output: str = ""


def run_static(filepath: str, timeout: int = 30) -> StaticResult:
    """Run PyCSL + Why3 on a file and parse the results."""
    result = StaticResult(filepath=filepath)
    pycsl_bin = os.path.join(_project_root, '.venv', 'bin', 'pycsl')
    if not os.path.isfile(pycsl_bin):
        import shutil
        pycsl_bin = shutil.which('pycsl') or 'pycsl'

    # Run pycsl which produces .mlw and invokes why3
    # We need to run the pipeline ourselves to get per-goal output
    try:
        # First, run the pipeline to produce WhyML
        sys.path.insert(0, _project_root)
        whyml_code = _run_pipeline(filepath)
        if whyml_code is None:
            result.overall = "ERROR"
            result.error_msg = "Pipeline failed to produce WhyML"
            return result
    except Exception as e:
        result.overall = "ERROR"
        result.error_msg = str(e)
        return result

    # Write to temp .mlw file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mlw', delete=False) as f:
        f.write(whyml_code)
        mlw_path = f.name

    try:
        cmd = [
            "why3", "prove", "-a", "split_vc",
            "-P", "alt-ergo",
            "--timelimit", str(timeout),
            mlw_path
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout * 3)
        result.raw_output = proc.stdout

        # Parse output lines: each line like "Module Goal ... : Valid" or "... : Unknown ..."
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # Lines look like: "M f'vc : Valid" or "M f'vc : Unknown (Alt-Ergo 2.5.4)"
            if ': ' in line:
                parts = line.rsplit(': ', 1)
                goal_name = parts[0].strip()
                status_part = parts[1].strip()
                status = status_part.split()[0] if status_part else "Unknown"
                prover = ""
                paren = re.search(r'\((.+?)\)', status_part)
                if paren:
                    prover = paren.group(1)
                result.goals.append(GoalResult(
                    name=goal_name, status=status, prover=prover
                ))

        # Determine overall result
        if not result.goals:
            result.overall = "SKIP"
        elif all(g.status == "Valid" for g in result.goals):
            result.overall = "PASS"
        elif any(g.status == "Invalid" for g in result.goals):
            result.overall = "FAIL"
        else:
            result.overall = "FAIL"

    except subprocess.TimeoutExpired:
        result.overall = "ERROR"
        result.error_msg = "Why3 timed out"
    except FileNotFoundError:
        result.overall = "ERROR"
        result.error_msg = "Why3 not found"
    finally:
        if os.path.exists(mlw_path):
            os.unlink(mlw_path)

    return result


def _run_pipeline(filepath: str) -> str:
    """Run PyCSL Modules 1-6 to produce WhyML code."""
    sys.path.insert(0, _project_root)

    from Module1_Ingestor import Module1_Ingestor
    from Module2_Parser import Module2_Parser
    from Module3_Weaver import Module3_Weaver
    from Module4_SemanticAnalyzer import Module4_SemanticAnalyzer
    from Module5_IREmitter import Module5_IREmitter
    from Module6_WhyMLTranspiler import Module6_WhyMLTranspiler

    with open(filepath, 'r') as f:
        source = f.read()

    ingestor = Module1_Ingestor(source)
    extracted = ingestor.process()

    parser = Module2_Parser()
    weaver = Module3_Weaver(source, extracted, parser)
    annotated_ast = weaver.process()

    analyzer = Module4_SemanticAnalyzer(annotated_ast, source)
    analyzer.analyze()

    emitter = Module5_IREmitter(annotated_ast)
    ir = emitter.emit()

    # Detect memory model from filename
    memory_model = "hoare"
    basename = os.path.basename(filepath).lower()
    if "typed" in basename or "heap" in basename:
        memory_model = "typed"
    elif "store" in basename:
        memory_model = "store"

    transpiler = Module6_WhyMLTranspiler(ir, memory_model=memory_model)
    return transpiler.transpile()
