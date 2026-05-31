# Object Diagram

An object diagram is a snapshot: which instances exist at a particular moment, what values they hold, and how they relate. It uses almost the same syntax as a class diagram but with `object` instead of `class`, and with concrete values instead of method signatures.

## Core syntax

Declare instances with `object`. Use `as` for an alias when the name has spaces:

```plantuml
@startuml
object firstObject
object "My Second Object" as o2
@enduml
```

## Fields

Use `:` to assign per-line:

```plantuml
@startuml
object user
user : name = "Dummy"
user : id = 123
@enduml
```

Or group inside `{}`:

```plantuml
@startuml
object user {
    name = "Dummy"
    id = 123
}
@enduml
```

## Relationships

Same arrow set as class diagrams:

- `<|--` extension (rare in object diagrams since instances don't usually extend each other)
- `*--` composition
- `o--` aggregation
- `-->` dependency
- `..>` weak dependency
- `--` plain link

With cardinality and labels:

```plantuml
@startuml
object Object01
object Object02
object Object03
object Object04

Object01 <|-- Object02
Object03 *-- Object04
Object05 o-- "4" Object06
Object07 .. Object08 : some labels
@enduml
```

## Worked example: a snapshot of state

```plantuml
@startuml
object customer {
    id = 4218
    name = "ACME Corp"
    tier = "Gold"
}
object order1 {
    id = 9001
    placed = "2026-05-25"
    total = 142.50
}
object order2 {
    id = 9002
    placed = "2026-05-23"
    total = 89.00
}

customer --> order1 : owns
customer --> order2 : owns
@enduml
```

## Map (associative array)

The `map` keyword renders a key-value table — useful for showing configuration, lookups, or actual data:

```plantuml
@startuml
map CapitalCity {
    UK      => London
    USA     => Washington
    Germany => Berlin
}
@enduml
```

Map entries can be referenced from outside the map using `::`:

```plantuml
@startuml
object London
map CapitalCity {
    UK  *-> London
    USA => Washington
}

NewYork --> CapitalCity::USA
@enduml
```

This is the most distinctive feature of PlantUML's object diagram support: maps are first-class and very useful for showing actual data structures rather than abstract instance shapes.

## Relationship to class diagrams

Object diagrams share most of their feature set with class diagrams:

- `hide` / `show` rules work the same way
- notes (`note left of`, `note as N1`) work the same way
- packages and skinparams work the same way

You can even mix objects and classes in a single diagram when the snapshot includes a type that's worth showing too.

## When to use this instead of a class diagram

Object diagrams are right when:

- You're explaining an example or test case ("what does the state look like after step 3?")
- You're showing the result of a transformation or computation
- The reader needs to see concrete values, not just types

If you're showing the static design of a system, use a class diagram instead.

## Common pitfalls

- **Reusing the same name for an object and its class.** Either prefix instance names (`order1`, `order2`) or use `as` aliases to disambiguate.
- **Showing too many objects.** Object diagrams scale poorly past 10–15 instances. Pick a representative snapshot, not the whole heap.
- **Using inheritance arrows.** `<|--` between objects is technically legal but usually meaningless — instances don't inherit from each other. Stick to associations.
