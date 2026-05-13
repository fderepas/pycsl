from math import pi


def circle_area(radius):
    if radius < 0:
        raise ValueError("radius must be non-negative")
    return pi * radius * radius


def add_event(log, event):
    if not event:
        raise ValueError("event must be a non-empty string")
    log.append(event)
    return len(log)


if __name__ == "__main__":
    print("area:", round(circle_area(2.5), 3))
    events = []
    add_event(events, "start")
    add_event(events, "stop")
    print("events:", events)
