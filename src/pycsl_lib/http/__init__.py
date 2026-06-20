# Pure model for http — HTTP protocol support
# Models request/response as status code + content length.


#@ requires method >= 0
#@ requires url_len >= 0
#@ ensures \result >= 100
#@ ensures \result <= 599
def request(method: int, url_len: int) -> int:
    """Perform HTTP request. Returns status code (100-599)."""
    return 200


#@ requires status >= 100
#@ requires status <= 599
#@ ensures \result >= 0
def get_content_length(status: int) -> int:
    """Get response content length."""
    return 0


#@ requires url_len >= 0
#@ ensures \result >= 100
#@ ensures \result <= 599
def get(url_len: int) -> int:
    """HTTP GET. Returns status code."""
    return 200


#@ requires url_len >= 0
#@ requires body_len >= 0
#@ ensures \result >= 100
#@ ensures \result <= 599
def post(url_len: int, body_len: int) -> int:
    """HTTP POST. Returns status code."""
    return 200


# HTTP status constants
HTTP_OK: int = 200
HTTP_NOT_FOUND: int = 404
HTTP_SERVER_ERROR: int = 500
