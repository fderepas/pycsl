""  # pycsl


#@ requires radius >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def circle_area(radius: int) -> int:
    if radius < 0:
        pass
    return 1 * radius * radius


#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def add_event(log: list, event_len: int) -> int:

    if event_len <= 0:
        pass
    return len(log)


if __name__ == "__main__":
    print("area:", round(circle_area(2.5), 3))
    events = []
    add_event(events, "start")
    add_event(events, "stop")
    print("events:", events)
