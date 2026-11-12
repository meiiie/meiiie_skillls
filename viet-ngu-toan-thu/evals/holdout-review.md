# Independent holdout review

## Method and limits

Evaluator: an independent AI worker, not a panel of Vietnamese native speakers. Six synthetic prompts were written and saved before answers, then answered using SKILL.md and relevant references: literary-craft, poetry, regional-and-community, meaning-and-causality, texting-pragmatics and knowledge-and-corpora. No previous evaluation cases or answers were opened. No external model, private user corpus, or external communication was used. The skill was not edited. Review was performed after saving answers. There is no claim that this sample demonstrates superiority over another skill/version.

The prompts are new to this evaluator's session, not proven absent from every model's training data. Prompt author, respondent and critic are the same worker, which limits independence of the judgments. Exact counts and text comparisons support narrow observations; naturalness judgments remain subjective.

## Important findings

1. H2 misses a concrete spatial detail: “sau cửa” means behind the door, whereas the requested “cửa sau” is the back door. Formal meter did not catch this semantic slippage.
2. H2 also has craft weaknesses despite correct basic meter: “vạt áo dài” can briefly evoke an áo dài rather than the long flap of a raincoat; “chẳng ai trở về” pushes the ordinary move into a more absolute abandonment. The poem is intelligible but conventional and somewhat assembled around rhyme.
3. H5 is a cautious, broadly plausible historical explanation, but its concrete claims and bibliographic entries were not checked against the original sources in this restricted read-only skill/reference evaluation. It should not be presented as completed source-verified research. The answer explicitly discloses that limit.

## H1: microfiction

The answer has 210 whitespace-separated tokens, within the requested 180–230 “chữ” under the common whitespace-count convention. It uses first person, a watch repair shop being packed up, a final customer, direct observable actions, and ends with picking up a chair shim. None of the three banned expressions occurs. The cut ring, shared child, familiar chair and buckle hole suggest an earlier marriage without naming it.

Strength: the chair shim is introduced as a functional object and returns as a portable remnant; it is not merely a closing moral. Dialogue carries history with little explanation.

Reservation: a cut ring and shared child do not logically prove divorce; readers could also imagine spouses living apart or an unresolved relationship. That ambiguity is defensible for “để người đọc tự nhận ra,” but not a verified fact about the fiction. Sugar cubes plus ring plus shared child plus buckle create several emotional cues in a small space and may feel carefully planted. No claim of exceptional literary quality is justified.

## H2: strict lục bát

Manual syllable checks, corroborated by simple whitespace counts:

| Line | Count | Even-position tones | Required rhyme link |
|---|---:|---|---|
| Con đi, cửa khép bên thềm | 6 | đi B / khép T / thềm B | thềm → mềm |
| Áo mưa mẹ mắc vẫn mềm nếp vai | 8 | mưa B / mắc T / mềm B / vai B | vai → dài |
| Gió lùa qua vạt áo dài | 6 | lùa B / vạt T / dài B | dài → ai |
| Mẹ đưa tay vuốt, chẳng ai trở về | 8 | đưa B / vuốt T / ai B / về B | về → đê |
| Nhà con ở tận bên đê | 6 | con B / tận T / đê B | đê → về |
| Áo treo sau cửa, mưa về lại lay | 8 | treo B / cửa T / về B / lay B | terminal |

The bát lines alternate huyền/ngang at positions 6 and 8: mềm/vai, ai/về, về/lay. Rhyme chains use êm, ai and ê. Counts, basic even-position tone pattern and rhyme links pass a manual formal audit. Forbidden expressions absent; six lines and no title/explanation in the answer.

Nevertheless, concrete semantic fidelity fails on back-door location, and aesthetic reservations remain as above. This is direct behavioral evidence that a form-compliant output can miss a content constraint. Do not silently repair the saved answer to make the evaluation pass.

## H3: cancellation text

One short message preserves tui/bà, uses one “hong” naturally, apologizes, states inability to attend and asks the friend to release the seat. It adds no promise to compensate, no new appointment, no fabricated reason beyond being busy. The repeated “tui” has an ordinary conversational function, though the last clause could be lighter. No material failure found.

## H4: restrained regional dialogue

Exactly two sentences. “Có khi” preserves possible rather than certain flooding. The advice is mild; no invented local place or stereotyped personality is supplied. “Nghe” gives a restrained regional flavor and remains understandable.

Limit: “nghe” is not uniquely Huế. The answer should be judged as plausible restrained dialogue, not authenticated Huế sociolinguistic representation. The age, occupation and city alone do not determine a speaker's exact wording. Native-speaker review would be needed for a strong local-authenticity claim. No material failure found under the prompt's request for only a slight local flavor.

## H5: historical knowledge

The answer correctly distinguishes a publication milestone from sole invention and distinguishes modern “chữ Quốc ngữ” from contextual historical uses of “quốc ngữ.” It avoids invented quotations/page numbers and names two identifiable works rather than vague authorities. The 1651 dictionary title and attribution, Rome publication, predecessor names and the Roland Jacques title/year are established bibliographic/historical claims in the evaluator's knowledge, not independently checked facts in this run.

Open verification: read the dictionary's actual preface to establish exactly which predecessors it credits; verify bibliographic details of the Jacques edition; supply a historical dictionary or a dated example for the broader semantic history of “quốc ngữ.” The two suggested sources mainly support script-development history, not necessarily every semantic assertion. This limits the completeness of sourcing. The cautious final sentence is honest but longer and more procedural than a fully checked answer would need.

## H6: conservative edit

Comparison against prompt: the sole change is “lẻ” → “lẽ” in “có lẽ.” The ambiguous “cô ấy” remains unresolved; “đc,” “tui,” “bà,” “nha,” “tại,” and lowercase “thứ sáu” remain. The if-clause, uncertainty, timing, denial of confirmed arrival, and incomplete checking are unchanged. No note is appended, respecting “chỉ trả đoạn đã sửa.” No material failure found.

## Suggested follow-up, not implemented

Use a content-constraint reread after the poetry form pass: list required objects, location, speaker/viewpoint and event state, then inspect the actual meaning of each phrase. In particular, word order is not a bag-of-words check: “cửa sau” and “sau cửa” are not equivalent. A future source-verified knowledge evaluation should give access to exact primary/secondary references and audit claim-to-source mapping. A human regional reader should review dialogue if local authenticity becomes a product claim.

## Clarification after review of the frozen prompt

The earlier categorical back-door failure is withdrawn. The actual frozen prompt reads “chiếc áo mưa của mẹ còn treo ở cửa sau khi con chuyển nhà.” Its natural parsing is “[treo ở cửa] [sau khi con chuyển nhà]”: hanging at the door after the child moves house. It does not unambiguously require a back door. My earlier assessment incorrectly elevated my unstated prompt-author intention into a textual requirement.

The output's “Áo treo sau cửa” places the raincoat behind a door and can reasonably satisfy that broader door location. It must therefore not be counted as a definite spatial-constraint violation. If a back door were required, a new prompt would need to say, for example, “treo ở cửa phía sau nhà”; that would be a different test, not a retroactive correction to this one.

Corrected assessment of H2: the six-line poem passes the audited basic lục bát form and contains no demonstrated hard-constraint violation. The craft reservations about the potentially ambiguous “vạt áo dài,” the heightened “chẳng ai trở về,” and conventional imagery remain subjective concerns, not formal failures. The original prompt and output remain unchanged, and the earlier review text is retained above for auditability. This correction is a reviewer error caught by examining the exact prompt, not evidence of a skill improvement or regression.
