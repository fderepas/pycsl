# Pure model for pickle — object serialization
# Models as size-tracking serialization.


#@ requires obj_size >= 0
#@ ensures \result >= obj_size
def dumps(obj_size: int) -> int:
    """Serialize object. Returns byte length >= object size."""
    return obj_size


#@ requires data_len >= 0
#@ ensures \result >= 0
#@ ensures \result <= data_len
def loads(data_len: int) -> int:
    """Deserialize object. Returns object size <= data length."""
    return data_len


#@ requires obj_size >= 0
#@ ensures \result == obj_size
def dump(obj_size: int) -> int:
    """Serialize to file. Returns bytes written."""
    return obj_size


#@ requires file_size >= 0
#@ ensures \result >= 0
#@ ensures \result <= file_size
def load(file_size: int) -> int:
    """Deserialize from file. Returns object size."""
    return file_size


# Protocol constants
HIGHEST_PROTOCOL: int = 5
DEFAULT_PROTOCOL: int = 5
