#@ requires radius >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def circle_area(radius: int) -> int:
    return radius * radius


#@ requires log_n >= 0
#@ requires event_len > 0
#@ ensures \result == log_n + 1
#@ assigns \nothing
def add_event(log_n: int, event_len: int) -> int:
    return log_n + 1


if __name__ == "__main__":
    print("area:", circle_area(2))
    log_n = 0
    log_n = add_event(log_n, len("start"))
    log_n = add_event(log_n, len("stop"))
    print("log size:", log_n)