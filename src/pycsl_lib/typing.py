"""PyCSL mock for Python's typing module.

Comprehensive trusted stubs covering the full typing module API.
Type aliases and special forms are modelled as identity functions.
Constructors (TypeVar, NamedTuple, etc.) return opaque ints (>= 0).
Decorators are identity passthroughs.  Functions like cast() and
reveal_type() preserve their semantically meaningful argument.

Classes used only for isinstance()/subclassing (Protocol, SupportsInt,
etc.) are omitted — they cannot be meaningfully mocked as functions.
"""
_ = 0  # anchor

# =========================================================================
# Type aliases to built-in types (identity)
# =========================================================================

#@ ensures \result == x
def List(x: int) -> int:
    """Mock: List type alias — identity."""
    return x

#@ ensures \result == x
def Dict(x: int) -> int:
    """Mock: Dict type alias — identity."""
    return x

#@ ensures \result == x
def Tuple(x: int) -> int:
    """Mock: Tuple type alias — identity."""
    return x

#@ ensures \result == x
def Set(x: int) -> int:
    """Mock: Set type alias — identity."""
    return x

#@ ensures \result == x
def FrozenSet(x: int) -> int:
    """Mock: FrozenSet type alias — identity."""
    return x

#@ ensures \result == x
def Type_(x: int) -> int:
    """Mock: Type type alias — identity."""
    return x

# =========================================================================
# Type aliases to collections types (identity)
# =========================================================================

#@ ensures \result == x
def Deque(x: int) -> int:
    """Mock: Deque type alias — identity."""
    return x

#@ ensures \result == x
def DefaultDict(x: int) -> int:
    """Mock: DefaultDict type alias — identity."""
    return x

#@ ensures \result == x
def OrderedDict(x: int) -> int:
    """Mock: OrderedDict type alias — identity."""
    return x

#@ ensures \result == x
def Counter(x: int) -> int:
    """Mock: Counter type alias — identity."""
    return x

#@ ensures \result == x
def ChainMap(x: int) -> int:
    """Mock: ChainMap type alias — identity."""
    return x

# =========================================================================
# Type aliases to collections.abc (identity)
# =========================================================================

#@ ensures \result == x
def Sequence(x: int) -> int:
    """Mock: Sequence type alias — identity."""
    return x

#@ ensures \result == x
def MutableSequence(x: int) -> int:
    """Mock: MutableSequence type alias — identity."""
    return x

#@ ensures \result == x
def MutableSet(x: int) -> int:
    """Mock: MutableSet type alias — identity."""
    return x

#@ ensures \result == x
def AbstractSet(x: int) -> int:
    """Mock: AbstractSet type alias — identity."""
    return x

#@ ensures \result == x
def Mapping(x: int) -> int:
    """Mock: Mapping type alias — identity."""
    return x

#@ ensures \result == x
def MutableMapping(x: int) -> int:
    """Mock: MutableMapping type alias — identity."""
    return x

#@ ensures \result == x
def MappingView(x: int) -> int:
    """Mock: MappingView type alias — identity."""
    return x

#@ ensures \result == x
def ItemsView(x: int) -> int:
    """Mock: ItemsView type alias — identity."""
    return x

#@ ensures \result == x
def KeysView(x: int) -> int:
    """Mock: KeysView type alias — identity."""
    return x

#@ ensures \result == x
def ValuesView(x: int) -> int:
    """Mock: ValuesView type alias — identity."""
    return x

#@ ensures \result == x
def Iterable(x: int) -> int:
    """Mock: Iterable type alias — identity."""
    return x

#@ ensures \result == x
def Iterator(x: int) -> int:
    """Mock: Iterator type alias — identity."""
    return x

#@ ensures \result == x
def Generator(x: int) -> int:
    """Mock: Generator type alias — identity."""
    return x

#@ ensures \result == x
def Reversible(x: int) -> int:
    """Mock: Reversible type alias — identity."""
    return x

#@ ensures \result == x
def Callable(x: int) -> int:
    """Mock: Callable type alias — identity."""
    return x

#@ ensures \result == x
def Collection(x: int) -> int:
    """Mock: Collection type alias — identity."""
    return x

#@ ensures \result == x
def Container(x: int) -> int:
    """Mock: Container type alias — identity."""
    return x

#@ ensures \result == x
def Hashable(x: int) -> int:
    """Mock: Hashable type alias — identity."""
    return x

#@ ensures \result == x
def Sized(x: int) -> int:
    """Mock: Sized type alias — identity."""
    return x

#@ ensures \result == x
def ByteString(x: int) -> int:
    """Mock: ByteString type alias — identity."""
    return x

# =========================================================================
# Async type aliases (identity)
# =========================================================================

#@ ensures \result == x
def Coroutine(x: int) -> int:
    """Mock: Coroutine type alias — identity."""
    return x

#@ ensures \result == x
def AsyncGenerator(x: int) -> int:
    """Mock: AsyncGenerator type alias — identity."""
    return x

#@ ensures \result == x
def AsyncIterator(x: int) -> int:
    """Mock: AsyncIterator type alias — identity."""
    return x

#@ ensures \result == x
def AsyncIterable(x: int) -> int:
    """Mock: AsyncIterable type alias — identity."""
    return x

#@ ensures \result == x
def Awaitable(x: int) -> int:
    """Mock: Awaitable type alias — identity."""
    return x

# =========================================================================
# Context manager aliases (identity)
# =========================================================================

#@ ensures \result == x
def ContextManager(x: int) -> int:
    """Mock: ContextManager type alias — identity."""
    return x

#@ ensures \result == x
def AsyncContextManager(x: int) -> int:
    """Mock: AsyncContextManager type alias — identity."""
    return x

# =========================================================================
# Regex and I/O aliases (identity)
# =========================================================================

#@ ensures \result == x
def Pattern(x: int) -> int:
    """Mock: Pattern type alias — identity."""
    return x

#@ ensures \result == x
def Match_(x: int) -> int:
    """Mock: Match type alias — identity."""
    return x

#@ ensures \result == x
def IO(x: int) -> int:
    """Mock: IO type alias — identity."""
    return x

#@ ensures \result == x
def TextIO(x: int) -> int:
    """Mock: TextIO type alias — identity."""
    return x

#@ ensures \result == x
def BinaryIO(x: int) -> int:
    """Mock: BinaryIO type alias — identity."""
    return x

#@ ensures \result == x
def Text(x: int) -> int:
    """Mock: Text type alias — identity."""
    return x

# =========================================================================
# Special types (identity)
# =========================================================================

#@ ensures \result == x
def Any_(x: int) -> int:
    """Mock: Any special type — identity."""
    return x

#@ ensures \result == x
def Optional(x: int) -> int:
    """Mock: Optional special form — identity."""
    return x

#@ ensures \result == x
def Union(x: int) -> int:
    """Mock: Union special form — identity."""
    return x

#@ ensures \result == x
def NoReturn(x: int) -> int:
    """Mock: NoReturn special type — identity."""
    return x

#@ ensures \result == x
def Never(x: int) -> int:
    """Mock: Never special type — identity."""
    return x

#@ ensures \result == x
def Self(x: int) -> int:
    """Mock: Self special type — identity."""
    return x

#@ ensures \result == x
def LiteralString(x: int) -> int:
    """Mock: LiteralString special type — identity."""
    return x

#@ ensures \result == x
def AnyStr(x: int) -> int:
    """Mock: AnyStr constrained type variable — identity."""
    return x

# =========================================================================
# Special forms (identity)
# =========================================================================

#@ ensures \result == x
def Final(x: int) -> int:
    """Mock: Final special form — identity."""
    return x

#@ ensures \result == x
def Literal(x: int) -> int:
    """Mock: Literal special form — identity."""
    return x

#@ ensures \result == x
def ClassVar(x: int) -> int:
    """Mock: ClassVar special form — identity."""
    return x

#@ ensures \result == x
def Concatenate(x: int) -> int:
    """Mock: Concatenate special form — identity."""
    return x

#@ ensures \result == x
def Unpack(x: int) -> int:
    """Mock: Unpack special form — identity."""
    return x

#@ ensures \result == x
def Required(x: int) -> int:
    """Mock: Required special form — identity."""
    return x

#@ ensures \result == x
def NotRequired(x: int) -> int:
    """Mock: NotRequired special form — identity."""
    return x

#@ ensures \result == x
def ReadOnly(x: int) -> int:
    """Mock: ReadOnly special form — identity."""
    return x

#@ ensures \result == x
def Annotated(x: int) -> int:
    """Mock: Annotated special form — identity."""
    return x

#@ ensures \result == x
def TypeGuard(x: int) -> int:
    """Mock: TypeGuard special form — identity."""
    return x

#@ ensures \result == x
def TypeIs(x: int) -> int:
    """Mock: TypeIs special form — identity."""
    return x

#@ ensures \result == x
def TypeForm(x: int) -> int:
    """Mock: TypeForm special form — identity."""
    return x

#@ ensures \result == x
def TypeAlias(x: int) -> int:
    """Mock: TypeAlias special form — identity."""
    return x

#@ ensures \result == x
def Generic(x: int) -> int:
    """Mock: Generic base class — identity."""
    return x

# =========================================================================
# Type variable constructors (opaque int)
# =========================================================================

#@ ensures \result >= 0
def TypeVar(name: str) -> int:
    """Mock: TypeVar constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def TypeVarTuple(name: str) -> int:
    """Mock: TypeVarTuple constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def ParamSpec(name: str) -> int:
    """Mock: ParamSpec constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def ParamSpecArgs(x: int) -> int:
    """Mock: ParamSpecArgs — returns opaque int."""
    return 0

#@ ensures \result >= 0
def ParamSpecKwargs(x: int) -> int:
    """Mock: ParamSpecKwargs — returns opaque int."""
    return 0

#@ ensures \result >= 0
def NewType(name: str, tp: int) -> int:
    """Mock: NewType constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def NamedTuple(typename: str, fields: int) -> int:
    """Mock: NamedTuple constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def TypedDict(typename: str, fields: int) -> int:
    """Mock: TypedDict constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def TypeAliasType(name: str, value: int) -> int:
    """Mock: TypeAliasType constructor — returns opaque int."""
    return 0

#@ ensures \result >= 0
def ForwardRef(arg: str) -> int:
    """Mock: ForwardRef constructor — returns opaque int."""
    return 0

# =========================================================================
# Functions with semantic contracts
# =========================================================================

#@ ensures \result == v
def cast(tp: int, v: int) -> int:
    """Mock: cast — returns v unchanged."""
    return v

#@ ensures \result == v
def assert_type(v: int, tp: int) -> int:
    """Mock: assert_type — returns v unchanged."""
    return v

#@ ensures \result >= 0
def assert_never(arg: int) -> int:
    """Mock: assert_never — opaque (raises at runtime)."""
    return 0

#@ ensures \result == obj
def reveal_type(obj: int) -> int:
    """Mock: reveal_type — returns obj unchanged."""
    return obj

# =========================================================================
# Introspection helpers (opaque int)
# =========================================================================

#@ ensures \result >= 0
def get_type_hints(obj: int) -> int:
    """Mock: get_type_hints — returns opaque int."""
    return 0

#@ ensures \result >= 0
def get_origin(tp: int) -> int:
    """Mock: get_origin — returns opaque int."""
    return 0

#@ ensures \result >= 0
def get_args(tp: int) -> int:
    """Mock: get_args — returns opaque int."""
    return 0

#@ ensures \result >= 0
def get_overloads(func: int) -> int:
    """Mock: get_overloads — returns opaque int."""
    return 0

#@ ensures \result >= 0
def clear_overloads() -> int:
    """Mock: clear_overloads — no-op, returns 0."""
    return 0

#@ ensures \result >= 0
def get_protocol_members(tp: int) -> int:
    """Mock: get_protocol_members — returns opaque int."""
    return 0

#@ ensures \result >= 0
def is_protocol(tp: int) -> int:
    """Mock: is_protocol — returns opaque int."""
    return 0

#@ ensures \result >= 0
def is_typeddict(tp: int) -> int:
    """Mock: is_typeddict — returns opaque int."""
    return 0

#@ ensures \result >= 0
def evaluate_forward_ref(forward_ref: int) -> int:
    """Mock: evaluate_forward_ref — returns opaque int."""
    return 0

# =========================================================================
# Decorators (passthrough identity)
# =========================================================================

#@ ensures \result == f
def dataclass_transform(f: int) -> int:
    """Mock: dataclass_transform decorator — passthrough."""
    return f

#@ ensures \result == f
def overload(f: int) -> int:
    """Mock: overload decorator — passthrough."""
    return f

#@ ensures \result == f
def final2(f: int) -> int:
    """Mock: final decorator — passthrough."""
    return f

#@ ensures \result == f
def no_type_check(f: int) -> int:
    """Mock: no_type_check decorator — passthrough."""
    return f

#@ ensures \result == f
def no_type_check_decorator(f: int) -> int:
    """Mock: no_type_check_decorator decorator — passthrough."""
    return f

#@ ensures \result == f
def override(f: int) -> int:
    """Mock: override decorator — passthrough."""
    return f

#@ ensures \result == f
def runtime_checkable(f: int) -> int:
    """Mock: runtime_checkable decorator — passthrough."""
    return f

#@ ensures \result == f
def type_check_only(f: int) -> int:
    """Mock: type_check_only decorator — passthrough."""
    return f

#@ ensures \result == f
def disjoint_base(f: int) -> int:
    """Mock: disjoint_base decorator — passthrough."""
    return f
