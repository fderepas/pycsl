"""Helper for corpus 7273 (route #467): json.loads of a non-JSON string."""
import json


def g(x: int) -> int:
    return json.loads("{") + x
