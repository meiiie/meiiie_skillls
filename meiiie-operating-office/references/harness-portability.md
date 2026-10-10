# Harness portability and bounded context

Use when importing orchestration or context-saving tools into another client. This reference supplements the office work-package rules; it does not create a runtime or require delegation for ordinary work.

## Check the actual capabilities

Identify the client's worker API, checkout ownership, shared files and completion/failure reporting. Do not assume a private tool or cloud execution is available. Where providers are restricted, verify the child's actual route; a parent setting is not proof of inheritance. Two agents can use the same model. Multiple roles or agreeing answers do not establish correctness.

Where event recording is required, verify the child's real inputs, tools and completion through that path. Parent hooks, metadata and offline fixtures do not establish child coverage. Never reconstruct missing events as observed logs.

## Delegate by context and ownership

Independent source reviews, read-only audits and disjoint implementation packages can benefit from separate contexts. Establish shared interfaces first. Serialize prerequisites and shared writes; one lead integrates the result. Start with a small worker when runtime behavior remains uncertain.

Give each worker the task, relevant file pointers, owned output, criteria, authority, dependencies and time/cost limits. Avoid copying the full conversation when only a few inputs are needed. Put substantial results in an artifact and return the important findings, checks and remaining gaps. The lead inspects the relevant artifact before accepting it.

[Poteto/Pstack](https://github.com/cursor/plugins/tree/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack) illustrates context isolation and worker artifacts. Its Cursor Task types, model defaults, cloud options and integrations are examples from that runtime, not portable commands or permission grants.

## Choose context-saving tools by fit

MCP is a tool protocol, not a token-saving guarantee. Definitions, results, repeated calls, retries and setup contribute to cost. Prefer an existing bounded CLI or source lookup when it satisfies the task. Add a server for a needed capability and verify tool selection in the actual client version.

[RTK](https://github.com/rtk-ai/rtk/tree/e001f773f80b22b7dc4c7a79521b30e35aaef026) is a deterministic CLI output filter, not an LLM or an MCP server. Noisy output can shrink, while compact native commands may already be cheaper. Measure representative outputs, exit status and important diagnostics. Terminal-output reduction is not total API-spend reduction.

Filtered output is a lossy view. Read unfiltered code/diffs for exact editing and review; keep recovery for failures or omitted details. Filters are not credential redaction or a substitute for required original records. Review command-rewrite hooks before modifying an existing audited hook chain; manual CLI use need not install a hook.

For a remote retrieval server, inspect what leaves the machine and whether its backend uses additional inference when the environment restricts that. A local MCP package does not make its backend local. Missing evidence remains a pending capability.

## Count shared resources

Count main, workers, product requests and work in flight against shared money and rate limits. Parallelism can improve time or reduce repeated parent context while increasing total tokens and integration effort. Compare useful accepted artifacts, latency and total cost. A new chat or worker does not reset a shared limit.

Use a bounded check that can change the decision. Stop broadening when the method meets the task or coordination costs outweigh independent work. Direct execution is appropriate when one agent and local tools suffice.
