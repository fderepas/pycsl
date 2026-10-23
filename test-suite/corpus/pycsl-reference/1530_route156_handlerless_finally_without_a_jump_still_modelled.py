r"""Test 1530 - ROUTE #156 control (gen #29): `try: x = 1 / finally: x = 7` — no handlers and no jump — is still EMITTED (#33's case) and `\result == 7` PROVES.
"""
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    x = 0
    try:
        x = 1
    finally:
        x = 7
    return x

