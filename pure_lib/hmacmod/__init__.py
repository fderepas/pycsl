# Pure model for hmac — HMAC message authentication
# Models HMAC as digest-size tracker.


#@ requires key_len > 0
#@ requires digest_size > 0
#@ ensures \result == digest_size
def new_hmac(key_len: int, digest_size: int) -> int:
    """Create HMAC object, return digest size."""
    return digest_size


#@ requires key_len > 0
#@ requires msg_len >= 0
#@ requires digest_size > 0
#@ ensures \result == digest_size
def digest(key_len: int, msg_len: int, digest_size: int) -> int:
    """Compute HMAC digest. Returns digest size."""
    return digest_size


#@ requires a_len > 0
#@ requires b_len > 0
#@ ensures \result >= 0
#@ ensures \result <= 1
def compare_digest(a_len: int, b_len: int) -> int:
    """Constant-time comparison. Returns 1 if equal length, 0 otherwise."""
    if a_len == b_len:
        return 1
    return 0
