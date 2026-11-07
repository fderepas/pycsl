def g(x: int) -> int:
    return len(open('/nonexistent/zz').read()) + x
