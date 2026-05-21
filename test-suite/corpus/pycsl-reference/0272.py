"""Test 0272 — Concurrent: unprotected shared variable, read-only access"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared log_level
_ = 0  # anchor

log_level = 1

def get_log_level() -> int:
    return log_level

if __name__ == "__main__":
    print("PASS")
