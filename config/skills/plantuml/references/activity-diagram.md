# Activity Diagram

An activity diagram describes a workflow or process: the steps, the order they happen in, and the decisions and parallel paths along the way. PlantUML's *beta* syntax (which is the current default and recommended for all new diagrams) is block-structured: you write actions and control flow keywords in the order they execute, and the layout is generated.

The older, deprecated activity syntax used arrows between named nodes; you'll see it in old documents but should not write new diagrams in it.

## Core syntax

Activity labels are wrapped: `:action text;` — colon at the start, semicolon at the end. They link in declaration order.

```plantuml
@startuml
:Hello world;
:This is defined on
several **lines**;
@enduml
```

`start` and `stop` (or `end`) mark the start and end nodes:

```plantuml
@startuml
start
:Read input;
:Process;
:Write output;
stop
@enduml
```

## Conditionals: if / then / else / endif

```plantuml
@startuml
start
if (Graphviz installed?) then (yes)
    :process all diagrams;
else (no)
    :process only sequence and activity diagrams;
endif
stop
@enduml
```

For multiple branches, use `elseif`:

```plantuml
@startuml
start
if (condition A) then (yes)
    :Text 1;
elseif (condition B) then (yes)
    :Text 2;
    stop
(no) elseif (condition C) then (yes)
    :Text 3;
else (nothing)
    :Text else;
endif
stop
@enduml
```

By default elseif chains lay out horizontally; switch to vertical with `!pragma useVerticalIf on` at the top of the diagram.

## Switch / case

For a multi-way branch on a single value, `switch` reads more cleanly than nested `elseif`:

```plantuml
@startuml
start
switch (test?)
case ( condition A )
    :Text 1;
case ( condition B )
    :Text 2;
case ( condition C )
    :Text 3;
endswitch
stop
@enduml
```

## Loops

`while` / `endwhile`:

```plantuml
@startuml
start
while (data available?)
    :read data;
    :process;
endwhile
stop
@enduml
```

`repeat` / `repeat while` (test at the end of the loop):

```plantuml
@startuml
start
repeat
    :read data;
    :generate diagrams;
repeat while (more data?) is (yes) not (no)
stop
@enduml
```

Both loops accept a `backward:Action;` to insert an action in the return path:

```plantuml
@startuml
start
while (check filesize?) is (not empty)
    :read file;
    backward:log;
endwhile (empty)
:close file;
stop
@enduml
```

## Parallel flow: fork

`fork` / `fork again` / `end fork` (or `end merge`):

```plantuml
@startuml
start
fork
    :action 1;
fork again
    :action 2;
fork again
    :action 3;
end fork
stop
@enduml
```

`end fork {and}` or `end fork {or}` adds a UML joinspec label.

## Split (related but distinct from fork)

`split` / `split again` / `end split` is the syntactic cousin of fork. It's useful for showing branching without strict parallelism, or for input/output splits with `[hidden]` arrows:

```plantuml
@startuml
start
split
    :A;
split again
    :B;
split again
    :C;
end split
:D;
end
@enduml
```

## Ending a branch: stop, end, kill, detach

`stop` and `end` close the diagram normally. Inside a branch, `kill` or `detach` after an action terminates *that branch only* without forcing the whole diagram to stop:

```plantuml
@startuml
if (condition?) then
    :error; <<#pink>>
    kill
endif
:action; <<#palegreen>>
@enduml
```

`break` inside a `repeat` loop exits the loop after the current action.

## Notes

Notes attach to the previous activity with `note left`, `note right`, etc., and can be multi-line:

```plantuml
@startuml
start
:foo1;
floating note left: This is a floating note
:foo2;
note right
    This note is on
    several //lines//
end note
stop
@enduml
```

## Colors and styling

`<<#color>>` or `<<#colorname>>` after an action colors it:

```plantuml
@startuml
start
:starting progress;
:reading configuration; <<#HotPink>>
:ending; <<#AAAAAA>>
stop
@enduml
```

Arrows can be styled with `-[#color,style]->` between actions:

```plantuml
@startuml
:foo1;
-[#blue]->
:foo2;
-[#green,dashed]->
:foo3;
@enduml
```

`skinparam ArrowHeadColor none` removes arrowheads entirely (sometimes wanted for flowchart-style diagrams).

## Partitions

`partition Name { ... }` boxes a group of activities, useful for swimlane-like groupings:

```plantuml
@startuml
start
partition "Phase 1" {
    :Initialize;
    :Load data;
}
partition "Phase 2" #LightBlue {
    :Process;
    :Save results;
}
stop
@enduml
```

## Common pitfalls

- **Forgetting the trailing `;` on actions.** `:do something` (without `;`) is a syntax error.
- **Mixing old and new syntax.** The legacy syntax (`(*) --> "Initialize"`) doesn't compose with `:action;` blocks. If you find yourself wanting both, you're probably reading old documentation; stick to one.
- **Over-using `fork` for sequential work.** Fork is for genuinely concurrent steps. Sequential conditional logic belongs in `if/elseif/endif`.
- **Trying to draw arrows manually.** Activity-beta syntax is block-structured; you don't draw the arrows, the layout engine does. If you need explicit nodes and arrows, you want either a state diagram (for behavior) or the legacy activity syntax (not recommended).
