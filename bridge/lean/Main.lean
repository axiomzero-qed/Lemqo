/-
SPDX-License-Identifier: Apache-2.0
Copyright (c) 2025 Lean FRO, LLC. All rights reserved.

The primitive target list and use of Comparator are adapted from
leanprover/comparator Main.lean, commit
d03acab154d269c06e60e4de7e4cc85deebff94b (author: Henrik Böving).
This executable performs offline statement binding, not proof checking.
-/
import Comparator
import Export.Parse

open Lean

namespace Lemqo

structure Config where
  reference_file : String
  solution_file : String
  theorem_names : Array String
  permitted_axioms : Array String
  deriving FromJson

def standardAxioms : Array String := #["propext", "Classical.choice", "Quot.sound"]

/-- Same kernel-sensitive declarations as the pinned Comparator. -/
def primitiveTargets : Array Name := #[
  ``Nat.add, ``Nat.sub, ``Nat.mul, ``Nat.pow, ``Nat.gcd, ``Nat.div,
  ``Nat.mod, ``Nat.beq, ``Nat.ble, ``Nat.land, ``Nat.lor, ``Nat.xor,
  ``Nat.shiftLeft, ``Nat.shiftRight, ``String.ofList, ``Char.ofNat,
  ``List, ``eagerReduce, ``Nat, ``String, ``String.mk, ``Char,
  ``optParam, ``autoParam, ``semiOutParam, ``outParam
]

def validateNames (label : String) (names : Array String) : Except String Unit := do
  let mut seen : Std.HashSet String := {}
  for name in names do
    if name.isEmpty || (name.splitOn ".").any String.isEmpty then
      throw s!"{label}: empty name or namespace component"
    if name.toName.toString != name then
      throw s!"{label}: name is not canonical: {name}"
    if seen.contains name then
      throw s!"{label}: duplicate name: {name}"
    seen := seen.insert name

def parseConfig (json : Json) : Except String Config := do
  let .obj fields := json | throw "configuration must be an object"
  let expected := #["reference_file", "solution_file", "theorem_names", "permitted_axioms"]
  for (key, _) in fields.toList do
    if !expected.contains key then
      throw s!"unexpected configuration field: {key}"
  let cfg : Config ← fromJson? json
  if cfg.reference_file.isEmpty || cfg.solution_file.isEmpty then
    throw "export paths must not be empty"
  if cfg.theorem_names.isEmpty then
    throw "theorem_names must not be empty"
  validateNames "theorem_names" cfg.theorem_names
  validateNames "permitted_axioms" cfg.permitted_axioms
  for axiomName in cfg.permitted_axioms do
    if !standardAxioms.contains axiomName then
      throw s!"axiom is not permitted by Lemqo: {axiomName}"
  for theoremName in cfg.theorem_names do
    if standardAxioms.contains theoremName then
      throw s!"a standard axiom cannot be a theorem target: {theoremName}"
  return cfg

def checkMetadata (header : String) : Except String Unit := do
  let root ← Json.parse header
  let exportMeta ← root.getObjVal? "meta"
  let format ← exportMeta.getObjVal? "format"
  let exporter ← exportMeta.getObjVal? "exporter"
  let lean ← exportMeta.getObjVal? "lean"
  if (← (← format.getObjVal? "version").getStr?) != "3.1.0" then
    throw "unsupported export format version"
  if (← (← exporter.getObjVal? "name").getStr?) != "lean4export" ||
      (← (← exporter.getObjVal? "version").getStr?) != "3.1.0" then
    throw "unsupported exporter metadata"
  if (← (← lean.getObjVal? "version").getStr?) != "4.34.1" ||
      (← (← lean.getObjVal? "githash").getStr?) !=
        "5045d0056413266e57c625dcd7c365b10e377c52" then
    throw "unsupported Lean toolchain metadata"

def readExport (path : String) : IO Export.ExportedEnv := do
  let handle ← IO.FS.Handle.mk path .read
  let header ← handle.getLine
  IO.ofExcept <| checkMetadata header
  -- The upstream parser skips metadata. Replay the validated header once,
  -- without reopening the file or copying its potentially large contents.
  let first ← IO.mkRef true
  let stream := { IO.FS.Stream.ofHandle handle with
    getLine := do
      if ← first.get then
        first.set false
        return header
      else
        handle.getLine
  }
  Export.parseStream stream

/-- Unsafe/partial declarations have no place in these proof certificates. -/
def checkSafety (label : String) (env : Export.ExportedEnv) : Except String Unit := do
  if env.constOrder.isEmpty then
    throw s!"{label}: export has no declarations"
  for name in env.constOrder do
    let some info := env.constMap[name]? | throw s!"{label}: missing declaration: {name}"
    if info.isUnsafe || info.isPartial then
      throw s!"{label}: unsafe or partial declaration: {name}"

def requireTheorems (label : String) (env : Export.ExportedEnv)
    (names : Array Name) : Except String Unit := do
  for name in names do
    let some (.thmInfo _) := env.constMap[name]?
      | throw s!"{label}: target is missing or is not a theorem: {name}"

def requireAxioms (label : String) (env : Export.ExportedEnv)
    (names : Array Name) : Except String Unit := do
  for name in names do
    let some (.axiomInfo _) := env.constMap[name]?
      | throw s!"{label}: permitted axiom is missing or has the wrong kind: {name}"

def verify (cfg : Config) : IO Unit := do
  let reference ← readExport cfg.reference_file
  let solution ← readExport cfg.solution_file
  let theoremNames := cfg.theorem_names.map String.toName
  let legalAxioms := cfg.permitted_axioms.map String.toName
  IO.ofExcept <| checkSafety "reference" reference
  IO.ofExcept <| checkSafety "solution" solution
  IO.ofExcept <| requireTheorems "reference" reference theoremNames
  IO.ofExcept <| requireTheorems "solution" solution theoremNames
  IO.ofExcept <| requireAxioms "reference" reference legalAxioms
  IO.ofExcept <| requireAxioms "solution" solution legalAxioms
  -- Reject even unused unapproved solution axioms. The reference may contain
  -- sorryAx for its theorem holes, but its proofs are never accepted as evidence.
  for name in solution.constOrder do
    if let some (.axiomInfo _) := solution.constMap[name]? then
      if !legalAxioms.contains name then
        throw <| IO.userError s!"solution: unpermitted axiom: {name}"
  let quotientTargets := if legalAxioms.contains ``Quot.sound then
    #[``Quot, ``Quot.mk, ``Quot.lift, ``Quot.ind] else #[]
  -- Axioms are comparison targets, so their universe parameters and TYPES
  -- match the trusted reference; a familiar name alone is insufficient.
  IO.ofExcept <| Comparator.compareAt reference solution
    (theoremNames ++ legalAxioms) #[] (primitiveTargets ++ quotientTargets)
  IO.ofExcept <| Comparator.checkAxioms solution theoremNames #[] legalAxioms
  -- Deliberately do not replay into the Lean kernel. Nanoda is a separate,
  -- mandatory proof-checking step performed by the Python caller.
  IO.println <| (Json.mkObj [
    ("status", Json.str "matched"),
    ("theorem_names", toJson cfg.theorem_names)
  ]).compress

end Lemqo

def main (args : List String) : IO UInt32 := do
  try
    let [configPath] := args
      | throw <| IO.userError "usage: lemqo_compare config.json"
    let configText ← IO.FS.readFile configPath
    let json ← IO.ofExcept <| Lean.Json.parse configText
    let cfg ← IO.ofExcept <| Lemqo.parseConfig json
    Lemqo.verify cfg
    return 0
  catch error =>
    (← IO.getStderr).putStrLn s!"lemqo_compare: {error}"
    return 1
