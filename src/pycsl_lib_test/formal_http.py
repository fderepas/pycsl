# Formal tests for pycsl_lib/http — http module
from pycsl_lib.http import request, get, HTTP_OK


#@ requires method >= 0
#@ requires url >= 0
#@ ensures \result >= 100
def test_request_valid_status(method: int, url: int) -> int:
    """request returns valid status code."""
    return request(method, url)


#@ requires url >= 0
#@ ensures \result >= 100
def test_get_valid(url: int) -> int:
    """get returns valid status code."""
    return get(url)


#@ ensures \result == 200
def test_http_ok_constant() -> int:
    """HTTP_OK is 200."""
    return HTTP_OK
