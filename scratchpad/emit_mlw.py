import sys
sys.path.insert(0, "src/pycsl")
import subprocess, os
# Use pycsl internals to emit .mlw. Easiest: monkeypatch tempfile to keep it.
