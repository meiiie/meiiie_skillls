---
name: meiiie-explain-clearly
description: Explain difficult ideas with precise, plain Vietnamese or English and choose text, diagrams, interactive HTML, or narrated visual explanations by learning need. Use for conceptual explanations, technical teaching, simplifying dense material without losing qualifications, and bespoke learning artifacts. Apply STE-inspired clarity without claiming ASD-STE100 compliance. Complement existing design and video production skills; do not activate for unrelated media production, generic copy polish, or formal STE certification alone.
---

# Meiiie Explain Clearly

Make the learner able to explain, predict, or apply the idea. Optimize for understanding and oversight, not impressive output or mandatory multimedia. Stay topic-, model-, and provider-independent.

## 1. Frame the learning need

- Extract the question, audience, prior knowledge, language, requested format, and intended takeaway from available context. Assume a sensible beginner level if none is given; ask only when a missing detail changes the explanation materially.
- Use the requested language. Otherwise follow the user's language; Vietnamese and English are both supported. Prefer natural Vietnamese over literal English syntax. Keep indispensable English technical terms beside a short Vietnamese definition on first use. If a translation is uncertain, mark it and preserve the source term rather than inventing certainty.
- Define one testable learning goal: what should the learner predict, distinguish, or do afterward? Identify the likely misconception and the minimum prerequisites. Do this privately or in a short opening, not an intake form.
- Verify niche, current, contested, or high-stakes facts using relevant primary sources. Distinguish supplied claims, observed facts, assumptions, and simplified models. A supplied attribution or screenshot is not proof of authorship or correctness.

## 2. Build a precise plain-language explanation

1. Lead with the answer or core mental model.
2. Explain the mechanism in a short causal sequence. Introduce prerequisites only when needed.
3. Use one concrete worked example with traceable inputs and outcomes.
4. State the boundary: when the model, analogy, or result no longer applies.
5. End with a small prediction or application check when useful; include an answer or explanation so it can stand alone. Do not turn every quick answer into a quiz.

Apply a strong STE-inspired house style. Treat “about 80% STE” as a soft editorial direction, never a measured score. Prefer explicit subjects, active verbs, one main idea per sentence, short paragraphs, and one instruction per step. Put conditions before the dependent action. Use a small glossary: same concept, same term. Define unfamiliar terms instead of replacing precise concepts with vague words.

Preserve all meaningful negations, quantifiers, units, ranges, prerequisites, exceptions, causal direction, and uncertainty. Do not change “may” to “will,” “some” to “all,” correlation to causation, or an example into evidence. Retain an equation when it makes the relation clearer; define symbols and connect it to the example. Split overloaded sentences without removing their conditions. Word counts are editing hints, not a correctness test; do not count Vietnamese syllables as English words.

Use analogies as labeled mappings. Say which objects/relations correspond and where the analogy breaks. Avoid anthropomorphism that quietly attributes goals or understanding to a mechanism. Do not simplify safety-critical procedures beyond what verified instructions support.

Read [clarity-and-sources.md](references/clarity-and-sources.md) for STE scope and formal-conformance boundaries. Read [worked-examples.md](references/worked-examples.md) only for examples of the approach; never inherit their topic or audience.

## 3. Choose the least costly medium that teaches the relation

Honor an explicit format request. Otherwise choose by the cognitive task, not a fixed text → diagram → HTML → video ladder:

- **Text:** a definition, distinction, argument, or short causal account. Stay in chat when that is enough.
- **Diagram:** parts, spatial relations, flows, dependencies, timelines, or comparison. Use labeled arrows and a legend; say what arrows encode. Keep scale honest and make a text equivalent available. A decorative illustration is not explanatory evidence.
- **Interactive HTML:** changing a parameter, comparing hypotheses, or predicting a response teaches more than watching a fixed example. Define controls → state → observable output → explanation. Provide defaults, bounded valid inputs, reset, units, and at least one useful edge case. Separate simulated behavior from observed real behavior. Never add an interaction whose only role is spectacle.
- **Video:** temporal change, coordinated geometry, a demonstration, or narration meaningfully helps. Plan the exact concept-to-visible-change mapping. Treat a request for a “3Blue1Brown-style” explanation as a request for original, mathematically grounded visual teaching, not a claim of affiliation or copied assets, voice, or branding. Prefer controllable vector/math animation for exact relationships; generated footage is optional.

A short text explanation can accompany any medium for orientation and fallback. Do not produce additional formats just to complete a ladder or expand a brief into a course.

## 4. Build through the actual artifact workflow

Read the relevant available skill before production. Use `visualize` for supported in-conversation interactive explanations, diagram/chart tools for deterministic structures or data, and document/presentation skills for those requested files. Use the current Sites/building skill for a requested hosted explainer; local repository work follows the software-engineering and environment rules. Use `meiiie-reference-to-product` only when reference fidelity, brand, typography, or rendered layout work is needed.

For a requested video, pass the learning goal, evidence, glossary, causal sequence, visual mappings, analogy limits, language, and comprehension check to `meiiie-product-motion` and the relevant available production provider. Let that skill own shots, audio, rendering, budget and final media QA. A storyboard, script, HTML animation, and encoded video are distinct deliverables.

Check tool access and existing authorized resources. Never hardcode a model, ask for API keys as a default, invent provider capabilities, or silently make paid calls. Obtain any required budget/provider and data-sharing permission before paid or external production. Use safe local deterministic drafts while dependent approval is pending. Do not publish a live Site merely to demonstrate format selection.

## 5. Verify meaning and the real artifact

- Check factual and mathematical consistency against the evidence and worked example. Trace each important qualification into the final explanation. Check the comprehension answer and a counterexample.
- Check terminology, audience fit, readable density, and the analogy boundary. Review Vietnamese accents and natural phrasing; use fonts with actual Vietnamese coverage and adequate line boxes.
- For diagrams, inspect labels, arrow direction, legend, and reading order. For HTML, test keyboard access, visible focus, control labels, reset, input bounds, narrow-screen reflow, and the displayed state against the model. Keep content understandable without color alone and with reduced motion; stop/pause moving content where appropriate.
- For video, verify actual narration, captions/transcript, readable holds, timing, and visual correspondence in the encoded output. Do not report caption or font checks that were only planned.
- Distinguish drafted, source-checked, executed, browser-rendered, and watched/exported evidence. Inspect the actual deliverable after changes. Report material gaps plainly; do not claim formal STE compliance, accessibility certification, or learning effectiveness from a checklist alone.

Deliver the requested explanation or artifact, the key takeaway, and only consequential caveats. Keep sources near claims when useful. Finish at the requested endpoint.
