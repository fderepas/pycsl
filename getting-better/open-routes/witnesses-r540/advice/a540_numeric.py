# Route #540 advice probe: witness g1207_ii1209_stmt_str_param with the value annotated
# with a numeric type (`s: int`), as PYCSL-R540-UNARY-PLUS-OPERAND advises.
#@ no_exception \all
def f(s: int) -> int:
    +s
    return 1


if __name__ == "__main__":
    print("result", f(3))
