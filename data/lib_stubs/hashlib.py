"""PyCSL mock for Python's hashlib module.

Provides trusted stubs for secure hash and message digest algorithms.
"""
_ = 0  # anchor

# ── Generic constructor ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def new(name: int, data: int) -> int:
    """Mock: generic hash constructor by algorithm name."""
    return 0

# ── Named constructors: MD5, SHA-1, SHA-2 ───────────────────────────

#@ \trusted
#@ ensures \result >= 0
def md5(data: int) -> int:
    """Mock: create MD5 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha1(data: int) -> int:
    """Mock: create SHA-1 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha224(data: int) -> int:
    """Mock: create SHA-224 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha256(data: int) -> int:
    """Mock: create SHA-256 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha384(data: int) -> int:
    """Mock: create SHA-384 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha512(data: int) -> int:
    """Mock: create SHA-512 hash object."""
    return 0

# ── SHA-3 constructors ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def sha3_224(data: int) -> int:
    """Mock: create SHA3-224 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_256(data: int) -> int:
    """Mock: create SHA3-256 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_384(data: int) -> int:
    """Mock: create SHA3-384 hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_512(data: int) -> int:
    """Mock: create SHA3-512 hash object."""
    return 0

# ── SHAKE constructors ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def shake_128(data: int) -> int:
    """Mock: create SHAKE-128 variable-length hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shake_256(data: int) -> int:
    """Mock: create SHAKE-256 variable-length hash object."""
    return 0

# ── BLAKE2 constructors ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def blake2b(data: int, digest_size: int, key: int, salt: int, person: int) -> int:
    """Mock: create BLAKE2b hash object."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s(data: int, digest_size: int, key: int, salt: int, person: int) -> int:
    """Mock: create BLAKE2s hash object."""
    return 0

# ── Hash object methods ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result == 0
def hash_update(h: int, data: int) -> int:
    """Mock: update hash object with data."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hash_digest(h: int) -> int:
    """Mock: return digest of data fed so far."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hash_hexdigest(h: int) -> int:
    """Mock: return hex-encoded digest string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hash_copy(h: int) -> int:
    """Mock: return copy of hash object."""
    return 0

# ── SHAKE variable-length digest methods ────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def shake_digest(h: int, length: int) -> int:
    """Mock: return variable-length SHAKE digest."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shake_hexdigest(h: int, length: int) -> int:
    """Mock: return variable-length hex-encoded SHAKE digest."""
    return 0

# ── Hash object attributes ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def hash_digest_size(h: int) -> int:
    """Mock: return size of resulting hash in bytes."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hash_block_size(h: int) -> int:
    """Mock: return internal block size of hash algorithm in bytes."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hash_name(h: int) -> int:
    """Mock: return canonical name of hash algorithm."""
    return 0

# ── Key derivation ──────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def pbkdf2_hmac(hash_name: int, password: int, salt: int, iterations: int, dklen: int) -> int:
    """Mock: PKCS#5 password-based key derivation function 2."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def scrypt(password: int, salt: int, n: int, r: int, p: int, maxmem: int, dklen: int) -> int:
    """Mock: scrypt password-based key derivation function."""
    return 0

# ── File hashing ────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def file_digest(fileobj: int, digest: int) -> int:
    """Mock: return digest object updated with file contents."""
    return 0

# ── Module data attributes ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def algorithms_guaranteed() -> int:
    """Mock: set of hash algorithm names guaranteed on all platforms."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def algorithms_available() -> int:
    """Mock: set of hash algorithm names available in this interpreter."""
    return 0

# ── BLAKE2 constants ────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def blake2b_SALT_SIZE() -> int:
    """Mock: maximum salt length for BLAKE2b."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s_SALT_SIZE() -> int:
    """Mock: maximum salt length for BLAKE2s."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2b_PERSON_SIZE() -> int:
    """Mock: maximum personalization string length for BLAKE2b."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s_PERSON_SIZE() -> int:
    """Mock: maximum personalization string length for BLAKE2s."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2b_MAX_KEY_SIZE() -> int:
    """Mock: maximum key size for BLAKE2b."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s_MAX_KEY_SIZE() -> int:
    """Mock: maximum key size for BLAKE2s."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2b_MAX_DIGEST_SIZE() -> int:
    """Mock: maximum digest size for BLAKE2b."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s_MAX_DIGEST_SIZE() -> int:
    """Mock: maximum digest size for BLAKE2s."""
    return 0
