"""Test 0273 — Concurrent: multiple unprotected shared variables"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared debug_mode
#@ shared trace_mode
_ = 0  # anchor

debug_mode = 0
trace_mode = 0

def get_debug() -> int:
    return debug_mode

def get_trace() -> int:
    return trace_mode

if __name__ == "__main__":
    print("PASS")
