# Evaluation status for v2

The intended six-cell Neko + GLM external-provider comparison did not produce a completed result. The external request required additional authorization, so it was stopped without an alternate route or retry. No v2 model-quality or live-Neko workflow success is claimed. An initial process had an uncertain outcome at the time of the block; no completed model result is used here.

A separate local CLI probe executed seven operations: edit lint/diff/check/verify, compose check/verify, and stale compose verify. Both exact records verified successfully; modifying the final invalidated the compose record. The edit check correctly returned findings for the original punctuation even though its corrected output was clean. Exact outputs are under local-cli-v2/results.json. These are constructed deterministic probe inputs/outputs, not independently generated model rewrites. The compose final in that fixture is intentionally mutated for the last stale-record rejection; the saved record is deliberately stale afterward.

For future model evaluation, choose fresh holdout prompts: the causal probe text has now been inspected during packaging, and the sunrise family was already used during development. Freeze the packaged hashes before execution. Obtain the required permission before sending prompts or skill material to an external provider.
