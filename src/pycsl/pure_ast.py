"""
pure_ast — a pure-Python reimplementation of the standard library ``ast`` module.

The real ``ast`` module is split in two: the *node hierarchy* and the *parser*
live in C (``_ast`` / ``Python-ast.c`` and CPython's PEG parser), while the
helper layer (``Lib/ast.py``) is already Python.  This module reimplements the
whole public surface in pure Python:

  * the complete AST node class hierarchy (``AST``, ``Module``, ``BinOp`` ...),
    defined from an ASDL-derived table rather than imported from ``_ast``;
  * every helper: ``dump``, ``literal_eval``, ``walk``, ``copy_location``,
    ``fix_missing_locations``, ``increment_lineno``, ``get_docstring``,
    ``get_source_segment``, ``iter_fields``, ``iter_child_nodes``,
    ``NodeVisitor``, ``NodeTransformer`` and ``unparse``;
  * the deprecated ``Num``/``Str``/``Bytes``/``NameConstant``/``Ellipsis``
    compatibility shims;
  * a ``main()`` CLI mirroring ``python -m ast``.

The one thing genuinely impossible to do in pure Python without re-implementing
CPython's grammar engine is turning *source text* into a tree.  ``parse`` here
delegates the grammar to the built-in ``compile(..., PyCF_ONLY_AST)`` and then
*transcribes* the resulting C nodes into the pure-Python classes defined below,
so every object the caller touches is one of our own classes.  See ``parse``.

Targets the node schema of the running interpreter (generated for 3.12).
"""

import sys as _sys

__all__ = [
    # core
    'AST', 'parse', 'dump', 'copy_location', 'fix_missing_locations',
    'increment_lineno', 'iter_fields', 'iter_child_nodes', 'get_docstring',
    'get_source_segment', 'walk', 'NodeVisitor', 'NodeTransformer',
    'literal_eval', 'unparse',
    # compile flags
    'PyCF_ONLY_AST', 'PyCF_TYPE_COMMENTS', 'PyCF_ALLOW_TOP_LEVEL_AWAIT',
]

# Compile-flag constants (values fixed by CPython's Include/cpython/compile.h).
PyCF_ONLY_AST = 0x0400
PyCF_TYPE_COMMENTS = 0x1000
PyCF_ALLOW_TOP_LEVEL_AWAIT = 0x2000


# ---------------------------------------------------------------------------
# Node hierarchy
# ---------------------------------------------------------------------------

class AST:
    """Base class of every node, mirroring ``_ast.AST``."""
    _fields = ()
    _attributes = ()

    def __init__(self, *args, **kwargs):
        cls = type(self)
        if len(args) > len(cls._fields):
            raise TypeError(
                f"{cls.__name__} constructor takes at most "
                f"{len(cls._fields)} positional argument"
                f"{'' if len(cls._fields) == 1 else 's'}"
            )
        for name, value in zip(cls._fields, args):
            setattr(self, name, value)
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __repr__(self):
        return f"<{type(self).__module__}.{type(self).__qualname__} object>"


# ASDL-derived schema: name -> (base-category-name, fields, attributes).
# Generated from the live node definitions of the running interpreter.
_NODE_SPEC = {
    # --- abstract base categories (parent is AST) -------------------------
    'mod': ('AST', (), ()),
    'stmt': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'expr': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'expr_context': ('AST', (), ()),
    'boolop': ('AST', (), ()),
    'operator': ('AST', (), ()),
    'unaryop': ('AST', (), ()),
    'cmpop': ('AST', (), ()),
    'slice': ('AST', (), ()),
    'excepthandler': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'pattern': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'type_ignore': ('AST', (), ()),
    'type_param': ('AST', (), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'comprehension': ('AST', ('target', 'iter', 'ifs', 'is_async'), ()),
    'arguments': ('AST', ('posonlyargs', 'args', 'vararg', 'kwonlyargs', 'kw_defaults', 'kwarg', 'defaults'), ()),
    'arg': ('AST', ('arg', 'annotation', 'type_comment'), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'keyword': ('AST', ('arg', 'value'), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'alias': ('AST', ('name', 'asname'), ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')),
    'withitem': ('AST', ('context_expr', 'optional_vars'), ()),
    'match_case': ('AST', ('pattern', 'guard', 'body'), ()),
    # --- mod --------------------------------------------------------------
    'Module': ('mod', ('body', 'type_ignores'), ()),
    'Interactive': ('mod', ('body',), ()),
    'Expression': ('mod', ('body',), ()),
    'FunctionType': ('mod', ('argtypes', 'returns'), ()),
    'Suite': ('mod', (), ()),
    # --- stmt -------------------------------------------------------------
    'FunctionDef': ('stmt', ('name', 'args', 'body', 'decorator_list', 'returns', 'type_comment', 'type_params'), None),
    'AsyncFunctionDef': ('stmt', ('name', 'args', 'body', 'decorator_list', 'returns', 'type_comment', 'type_params'), None),
    'ClassDef': ('stmt', ('name', 'bases', 'keywords', 'body', 'decorator_list', 'type_params'), None),
    'Return': ('stmt', ('value',), None),
    'Delete': ('stmt', ('targets',), None),
    'Assign': ('stmt', ('targets', 'value', 'type_comment'), None),
    'AugAssign': ('stmt', ('target', 'op', 'value'), None),
    'AnnAssign': ('stmt', ('target', 'annotation', 'value', 'simple'), None),
    'For': ('stmt', ('target', 'iter', 'body', 'orelse', 'type_comment'), None),
    'AsyncFor': ('stmt', ('target', 'iter', 'body', 'orelse', 'type_comment'), None),
    'While': ('stmt', ('test', 'body', 'orelse'), None),
    'If': ('stmt', ('test', 'body', 'orelse'), None),
    'With': ('stmt', ('items', 'body', 'type_comment'), None),
    'AsyncWith': ('stmt', ('items', 'body', 'type_comment'), None),
    'Match': ('stmt', ('subject', 'cases'), None),
    'Raise': ('stmt', ('exc', 'cause'), None),
    'Try': ('stmt', ('body', 'handlers', 'orelse', 'finalbody'), None),
    'TryStar': ('stmt', ('body', 'handlers', 'orelse', 'finalbody'), None),
    'Assert': ('stmt', ('test', 'msg'), None),
    'Import': ('stmt', ('names',), None),
    'ImportFrom': ('stmt', ('module', 'names', 'level'), None),
    'Global': ('stmt', ('names',), None),
    'Nonlocal': ('stmt', ('names',), None),
    'Expr': ('stmt', ('value',), None),
    'Pass': ('stmt', (), None),
    'Break': ('stmt', (), None),
    'Continue': ('stmt', (), None),
    'TypeAlias': ('stmt', ('name', 'type_params', 'value'), None),
    # --- expr -------------------------------------------------------------
    'BoolOp': ('expr', ('op', 'values'), None),
    'NamedExpr': ('expr', ('target', 'value'), None),
    'BinOp': ('expr', ('left', 'op', 'right'), None),
    'UnaryOp': ('expr', ('op', 'operand'), None),
    'Lambda': ('expr', ('args', 'body'), None),
    'IfExp': ('expr', ('test', 'body', 'orelse'), None),
    'Dict': ('expr', ('keys', 'values'), None),
    'Set': ('expr', ('elts',), None),
    'ListComp': ('expr', ('elt', 'generators'), None),
    'SetComp': ('expr', ('elt', 'generators'), None),
    'DictComp': ('expr', ('key', 'value', 'generators'), None),
    'GeneratorExp': ('expr', ('elt', 'generators'), None),
    'Await': ('expr', ('value',), None),
    'Yield': ('expr', ('value',), None),
    'YieldFrom': ('expr', ('value',), None),
    'Compare': ('expr', ('left', 'ops', 'comparators'), None),
    'Call': ('expr', ('func', 'args', 'keywords'), None),
    'FormattedValue': ('expr', ('value', 'conversion', 'format_spec'), None),
    'JoinedStr': ('expr', ('values',), None),
    'Constant': ('expr', ('value', 'kind'), None),
    'Attribute': ('expr', ('value', 'attr', 'ctx'), None),
    'Subscript': ('expr', ('value', 'slice', 'ctx'), None),
    'Starred': ('expr', ('value', 'ctx'), None),
    'Name': ('expr', ('id', 'ctx'), None),
    'List': ('expr', ('elts', 'ctx'), None),
    'Tuple': ('expr', ('elts', 'ctx'), None),
    'Slice': ('expr', ('lower', 'upper', 'step'), None),
    # legacy slice helpers
    'Index': ('slice', (), ()),
    'ExtSlice': ('slice', (), ()),
    # --- expr_context -----------------------------------------------------
    'Load': ('expr_context', (), ()),
    'Store': ('expr_context', (), ()),
    'Del': ('expr_context', (), ()),
    'AugLoad': ('expr_context', (), ()),
    'AugStore': ('expr_context', (), ()),
    'Param': ('expr_context', (), ()),
    # --- boolop / operator / unaryop / cmpop ------------------------------
    'And': ('boolop', (), ()), 'Or': ('boolop', (), ()),
    'Add': ('operator', (), ()), 'Sub': ('operator', (), ()),
    'Mult': ('operator', (), ()), 'MatMult': ('operator', (), ()),
    'Div': ('operator', (), ()), 'Mod': ('operator', (), ()),
    'Pow': ('operator', (), ()), 'LShift': ('operator', (), ()),
    'RShift': ('operator', (), ()), 'BitOr': ('operator', (), ()),
    'BitXor': ('operator', (), ()), 'BitAnd': ('operator', (), ()),
    'FloorDiv': ('operator', (), ()),
    'Invert': ('unaryop', (), ()), 'Not': ('unaryop', (), ()),
    'UAdd': ('unaryop', (), ()), 'USub': ('unaryop', (), ()),
    'Eq': ('cmpop', (), ()), 'NotEq': ('cmpop', (), ()),
    'Lt': ('cmpop', (), ()), 'LtE': ('cmpop', (), ()),
    'Gt': ('cmpop', (), ()), 'GtE': ('cmpop', (), ()),
    'Is': ('cmpop', (), ()), 'IsNot': ('cmpop', (), ()),
    'In': ('cmpop', (), ()), 'NotIn': ('cmpop', (), ()),
    # --- excepthandler ----------------------------------------------------
    'ExceptHandler': ('excepthandler', ('type', 'name', 'body'), None),
    # --- pattern ----------------------------------------------------------
    'MatchValue': ('pattern', ('value',), None),
    'MatchSingleton': ('pattern', ('value',), None),
    'MatchSequence': ('pattern', ('patterns',), None),
    'MatchMapping': ('pattern', ('keys', 'patterns', 'rest'), None),
    'MatchClass': ('pattern', ('cls', 'patterns', 'kwd_attrs', 'kwd_patterns'), None),
    'MatchStar': ('pattern', ('name',), None),
    'MatchAs': ('pattern', ('pattern', 'name'), None),
    'MatchOr': ('pattern', ('patterns',), None),
    # --- type_ignore / type_param ----------------------------------------
    'TypeIgnore': ('type_ignore', ('lineno', 'tag'), ()),
    'TypeVar': ('type_param', ('name', 'bound'), None),
    'ParamSpec': ('type_param', ('name',), None),
    'TypeVarTuple': ('type_param', ('name',), None),
}

# Attributes shared by the located node families. ``None`` in the table above
# means "inherit this family's standard attribute set".
_LOCATED = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')


# Optional fields (ASDL ``?`` markers): these carry a class-level default of
# ``None`` so that constructing a node without them leaves the attribute
# readable, and so that ``dump`` can omit them when unset -- matching CPython.
_OPTIONAL_FIELDS = {
    'AnnAssign': ('value',),
    'Assert': ('msg',),
    'Assign': ('type_comment',),
    'AsyncFor': ('type_comment',),
    'AsyncFunctionDef': ('returns', 'type_comment'),
    'AsyncWith': ('type_comment',),
    'Constant': ('kind',),
    'ExceptHandler': ('type', 'name'),
    'For': ('type_comment',),
    'FormattedValue': ('format_spec',),
    'FunctionDef': ('returns', 'type_comment'),
    'ImportFrom': ('module', 'level'),
    'MatchAs': ('pattern', 'name'),
    'MatchMapping': ('rest',),
    'MatchStar': ('name',),
    'Raise': ('exc', 'cause'),
    'Return': ('value',),
    'Slice': ('lower', 'upper', 'step'),
    'TypeVar': ('bound',),
    'With': ('type_comment',),
    'Yield': ('value',),
    'alias': ('asname',),
    'arg': ('annotation', 'type_comment'),
    'arguments': ('vararg', 'kwarg'),
    'keyword': ('arg',),
    'match_case': ('guard',),
    'withitem': ('optional_vars',),
}


def _build_nodes(namespace):
    """Create every node class from ``_NODE_SPEC`` into ``namespace``."""
    created = {'AST': AST}

    def make(name):
        if name in created:
            return created[name]
        base_name, fields, attributes = _NODE_SPEC[name]
        base = created.get(base_name) or make(base_name)
        if attributes is None:
            attributes = _LOCATED
        body = {'_fields': tuple(fields),
                '_attributes': tuple(attributes),
                '__module__': 'ast'}
        for opt in _OPTIONAL_FIELDS.get(name, ()):
            body[opt] = None
        cls = type(name, (base,), body)
        created[name] = cls
        namespace[name] = cls
        return cls

    for node_name in _NODE_SPEC:
        make(node_name)


_build_nodes(globals())


# ---------------------------------------------------------------------------
# Deprecated Constant compatibility shims (Num/Str/Bytes/NameConstant/Ellipsis)
# ---------------------------------------------------------------------------

# Expose ``Constant.n`` / ``Constant.s`` as aliases of ``.value`` (back-compat).
def _const_value_getter(self):
    return self.value


def _const_value_setter(self, value):
    self.value = value


Constant.n = property(_const_value_getter, _const_value_setter)  # noqa: F821
Constant.s = property(_const_value_getter, _const_value_setter)  # noqa: F821


class _ABC(type):
    """Metaclass making ``isinstance(Constant(x), Num)`` & friends work."""
    def __instancecheck__(cls, inst):
        if not isinstance(inst, Constant):  # noqa: F821
            return False
        if cls in _const_types:
            try:
                value = inst.value
            except AttributeError:
                return False
            return (isinstance(value, _const_types[cls]) and
                    not isinstance(value, _const_types_not.get(cls, ())))
        return type.__instancecheck__(cls, inst)


def _new(cls, *args, **kwargs):
    if cls in _const_types:
        return Constant(*args, **kwargs)  # noqa: F821
    return Constant.__new__(cls, *args, **kwargs)  # noqa: F821


class Num(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ('n',)
    __new__ = _new


class Str(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ('s',)
    __new__ = _new


class Bytes(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ('s',)
    __new__ = _new


class NameConstant(Constant, metaclass=_ABC):  # noqa: F821
    __new__ = _new


class Ellipsis(Constant, metaclass=_ABC):  # noqa: F821
    _fields = ()

    def __new__(cls, *args, **kwargs):
        if cls is Ellipsis:
            return Constant(..., *args, **kwargs)  # noqa: F821
        return Constant.__new__(cls, *args, **kwargs)  # noqa: F821


_const_types = {
    Num: (int, float, complex),
    Str: (str,),
    Bytes: (bytes,),
    NameConstant: (type(None), bool),
    Ellipsis: (type(...),),
}
_const_types_not = {
    Num: (bool,),
}

__all__ += ['Num', 'Str', 'Bytes', 'NameConstant', 'Ellipsis']


# ---------------------------------------------------------------------------
# Parsing — grammar delegated to the built-in compiler, then transcribed into
# the pure-Python node classes above so callers only ever see our objects.
# ---------------------------------------------------------------------------

# The C AST base class, obtained without importing ``_ast``: the MRO of any mod
# node is (Expression, mod, AST, object), so index -2 is the C ``AST`` base.
_C_AST_BASE = type(compile('0', '<pure_ast>', 'eval', PyCF_ONLY_AST)).__mro__[-2]


def _from_builtin(node):
    """Recursively rebuild a C AST node as the corresponding pure-Python node."""
    if isinstance(node, _C_AST_BASE):
        cls = globals().get(type(node).__name__)
        if cls is None:
            raise ValueError(f"unknown AST node type {type(node).__name__!r}")
        new = cls()
        for field in node._fields:
            try:
                value = getattr(node, field)
            except AttributeError:
                continue
            setattr(new, field, _from_builtin(value))
        for attr in node._attributes:
            try:
                setattr(new, attr, getattr(node, attr))
            except AttributeError:
                pass
        return new
    if isinstance(node, list):
        return [_from_builtin(item) for item in node]
    return node


def parse(source, filename='<unknown>', mode='exec', *,
          type_comments=False, feature_version=None):
    """Parse source into a pure-Python AST node (see module docstring)."""
    flags = PyCF_ONLY_AST
    if type_comments:
        flags |= PyCF_TYPE_COMMENTS
    if isinstance(feature_version, tuple):
        major, feature_minor = feature_version
        if major != 3:
            raise ValueError(f"Unsupported major version: {major}")
    elif feature_version is None:
        feature_minor = -1
    else:
        feature_minor = feature_version
    try:
        tree = compile(source, filename, mode, flags,
                       _feature_version=feature_minor)
    except TypeError:
        # Older/limited compile() without the private _feature_version kwarg.
        tree = compile(source, filename, mode, flags)
    return _from_builtin(tree)


# ---------------------------------------------------------------------------
# literal_eval
# ---------------------------------------------------------------------------

def literal_eval(node_or_string):
    """Safely evaluate an expression node or string of Python literals."""
    if isinstance(node_or_string, str):
        node_or_string = parse(node_or_string.lstrip(" \t"), mode='eval')
    if isinstance(node_or_string, Expression):  # noqa: F821
        node_or_string = node_or_string.body

    def _raise_malformed_node(node):
        msg = "malformed node or string"
        lno = getattr(node, 'lineno', None)
        if lno is not None:
            msg += f' on line {lno}'
        raise ValueError(msg + f': {node!r}')

    def _convert_num(node):
        if (not isinstance(node, Constant)  # noqa: F821
                or type(node.value) not in (int, float, complex)):
            _raise_malformed_node(node)
        return node.value

    def _convert_signed_num(node):
        if isinstance(node, UnaryOp) and isinstance(node.op, (UAdd, USub)):  # noqa: F821
            operand = _convert_num(node.operand)
            if isinstance(node.op, UAdd):  # noqa: F821
                return +operand
            return -operand
        return _convert_num(node)

    def _convert(node):
        if isinstance(node, Constant):  # noqa: F821
            return node.value
        if isinstance(node, Tuple):  # noqa: F821
            return tuple(map(_convert, node.elts))
        if isinstance(node, List):  # noqa: F821
            return list(map(_convert, node.elts))
        if isinstance(node, Set):  # noqa: F821
            return set(map(_convert, node.elts))
        if (isinstance(node, Call) and isinstance(node.func, Name) and  # noqa: F821
                node.func.id == 'set' and node.args == node.keywords == []):
            return set()
        if isinstance(node, Dict):  # noqa: F821
            if len(node.keys) != len(node.values):
                _raise_malformed_node(node)
            return dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        if isinstance(node, BinOp) and isinstance(node.op, (Add, Sub)):  # noqa: F821
            left = _convert_signed_num(node.left)
            right = _convert_num(node.right)
            if isinstance(left, (int, float)) and isinstance(right, complex):
                if isinstance(node.op, Add):  # noqa: F821
                    return left + right
                return left - right
        return _convert_signed_num(node)

    return _convert(node_or_string)


# ---------------------------------------------------------------------------
# Tree introspection helpers
# ---------------------------------------------------------------------------

def iter_fields(node):
    """Yield ``(fieldname, value)`` for each field present on *node*."""
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


def iter_child_nodes(node):
    """Yield all direct child nodes of *node*."""
    for _name, field in iter_fields(node):
        if isinstance(field, AST):
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, AST):
                    yield item


def walk(node):
    """Recursively yield all descendant nodes (including *node*)."""
    from collections import deque
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def get_docstring(node, clean=True):
    """Return the docstring of *node*, or ``None``."""
    if not isinstance(node, (AsyncFunctionDef, FunctionDef, ClassDef, Module)):  # noqa: F821
        raise TypeError("%r can't have docstrings" % node.__class__.__name__)
    if not (node.body and isinstance(node.body[0], Expr)):  # noqa: F821
        return None
    node = node.body[0].value
    if isinstance(node, Constant) and isinstance(node.value, str):  # noqa: F821
        text = node.value
    else:
        return None
    if clean:
        import inspect
        text = inspect.cleandoc(text)
    return text


def copy_location(new_node, old_node):
    """Copy source location attributes from *old_node* to *new_node*."""
    for attr in ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'):
        if attr in old_node._attributes and attr in new_node._attributes \
                and hasattr(old_node, attr):
            value = getattr(old_node, attr)
            if value is not None or (
                hasattr(new_node, attr) and getattr(new_node, attr) is None
            ):
                setattr(new_node, attr, value)
    return new_node


def fix_missing_locations(node):
    """Recursively fill in missing location attributes from the parent."""
    def _fix(node, lineno, col_offset, end_lineno, end_col_offset):
        if 'lineno' in node._attributes:
            if getattr(node, 'lineno', None) is None:
                node.lineno = lineno
            else:
                lineno = node.lineno
        if 'end_lineno' in node._attributes:
            if getattr(node, 'end_lineno', None) is None:
                node.end_lineno = end_lineno
            else:
                end_lineno = node.end_lineno
        if 'col_offset' in node._attributes:
            if getattr(node, 'col_offset', None) is None:
                node.col_offset = col_offset
            else:
                col_offset = node.col_offset
        if 'end_col_offset' in node._attributes:
            if getattr(node, 'end_col_offset', None) is None:
                node.end_col_offset = end_col_offset
            else:
                end_col_offset = node.end_col_offset
        for child in iter_child_nodes(node):
            _fix(child, lineno, col_offset, end_lineno, end_col_offset)
    _fix(node, 1, 0, 1, 0)
    return node


def increment_lineno(node, n=1):
    """Increment the line numbers of every node in *node* by *n*."""
    for child in walk(node):
        if 'lineno' in child._attributes:
            child.lineno = getattr(child, 'lineno', 0) + n
        if 'end_lineno' in child._attributes:
            end = getattr(child, 'end_lineno', None)
            if end is not None:
                child.end_lineno = end + n
    return node


# ---------------------------------------------------------------------------
# dump
# ---------------------------------------------------------------------------

def dump(node, annotate_fields=True, include_attributes=False, *, indent=None):
    """Return a formatted dump of the tree in *node* (mirrors ``ast.dump``)."""
    def _format(node, level=0):
        if indent is not None:
            level += 1
            prefix = '\n' + indent * level
            sep = ',\n' + indent * level
        else:
            prefix = ''
            sep = ', '
        if isinstance(node, AST):
            cls = type(node)
            args = []
            allsimple = True
            keywords = annotate_fields
            for name in node._fields:
                try:
                    value = getattr(node, name)
                except AttributeError:
                    keywords = True
                    continue
                if value is None and getattr(cls, name, ...) is None:
                    keywords = True
                    continue
                value, simple = _format(value, level)
                allsimple = allsimple and simple
                if keywords:
                    args.append('%s=%s' % (name, value))
                else:
                    args.append(value)
            if include_attributes and node._attributes:
                for name in node._attributes:
                    try:
                        value = getattr(node, name)
                    except AttributeError:
                        continue
                    if value is None and getattr(cls, name, ...) is None:
                        continue
                    value, simple = _format(value, level)
                    allsimple = allsimple and simple
                    args.append('%s=%s' % (name, value))
            if allsimple and len(args) <= 3:
                return '%s(%s)' % (node.__class__.__name__, ', '.join(args)), not args
            return '%s(%s%s)' % (node.__class__.__name__, prefix, sep.join(args)), False
        elif isinstance(node, list):
            if not node:
                return '[]', True
            return '[%s%s]' % (prefix, sep.join(_format(x, level)[0] for x in node)), False
        return repr(node), True

    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    if indent is not None and not isinstance(indent, str):
        indent = ' ' * indent
    return _format(node)[0]


# ---------------------------------------------------------------------------
# get_source_segment
# ---------------------------------------------------------------------------

def _splitlines_no_ff(source):
    """Split a string into lines ignoring form feed and other chars (\\n only)."""
    idx = 0
    lines = []
    next_line = ''
    while idx < len(source):
        c = source[idx]
        next_line += c
        idx += 1
        if c == '\r' and idx < len(source) and source[idx] == '\n':
            next_line += '\n'
            idx += 1
            lines.append(next_line)
            next_line = ''
        elif c in '\r\n':
            lines.append(next_line)
            next_line = ''
    if next_line:
        lines.append(next_line)
    return lines


def _pad_whitespace(source):
    r"""Replace all chars except '\f\t' in a line with spaces."""
    result = ''
    for c in source:
        if c in '\f\t':
            result += c
        else:
            result += ' '
    return result


def get_source_segment(source, node, *, padded=False):
    """Get the source segment of *source* that generated *node*."""
    try:
        if node.end_lineno is None or node.end_col_offset is None:
            return None
        lineno = node.lineno - 1
        end_lineno = node.end_lineno - 1
        col_offset = node.col_offset
        end_col_offset = node.end_col_offset
    except AttributeError:
        return None

    lines = _splitlines_no_ff(source)
    if end_lineno == lineno:
        return lines[lineno].encode()[col_offset:end_col_offset].decode()

    if padded:
        padding = _pad_whitespace(lines[lineno].encode()[:col_offset].decode())
    else:
        padding = ''

    first = padding + lines[lineno].encode()[col_offset:].decode()
    last = lines[end_lineno].encode()[:end_col_offset].decode()
    lines = lines[lineno + 1:end_lineno]

    lines.insert(0, first)
    lines.append(last)
    return ''.join(lines)


# ---------------------------------------------------------------------------
# Visitors
# ---------------------------------------------------------------------------

_const_node_type_names = {
    bool: 'NameConstant',
    type(None): 'NameConstant',
    int: 'Num',
    float: 'Num',
    complex: 'Num',
    str: 'Str',
    bytes: 'Bytes',
    type(...): 'Ellipsis',
}


class NodeVisitor:
    """Walk a tree, dispatching to ``visit_<Classname>`` methods."""

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for _field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)

    def visit_Constant(self, node):
        value = node.value
        type_name = _const_node_type_names.get(type(value))
        if type_name is None:
            for cls, name in _const_node_type_names.items():
                if isinstance(value, cls):
                    type_name = name
                    break
        if type_name is not None:
            method = 'visit_' + type_name
            try:
                visitor = getattr(self, method)
            except AttributeError:
                pass
            else:
                import warnings
                warnings.warn(f"{method} is deprecated; add visit_Constant",
                              DeprecationWarning, 2)
                return visitor(node)
        return self.generic_visit(node)


class NodeTransformer(NodeVisitor):
    """In-place AST transformer (mirrors ``ast.NodeTransformer``)."""

    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif not isinstance(value, AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


# ---------------------------------------------------------------------------
# unparse — AST back to source (port of CPython's _Unparser)
# ---------------------------------------------------------------------------

import enum as _enum
from contextlib import contextmanager as _contextmanager, nullcontext as _nullcontext

_SINGLE_QUOTES = ("'", '"')
_MULTI_QUOTES = ('"""', "'''")
_ALL_QUOTES = (*_SINGLE_QUOTES, *_MULTI_QUOTES)
_INFSTR = "1e" + repr(_sys.float_info.max_10_exp + 1)


class _Precedence(_enum.IntEnum):
    NAMED_EXPR = _enum.auto()   # <target> := <expr1>
    TUPLE = _enum.auto()        # <expr1>, <expr2>
    YIELD = _enum.auto()        # 'yield', 'yield from'
    TEST = _enum.auto()         # 'if'-'else', 'lambda'
    OR = _enum.auto()           # 'or'
    AND = _enum.auto()          # 'and'
    NOT = _enum.auto()          # 'not'
    CMP = _enum.auto()          # comparisons
    EXPR = _enum.auto()
    BOR = EXPR                  # '|'
    BXOR = _enum.auto()         # '^'
    BAND = _enum.auto()         # '&'
    SHIFT = _enum.auto()        # '<<', '>>'
    ARITH = _enum.auto()        # '+', '-'
    TERM = _enum.auto()         # '*', '@', '/', '%', '//'
    FACTOR = _enum.auto()       # unary '+', '-', '~'
    POWER = _enum.auto()        # '**'
    AWAIT = _enum.auto()        # 'await'
    ATOM = _enum.auto()

    def next(self):
        try:
            return self.__class__(self + 1)
        except ValueError:
            return self


class _Unparser(NodeVisitor):
    """Methods in this class recursively traverse an AST and output source."""

    def __init__(self, *, _avoid_backslashes=False):
        self._source = []
        self._precedences = {}
        self._type_ignores = {}
        self._indent = 0
        self._avoid_backslashes = _avoid_backslashes
        self._in_try_star = False

    def interleave(self, inter, f, seq):
        seq = iter(seq)
        try:
            f(next(seq))
        except StopIteration:
            pass
        else:
            for x in seq:
                inter()
                f(x)

    def items_view(self, traverser, items):
        if len(items) == 1:
            traverser(items[0])
            self.write(",")
        else:
            self.interleave(lambda: self.write(", "), traverser, items)

    def maybe_newline(self):
        if self._source:
            self.write("\n")

    def fill(self, text=""):
        self.maybe_newline()
        self.write("    " * self._indent + text)

    def write(self, *text):
        self._source.extend(text)

    @_contextmanager
    def buffered(self, buffer=None):
        if buffer is None:
            buffer = []
        original_source = self._source
        self._source = buffer
        yield buffer
        self._source = original_source

    @_contextmanager
    def block(self, *, extra=None):
        self.write(":")
        if extra:
            self.write(extra)
        self._indent += 1
        yield
        self._indent -= 1

    @_contextmanager
    def delimit(self, start, end):
        self.write(start)
        yield
        self.write(end)

    def delimit_if(self, start, end, condition):
        if condition:
            return self.delimit(start, end)
        return _nullcontext()

    def require_parens(self, precedence, node):
        return self.delimit_if("(", ")", self.get_precedence(node) > precedence)

    def get_precedence(self, node):
        return self._precedences.get(node, _Precedence.TEST)

    def set_precedence(self, precedence, *nodes):
        for node in nodes:
            self._precedences[node] = precedence

    def get_raw_docstring(self, node):
        if not isinstance(node, (AsyncFunctionDef, FunctionDef, ClassDef, Module)) \
                or len(node.body) < 1:
            return None
        node = node.body[0]
        if not isinstance(node, Expr):
            return None
        node = node.value
        if isinstance(node, Constant) and isinstance(node.value, str):
            return node
        return None

    def get_type_comment(self, node):
        comment = self._type_ignores.get(getattr(node, "lineno", None)) \
            or getattr(node, "type_comment", None)
        if comment is not None:
            return f" # type: {comment}"
        return None

    def traverse(self, node):
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
        else:
            super().visit(node)

    def visit(self, node):
        self._source = []
        self.traverse(node)
        return "".join(self._source)

    def _write_docstring_and_traverse_body(self, node):
        docstring = self.get_raw_docstring(node)
        if docstring:
            self._write_docstring(docstring)
            self.traverse(node.body[1:])
        else:
            self.traverse(node.body)

    def visit_Module(self, node):
        self._type_ignores = {
            ignore.lineno: f"ignore{ignore.tag}"
            for ignore in node.type_ignores
        }
        self._write_docstring_and_traverse_body(node)
        self._type_ignores.clear()

    def visit_FunctionType(self, node):
        with self.delimit("(", ")"):
            self.interleave(lambda: self.write(", "), self.traverse, node.argtypes)
        self.write(" -> ")
        self.traverse(node.returns)

    def visit_Expr(self, node):
        self.fill()
        self.set_precedence(_Precedence.YIELD, node.value)
        self.traverse(node.value)

    def visit_NamedExpr(self, node):
        with self.require_parens(_Precedence.NAMED_EXPR, node):
            self.set_precedence(_Precedence.ATOM, node.target, node.value)
            self.traverse(node.target)
            self.write(" := ")
            self.traverse(node.value)

    def visit_Import(self, node):
        self.fill("import ")
        self.interleave(lambda: self.write(", "), self.traverse, node.names)

    def visit_ImportFrom(self, node):
        self.fill("from ")
        self.write("." * (node.level or 0))
        if node.module:
            self.write(node.module)
        self.write(" import ")
        self.interleave(lambda: self.write(", "), self.traverse, node.names)

    def visit_Assign(self, node):
        self.fill()
        for target in node.targets:
            self.set_precedence(_Precedence.TUPLE, target)
            self.traverse(target)
            self.write(" = ")
        self.traverse(node.value)
        type_comment = self.get_type_comment(node)
        if type_comment:
            self.write(type_comment)

    def visit_AugAssign(self, node):
        self.fill()
        self.traverse(node.target)
        self.write(" " + self.binop[node.op.__class__.__name__] + "= ")
        self.traverse(node.value)

    def visit_AnnAssign(self, node):
        self.fill()
        with self.delimit_if(
            "(", ")", not node.simple and isinstance(node.target, Name)
        ):
            self.traverse(node.target)
        self.write(": ")
        self.traverse(node.annotation)
        if node.value:
            self.write(" = ")
            self.traverse(node.value)

    def visit_Return(self, node):
        self.fill("return")
        if node.value:
            self.write(" ")
            self.traverse(node.value)

    def visit_Pass(self, node):
        self.fill("pass")

    def visit_Break(self, node):
        self.fill("break")

    def visit_Continue(self, node):
        self.fill("continue")

    def visit_Delete(self, node):
        self.fill("del ")
        self.interleave(lambda: self.write(", "), self.traverse, node.targets)

    def visit_Assert(self, node):
        self.fill("assert ")
        self.traverse(node.test)
        if node.msg:
            self.write(", ")
            self.traverse(node.msg)

    def visit_Global(self, node):
        self.fill("global ")
        self.interleave(lambda: self.write(", "), self.write, node.names)

    def visit_Nonlocal(self, node):
        self.fill("nonlocal ")
        self.interleave(lambda: self.write(", "), self.write, node.names)

    def visit_Await(self, node):
        with self.require_parens(_Precedence.AWAIT, node):
            self.write("await")
            if node.value:
                self.write(" ")
                self.set_precedence(_Precedence.ATOM, node.value)
                self.traverse(node.value)

    def visit_Yield(self, node):
        with self.require_parens(_Precedence.YIELD, node):
            self.write("yield")
            if node.value:
                self.write(" ")
                self.set_precedence(_Precedence.ATOM, node.value)
                self.traverse(node.value)

    def visit_YieldFrom(self, node):
        with self.require_parens(_Precedence.YIELD, node):
            self.write("yield from ")
            if not node.value:
                raise ValueError("Node can't be used without a value attribute.")
            self.set_precedence(_Precedence.ATOM, node.value)
            self.traverse(node.value)

    def visit_Raise(self, node):
        self.fill("raise")
        if not node.exc:
            if node.cause:
                raise ValueError("Node can't use cause without an exception.")
            return
        self.write(" ")
        self.traverse(node.exc)
        if node.cause:
            self.write(" from ")
            self.traverse(node.cause)

    def do_visit_try(self, node):
        self.fill("try")
        with self.block():
            self.traverse(node.body)
        for ex in node.handlers:
            self.traverse(ex)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)
        if node.finalbody:
            self.fill("finally")
            with self.block():
                self.traverse(node.finalbody)

    def visit_Try(self, node):
        prev_in_try_star = self._in_try_star
        try:
            self._in_try_star = False
            self.do_visit_try(node)
        finally:
            self._in_try_star = prev_in_try_star

    def visit_TryStar(self, node):
        prev_in_try_star = self._in_try_star
        try:
            self._in_try_star = True
            self.do_visit_try(node)
        finally:
            self._in_try_star = prev_in_try_star

    def visit_ExceptHandler(self, node):
        self.fill("except*" if self._in_try_star else "except")
        if node.type:
            self.write(" ")
            self.traverse(node.type)
        if node.name:
            self.write(" as ")
            self.write(node.name)
        with self.block():
            self.traverse(node.body)

    def visit_ClassDef(self, node):
        self.maybe_newline()
        for deco in node.decorator_list:
            self.fill("@")
            self.traverse(deco)
        self.fill("class " + node.name)
        self._type_params_helper(node.type_params)
        with self.delimit_if("(", ")", condition=node.bases or node.keywords):
            comma = False
            for e in node.bases:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
            for e in node.keywords:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
        with self.block():
            self._write_docstring_and_traverse_body(node)

    def visit_FunctionDef(self, node):
        self._function_helper(node, "def")

    def visit_AsyncFunctionDef(self, node):
        self._function_helper(node, "async def")

    def _function_helper(self, node, fill_suffix):
        self.maybe_newline()
        for deco in node.decorator_list:
            self.fill("@")
            self.traverse(deco)
        def_str = fill_suffix + " " + node.name
        self.fill(def_str)
        self._type_params_helper(node.type_params)
        with self.delimit("(", ")"):
            self.traverse(node.args)
        if node.returns:
            self.write(" -> ")
            self.traverse(node.returns)
        with self.block(extra=self.get_type_comment(node)):
            self._write_docstring_and_traverse_body(node)

    def _type_params_helper(self, type_params):
        if type_params is not None and len(type_params) > 0:
            with self.delimit("[", "]"):
                self.interleave(lambda: self.write(", "), self.traverse, type_params)

    def visit_TypeVar(self, node):
        self.write(node.name)
        if node.bound:
            self.write(": ")
            self.traverse(node.bound)

    def visit_TypeVarTuple(self, node):
        self.write("*" + node.name)

    def visit_ParamSpec(self, node):
        self.write("**" + node.name)

    def visit_TypeAlias(self, node):
        self.fill("type ")
        self.traverse(node.name)
        self._type_params_helper(node.type_params)
        self.write(" = ")
        self.traverse(node.value)

    def visit_For(self, node):
        self._for_helper("for ", node)

    def visit_AsyncFor(self, node):
        self._for_helper("async for ", node)

    def _for_helper(self, fill, node):
        self.fill(fill)
        self.set_precedence(_Precedence.TUPLE, node.target)
        self.traverse(node.target)
        self.write(" in ")
        self.traverse(node.iter)
        with self.block(extra=self.get_type_comment(node)):
            self.traverse(node.body)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

    def visit_If(self, node):
        self.fill("if ")
        self.traverse(node.test)
        with self.block():
            self.traverse(node.body)
        while node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], If):
            node = node.orelse[0]
            self.fill("elif ")
            self.traverse(node.test)
            with self.block():
                self.traverse(node.body)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

    def visit_While(self, node):
        self.fill("while ")
        self.traverse(node.test)
        with self.block():
            self.traverse(node.body)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

    def visit_With(self, node):
        self.fill("with ")
        self.interleave(lambda: self.write(", "), self.traverse, node.items)
        with self.block(extra=self.get_type_comment(node)):
            self.traverse(node.body)

    def visit_AsyncWith(self, node):
        self.fill("async with ")
        self.interleave(lambda: self.write(", "), self.traverse, node.items)
        with self.block(extra=self.get_type_comment(node)):
            self.traverse(node.body)

    def _write_docstring(self, node):
        self.fill()
        if node.kind == "u":
            self.write("u")
        self._write_str_avoiding_backslashes(node.value, quote_types=_MULTI_QUOTES)

    def _write_constant(self, value):
        if isinstance(value, (float, complex)):
            # Substitute overflowing decimal literal for AST infinities,
            # and inf - inf for NaNs.
            self.write(
                repr(value)
                .replace("inf", _INFSTR)
                .replace("nan", f"({_INFSTR}-{_INFSTR})")
            )
        elif self._avoid_backslashes and isinstance(value, str):
            self._write_str_avoiding_backslashes(value)
        else:
            self.write(repr(value))

    def visit_Constant(self, node):
        value = node.value
        if isinstance(value, tuple):
            with self.delimit("(", ")"):
                self.items_view(self._write_constant, value)
        elif value is ...:
            self.write("...")
        else:
            if node.kind == "u":
                self.write("u")
            self._write_constant(node.value)

    def visit_List(self, node):
        with self.delimit("[", "]"):
            self.interleave(lambda: self.write(", "), self.traverse, node.elts)

    def visit_ListComp(self, node):
        with self.delimit("[", "]"):
            self.traverse(node.elt)
            for gen in node.generators:
                self.traverse(gen)

    def visit_GeneratorExp(self, node):
        with self.delimit("(", ")"):
            self.traverse(node.elt)
            for gen in node.generators:
                self.traverse(gen)

    def visit_SetComp(self, node):
        with self.delimit("{", "}"):
            self.traverse(node.elt)
            for gen in node.generators:
                self.traverse(gen)

    def visit_DictComp(self, node):
        with self.delimit("{", "}"):
            self.traverse(node.key)
            self.write(": ")
            self.traverse(node.value)
            for gen in node.generators:
                self.traverse(gen)

    def visit_comprehension(self, node):
        if node.is_async:
            self.write(" async for ")
        else:
            self.write(" for ")
        self.set_precedence(_Precedence.TUPLE, node.target)
        self.traverse(node.target)
        self.write(" in ")
        self.set_precedence(_Precedence.TEST.next(), node.iter, *node.ifs)
        self.traverse(node.iter)
        for if_clause in node.ifs:
            self.write(" if ")
            self.traverse(if_clause)

    def visit_IfExp(self, node):
        with self.require_parens(_Precedence.TEST, node):
            self.set_precedence(_Precedence.TEST.next(), node.body, node.test)
            self.traverse(node.body)
            self.write(" if ")
            self.traverse(node.test)
            self.write(" else ")
            self.set_precedence(_Precedence.TEST, node.orelse)
            self.traverse(node.orelse)

    def visit_Set(self, node):
        if node.elts:
            with self.delimit("{", "}"):
                self.interleave(lambda: self.write(", "), self.traverse, node.elts)
        else:
            # `{}` would be interpreted as a dictionary literal, and
            # `set` might be shadowed. Thus:
            self.write("{*()}")

    def visit_Dict(self, node):
        def write_key_value_pair(k, v):
            self.traverse(k)
            self.write(": ")
            self.traverse(v)

        def write_item(item):
            k, v = item
            if k is None:
                # for dictionary unpacking operator in dicts {**{'y': 2}}
                # see PEP 448 for details
                self.write("**")
                self.set_precedence(_Precedence.EXPR, v)
                self.traverse(v)
            else:
                write_key_value_pair(k, v)

        with self.delimit("{", "}"):
            self.interleave(
                lambda: self.write(", "), write_item, zip(node.keys, node.values)
            )

    def visit_Tuple(self, node):
        with self.delimit_if(
            "(",
            ")",
            len(node.elts) == 0 or self.get_precedence(node) > _Precedence.TUPLE,
        ):
            self.items_view(self.traverse, node.elts)

    unop = {"Invert": "~", "Not": "not", "UAdd": "+", "USub": "-"}
    unop_precedence = {
        "not": _Precedence.NOT,
        "~": _Precedence.FACTOR,
        "+": _Precedence.FACTOR,
        "-": _Precedence.FACTOR,
    }

    def visit_UnaryOp(self, node):
        operator = self.unop[node.op.__class__.__name__]
        operator_precedence = self.unop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            self.write(operator)
            # factor prefixes (+, -, ~) shouldn't be separated
            # from the value they belong, (e.g: +1 instead of + 1)
            if operator_precedence is not _Precedence.FACTOR:
                self.write(" ")
            self.set_precedence(operator_precedence, node.operand)
            self.traverse(node.operand)

    binop = {
        "Add": "+",
        "Sub": "-",
        "Mult": "*",
        "MatMult": "@",
        "Div": "/",
        "Mod": "%",
        "LShift": "<<",
        "RShift": ">>",
        "BitOr": "|",
        "BitXor": "^",
        "BitAnd": "&",
        "FloorDiv": "//",
        "Pow": "**",
    }

    binop_precedence = {
        "+": _Precedence.ARITH,
        "-": _Precedence.ARITH,
        "*": _Precedence.TERM,
        "@": _Precedence.TERM,
        "/": _Precedence.TERM,
        "%": _Precedence.TERM,
        "<<": _Precedence.SHIFT,
        ">>": _Precedence.SHIFT,
        "|": _Precedence.BOR,
        "^": _Precedence.BXOR,
        "&": _Precedence.BAND,
        "//": _Precedence.TERM,
        "**": _Precedence.POWER,
    }

    binop_rassoc = frozenset(("**",))

    def visit_BinOp(self, node):
        operator = self.binop[node.op.__class__.__name__]
        operator_precedence = self.binop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            if operator in self.binop_rassoc:
                left_precedence = operator_precedence.next()
                right_precedence = operator_precedence
            else:
                left_precedence = operator_precedence
                right_precedence = operator_precedence.next()

            self.set_precedence(left_precedence, node.left)
            self.traverse(node.left)
            self.write(f" {operator} ")
            self.set_precedence(right_precedence, node.right)
            self.traverse(node.right)

    cmpops = {
        "Eq": "==",
        "NotEq": "!=",
        "Lt": "<",
        "LtE": "<=",
        "Gt": ">",
        "GtE": ">=",
        "Is": "is",
        "IsNot": "is not",
        "In": "in",
        "NotIn": "not in",
    }

    def visit_Compare(self, node):
        with self.require_parens(_Precedence.CMP, node):
            self.set_precedence(_Precedence.CMP.next(), node.left, *node.comparators)
            self.traverse(node.left)
            for o, e in zip(node.ops, node.comparators):
                self.write(" " + self.cmpops[o.__class__.__name__] + " ")
                self.traverse(e)

    boolops = {"And": "and", "Or": "or"}
    boolop_precedence = {"and": _Precedence.AND, "or": _Precedence.OR}

    def visit_BoolOp(self, node):
        operator = self.boolops[node.op.__class__.__name__]
        operator_precedence = self.boolop_precedence[operator]

        def increasing_level_traverse(node):
            nonlocal operator_precedence
            operator_precedence = operator_precedence.next()
            self.set_precedence(operator_precedence, node)
            self.traverse(node)

        with self.require_parens(operator_precedence, node):
            s = f" {operator} "
            self.interleave(lambda: self.write(s), increasing_level_traverse, node.values)

    def visit_Attribute(self, node):
        self.set_precedence(_Precedence.ATOM, node.value)
        self.traverse(node.value)
        # Special case: 3.__abs__() is a syntax error, so if node.value
        # is an integer literal then we need to either parenthesize
        # it or add an extra space to get 3 .__abs__().
        if isinstance(node.value, Constant) and isinstance(node.value.value, int):
            self.write(" ")
        self.write(".")
        self.write(node.attr)

    def visit_Call(self, node):
        self.set_precedence(_Precedence.ATOM, node.func)
        self.traverse(node.func)
        with self.delimit("(", ")"):
            comma = False
            for e in node.args:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
            for e in node.keywords:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)

    def visit_Subscript(self, node):
        def is_non_empty_tuple(slice_value):
            return isinstance(slice_value, Tuple) and slice_value.elts

        self.set_precedence(_Precedence.ATOM, node.value)
        self.traverse(node.value)
        with self.delimit("[", "]"):
            if is_non_empty_tuple(node.slice):
                # parentheses can be omitted if the tuple isn't empty
                self.items_view(self.traverse, node.slice.elts)
            else:
                self.traverse(node.slice)

    def visit_Starred(self, node):
        self.write("*")
        self.set_precedence(_Precedence.EXPR, node.value)
        self.traverse(node.value)

    def visit_Ellipsis(self, node):
        self.write("...")

    def visit_Slice(self, node):
        if node.lower:
            self.traverse(node.lower)
        self.write(":")
        if node.upper:
            self.traverse(node.upper)
        if node.step:
            self.write(":")
            self.traverse(node.step)

    def visit_Name(self, node):
        self.write(node.id)

    def visit_arg(self, node):
        self.write(node.arg)
        if node.annotation:
            self.write(": ")
            self.traverse(node.annotation)

    def visit_arguments(self, node):
        first = True
        # normal arguments
        all_args = node.posonlyargs + node.args
        defaults = [None] * (len(all_args) - len(node.defaults)) + node.defaults
        for index, elements in enumerate(zip(all_args, defaults), 1):
            a, d = elements
            if first:
                first = False
            else:
                self.write(", ")
            self.traverse(a)
            if d:
                self.write("=")
                self.traverse(d)
            if index == len(node.posonlyargs):
                self.write(", /")

        # varargs, or bare '*' if no varargs but keyword-only arguments present
        if node.vararg or node.kwonlyargs:
            if first:
                first = False
            else:
                self.write(", ")
            self.write("*")
            if node.vararg:
                self.write(node.vararg.arg)
                if node.vararg.annotation:
                    self.write(": ")
                    self.traverse(node.vararg.annotation)

        # keyword-only arguments
        if node.kwonlyargs:
            for a, d in zip(node.kwonlyargs, node.kw_defaults):
                self.write(", ")
                self.traverse(a)
                if d:
                    self.write("=")
                    self.traverse(d)

        # kwargs
        if node.kwarg:
            if first:
                first = False
            else:
                self.write(", ")
            self.write("**" + node.kwarg.arg)
            if node.kwarg.annotation:
                self.write(": ")
                self.traverse(node.kwarg.annotation)

    def visit_keyword(self, node):
        if node.arg is None:
            self.write("**")
        else:
            self.write(node.arg)
            self.write("=")
        self.traverse(node.value)

    def visit_Lambda(self, node):
        with self.require_parens(_Precedence.TEST, node):
            self.write("lambda")
            with self.buffered() as buffer:
                self.traverse(node.args)
            if buffer:
                self.write(" ", *buffer)
            self.write(": ")
            self.set_precedence(_Precedence.TEST, node.body)
            self.traverse(node.body)

    def visit_alias(self, node):
        self.write(node.name)
        if node.asname:
            self.write(" as " + node.asname)

    def visit_withitem(self, node):
        self.traverse(node.context_expr)
        if node.optional_vars:
            self.write(" as ")
            self.traverse(node.optional_vars)

    # ---- f-string / string-literal helpers -------------------------------

    def _str_literal_helper(
        self, string, *, quote_types=_ALL_QUOTES, escape_special_whitespace=False
    ):
        """Helper for writing string literals, minimizing escapes.

        Returns the tuple (string literal to write, possible quote types).
        """

        def escape_char(c):
            # \n and \t are non-printable, but we only escape them if
            # escape_special_whitespace is True
            if not escape_special_whitespace and c in "\n\t":
                return c
            # Always escape backslashes and other non-printable characters
            if c == "\\" or not c.isprintable():
                return c.encode("unicode_escape").decode("ascii")
            return c

        escaped_string = "".join(map(escape_char, string))
        possible_quotes = quote_types
        if "\n" in escaped_string:
            possible_quotes = [q for q in possible_quotes if q in _MULTI_QUOTES]
        possible_quotes = [q for q in possible_quotes if q not in escaped_string]
        if not possible_quotes:
            # If there aren't any possible_quotes, fallback to using repr
            # on the original string. Try to use a quote we can use later.
            string = repr(string)
            quote = next((q for q in quote_types if string[0] in q), string[0])
            return string[1:-1], [quote]
        if escaped_string:
            # Sort so that we prefer '''"''' over """\""""
            possible_quotes.sort(key=lambda q: q[0] == escaped_string[-1])
            # If we're using triple quotes and we'd need to escape a final
            # quote, escape it
            if possible_quotes[0][0] == escaped_string[-1]:
                assert len(possible_quotes[0]) == 3
                escaped_string = escaped_string[:-1] + "\\" + escaped_string[-1]
        return escaped_string, possible_quotes

    def _write_str_avoiding_backslashes(self, string, *, quote_types=_ALL_QUOTES):
        """Write string literal value with a best effort attempt to avoid backslashes."""
        string, quote_types = self._str_literal_helper(string, quote_types=quote_types)
        quote_type = quote_types[0]
        self.write(f"{quote_type}{string}{quote_type}")

    def visit_JoinedStr(self, node):
        self.write("f")
        if self._avoid_backslashes:
            with self.buffered() as buffer:
                self._write_fstring_inner(node)
            return self._write_str_avoiding_backslashes("".join(buffer))

        # If we don't need to avoid backslashes globally (i.e., we only need
        # to avoid them inside FormattedValues), it's cosmetically preferred
        # to use escaped whitespace. That is, it's preferred to use backslashes
        # for cases like: f"{x}\n". To accomplish this, we keep track of what
        # in our buffer corresponds to FormattedValues and what corresponds to
        # Constant parts of the f-string, and allow escapes accordingly.
        buffer = []
        for value in node.values:
            meth = getattr(self, "_fstring_" + type(value).__name__)
            with self.buffered() as buf:
                meth(value)
            buffer.append(("".join(buf), isinstance(value, Constant)))
        new_buffer = []
        quote_types = _ALL_QUOTES
        for value, is_constant in buffer:
            # Repeatedly narrow down the list of possible quote_types
            value, quote_types = self._str_literal_helper(
                value,
                quote_types=quote_types,
                escape_special_whitespace=is_constant,
            )
            new_buffer.append(value)
        value = "".join(new_buffer)
        quote_type = quote_types[0]
        self.write(f"{quote_type}{value}{quote_type}")

    def _write_fstring_inner(self, node):
        if isinstance(node, JoinedStr):
            # for both the f-string itself, and format_spec
            for value in node.values:
                self._write_fstring_inner(value)
        elif isinstance(node, Constant) and isinstance(node.value, str):
            value = node.value.replace("{", "{{").replace("}", "}}")
            self.write(value)
        elif isinstance(node, FormattedValue):
            self.visit_FormattedValue(node)
        else:
            raise ValueError(f"Unexpected node inside JoinedStr, {node!r}")

    def _fstring_JoinedStr(self, node):
        self._write_fstring_inner(node)

    def _fstring_Constant(self, node):
        self._write_fstring_inner(node)

    def _fstring_FormattedValue(self, node):
        self.visit_FormattedValue(node)

    def visit_FormattedValue(self, node):
        def unparse_inner(inner):
            unparser = type(self)(_avoid_backslashes=True)
            unparser.set_precedence(_Precedence.TEST.next(), inner)
            return unparser.visit(inner)

        with self.delimit("{", "}"):
            expr = unparse_inner(node.value)
            if expr.startswith("{"):
                # Separate pair of opening brackets as "{ {"
                self.write(" ")
            self.write(expr)
            if node.conversion != -1:
                self.write(f"!{chr(node.conversion)}")
            if node.format_spec:
                self.write(":")
                self._write_fstring_inner(node.format_spec)

    # ---- match statement -------------------------------------------------

    def visit_Match(self, node):
        self.fill("match ")
        self.traverse(node.subject)
        with self.block():
            for case in node.cases:
                self.traverse(case)

    def visit_match_case(self, node):
        self.fill("case ")
        self.traverse(node.pattern)
        if node.guard:
            self.write(" if ")
            self.traverse(node.guard)
        with self.block():
            self.traverse(node.body)

    def visit_MatchValue(self, node):
        self.traverse(node.value)

    def visit_MatchSingleton(self, node):
        self._write_constant(node.value)

    def visit_MatchSequence(self, node):
        with self.delimit("[", "]"):
            self.interleave(
                lambda: self.write(", "), self.traverse, node.patterns
            )

    def visit_MatchStar(self, node):
        name = node.name
        if name is None:
            name = "_"
        self.write(f"*{name}")

    def visit_MatchMapping(self, node):
        def write_key_pattern_pair(pair):
            k, p = pair
            self.traverse(k)
            self.write(": ")
            self.traverse(p)

        with self.delimit("{", "}"):
            keys = node.keys
            self.interleave(
                lambda: self.write(", "),
                write_key_pattern_pair,
                zip(keys, node.patterns, strict=True),
            )
            rest = node.rest
            if rest is not None:
                if keys:
                    self.write(", ")
                self.write(f"**{rest}")

    def visit_MatchClass(self, node):
        self.set_precedence(_Precedence.ATOM, node.cls)
        self.traverse(node.cls)
        with self.delimit("(", ")"):
            patterns = node.patterns
            self.interleave(
                lambda: self.write(", "), self.traverse, patterns
            )
            attrs = node.kwd_attrs
            if attrs:
                def write_attr_pattern(pair):
                    attr, pattern = pair
                    self.write(f"{attr}=")
                    self.traverse(pattern)

                if patterns:
                    self.write(", ")
                self.interleave(
                    lambda: self.write(", "),
                    write_attr_pattern,
                    zip(attrs, node.kwd_patterns, strict=True),
                )

    def visit_MatchAs(self, node):
        name = node.name
        pattern = node.pattern
        if name is None:
            self.write("_")
        elif pattern is None:
            self.write(node.name)
        else:
            with self.require_parens(_Precedence.TEST, node):
                self.set_precedence(_Precedence.BOR, node.pattern)
                self.traverse(node.pattern)
                self.write(f" as {node.name}")

    def visit_MatchOr(self, node):
        with self.require_parens(_Precedence.BOR, node):
            self.set_precedence(_Precedence.BOR.next(), *node.patterns)
            self.interleave(lambda: self.write(" | "), self.traverse, node.patterns)


def unparse(ast_obj):
    unparser = _Unparser()
    return unparser.visit(ast_obj)


def main(args=None):
    import argparse

    parser = argparse.ArgumentParser(prog="python -m ast")
    parser.add_argument(
        "infile",
        nargs="?",
        default="-",
        help="the file to parse; defaults to stdin",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="exec",
        choices=("exec", "single", "eval", "func_type"),
        help="specify what kind of code must be parsed",
    )
    parser.add_argument(
        "--no-type-comments",
        default=True,
        action="store_false",
        help="don't add information about type comments",
    )
    parser.add_argument(
        "-a",
        "--include-attributes",
        action="store_true",
        help="include attributes such as line numbers and column offsets",
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=int,
        default=3,
        help="indentation of nodes (number of spaces)",
    )
    args = parser.parse_args(args)

    if args.infile == "-":
        name = "<stdin>"
        source = _sys.stdin.buffer.read()
    else:
        name = args.infile
        with open(args.infile, "rb") as infile:
            source = infile.read()
    tree = parse(source, name, args.mode, type_comments=args.no_type_comments)
    print(dump(tree, include_attributes=args.include_attributes, indent=args.indent))


if __name__ == "__main__":
    main()
