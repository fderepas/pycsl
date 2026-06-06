"""Dynamic oracle — instruments and runs annotated Python files."""

import sys
import os
import subprocess
import tempfile
from dataclasses import dataclass

_instrumenter_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instrumenter')
_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, _instrumenter_dir)
sys.path.insert(0, _project_root)


@dataclass
class DynamicResult:
    """Result of running an instrumented file."""
    filepath: str
    overall: str = "UNKNOWN"  # "PASS", "FAIL", "ERROR", "SKIP"
    error_msg: str = ""
    assertion_msg: str = ""
    stdout: str = ""
    stderr: str = ""


def run_dynamic(filepath: str, timeout: int = 30) -> DynamicResult:
    """Instrument a file and run it, checking for assertion failures."""
    result = DynamicResult(filepath=filepath)

    try:
        from instrumenter import instrument_file
        instrumented = instrument_file(filepath)
    except Exception as e:
        result.overall = "ERROR"
        result.error_msg = f"Instrumentation failed: {e}"
        return result

    # The instrumented code needs a main guard to actually run
    # Check if there's a __main__ block; if not, the file might only define functions
    if '__main__' not in instrumented and 'if __name__' not in instrumented:
        # Try to detect top-level calls or just run it
        pass

    with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, dir='/tmp') as f:
        f.write(instrumented)
        tmp_path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True,
            timeout=timeout
        )
        result.stdout = proc.stdout
        result.stderr = proc.stderr

        if proc.returncode == 0:
            result.overall = "PASS"
        else:
            # Check for AssertionError specifically
            if "AssertionError" in proc.stderr:
                result.overall = "FAIL"
                # Extract assertion message
                for line in proc.stderr.splitlines():
                    if "AssertionError:" in line:
                        result.assertion_msg = line.split("AssertionError:", 1)[1].strip()
                        break
            else:
                result.overall = "ERROR"
                result.error_msg = proc.stderr[:500]
    except subprocess.TimeoutExpired:
        result.overall = "ERROR"
        result.error_msg = "Execution timed out"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return result
