"""Test codecs.win32_code_page_search_function L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import codecs  # noqa: F401


#@ requires True
#@ ensures True
def use_win32_code_page_search_function(x: int) -> int:
    return codecs.win32_code_page_search_function(x)


if __name__ == "__main__":
    pass
