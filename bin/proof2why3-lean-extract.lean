/-
  proof2why3-lean-extract.lean — extract theorem statement types
  from a Lean .lean proof file into structured JSON IR.

  Replaces the v1 `#check`-pretty-print extraction
  (`extract.py:extract_lean_statements`) with a direct query of
  the Lean environment. Per sticky-02.md Phase B.

  Invocation (via the wrapper in extract_lean_meta.py):

      lake env lean --run bin/proof2why3-lean-extract.lean \
          <import-module> <qualname>[,<qualname>...]

  E.g. `lake env lean --run bin/proof2why3-lean-extract.lean Gcd \
       Pycsl.Reference.Gcd.gcd_step,Pycsl.Reference.Gcd.gcd_0`.

  The script must be run from a directory containing a `lakefile.lean`
  that knows where to find the import module (e.g.
  `test-suite/corpus/pycsl-reference/0342.proofs/lean/lakefile.lean`).

  Output: one JSON object per cited qualname, written one-per-line
  to stdout, terminated by a sentinel `{"end": true}`:

      {"qualname": "Pycsl.Reference.Gcd.gcd_step",
       "type": "...pretty-printed type...",
       "ast": { ... structured Lean.Expr ... }}
      ...
      {"end": true}
-/
import Lean
open Lean Elab Meta

/-- Produce a stable JSON representation of a Lean.Expr that the
    Python projector can map into the shared IR. The shape mirrors
    `proof2why3.ir`:

      {"kind":"forall", "binder":"a", "ty":<sub>, "body":<sub>}
      {"kind":"app",    "fn":<sub>,   "arg":<sub>}
      {"kind":"const",  "name":"Pycsl.Reference.Gcd.gcd_step"}
      {"kind":"fvar",   "id":<string>}
      {"kind":"bvar",   "idx":<nat>}
      {"kind":"lit",    "value":"123"}
      {"kind":"sort",   "level":<string>}
      {"kind":"unsupported", "raw":<string>}                       -/
partial def exprToJson : Expr → MetaM Json
  | .forallE n t b _ => do
      let tJson ← exprToJson t
      let bJson ← exprToJson b
      return Json.mkObj [
        ("kind",   Json.str "forall"),
        ("binder", Json.str n.toString),
        ("ty",     tJson),
        ("body",   bJson)
      ]
  | .lam n t b _ => do
      let tJson ← exprToJson t
      let bJson ← exprToJson b
      return Json.mkObj [
        ("kind",   Json.str "lam"),
        ("binder", Json.str n.toString),
        ("ty",     tJson),
        ("body",   bJson)
      ]
  | .app f a => do
      let fJson ← exprToJson f
      let aJson ← exprToJson a
      return Json.mkObj [
        ("kind", Json.str "app"),
        ("fn",   fJson),
        ("arg",  aJson)
      ]
  | .const n _ =>
      return Json.mkObj [
        ("kind", Json.str "const"),
        ("name", Json.str n.toString)
      ]
  | .fvar id =>
      return Json.mkObj [
        ("kind", Json.str "fvar"),
        ("id",   Json.str id.name.toString)
      ]
  | .bvar i =>
      return Json.mkObj [
        ("kind", Json.str "bvar"),
        ("idx",  Json.num i)
      ]
  | .lit lit =>
      let v := match lit with
               | .natVal n => toString n
               | .strVal s => s
      return Json.mkObj [
        ("kind",  Json.str "lit"),
        ("value", Json.str v)
      ]
  | .sort u =>
      return Json.mkObj [
        ("kind",  Json.str "sort"),
        ("level", Json.str (toString u))
      ]
  | .mvar id =>
      return Json.mkObj [
        ("kind", Json.str "mvar"),
        ("id",   Json.str id.name.toString)
      ]
  | .letE n t v b _ => do
      let tJson ← exprToJson t
      let vJson ← exprToJson v
      let bJson ← exprToJson b
      return Json.mkObj [
        ("kind",   Json.str "let"),
        ("binder", Json.str n.toString),
        ("ty",     tJson),
        ("val",    vJson),
        ("body",   bJson)
      ]
  | other =>
      return Json.mkObj [
        ("kind", Json.str "unsupported"),
        ("raw",  Json.str (toString other))
      ]

/-- Look up a theorem by qualified name in the current environment
    and emit one JSON object per line on stdout describing its type. -/
def extractOne (qn : Name) : MetaM Unit := do
  let env ← getEnv
  match env.find? qn with
  | none => do
      let j := Json.mkObj [
        ("qualname", Json.str qn.toString),
        ("error",    Json.str "not found in environment")
      ]
      IO.println j.compress
  | some info => do
      let typeStr := toString (← Meta.ppExpr info.type)
      let ast ← exprToJson info.type
      let j := Json.mkObj [
        ("qualname", Json.str qn.toString),
        ("type",     Json.str typeStr),
        ("ast",      ast)
      ]
      IO.println j.compress

unsafe def main (args : List String) : IO UInt32 := do
  enableInitializersExecution
  match args with
  | importModule :: qnList :: _ => do
      let _ ← Lean.findSysroot
      let env ← importModules (loadExts := true)
                  #[{module := `Init},
                    {module := importModule.toName}]
                  {}
      let qns := (qnList.splitOn ",").map String.toName
      let metaAction : MetaM Unit := do
        for qn in qns do
          extractOne qn
      let coreAction : CoreM Unit := metaAction.run' {}
      let coreCtx : Core.Context :=
        { fileName := "<extract>", fileMap := default }
      let coreState : Core.State := { env := env }
      let _ ← coreAction.toIO coreCtx coreState
      IO.println "{\"end\": true}"
      return 0
  | _ => do
      IO.eprintln "usage: proof2why3-lean-extract <ImportModule> <qn1,qn2,...>"
      return 2
