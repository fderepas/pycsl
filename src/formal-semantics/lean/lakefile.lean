import Lake
open Lake DSL

package PyCSL where
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib PyCSL where
  srcDir := "."
  roots := #[`PyCSL]
