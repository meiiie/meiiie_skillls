# Independent audit: Việt ngữ toàn thư v1 against Yomiyasu v3.0.0

Audit date: 2026-11-12 UTC. This audits v1, not the concurrently developing v2. No product code was changed by this auditor.

## Finding

v1 is a conservative Vietnamese editing guide with a small deterministic guard. It adopts core preservation and final-file verification ideas, but is not a full architecture port. Its own architecture document correctly disclaims compatibility. The main improvement is to make the important editorial mechanisms operational, rather than translate Japanese rules or enlarge a list of forbidden words.

## Exact upstream evidence

Fetched via connected GitHub tool:

- [Tagged SKILL.md](https://github.com/nanaism/yomiyasu/blob/v3.0.0/skills/yomiyasu/SKILL.md), blob `a1cc491efb3e9185b5609be92003a7f87a63cf8a`, full contents read.
- [Recursive tagged tree](https://api.github.com/repos/nanaism/yomiyasu/git/trees/v3.0.0?recursive=1), tree `7b212ff2f037953b8c233ae315e5c08e7fc36da6`, not truncated. This establishes file existence and exact paths, not that every implementation was read or tested.
- Upstream root references/scripts are mirrored in `skills/yomiyasu/`. Paths below refer to the installed skill tree unless explicitly stated otherwise.

## Component parity matrix

| Component and upstream evidence | v1 implementation | Assessment and priority |
|---|---|---|
| Explicit invocation; SKILL frontmatter and opening paragraphs | Broad Vietnamese automatic selection and no directory discovery | Intentional host-policy adaptation, not a defect. Preserve narrow document scope and avoid silently scanning private files. |
| Editing versus composing; SKILL first section and Step 3 `--source`/`--material` | Text says distinguish modes; CLI requires before and after for all operations | P1 operational gap. Add explicit compose mode/material grounding or an honest separate compose protocol. Do not compare a writing request as if it were an original paragraph. |
| Four top-level invariants and six-point rephrase test; SKILL section 1 and Step 2, `references/rephrase-test.md` | Six invariants in mandatory meaning reference | Strong adaptation. Add a per-edit acceptance/rollback procedure and negative examples, rather than only a checklist. |
| Sentence function inventory before/after; SKILL section 1 | Speech acts mentioned as one invariant | P1 mechanism under-specified. Preserve question, joke, irony, suggestion, obligation, quotation and hypothesis at sentence level. |
| Document stance, separate from genre; SKILL section 1 (`勧め`, `決まり`, `説明`) | Genre table, no distinct stance procedure | P1 add recommendation/rule/explanation distinctions, actor, tense and commitment checks. Technical genre alone must not turn advice into obligation. |
| Genre-specific mandatory loading; `references/doc-types/` | One table in genres-and-register.md | Partial adaptation. Exact 13 upstream files: article, essay, formal, incident, mail, manual, minutes, paper, pr, promo, proposal, script, slides. v1 table lacks a dedicated slide route. Add targeted genre references with positive examples and exceptions, not equal-size boilerplate. |
| Audience and relationship; `references/audience.md`, `references/persona.md` and Step 1 | Three audience levels and Vietnamese pronoun caution | Good foundation, compressed. Add source-grounded explanations and relationship-specific pronoun tests. Japanese honorific transforms must not be ported. |
| Local ambiguity and factual recovery; `references/fact-recovery.md`, `fact-recovery-details.md`, SKILL Step 2 | Causality/fact-check separation, source list | P1 add source ledger for missing actionable values, contradictions and proposed insertions. Preserve unknowns; do not invent actors, dates or mechanisms. Do not treat prior AI prose as evidence. |
| Concrete editorial diagnoses; `references/calques.md`, `slop-catalog.md`, `review-points.md`, `domains/` | Generic warnings about vague language and literal translation | P1 for quality. Add Vietnamese contextual before/after/counterexample sets for nominalization, empty evaluation, literal translation, stacked metaphors and redundant conclusions. A ban list or AI-authorship detector is inappropriate. |
| Contextual one-location edits; SKILL Step 2 | No bulk regex rewrites, read whole text | Adapted. Add bounded correction loop: one candidate, reject changed meaning, one post-check revision rather than endless warning minimization. |
| Lint/diff/check/verify; SKILL Steps 2–5; scripts/yomiyasu_lint.py, yomiyasu_diff.py, yomiyasu_check.py | Single viet_guard.py with four commands, SHA-256 records and full textual diff | Same high-level separation, much smaller detection coverage. Do not claim algorithm equivalence. Verification is artifact consistency, not approval or semantic certification. |
| Markdown visibility; scripts/markdown_visibility.py | Small fence/backtick/HTTP recognizer | P1 protect quotations and link destinations explicitly or document manual-only coverage. Full CommonMark is not implemented. |
| stdin and no-record; SKILL Steps 3 and 5 | Manual fallback if files prohibited | Intentional documented omission, but practical gap for chat/no-save requests. Optional stdin should preserve privacy and precise unverified status. |
| Custom allow/flag/pattern files; SKILL Step 1 | Not implemented | P2 add scoped literal glossary first if needed. Arbitrary regex needs resource limits and validation; do not treat glossary content as instructions. |
| Optional host integration; scripts/yomiyasu_hook.py and plugin manifests in tree | No hook or plugin integration | Not ported, correctly disclosed. Installation must never silently change host settings or imply enforcement. |
| Evaluation; root evals/comparison_benchmark.md and tests/ | 69 deterministic tests, 12 self-reviewed editing cases, separate 1-pair Neko trial | Different evidence types. Do not infer quality uplift or general linguistic coverage from successful hash verification. |
| Vietnamese regional and community coverage | Dedicated references and 54-group registry | Vietnamese addition, not inherited parity. Registry coverage is not language competence; keep actual source depth and gaps explicit. |

## Reproduced correctness/security cases in v1

Ran against local `scripts/viet_guard.py` (VERSION 1.1.1). Findings below are observed, not speculative:

1. `Minh nói: “đồng ý”.` → `Minh nói: “từ chối”.`: `risks=[]`. Exact quotation preservation is a documented AI requirement, but not enforced by protected-span diff. Add quote tests, including apostrophes in names and legitimate quotation editing requested by user.
2. `Xem [bản](docs/a.md).` → `Xem [bản](docs/b.md).`: `risks=[]`. Relative link target not protected. Test Markdown links, reference definitions, images and balanced parentheses.
3. `Lan không đi. Minh đi.` → `Lan đi. Minh không đi.`: `risks=[]`. Document-global keyword sequences cannot bind negation to actors. This is a known heuristic limit, not something solvable by adding more keywords. Require sentence-by-sentence semantic review and keep this as a negative control.
4. `Xem https://example.com.` → `Xem https://example.com!`: `protected_changed` because trailing punctuation is included in the URL token. Warn conservatively but do not describe it as proven URL corruption. Add punctuation and balanced-delimiter boundary tests.
5. A FIFO named `input.txt` inside permitted cwd passed safe_path and `lint input.txt` blocked for over one second until the test killed its subprocess. Reject non-regular existing inputs/records and non-regular output targets before I/O. Add timeout-bounded FIFO tests. This is a local availability failure, not demonstrated private-data exfiltration.

Other residual risks: file content is read without size limits; regex/SequenceMatcher cost needs adversarial-length tests; safe-path resolution remains subject to races in concurrently hostile workspaces, already explicitly disclaimed. A checksum can be regenerated by anyone who can edit the record and is not a signature. Records include original/edited text in diffs, so they should not be shared casually.

## Real Neko experiment and its limitations

Read `sunrise-neko-comparison/REPORT.md` and `run.ts`. The real Neko Agent, ToolRegistry, loadSkill and AnthropicProvider ran against GLM-5.3. This was an embedded runtime test, not CLI/TUI end-to-end. Fresh histories, one sample per arm, temperature 0, no seed, baseline first. Dream patch present but no Dream memory consolidation used.

- Baseline: 15.608 seconds, 1 request, 3,205 reported total tokens.
- Skill arm: 60.201 seconds, 4 requests, 29,659 reported total tokens including 18,496 cached tokens.
- Treatment loaded skill plus meaning, genre, orthography and checking references.
- Harness rejected `ls -R` because it permitted only narrow checker Python invocations. The model generalized this to execution being unavailable and never attempted the allowed checker. No lint/diff/check/verify ran.
- This is partial instruction use, not a successful complete workflow. Do not state Python or Neko lacked execution capability. A denial of listing is not a denial of a separately permitted checker, but any actual access denial must not be bypassed.
- Treatment added a heading and workflow note to a simple request for one descriptive paragraph. Its prose was more elaborate but retained awkward imagery. No blind independent quality assessment supports an uplift claim.

## Recommended v2 acceptance tests

1. Creative paragraph: output only the paragraph, coherent physical scene, no invented assertion of real-world evidence, no source-as-original fiction.
2. Factual composition: material containing names, dates, conditions; verify grounding and differentiate creative details from factual additions.
3. Narrow command rejection: model reports exactly the failed action, then uses a separately allowed checker without attempting denied access again.
4. Explicit no-file request: no file writes and no false hash-verification claim; stdin behavior tested if implemented.
5. Three negative controls above must remain visible in evaluation even if new heuristics catch them; no zero-risk semantic-pass shortcut.
6. Genre matrix: poem, incident report, proposal, minutes, promotional prose, email and slide bullets. Same expression may correctly change in one genre and remain in another.
7. Full final artifact: one-byte changes invalidate records; same-path and hard-link record aliases cannot overwrite source/final; malformed/extra schema fields fail.
8. Resource and path safety: FIFO/socket/device targets rejected, traversal and symlink escapes rejected, large/pathological text bounded, private review records not bundled by default.
9. Independent held-out comparison: randomized A/B order, identical model/settings, multiple prompts and repeats, blind native-Vietnamese raters, separate preservation/readability/genre/workflow scores, latency and cache-aware token accounting. Freeze skill hash before evaluation.

This report does not certify v2 fixes. Each accepted recommendation needs its own test result against the packaged artifact.
