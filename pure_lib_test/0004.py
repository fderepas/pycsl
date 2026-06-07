"""Concrete test 0004: pure_lib/json — loads, dumps, detect_encoding, errors.

Tests the key symbols from calling.json: dumps, loads, load,
JSONDecodeError, detect_encoding, encode, decode.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pure_lib.json import dumps, loads, load, JSONDecodeError, JSONEncoder, JSONDecoder
from pure_lib.json import detect_encoding


def test_dumps_basic():
    result = dumps(42)
    assert result == "42", f"expected '42', got {result!r}"
    print("PASS: 1 — dumps integer")


def test_dumps_string():
    result = dumps("hello")
    assert result == '"hello"', f"expected '\"hello\"', got {result!r}"
    print("PASS: 2 — dumps string")


def test_dumps_list():
    result = dumps([1, 2, 3])
    assert result == "[1, 2, 3]", f"expected '[1, 2, 3]', got {result!r}"
    print("PASS: 3 — dumps list")


def test_dumps_dict():
    result = dumps({"a": 1})
    assert result == '{"a": 1}', f"expected dict encoding, got {result!r}"
    print("PASS: 4 — dumps dict")


def test_dumps_nested():
    result = dumps({"key": [1, True, None, "val"]})
    assert '"key"' in result and "null" in result
    print("PASS: 5 — dumps nested structure")


def test_loads_basic():
    result = loads("42")
    assert result == 42, f"expected 42, got {result}"
    print("PASS: 6 — loads integer")


def test_loads_string():
    result = loads('"hello"')
    assert result == "hello", f"expected 'hello', got {result!r}"
    print("PASS: 7 — loads string")


def test_loads_dict():
    result = loads('{"a": 1, "b": 2}')
    assert result == {"a": 1, "b": 2}
    print("PASS: 8 — loads dict")


def test_loads_roundtrip():
    obj = {"name": "test", "values": [1, 2, 3], "flag": True, "empty": None}
    assert loads(dumps(obj)) == obj
    print("PASS: 9 — loads/dumps round-trip")


def test_json_decode_error():
    try:
        loads("{invalid json")
        assert False, "expected JSONDecodeError"
    except JSONDecodeError as e:
        assert "Expecting property name" in str(e) or "Expecting value" in str(e)
    print("PASS: 10 — JSONDecodeError raised")


def test_detect_encoding_utf8():
    result = detect_encoding(b'{"key": "value"}')
    assert result == 'utf-8', f"expected utf-8, got {result}"
    print("PASS: 11 — detect_encoding utf-8 default")


def test_detect_encoding_bom():
    result = detect_encoding(b'\xef\xbb\xbf{"key": "value"}')
    assert result == 'utf-8-sig', f"expected utf-8-sig, got {result}"
    print("PASS: 12 — detect_encoding utf-8-sig BOM")


def test_encoder_object():
    enc = JSONEncoder()
    result = enc.encode([1, 2])
    assert result == "[1, 2]", f"expected '[1, 2]', got {result!r}"
    print("PASS: 13 — JSONEncoder.encode()")


def test_decoder_object():
    dec = JSONDecoder()
    result = dec.decode('{"x": 10}')
    assert result == {"x": 10}
    print("PASS: 14 — JSONDecoder.decode()")


def test_escape_chars():
    result = dumps("line1\nline2\ttab")
    assert "\\n" in result and "\\t" in result
    print("PASS: 15 — escape characters in strings")


if __name__ == '__main__':
    test_dumps_basic()
    test_dumps_string()
    test_dumps_list()
    test_dumps_dict()
    test_dumps_nested()
    test_loads_basic()
    test_loads_string()
    test_loads_dict()
    test_loads_roundtrip()
    test_json_decode_error()
    test_detect_encoding_utf8()
    test_detect_encoding_bom()
    test_encoder_object()
    test_decoder_object()
    test_escape_chars()
    print("\nPASS: 0004 — all pure_lib/json tests passed")
