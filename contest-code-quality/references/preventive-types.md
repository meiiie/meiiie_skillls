# Preventive typed design (experimental)

Use this small gate before or alongside the existing test/repair loop when a type or boundary can prevent a concrete defect. It adds no required orchestrator, model or dependency.

## Name the invariant and keep the representation small

Write the observable rule and its distinguishing bad example before editing. Separate shape rules that the compiler can enforce from value rules that need runtime evidence. Reuse an authoritative schema when one exists rather than maintaining a second wire shape.

For example, a queued job has no start/result, a running job requires a start, and a done job requires completion and a result. A bag of optional fields admits contradictory combinations. The tested TypeScript representation was:

```ts
type RunState =
  | { phase: "queued"; jobId: string; startedMs?: never; completedMs?: never; result?: never }
  | { phase: "running"; jobId: string; startedMs: number; completedMs?: never; result?: never }
  | { phase: "done"; jobId: string; startedMs: number; completedMs: number; result: string };
```

Here, `exactOptionalPropertyTypes` matters: absence must differ from a forbidden property explicitly present as `undefined`. Check intermediate-variable assignments as well as direct literals. Strings and numbers in this shape do not prove nonempty text, finiteness or time ordering.

Use a private constructor, refined value or distinct semantic ID only where an observed partial operation, ownership rule or primitive mix-up warrants it. Keep unrelated values ordinary. Avoid generic factories, pass-through layers and speculative brands that make the actual rule harder to find.

## Parse external data, then consume the domain state

Start JSON, CLI, environment, storage and network data as `unknown` or the language's equivalent. A runtime parser must check the actual required fields and value constraints and construct the accepted domain value. An assertion such as `raw as RunState` supplies no validation. Declare the project's unknown-field, prototype, error and normalization policies; the pilot's policy is an example, not a universal transport requirement.

Keep domain behavior easy to trace and put validation at the owned boundary. If internal callers can construct values that bypass a needed value invariant, address that construction path rather than claiming the union alone protects it. Keep transport/framework types behind their adapter when that distinction serves the domain.

Consume variants with the language's exhaustive mechanism. Test the real consumer by adding a variant to an isolated source copy while leaving its handler unchanged. A compiler rejection at that consumer is evidence; passing a separate wider type to an unrelated function is not the same test.

## Run a thin, honest gate

1. Freeze the contract, important assumptions, source/tests and configuration identities. When independently designed challenges are used and delegation is authorized, freeze their design before disclosure. Record conventions added later.
2. Compile positive valid neighbours. Compile separate syntax-valid negative fixtures for missing fields, contradictory fields, wrong variants and unparsed input. Require the intended diagnostic at the intended fixture; unrelated errors, parser failures, missing tools and timeouts remain separate.
3. Inspect the real compiler configuration and file/import scope. Use project-appropriate strict checks; for the TypeScript example, `strict`, `exactOptionalPropertyTypes` and `noUncheckedIndexedAccess` were enabled. Check explicit strict-family overrides, exclusions, unchecked JavaScript/declarations and dependency boundaries. A configuration display may omit flags implied by `strict`; verify effective semantics instead of treating an omitted field as false. Runtime emission is a separate declared command.
4. Review `any`, type/double assertions, non-null assertions, suppressions and new imports or escape helpers. Use the project's existing compiler/linter and inspect affected declarations and callees. A grep or text-pattern audit can flag a known escape but does not prove alias, transitive-import or semantic safety. Negative-test suppressions must not be the sole evidence that invalid states fail.
5. Run parser/value/behavior tests separately, including valid boundaries. Use the optional command-evidence runner for reviewed compiler and test commands when useful; classify compile diagnostics explicitly in the project adapter. Its plain nonzero-exit mode does not infer type rejection.
6. After a warranted change, rerun fresh against preserved identities. Inspect configuration changes and report the scoped evidence, known escapes and unavailable checks.

Use already available tooling. If a compiler or adapter is unavailable, report that limit and use appropriate existing-language evidence; do not claim TypeScript compilation or install a stack to make the report pass. UI, rendering, integration and runtime correctness retain their own endpoint checks.

## Exercised scope

An isolated Windows pilot used existing TypeScript 7.0.2, Node 25.9.0 and Python 3.13.7. A permissive optional-field model rejected 2 of 6 negative type fixtures; the discriminated model rejected all 6. A new unhandled variant compiled before and failed at the canonical consumer afterward. Both positive type baselines compiled under identical strict configuration.

The unchecked boundary passed 5 of 42 runtime checks; the parser passed all 42, covering valid states, field presence, strings, time bounds and fresh state construction. Eight curated text/config escape controls were detected. Two frozen independent scenarios passed: two further negative type fixtures and nine runtime checks, including present-but-undefined forbidden fields and nonenumerable/Symbol/inherited fields. Executable challenge adapters were authored after disclosure; visible tests and source had the same author. Original independent design preceded source; a convention-only supplement was frozen later without source/test access.

One test-harness repair corrected interpretation of omitted strict-family flags; feature source and before/after compiler configuration stayed unchanged. Fresh reruns preserved hashes. The audit has a declared narrow text/config scope and is not a general AST or transitive analyzer. These checks support the exercised invariants, not universal correctness, security, UI quality or model/token performance.

## Primary design references

Read at commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a` of cursor/plugins on 2026-10-04; its pstack manifest reported 0.15.9 (the earlier research observation was 0.14.8). Lauren Tan's pstack is [MIT licensed](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/LICENSE).

- [Type system discipline](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/principle-type-system-discipline/SKILL.md): representation, boundary parsing and exhaustive consumers.
- [Boundary discipline](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/principle-boundary-discipline/SKILL.md): owned validation and domain/adapter separation.
- [Minimize reader load](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/principle-minimize-reader-load/SKILL.md): fewer needless layers and less hidden state.
- [TypeScript strict](https://www.typescriptlang.org/tsconfig/strict.html): implied strict-family checks and explicit overrides.

This is independently authored guidance and pilot code informed by those references. No pstack implementation, substantial source text or orchestration is bundled or executed; no repository-wide license grant is introduced.
