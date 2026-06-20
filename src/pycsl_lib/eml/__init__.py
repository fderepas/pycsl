# Pure model for email — email handling
# Models as header/body size tracking.


#@ requires body_len >= 0
#@ ensures \result >= body_len
def create_message(body_len: int) -> int:
    """Create email message. Returns total size >= body."""
    return body_len


#@ requires msg_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= msg_len
def get_body(msg_len: int) -> int:
    """Extract body from message. Length <= message."""
    return msg_len


#@ requires msg_len >= 0
#@ ensures \result >= 0
def get_header_count(msg_len: int) -> int:
    """Count headers in message."""
    return 0


#@ requires msg_len >= 0
#@ ensures \result >= msg_len
def as_string(msg_len: int) -> int:
    """Serialize message to string. Length >= body."""
    return msg_len


#@ requires raw_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= raw_len
def parse_message(raw_len: int) -> int:
    """Parse raw email. Returns body length <= raw."""
    return raw_len
