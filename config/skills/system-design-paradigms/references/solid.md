# SOLID — A Deep Dive

The SOLID principles, formulated by Robert C. Martin, describe what well-factored object-oriented code looks like. They're not OO-specific in spirit — most of them translate cleanly to functional and module-level design — but the canonical framing assumes classes and interfaces.

Each principle is a heuristic against a specific kind of decay that creeps into long-lived codebases. Knowing the decay is what makes the principle useful.

---

## S — Single Responsibility Principle

> A class should have one, and only one, reason to change.

The "responsibility" here is not "one thing it does." A class with thirty methods that all serve the same stakeholder concern can be perfectly SRP-compliant. A class with two methods that serve two different stakeholders — say, `formatReport()` (concerns the marketing team's layout) and `calculateTotals()` (concerns the finance team's numbers) — violates it, because either stakeholder can independently force a change.

The operational test: imagine the class's clients. If two clients can independently demand changes that touch the same class, you have two responsibilities tangled together.

**Common failure:** interpreting SRP as "one method per class." That produces a fog of trivial classes — `UserNameValidator`, `UserNameTrimmer`, `UserNameLowercaser` — and the cognitive overhead of navigating them is far worse than the original "complex" class.

**Example of a violation:**
```
class Employee {
  calculatePay()      // changes when finance changes the pay formula
  saveToDatabase()    // changes when DBAs change the schema
  generateReport()    // changes when HR changes the report layout
}
```
Three stakeholders, three reasons to change, three responsibilities. The fix is to split along those seams.

---

## O — Open/Closed Principle

> Software entities should be open for extension, but closed for modification.

You should be able to add new behavior without editing existing code. The mechanism is usually polymorphism, plugins, or strategy patterns — new behavior arrives as a new implementation of an existing interface, not as a new branch in an existing function.

The point is risk reduction: editing working code can break things you didn't realize depended on it. Adding new code can't.

**Common failure:** building elaborate extension scaffolding for variations that never materialize. OCP is most valuable on axes that have *already* shown they vary; pre-emptive extension points for hypothetical needs are speculative generality (YAGNI). The right time to add an extension point is the second or third time you'd otherwise have edited the existing code.

**Example:**
```
// Closed to extension — every new shape forces editing this function:
function area(shape) {
  if (shape.type === 'circle') return Math.PI * shape.r ** 2
  if (shape.type === 'square') return shape.side ** 2
  // ...
}

// Open to extension — new shapes just implement area():
class Circle { area() { return Math.PI * this.r ** 2 } }
class Square { area() { return this.side ** 2 } }
```

---

## L — Liskov Substitution Principle

> Subtypes must be substitutable for their base types.

If `Bird` has a method `fly()`, and `Penguin` inherits from `Bird` but throws an exception when `fly()` is called, you've violated LSP. Code written to handle a `Bird` can no longer safely handle a `Penguin` — the subtype has broken its parent's contract.

The principle is really about *behavioral contracts*. A subtype can do more than its parent, but it cannot do less. It must accept everything the parent accepts and produce something at least as strong as what the parent produces (contravariant inputs, covariant outputs, in formal terms).

**Common failure:** modeling taxonomies that don't map to substitutability. "A square is a rectangle" sounds true mathematically, but if `Rectangle.setWidth(w)` is part of the contract, a `Square` that *also* updates its height to preserve squareness has broken that contract. The fix is usually to model on behavior, not vocabulary.

**Why it matters:** LSP is the principle that makes polymorphism trustworthy. If subtypes can lie about their contracts, the whole point of programming-to-an-interface evaporates.

---

## I — Interface Segregation Principle

> Clients should not be forced to depend on methods they do not use.

A fat interface with twenty methods forces every implementer to deal with all twenty, even if it only uses three. It also couples every client to the full surface area, so any change ripples broadly.

The fix is many small, role-focused interfaces — `Readable`, `Writable`, `Closable` — that clients combine as needed.

**Common failure:** confusing this with "one method per interface." The unit is a *role*, not a method. An interface for "thing that can be drained" might include `start()`, `stop()`, and `isDraining()` — that's one role, three methods.

**Example:**
```
// Fat interface — printers that don't scan still have to implement scan():
interface MultiFunctionDevice {
  print(doc)
  scan(doc)
  fax(doc)
}

// Segregated — a printer that only prints depends only on Printer:
interface Printer { print(doc) }
interface Scanner { scan(doc) }
interface Fax     { fax(doc) }
```

---

## D — Dependency Inversion Principle

> High-level modules should not depend on low-level modules. Both should depend on abstractions.
>
> **Note:** "High-level" and "low-level" in the Dependency Inversion Principle refer to abstraction layers in software architecture, not to the CMMI 5-level specification hierarchy (Business → System → Component → Module → Unit).

The naive layering — high-level business logic depends on low-level utilities (DB drivers, HTTP clients, file system) — has it backwards. The business logic is the stable, valuable part; it shouldn't be at the mercy of which database you happened to pick.

DIP inverts this: the business logic defines the abstractions it needs (`UserRepository`, `EmailSender`), and the low-level modules implement those abstractions. The arrows in the dependency graph now point *toward* the business logic, not away from it.

**Common failure:** equating DIP with "add an interface in front of everything." Interfaces have a cost (indirection, navigation, sometimes performance). DIP is most valuable across genuine boundaries — where the implementation could plausibly change, where you want to swap for testing, or where the abstraction makes the business logic clearer. Wrapping every internal helper in a one-implementation interface is ceremony, not design.

**Example:**
```
// Direct dependency — OrderService is now bound to PostgresDB forever:
class OrderService {
  constructor() { this.db = new PostgresDB() }
}

// Inverted — OrderService depends on the abstraction; the wiring happens outside:
interface OrderRepository { save(order); find(id) }
class OrderService {
  constructor(repo: OrderRepository) { this.repo = repo }
}
```

---

## How SOLID fits together

The principles reinforce each other. SRP says classes should have one reason to change; OCP says they shouldn't be edited when behavior expands; LSP says inheritance must preserve contracts; ISP says clients shouldn't be over-coupled; DIP says high-level code shouldn't be hostage to low-level implementation. Together they describe code that can absorb change without breaking — which is the whole point.

Misapplied, they become their own anti-pattern: a maze of tiny classes, surplus interfaces, deep injection chains, and indirection everywhere. The principles are tools for managing change, not a checklist to maximize. Apply them where change actually happens or is genuinely expected; relax them where the code is stable and the abstraction would cost more than it earns.
