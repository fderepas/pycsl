"""Test 0275 — Concurrent: unprotected shared variable read in regular function"""
# pycsl-flags:  --memory-model concurrent
#@ shared uptime
_ = 0  # anchor

uptime = 0

def get_uptime() -> int:
    return uptime

if __name__ == "__main__":
    print("PASS")
