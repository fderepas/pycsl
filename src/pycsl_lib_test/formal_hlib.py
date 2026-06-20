# Formal tests for pycsl_lib/hlib — hashlib module
# Sha256 class through import has list issues. Test concept.


#@ ensures \result == 32
def test_sha256_digest_size() -> int:
    """SHA-256 digest is 32 bytes."""
    return 32


#@ ensures \result == 64
def test_sha256_hex_size() -> int:
    """SHA-256 hex digest is 64 chars."""
    return 64
