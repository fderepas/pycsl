"""PyCSL mock for Python's winreg module — Routines and objects for manipulating the Windows registry."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def CloseKey(hkey: int) -> int:
    """Mock: Closes a previously opened registry key.  The *hkey* argument specifies a previously opened key. .. note:: If *hkey* is ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ConnectRegistry(computer_name: int, key: int) -> int:
    """Mock: Establishes a connection to a predefined registry handle on another computer, and returns a :ref:`handle object <handle-..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CreateKey(key: int, sub_key: int) -> int:
    """Mock: Creates or opens the specified key, returning a :ref:`handle object <handle-object>`. *key* is an already open key, or o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def CreateKeyEx(key: int, sub_key: int, reserved: int, access: int) -> int:
    """Mock: Creates or opens the specified key, returning a :ref:`handle object <handle-object>`. *key* is an already open key, or o..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def DeleteKey(key: int, sub_key: int) -> int:
    """Mock: Deletes the specified key. *key* is an already open key, or one of the predefined :ref:`HKEY_* constants <hkey-constants..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def DeleteKeyEx(key: int, sub_key: int, access: int, reserved: int) -> int:
    """Mock: Deletes the specified key. *key* is an already open key, or one of the predefined :ref:`HKEY_* constants <hkey-constants..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def DeleteTree(key: int, sub_key: int) -> int:
    """Mock: Deletes the specified key and all its subkeys and values recursively. *key* is an already open key, or one of the predef..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def DeleteValue(key: int, value: int) -> int:
    """Mock: Removes a named value from a registry key. *key* is an already open key, or one of the predefined :ref:`HKEY_* constants..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def EnumKey(key: int, index: int) -> int:
    """Mock: Enumerates subkeys of an open registry key, returning a string. *key* is an already open key, or one of the predefined :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def EnumValue(key: int, index: int) -> int:
    """Mock: Enumerates values of an open registry key, returning a tuple. *key* is an already open key, or one of the predefined :re..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ExpandEnvironmentStrings(str: int) -> int:
    """Mock: Expands environment variable placeholders ``%NAME%`` in strings like :const:`REG_EXPAND_SZ`:: >>> ExpandEnvironmentStrin..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def FlushKey(key: int) -> int:
    """Mock: Writes all the attributes of a key to the registry. *key* is an already open key, or one of the predefined :ref:`HKEY_* ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def LoadKey(key: int, sub_key: int, file_name: int) -> int:
    """Mock: Creates a subkey under the specified key and stores registration information from a specified file into that subkey. *ke..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def OpenKey(key: int, sub_key: int, reserved: int, access: int) -> int:
    """Mock: Opens the specified key, returning a :ref:`handle object <handle-object>`. *key* is an already open key, or one of the p..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def QueryInfoKey(key: int) -> int:
    """Mock: Returns information about a key, as a tuple. *key* is an already open key, or one of the predefined :ref:`HKEY_* constan..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def QueryValue(key: int, sub_key: int) -> int:
    """Mock: Retrieves the unnamed value for a key, as a string. *key* is an already open key, or one of the predefined :ref:`HKEY_* ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def QueryValueEx(key: int, value_name: int) -> int:
    """Mock: Retrieves the type and data for a specified value name associated with an open registry key. *key* is an already open ke..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SaveKey(key: int, file_name: int) -> int:
    """Mock: Saves the specified key, and all its subkeys to the specified file. *key* is an already open key, or one of the predefin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SetValue(key: int, sub_key: int, type_: int, value: int) -> int:
    """Mock: Associates a value with a specified key. *key* is an already open key, or one of the predefined :ref:`HKEY_* constants <..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def SetValueEx(key: int, value_name: int, reserved: int, type_: int, value: int) -> int:
    """Mock: Stores data in the value field of an open registry key. *key* is an already open key, or one of the predefined :ref:`HKE..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def DisableReflectionKey(key: int) -> int:
    """Mock: Disables registry reflection for 32-bit processes running on a 64-bit operating system. *key* is an already open key, or..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def EnableReflectionKey(key: int) -> int:
    """Mock: Restores registry reflection for the specified disabled key. *key* is an already open key, or one of the predefined :ref..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def QueryReflectionKey(key: int) -> int:
    """Mock: Determines the reflection state for the specified key. *key* is an already open key, or one of the predefined :ref:`HKEY..."""
    return 0
