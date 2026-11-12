# v3 evaluation: evidence, not a quality certificate

## What prompted revision
The owner preferred v1 to v2. Recovered historical outputs show a concrete v2 prose problem: “tiếng nước vỗ đều đều vào mạn phà, một mình”. Its editing output also changed ambiguous “họ” into “Ban quản lý” before asking the user to confirm. v1 retained the referent but appended workflow text to a paragraph-only request. All three historical editing arms preserved the core negation/causality distinctions; there was no demonstrated general v2 advantage. Full historical outputs are in historical-v1-v2-outputs.md.

## Actual fresh behavior runs
- Five no-domain-skill tasks and the same five with v3: baseline-output.md and forward-output.md. These test short informal editing, delay notice, ambiguous referents, four-line lục bát and object-driven description.
- Six separately authored, frozen holdout tasks: holdout-prompts.json and holdout-output.md. Their author did not read the previous test outputs; prompts were saved before solving. This is one AI evaluation session, not six independent human readers.
- Ten fresh-context ambiguity microtests, five per arm: microtest-outputs.md. Control and treatment both preserve the ambiguous referent. No superiority established. v3 has fewer distinct surface strings, but this is not a quality measure.
- One v3 sunrise regression on the original task: sunrise-v3.txt. This uses the current evaluation model, not the historical GLM-5.3 configuration. Any comparison confounds model/runtime with skill version.

The fresh evaluation runtime does not expose a controlled model snapshot, random seed or authoritative token/cost trace in these artifacts. The sessions genuinely generated the supplied outputs, but exact statistical replication is not claimed. No new request to z.ai was made: prior authorization was tied to the historical round. No private correspondence or external corpus text was sent for these tests.

## Observed outcomes and negatives
The baseline is already strong. It preserves the informal message and ambiguous chị; its poem has regular 6/8/6/8, matched required tones and plausible rhymes. Its prose has 98 whitespace-delimited units and begins rain at the end, which may stretch “sắp mưa”.

v3 preserves the same message and ambiguity. Its delay message uses an explicit skill example, so it is not generalization evidence. Its poem has 6/8/6/8 and required orthographic tones, but repeats “tay” as rhyme and imagery; this is aesthetically weaker than the baseline in that respect. The initial thưa–lùa rhyme was rejected manually and corrected, demonstrating the script alone cannot check rhyme. Its prose has 103 units, develops the key through visible operations, and keeps rain impending. These are examples, not a universal win.

The holdout completes prose, restrained texting, regional dialogue and conservative editing without stereotyped slang stuffing. The six-line poem meets the traditional formal checks but has questionable “vạt áo dài” imagery and invented emotional implications. Its prompt “ở cửa sau khi con chuyển nhà” is grammatically ambiguous: the intended back-door reading and the after-moving reading must not be conflated. A reviewer initially called a location violation; this requires qualification, not a definite failed constraint. Historical-language claims in the knowledge answer were not independently source-verified in that run and are explicitly presented with suggested checks.

The sunrise regression contains one paragraph, 114 whitespace-delimited units, a traceable light progression and chain sound, without an audit appendix. A prose-only blinded comparison favored v3, then v1, then v2 for this brief, while noting v1 has more memorable life and v3 safer imagery. See blind-prose-review.md. This remains one AI reader’s taste and is confounded by different generation models, not native-reader consensus or causal proof.

## Deterministic verification
119 unittest tests pass after integration. This includes the inherited v2 guard suite plus 16 poetry diagnostics/boundary tests. New poetry code first failed missing-implementation tests; integrated path tests later exposed nine unsafe subcases. Reusing safe_path fixed outside/hidden/traversal/symlink/special-file reads. A test-path packaging error was also observed and repaired. Unit test counts measure covered program behavior, not language quality.

The unchanged text guard remains engine 2.0.0/schema 2. The package is version 3.0.0. Poetry analysis retains original bytes as decoded text, uses NFC only for analysis, reports candidate counts and orthographic tone, and leaves every rhyme pair for human review. It cannot establish rhythm, phonological rhyme, semantics or literary merit. Path confinement still assumes no concurrent symlink replacement.

## What is not established
No newly matched v1/v2/v3 GLM run, broad corpus benchmark, blinded multi-region human panel, commercial corpus clearance, language-wide certification, or host installation was completed. Research is selective through 12 November 2026, not proof of every current trend. A later external-model round needs scope-appropriate approval. Wider conclusions require matched repeated runs and independent Vietnamese readers from relevant communities.

Final malformed-symlink regression: a self-referential symlink raised uncaught RuntimeError on Python 3.12; a failing test reproduced it, then explicit handling produced exit 2 without traceback. Final full suite: 119 tests.
