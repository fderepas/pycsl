# State Diagram

A state diagram captures how an entity moves between distinct states in response to events. It's the right diagram for any system with a lifecycle (orders, sessions, connections, protocols) or any object whose behavior depends on what mode it's in.

## Core syntax

`[*]` is both the start and the end pseudo-state — it's interpreted as start when it's the source of an arrow, end when it's the target. Arrows are the only relationship; the transition label after `:` carries the event and any actions.

```plantuml
@startuml
[*] --> State1
State1 --> State2 : event
State2 --> [*]
@enduml
```

A state may carry a description with `:` (the same line that declares it or a new line):

```plantuml
@startuml
[*] --> Idle
Idle  : entry / log("idle")
Idle  : the resting state
Idle  --> Active : start
Active --> Idle  : stop
Active --> [*]   : shutdown
@enduml
```

## Long names and aliases

For state names with spaces or special characters, use `state "..." as ...`:

```plantuml
@startuml
state "Accumulate Enough Data" as accumulating
[*] --> accumulating
accumulating --> accumulating : new data
accumulating --> Done : threshold reached
@enduml
```

## Composite states

A state can nest other states. Use `state Name { ... }`:

```plantuml
@startuml
[*] --> NotShooting

state NotShooting {
    [*] --> Idle
    Idle --> Configuring : EvConfig
    Configuring --> Idle : EvConfig
}

state Configuring {
    [*] --> NewValueSelection
    NewValueSelection --> NewValuePreview : EvNewValue
    NewValuePreview   --> NewValueSelection : EvNewValueRejected
    NewValuePreview   --> NewValueSelection : EvNewValueSaved
}
@enduml
```

The inner `[*] --> ...` declares the *initial* sub-state when the composite is entered.

## Concurrent regions

Inside a composite state, `--` or `||` separates parallel regions that run simultaneously:

```plantuml
@startuml
[*] --> Active

state Active {
    [*] --> NumLockOff
    NumLockOff --> NumLockOn  : NumLockPressed
    NumLockOn  --> NumLockOff : NumLockPressed
    --
    [*] --> CapsLockOff
    CapsLockOff --> CapsLockOn  : CapsLockPressed
    CapsLockOn  --> CapsLockOff : CapsLockPressed
}
@enduml
```

`--` separates regions vertically; `||` separates them horizontally. Within Active, the NumLock and CapsLock regions are independent — each tracks its own state.

## Pseudo-states (stereotypes)

Use `<<>>` stereotypes to declare special UML pseudo-states:

- `<<start>>` — alternative to `[*]`
- `<<end>>` — alternative to `[*]` as terminal
- `<<choice>>` — conditional branch point
- `<<fork>>` and `<<join>>` — concurrent split / sync
- `<<history>>` — history (re-enter the last sub-state)
- `<<history*>>` — deep history (re-enter the last sub-state at any nesting depth)
- `<<entryPoint>>` and `<<exitPoint>>` — named transition points on a composite state's boundary
- `<<inputPin>>`, `<<outputPin>>`, `<<expansionInput>>`, `<<expansionOutput>>` — UML pin / expansion notation

```plantuml
@startuml
state c <<choice>>
state forked <<fork>>
state joined <<join>>

[*] --> c
c --> Minor : [value <= 10]
c --> Major : [value > 10]

Minor --> forked
forked --> Step1
forked --> Step2
Step1 --> joined
Step2 --> joined
joined --> [*]
@enduml
```

## Sub-state to sub-state transitions

You can draw arrows between sub-states of different composite states. The path is implicit:

```plantuml
@startuml
state A {
    state X
    state Y
}
state B {
    state Z
}

X --> Z
Z --> Y
@enduml
```

The dotted-name form `state A.X` is equivalent to declaring `X` inside `A`.

## Arrow direction

Forced direction works the same as elsewhere: `-up->`, `-down->`, `-left->`, `-right->`. Default is `-down->` for `-->` and `-right->` for `->`.

## Line color and style

Bracketed style on transitions:

```plantuml
@startuml
S1 -[#DD00AA]-> S2
S1 -left[#yellow]-> S3
S1 -up[#red,dashed]-> S4
S1 -right[dotted,#blue]-> S5
@enduml
```

## Notes

Notes work as everywhere: `note left of`, `note right of`, multi-line with `end note`, floating with `note "text" as N1` then `N1 .. SomeState`.

## Hiding empty descriptions

Without a description line, a state renders as a fat box. `hide empty description` collapses descriptionless states to simple boxes, which often looks cleaner:

```plantuml
@startuml
hide empty description
[*] --> State1
State1 --> State2
State2 --> [*]
@enduml
```

## Common pitfalls

- **Confusing `[*]` for both start and end.** It's the same symbol but its role is determined by direction. `[*] --> A` is "start to A"; `A --> [*]` is "A to end". Both are common in the same diagram.
- **Forgetting the initial transition inside a composite state.** A composite state needs `[*] --> SubState` to say which sub-state is entered first. Without it, the diagram is ambiguous.
- **Drawing transitions between sub-states across boundaries without realizing you can.** Cross-composite transitions are legal and often the clearest way to express "exit this whole region and enter that one". Don't paper over them with extra exit/entry states.
- **Using state diagrams for sequential workflows.** If the entity has no real "state" — just a sequence of steps — an activity diagram is the right tool. State diagrams are for *modes* that affect *future* behavior.
