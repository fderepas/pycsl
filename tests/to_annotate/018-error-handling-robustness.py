def parse_int_list(text):
    values = []
    for raw in text.split(","):
        token = raw.strip()
        if not token:
            raise ValueError("empty token is not allowed")
        values.append(int(token))
    return values


def safe_divide(a, b):
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


if __name__ == "__main__":
    try:
        numbers = parse_int_list("10, 20, 30")
        print("numbers:", numbers)
        print("ratio:", safe_divide(numbers[0], numbers[1]))
    except (ValueError, ZeroDivisionError) as exc:
        print("error:", exc)

