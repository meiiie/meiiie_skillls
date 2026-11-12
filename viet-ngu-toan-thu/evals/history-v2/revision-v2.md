# Việt ngữ toàn thư v2.0.0: what changed and what did not

Date: 2026-11-12 UTC. Stable v1 was preserved in its original directory and ZIP. This is a separately packaged revision, not an installed account or system setting change.

## Implemented from the parity audit

| Mechanism | v2 implementation | Evidence/limit |
|---|---|---|
| Edit/compose separation | Explicit --mode compose binds material and final, comparison null | Unit regression; no automated semantic grounding claim |
| Meaning/rephrase procedure | Six invariants, per-sentence function, candidate rejection, bounded correction | Instruction-level adaptation; requires actual model behavior |
| Genre/audience/stance | 13 profiles including slides; recommendation/rule/explanation separated | Vietnamese guidance, not translation of Japanese honorific rules |
| Factual recovery | Source quotation/location ledger and contradictions/unknowns protocol | Does not grant permission to search private sources |
| Concrete editorial diagnosis | Eight sections with examples and counterexamples: calques, nominalization, reference, empty claims, metaphor, contrast, rhythm, format | Manual contextual review, not an automatic style detector |
| Configurable terms | Explicit JSON allow/flag/protect literals | Config bytes bound; no user regex or silent replacements |
| Review accounting | Optional per-finding kept/resolved/needs_author decisions; strict flag | Self-attestation, not authenticated human approval |
| Meaning-risk cues | Conditions, exceptions, quantifiers, time, comparison, per-sentence cue redistribution | Still misses actor swaps and same-cue semantic changes |
| Protected spans | Quotes, frontmatter, markup attributes, relative links and reference definitions | Small recognizer, not full CommonMark or multilingual quote parser |
| File safety | Regular files only, prevents FIFO blocking and source/config overwrite | Trusted-workspace assumption; no hostile concurrent symlink-race defense |
| Host execution | Exact independently permitted checker calls; narrow denied-command reporting; no bypass | Neko trial separately reported; no automatic hooks/settings changed |
| Evidence | 103 distinct unit tests passed (69 existing +34 new), compile and skill validator passed | Does not establish a general writing-quality improvement |

## Intentionally not ported

Japanese detectors and word lists, Japanese punctuation restrictions and honorific transformations, source Unicode data tables, full Markdown parser, host hooks, stdin/no-record mode, regex project patterns and upstream corpus benchmark. The manual no-file fallback remains. No claim of full Yomiyasu equivalence, exhaustive Vietnamese grammar or coverage of every regional/community language.

## Reading the evidence

`parity-audit-v1.md` is the independent assessment of v1 before this revision, not certification of v2. `unit-tests-v2.log` records executed deterministic tests. `historical-v1/` retains original v1 reports for provenance; those reports do not describe the current package and their self-rated model trials are not independent holdout evidence.

Live Neko evaluation is separate from unit tests. Report exact model, steps and verify results; do not equate successful hashes with meaning preservation. The prior sunrise run is a development regression and cannot become an unseen holdout simply by changing wording.

## Remaining limits

Semantic review is still essential: same words can attach to different people or scopes; same names and numbers can express changed claims. Quote recognition excludes multiline and some locale conventions. URL punctuation can be ambiguous when punctuation belongs to the path. Files are read into memory with no hard size cap; very large/adversarial files are not an approved benchmark target and need separate resource hardening. File paths are constrained but this tool is not a sandbox. Review records can contain private source text in diffs; share only with authorized recipients. A checksum is not a signature.

## Attribution

Architecture adapted from nanaism/yomiyasu v3.0.0, tagged tree 7b212ff2f037953b8c233ae315e5c08e7fc36da6. MIT copyright and permission notice retained in LICENSE. Upstream Japanese grammar rules and bundled Unicode datasets are not copied as Vietnamese rules/data. This revision adds independently written Vietnamese guidance and checker extensions. The upstream repository does not endorse this derivative.
