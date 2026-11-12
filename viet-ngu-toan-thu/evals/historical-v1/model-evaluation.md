# Observed with-skill AI editing smoke test

Exact model identifier: unavailable in this evaluation context; none is inferred. CLI tool version: 1.1.1. All 12 scenarios were answered in one continuous AI context.

Date: 2026-11-11. Twelve scenarios were actually answered by the evaluation AI after reading SKILL.md and the meaning, grammar, punctuation, regional/community, genre, and checking references. The exact model-written outputs are recorded below. The Python harness did not generate or edit these outputs: it stored them and ran the real CLI on source/output pairs.

**Limitations:** same AI selected the scenarios, wrote the outputs, and assessed them. It had already designed evaluation cases and knew the desired invariants. This is an unblinded, single-pass, self-reviewed smoke test, not independent validation, a held-out benchmark, or evidence of improvement over baseline. No external model API or fresh isolated agent was run. No human reviewed the outputs. Many cases deliberately exercise restraint/minimal edits, so success here does not establish deep rewriting ability.

## Executed checks

Working directory outside package: `vietnamese-skill-work/evaluation-run`. Commands used for every case:

```sh
python3 ../viet-ngu-toan-thu/scripts/viet_guard.py lint E01-before.txt
python3 ../viet-ngu-toan-thu/scripts/viet_guard.py diff E01-before.txt E01-after.txt
python3 ../viet-ngu-toan-thu/scripts/viet_guard.py check E01-before.txt E01-after.txt --record E01-record.json --reviewer "AI assistant" --review "Giữ trình tự thời gian và chưa biết nguyên nhân; chỉ bỏ khoảng trắng trước phẩy."
python3 ../viet-ngu-toan-thu/scripts/viet_guard.py verify E01-before.txt E01-after.txt --record E01-record.json
```

Each case uses its own filenames and the review quoted under that case. Raw stdout/stderr, exit codes, prompts, outputs and rubric are in `evaluation-run/results.json` outside the distributable package. Check records were actually written and verified, not simulated.

## E01

Exact prompt:

```text
Chỉ sửa dấu câu và khoảng trắng, chỉ trả bản văn.

Sau đợt nâng cấp , số lỗi tăng; chưa xác định được nguyên nhân.
```

Actual edited output:

```text
Sau đợt nâng cấp, số lỗi tăng; chưa xác định được nguyên nhân.
```

AI review: Giữ trình tự thời gian và chưa biết nguyên nhân; chỉ bỏ khoảng trắng trước phẩy.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E02

Exact prompt:

```text
Chỉ sửa câu chữ, không kiểm chứng hay thay đổi nội dung. Chỉ trả bản văn.

Đợt nâng cấp chắc chắn khiến số lỗi tăng.
```

Actual edited output:

```text
Đợt nâng cấp chắc chắn khiến số lỗi tăng.
```

AI review: Giữ khẳng định nhân quả và chắc chắn; không bịa nhận xét về bằng chứng.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=0, diff=0, check=0, verify=0.

## E03

Exact prompt:

```text
Sửa lỗi trình bày rõ ràng, chỉ trả bản văn.

Nếu ban giám đốc đồng ý , nhóm có thể thử nghiệm vào quý IV; chưa có ngày bắt đầu.
```

Actual edited output:

```text
Nếu ban giám đốc đồng ý, nhóm có thể thử nghiệm vào quý IV; chưa có ngày bắt đầu.
```

AI review: Giữ điều kiện, khả năng, quý IV và chưa có ngày.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E04

Exact prompt:

```text
Biên tập nhẹ cho dễ đọc, chỉ trả bản văn.

Tôi chưa nói rằng Nam không muốn tham gia.
```

Actual edited output:

```text
Tôi chưa nói rằng Nam không muốn tham gia.
```

AI review: Không biến lời chưa nói thành quyết định của Nam.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=0, diff=0, check=0, verify=0.

## E05

Exact prompt:

```text
Chỉ sửa khoảng trắng và dấu câu, chỉ trả bản văn.

Không phải hồ sơ nào cũng được duyệt ; chỉ hồ sơ nộp trước 17 giờ mới được xét, trừ bản thiếu chữ ký.
```

Actual edited output:

```text
Không phải hồ sơ nào cũng được duyệt; chỉ hồ sơ nộp trước 17 giờ mới được xét, trừ bản thiếu chữ ký.
```

AI review: Giữ không-phải-tất-cả, điều kiện xét khác duyệt, 17 giờ và ngoại lệ.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E06

Exact prompt:

```text
Sửa lỗi trình bày, giữ giọng hội thoại và chỉ trả bản văn.

Dạ , bữa nay má mua bắp về nấu chè, con ăn nghen.
```

Actual edited output:

```text
Dạ, bữa nay má mua bắp về nấu chè, con ăn nghen.
```

AI review: Giữ má/bắp/bữa nay/nghen và quan hệ xưng hô; chỉ sửa khoảng trắng.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E07

Exact prompt:

```text
Chỉ sửa lỗi rõ ràng, không chuẩn hóa tên. Chỉ trả bản văn.

H’Hen Niê nhắc đến Ê Đê, M’nông và H’Mông.
```

Actual edited output:

```text
H’Hen Niê nhắc đến Ê Đê, M’nông và H’Mông.
```

AI review: Giữ tên, dấu nháy và danh tính; không suy luận cộng đồng của người.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=0, diff=0, check=0, verify=0.

## E08

Exact prompt:

```text
Chỉnh câu chữ cho tài liệu kỹ thuật, giữ nguyên mã và URL. Chỉ trả bản văn.

Chạy `npm run build` , rồi mở [bản thử](https://example.com/a_b?v=1.2.3). Máy chủ lắng nghe trên cổng 8080.
```

Actual edited output:

```text
Chạy `npm run build`, rồi mở [bản thử](https://example.com/a_b?v=1.2.3). Máy chủ lắng nghe trên cổng 8080.
```

AI review: Giữ byte mã/URL, port và thuật ngữ lắng nghe; chỉ sửa phẩy.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E09

Exact prompt:

```text
Biên tập nhẹ, giữ nguyên số liệu và chỉ trả bản văn.

Tỷ lệ lỗi giảm từ 8% xuống 5% , tức giảm 3 điểm phần trăm.
```

Actual edited output:

```text
Tỷ lệ lỗi giảm từ 8% xuống 5%, tức giảm 3 điểm phần trăm.
```

AI review: Giữ 8%,5%,3 điểm phần trăm, không đổi thành giảm tương đối 3%.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E10

Exact prompt:

```text
Chỉ sửa lỗi trình bày ngoài trích dẫn, chỉ trả bản văn.

Minh nói : “Tôi không hứa giao vào thứ Hai.” Lan chuyển lời này cho Huy.
```

Actual edited output:

```text
Minh nói: “Tôi không hứa giao vào thứ Hai.” Lan chuyển lời này cho Huy.
```

AI review: Giữ Minh phát biểu, Lan chuyển, Huy nhận, nguyên văn phủ định cam kết.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=1, diff=0, check=1, verify=0.

## E11

Exact prompt:

```text
Giữ chất thơ, chỉ sửa nếu có lỗi rõ ràng. Chỉ trả bản văn.

Gió khâu lại những khoảng trời rách. Mưa. Rồi im lặng.
```

Actual edited output:

```text
Gió khâu lại những khoảng trời rách. Mưa. Rồi im lặng.
```

AI review: Giữ nhân hóa, câu đặc biệt và nhịp thơ; không coi chúng là lỗi.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=0, diff=0, check=0, verify=0.

## E12

Exact prompt:

```text
Thống nhất kĩ thuật thành kỹ thuật trong phần văn xuôi; giữ nguyên tên, mã và trích dẫn. Chỉ trả bản văn.

Vy viết tài liệu kĩ thuật cho `ki_thuat`. Bản cũ ghi: “kĩ thuật”.
```

Actual edited output:

```text
Vy viết tài liệu kỹ thuật cho `ki_thuat`. Bản cũ ghi: “kĩ thuật”.
```

AI review: Đúng phạm vi chuẩn đích; giữ Vy, code và trích dẫn nguyên văn.

Result: PASS on the specified invariants; not an independent human judgment

CLI exit codes: lint=0, diff=0, check=0, verify=0.

## Summary and honest weaknesses

AI self-review found no specified invariant violations in 12/12 outputs. CLI verify returned 0 for 12/12 recorded pairs. These are observed counts on this small, highly guided set, not an estimated general success rate.

Check exit 1 where present means findings were retained in the original or diff, not execution failure; verify 0 means the record matches the checked artifacts, not that Vietnamese meaning is proved.

The main weakness is evidence coverage: these prompts mostly demand narrow editing and disclose protected spans. They do not test spontaneous recognition under long distracting text, all dialects, unknown languages, ambiguous quotations, adversarial Markdown, full factual review, or substantive multi-paragraph rewriting. Unicode and parser coverage belong to separate deterministic tests; no such language-performance claim is inferred here. A blinded independent human comparison and genuine held-out model runs remain outstanding.

## Actual workflow evidence (E01)

Check stdout:
```json
{
  "attestation_only": true,
  "findings": true,
  "human_review_required": true,
  "record_written": true
}
```

Verify stdout:
```json
{
  "attestation_only": true,
  "human_review_required": true,
  "meaning_certified": false,
  "valid": true,
  "warning": "Checksum is not authentication. A rewritten record can be rehashed."
}
```

SKILL.md SHA-256 at run: `dab0ec19d1ab62af3df7630fd5d6e81019102c9efb6244db172de89f24b739c9`.
