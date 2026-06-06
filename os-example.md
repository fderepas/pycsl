System call require building dedicated structures. Let's show an example.

# The examples

Here are two example that should work with PyCSL

## Python way of doing things

```python
# WRITING TO A FILE
# 'w' mode opens for writing (truncating the file if it exists)
with open("example.txt", "w") as f:
    f.write("Hello from Python!")
# The file is automatically closed here

# READING FROM A FILE
# 'r' mode opens for reading
with open("example.txt", "r") as f:
    content = f.read()
    print(content)
```

## Low level
Equivalent of previous example:
```python
import os

### 1. OPEN (Equivalent to C's open)
### Flags are combined using the bitwise OR (|) operator, just like in C
flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
mode = 0o644  # File permissions (octal)
fd = os.open("low_level.txt", flags, mode)

### 2. WRITE (Equivalent to C's write)
### Requires a bytes object (hence the b"...")
text_to_write = b"Hello from the low-level OS module!"
os.write(fd, text_to_write)

### 3. CLOSE (Equivalent to C's close)
os.close(fd)


### --- READING BACK ---

### 1. OPEN
fd = os.open("low_level.txt", os.O_RDONLY)

### 2. READ
### You must specify the maximum number of bytes to read (buffer size)
buffer_size = 100
content_bytes = os.read(fd, buffer_size)

### Decode bytes back to a string for printing
print(content_bytes.decode('utf-8'))

### 3. CLOSE
os.close(fd)
```

# What to build.