""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def parse_int_list(tokens: list) -> int:
    n = len(tokens)
    return n


#@ requires b != 0
#@ ensures 1 == 1
#@ assigns \nothing
def safe_divide(a: int, b: int) -> int:
    return a // b


if __name__ == "__main__":
    tokens = [10, 20, 30]
    count = parse_int_list(tokens)
    print("count:", count)
    print("ratio:", safe_divide(tokens[0], tokens[1]))