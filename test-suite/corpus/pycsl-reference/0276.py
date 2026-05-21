"""Test 0276 — Concurrent: unprotected shared alongside thread_entry (ConcurrencyChecker warning path)"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared request_count
#@ shared response_count
_ = 0  # anchor

request_count = 0
response_count = 0

#@ thread_entry
#@ \diverges
def handle() -> int:
    request_count += 1
    response_count += 1
    return 0

if __name__ == "__main__":
    print("PASS")
