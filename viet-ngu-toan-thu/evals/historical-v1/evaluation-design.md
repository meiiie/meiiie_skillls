# Vietnamese editing evaluation design

## Grounding and scope

Verified source: https://github.com/nanaism/yomiyasu/blob/v3.0.0/README.en.md (read through GitHub connector). Its useful transferable principles are minimal intervention; preservation of numbers, negation, conditions, actors and certainty; respect for genre and relationship; contextual review rather than mechanical substitutions; final-draft lint plus source/final diff; and explicit acknowledgment that fixed-pattern checks cannot certify meaning or readability. Its Japanese lexical rules and Japanese evaluation results are NOT evidence of Vietnamese quality.

This is a proposed test specification, not completed model evaluation. Examples below are original test fixtures, not declarations of universal Vietnamese norms. An unchanged result can be correct. Multiple rewrites may pass.

## Critical semantic cases

For each case: request = “Chỉnh cho dễ đọc, không đổi ý”, unless overridden. Preserve all listed invariants. Any violation is a critical failure even if the prose sounds better.

1. **Causality**: “Số đơn giảm sau khi đổi giao diện; chưa đủ dữ liệu để nói giao diện là nguyên nhân.” Preserve temporal sequence and explicitly unproven causation. Reject “Do đổi giao diện, số đơn giảm.”
2. **Conditional possibility**: “Nếu được duyệt, nhóm có thể triển khai trong tháng 6.” Preserve approval condition, possibility, and timeframe. Reject a promise using “sẽ triển khai”.
3. **Nested negation**: “Mình chưa nói là Lan không đồng ý.” Preserve what the speaker has not said; do not assert Lan agrees or disagrees. Leaving intact passes.
4. **Scope of quantifier**: “Không phải khách nào cũng được hoàn tiền.” Preserve not-all; reject “Không khách nào được hoàn tiền.”
5. **Only + exception**: “Chỉ hoàn tiền nếu hủy trước 18 giờ, trừ vé khuyến mại.” Preserve eligibility condition, cutoff, and exclusion. Do not infer a date/timezone or change “trước” to “đến”.
6. **Attribution and uncertainty**: “Theo Lan, lỗi có thể nằm ở bộ nhớ đệm; nhóm chưa xác nhận.” Preserve Lan as source, possibility, and lack of group confirmation. Reject a factual diagnosis.
7. **Actor/recipient**: “Lan gửi bản nháp cho Minh để Minh chuyển cho Huy.” Preserve both transfers and who performs each. Reject “Minh gửi bản nháp cho Lan”.
8. **Omitted actor**: “Cần xác nhận trước thứ Sáu.” Do not invent a PM, user, manager, calendar date or approver. Preserve unspecified actor or ask only if action depends on it.
9. **Numbers/units**: “Tỷ lệ lỗi giảm từ 5% xuống 3%, tức giảm 2 điểm phần trăm.” Preserve 5%, 3%, 2 percentage points. Reject “giảm 2%” as a substitute.
10. **Range/comparison**: “Khoảng 12–15 người tham gia; không quá 3 người đến muộn.” Preserve approximation, range and upper bound. Reject exact attendance or “ít nhất 3”.
11. **Necessity vs sufficiency**: “Có tài khoản là điều kiện cần, nhưng chưa đủ để được duyệt.” Preserve both clauses; do not say account ownership guarantees approval.
12. **Quoted wording**: “Biên bản ghi nguyên văn: ‘Tôi không cam kết giao vào thứ Sáu.’” Preserve quoted text exactly in copyediting mode, especially negation and absence of commitment.

12b. **Do not silently weaken source claims**: “Thay giao diện khiến số đơn giảm.” With request “Chỉ sửa lỗi diễn đạt rõ ràng”, do not rewrite to “Chưa có bằng chứng cho thấy giao diện làm giảm số đơn.” That introduces an unsupported claim about the evidence and changes the author's certainty. A separate note may flag the causal claim for verification; a qualified alternative must be labeled as an optional substantive change, not silently substituted. Source strength must be preserved in BOTH directions. The build worker reported this risk in an independent baseline at `vietnamese-skill-work/baseline.md`; surrounding prompt wording made scope partly ambiguous, so this is a diagnostic case, not proof of a model-level advantage.

## Vietnamese-specific restraint and style cases

13. **Dialect + relationship** (request: fix punctuation only): “Dạ bữa ni em gửi anh bản nháp nghen.” Adding a comma after “Dạ” is acceptable; preserve “bữa ni”, “nghen”, “em”, “anh”. Do not label dialect incorrect or replace with a single regional standard.
14. **Register switch explicitly requested**: Same sentence, request “Chuyển sang giọng trung tính cho báo cáo nội bộ.” Dialect neutralization is now allowed, but do not invent completion or change future/current sending to a past event. Score separately from case 13.
15. **Ethnonyms**: “Bài viết nhắc đến Ê Đê, M’nông và H’Mông.” Preserve source spelling and identity absent requested house style or verified source. No universal auto-replacement mapping for apostrophes, spaces, or capitalization.
16. **Personal names**: “H’Hen Niê trao đổi với Y Đôn.” Preserve names exactly; do not remove apostrophes or infer gender, titles, ethnicity, or pronouns.
17. **Vietnamese orthographic variants**: “Tài liệu dùng ‘kĩ thuật’ và ‘lí thuyết’.” Do not categorically mark these errors or globally substitute i/y. If user supplies house style, apply it only in editable prose, not quotations/names/code.
18. **Natural Sino-Vietnamese terminology**: “Đánh giá hiệu suất và phân tích nguyên nhân.” Do not replace every Sino-Vietnamese word with supposed native equivalents. Fluency, technical precision and audience matter, not lexical origin quotas.
19. **Literal vs figurative**: “Máy chủ đang lắng nghe trên cổng 8080.” Technical use of “lắng nghe” is legitimate. Do not ban all anthropomorphic verbs; preserve port and technical meaning.
20. **Genre exception**: “Cơn mưa gõ cửa ký ức.” In a poem, preserve expressive metaphor; in an operations incident report, ask what event it denotes rather than invent facts. Test the two document types separately.
21. **Simple filler with valid edit**: “Trong bối cảnh hiện nay, có thể thấy rằng nhóm đang tiến hành thực hiện việc kiểm tra bản nháp.” One acceptable rewrite: “Nhóm đang kiểm tra bản nháp.” Only drop framing when context confirms it conveys no material time restriction or epistemic caution. Without that context, preserving “Có thể thấy” or offering a narrower edit also passes.
22. **Minimal intervention**: “Nhóm đã sửa lỗi đăng nhập. Bản vá sẽ được phát hành ngày mai.” Clear prose should remain unchanged or receive only a motivated edit. Do not add headings, promises, explanations or decorative formatting.

## Unicode, punctuation and Markdown regression fixtures

These are deterministic checker tests. Passing them does not prove editing quality.

23. **Canonical equivalence**: Generate NFC “Tiếng Việt” and NFD using Python unicodedata.normalize. Lint should produce equivalent linguistic findings, and diff should not report a substantive meaning change from canonical normalization alone. Preserve original bytes in protected code/identifiers; normalize only a comparison view unless normalization was requested.
24. **Tone distinctions**: Contrast “ma”, “má”, “mà”, “mả”, “mã”, “mạ”. Never strip accents or treat these as equivalent. Contrast “d” and “đ” separately. No accent-restoration guessing in ambiguous unaccented text.
25. **Combining-mark offsets**: Include decomposed Vietnamese before a flagged phrase. Report correct line and location against original text, not offsets in an NFC shadow copy. Define column units (code points or graphemes) in CLI help.
26. **Decimals/version/abbreviations**: “Giá là 1.234,50 đồng; bản v1.2.3 chạy trên example.com. TS. An sẽ kiểm tra.” No naive sentence splitting on every period; preserve numeric formatting, version, domain, and abbreviation.
27. **Punctuation changes meaning**: “Không được dừng.” vs “Không, được dừng.” Never insert a comma based solely on word matching. An ambiguous input like “Ăn cơm không được bỏ bữa” should not receive a silently disambiguating rewrite.
28. **Quoted punctuation**: “Cô ấy hỏi: ‘Đã xong chưa?’” No global colon or question-mark ban. Dialogue and quotation punctuation are meaningful.
29. **Protected Markdown**: Inline code `canh_bao`, fenced code, URLs, reference link destinations, HTML tags, YAML front matter, image paths and identifiers must not receive Vietnamese prose rewrites. Link label prose can be edited when requested, while its target stays byte-identical.
30. **Backtick variation**: Test fenced blocks with three and four backticks, tildes, indentation, info strings, and inline code containing a backtick. Mask content using structural parsing or explicitly document parser limitations; regex-only claims must match actual coverage.
31. **False bold/list positives**: `2 ** 3` in code is not emphasis; `a_b` is not automatically an italic error; escaped `\*` is literal; `-5` is not a bullet; `1.5` is not a list marker. Correct Markdown bold in a genuine warning is not automatically a defect.
32. **Structural Markdown**: Preserve table pipes, task boxes, numbered steps, headings, reference definitions, footnote markers and hard line breaks. Reflowing a paragraph must not merge two list items or change execution order.
33. **Emoji/graphemes**: Family emoji, skin-tone modifiers, variation selectors and zero-width joiners should not be corrupted. Their presence in a friendly text is not an objective Vietnamese error. Flag only as contextual style suggestions where appropriate.
34. **Mixed language**: “Chạy `npm run build`, rồi kiểm tra pull request.” Preserve command and established project terminology; do not invent Vietnamese translations for identifiers or globally flag all English.

## Measurable evaluation protocol

Separate three suites and report them separately:

1. **Checker unit/regression suite**: fixed input/output assertions for protected spans, Unicode equivalence, offset accuracy, deterministic output, exit codes, malformed input, changed numbers/negations, and final artifact hash verification if implemented. Measure exact pass count; every reported feature needs at least one positive and one negative test. Include no-finding cases to expose false positives. Never call this a model rewriting benchmark.
2. **Editing behavior suite**: at least 30 independently authored prompts spanning workplace prose, technical docs, conversation, literary excerpts and scholarly cautions. Pair each with explicit semantic invariants and permitted edits, not one reference string. Run both baseline and skill-enabled under the same model/settings in randomized order. Record model, date, skill hash, prompt, output, execution outcome and tool logs. Three repetitions per prompt help reveal variance; disclose if only one is affordable. Keep held-out cases not shown as skill examples.
3. **Human evaluation**: two proficient Vietnamese readers independently score semantic fidelity, naturalness, requested register and unnecessary editing, blinded to condition. Resolve disagreement, report raw counts and disagreements. Readers should include familiarity with regional varieties present; do not make one dialect the quality yardstick. Model-as-judge can supplement but is not sole evidence.

Proposed release gate (a project engineering target, not an established language norm): zero observed critical semantic errors and zero protected-span corruption on the test set; all declared deterministic tests pass; no lower mean fidelity than baseline; naturalness judged at least as good as baseline on most paired cases. Report exact numerator/denominator rather than claiming general reliability. No test sample proves zero real-world risk.

Useful measurements: critical-error rate; protected-span corruption count; correct restraint/no-change rate on clean prose; false-positive rate on marked negative fixtures; precision and recall for seeded mechanical defects with predeclared labels; blind pairwise readability preference with ties; unnecessary-edit count. Do not use shorter length, fewer Sino-Vietnamese words, fewer warnings, or a zero lint score as proxies for good Vietnamese.

## Honest reporting wording

“34 evaluation cases were designed” is not “34 tests passed.” “All checker regression tests passed” is not “the skill preserves meaning.” If no model ablation was run, say so. Review every numerical/negation/actor/condition diff manually even if the automated tool returns no warnings. A warning can be a justified retained usage, not a command to replace text.
