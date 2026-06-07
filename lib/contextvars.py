try:
    import _collections_abc
except ImportError:
    _collections_abc = None

try:
    from _contextvars import Context, ContextVar, Token, copy_context
except ImportError:
    # Stub implementations for standalone analysis
    class Token:
        """Stub for contextvars.Token."""
        pass

    class ContextVar:
        """Stub for contextvars.ContextVar."""
        def __init__(self, name, *, default=None):
            self._name = name
            self._default = default
        def get(self, default=None):
            return self._default if default is None else default
        def set(self, value):
            return Token()

    class Context:
        """Stub for contextvars.Context."""
        pass

    def copy_context():
        return Context()


__all__ = ('Context', 'ContextVar', 'Token', 'copy_context')


if _collections_abc is not None:
    _collections_abc.Mapping.register(Context)
