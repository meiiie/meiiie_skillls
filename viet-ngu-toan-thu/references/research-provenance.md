# Research provenance and limitations, 12 November 2026

This registry is original research synthesis with source links, not a bundled corpus. External texts were not bulk downloaded or redistributed. The package MIT license covers original package material; linked resources retain their own rights.

# Vietnamese literary and linguistic sources: v3 evidence memo

Research performed 2026-11-12 using public web pages and dataset/repository documentation. This is a selective source audit, not a complete review through that date. Search-engine crawl dates are not publication dates. No gated data was accessed, accounts created, agreements signed, or copyrighted corpus downloaded. All advice below distinguishes a source's declared license from demonstrated rights in individual works.

## Immediate design decisions

1. Build the skill around original examples, paraphrased linguistic principles, and an edition-aware source registry. Do not bundle a scraped anthology.
2. Separate three questions: Is a source useful? Is the transcription reliable? Is the particular use legally permitted? A positive answer to one does not settle the others.
3. Treat literature as a set of registers, not the default voice for business, academic, explanatory, or everyday Vietnamese.
4. Record author, title, edition, translator/editor, publication date, page/line, exact URL, access date, declared license, verified rights scope, permitted use, and uncertainty for every reused passage.
5. Never claim that installing a skill trains model weights or that reading a corpus guarantees new persistent linguistic ability. The artifact supplies instructions, references, procedures, and examples.

## Verified source registry

### 1. Vietnamese Wikisource: promising public-domain/free-license discovery
- Policy: https://vi.wikisource.org/wiki/Wikisource:Bản_quyền
- Verified: the copyright policy describes a free-content collection, licenses for contributor material, and US copyright relevance. It explicitly distinguishes original works and translations.
- Rights status: mixed by work and contribution. NOT a blanket assertion that every poem on the site is public domain worldwide. Inspect the individual work's rights template and scan/edition provenance.
- Useful for: older prose, poetry, historical spelling and primary-text comparison when the exact edition is documented.
- Bias/quality risks: survival and contributor selection, old orthography, uneven proofreading, variant editions, incomplete transcription. A transcribed line is not automatically an authoritative critical edition.
- Skill policy: link and annotate verified items; prefer scan-backed text. Keep original spelling in quotations and put modernization in a separately labeled field. Verify modern translations, introductions, annotations and editorial additions separately.

### 2. Thi Viện: broad poetry discovery, not established open corpus
- https://www.thivien.net/
- Verified: the site distinguishes its main poetry library from member poetry and hosts Vietnamese, Chinese and other-language works. Its front page supplies source citations for some works and announces support for multiple versions.
- Rights status: no blanket reusable-text license was established in this audit. Public visibility is not permission to republish or train on the whole collection.
- Useful for: locating titles/authors, comparing variants, identifying cited books and journals, discovering verse forms.
- Bias/quality risks: member submissions, variable source documentation, translated poems mixed with originals, uneven regional/historical coverage. Verify attribution and edition against the cited publication before asserting an exact quotation.
- Skill policy: use as a discovery index and reading reference; do not bulk copy it. Contemporary member poetry requires rights checking too.

### 3. FPT Software AI Lab Poem-Generator: declared MIT software, underlying poetry unresolved
- https://github.com/fsoft-ailab/Poem-Generator
- Verified documentation: 171,188 poems collected from Facebook groups, Vườn Thơ Tkaraoke, lucbat.com and other sources. The largest category is lục bát. Preprocessing lowercases text, removes special characters, drops short residual blocks, and concatenates blocks. The included MIT license expressly describes software/documentation.
- Rights status: MIT declaration verified for repository software; author-by-author permission for collected poetry was NOT demonstrated. Do not infer that the repo owner can license every underlying poem.
- Useful for: historical computational-poetry methods and candidate rhyme/tone-checking ideas, not authoritative stylistic ground truth.
- Bias/quality risks: scraped amateur/public-platform material; form imbalance; preprocessing destroys punctuation, casing, poem boundaries and short forms. Counts of poems, blocks and model examples are different units.
- Skill policy: describe methods, not redistribute the corpus. Its automatic score is a narrow formal metric, not literary quality or semantic coherence.

### 4. BigScience ROOTS Vietnamese poetry subset
- https://huggingface.co/datasets/bigscience-data/roots_vi_vietnamese_poetry
- Verified: card declares MIT, identifies FPT poetry as upstream, and describes a 171,188-poem source. Access is gated behind contact-information sharing and the BigScience Ethical Charter. Document deduplication and a small-document filter are documented.
- Rights status: declared dataset license MIT; underlying poem rights unresolved in this audit. Ethical/access conditions and upstream rights are independent questions.
- Useful for: corpus lineage and research reproducibility after appropriate permission, not automatic adoption as a rights-cleared anthology.
- Bias/quality risks: inherited source biases, additional filtering, likely overlap with other scraped poetry uploads. Short texts may be underrepresented.
- Skill policy: mark "gated; declared MIT; underlying rights unverified." Do not use alternate mirrors to evade gates or infer that a derivative card resolves upstream rights.

### 5. phamson02/vietnamese-poetry-corpus
- https://huggingface.co/datasets/phamson02/vietnamese-poetry-corpus/tree/main
- https://huggingface.co/datasets/phamson02/vietnamese-poetry-corpus/viewer
- Verified: listing declares CC BY 4.0; viewer examples include source fields pointing to Thi Viện and poetic classification metadata.
- Rights status: uploader-declared CC BY 4.0, not independently verified authorization from the underlying poets/translators. The README endpoint failed in the browsing tool; listing/viewer remained available. No comprehensive provenance agreement was established.
- Useful for: identifying metadata schemas and possible source overlaps.
- Risks: preprocessing artifacts, taxonomy errors, duplicated poems, missing edition specificity and uploader licensing assumptions.
- Skill policy: do not label "cleared for commercial use" solely from the platform badge.

### 6. National Library of Vietnam Hán-Nôm collection
- https://nlv.gov.vn/ef/han-nom-collection.html
- Verified: institutional description of a historical Hán-Nôm collection and a digitization collaboration with the Vietnamese Nôm Preservation Foundation. The page links a separate digital collection and has an all-rights-reserved footer.
- Rights status: underlying historical works may be public domain, but this audit did not establish blanket scan/transcription reuse rights. A footer does not alone determine rights in each historical work either.
- Useful for: manuscript/edition provenance and historical textual comparison.
- Bias/quality risks: Hán and Nôm are not interchangeable; historical texts are not modern conversational Vietnamese. OCR and automatic reading require expert checks.
- Skill policy: use catalog evidence, scans for verification when accessible, and explicitly distinguish original script, transliteration, translation and editorial commentary. Do not present modern Quốc ngữ readings as identical to the manuscript.

### 7. VIETLEX: linguistic authority and corpus collaboration, not an open dump
- https://www.vietlex.com/about/index.html
- https://www.vietlex.com/order/index.html
- Verified: lexicographic organization founded by Hoàng Phê in 1993; reports a Vietnamese corpus of about 150 million syllables and offers corpus/annotation collaboration. The site offers published dictionary editions and carries an all-rights-reserved notice.
- Rights status: no open corpus/definition redistribution license established here.
- Useful for: sense distinctions, register labels, orthography, collocations and lexicographic checking. Cite a specific dictionary edition, not merely "Hoàng Phê," since editions differ.
- Bias/quality risks: dictionary coverage and normative judgments depend on edition and time; corpus volume does not establish balance across region, age or setting.
- Skill policy: consult targeted entries lawfully, paraphrase explanations, record edition/page, and avoid copying the dictionary as a skill resource.

### 8. VLSP resources: agreements are part of access
- https://vlsp.org.vn/resources
- Verified: the association directs applicants to download, fill, sign and send a general data-user form; it warns older challenge-specific forms may no longer apply. Listed resources cover segmentation, POS, NER, sentiment, speech and related tasks.
- Rights status: obtain the current dataset-specific/general agreement. Do not call the entire VLSP collection open licensed or assume all tasks have identical conditions.
- Useful for: formal NLP evaluation and task definitions.
- Risks: challenge/domain bias; a news-trained tagger is not a universal grammar judge for poetry or dialogue.
- Skill policy: cite available documentation; request access only with the required authorization. Public papers can inform procedures without obtaining the underlying restricted corpus.

### 9. VnCoreNLP: a diagnostic tool, not a writing authority
- https://github.com/vncorenlp/VnCoreNLP
- License verified: https://github.com/vncorenlp/VnCoreNLP/blob/master/LICENSE.md (GPL v3 or later).
- Paper: https://aclanthology.org/N18-5012.pdf
- Useful for segmentation, POS, named entities and dependency diagnostics. Software license does not license input corpora.
- Skill policy: automatic labels are fallible; preserve the original text and record tool version. Never equate syllable spacing with lexical word boundaries or POS tagging with literary correctness.

### 10. Descriptive grammar: bibliographic authority with historical limits
- Laurence C. Thompson, A Vietnamese Grammar (1965), verified institutional bibliography: https://eric.ed.gov/?id=ED015448
- Cross-check: https://wals.info/refdb/record/Thompson-1965
- Useful as a scholarly anchor for phonology, grammar and linguistic description. No open text license established here. An old book being searchable online does not make it public domain.
- Skill policy: distinguish phonetic/grammatical description from present-day prescriptive style. Supplement historical descriptions with current examples, region-specific evidence and native editorial judgment. Avoid flattening all Vietnamese into Hanoi pronunciation or treating southern/central forms as errors.

## Edition-aware public-domain procedure

WIPO's 2023 intellectual-property adjudication reference summarizes a life-plus-50-year term for the general class of works, with category-specific exceptions and continuing moral-right considerations:
https://www.wipo.int/edocs/pubdocs/en/wipo-pub-1081-3-en-intellectual-property-adjudication-in-viet-nam.pdf

This is a dated reference, NOT a verified consolidated legal opinion for November 2026. Search surfaced newer consolidated legislation, but this audit did not complete verification of all amendments. Therefore the skill must not hard-code "author died before year X, therefore safe everywhere."

For every candidate: determine relevant jurisdictions; verify author/coauthor identity and death dates; establish publication history, category and term; check translations and editorial contributions separately; preserve attribution; check edition/scan conditions; record uncertainty. A Nguyễn Du original, a recent translation, a modern annotated school edition and an audiobook are distinct objects. For folk verse, separate traditional underlying material from modern collection, arrangement, commentary and recording. When uncertain, retain a link and bibliographic note instead of copying the text.

## Recommendations for linguistic and literary competence

- Maintain a source ladder: reliable edition/primary publication; scholarly dictionary/grammar; institutional corpus documentation; curated library; community page; repost. Lower tiers are leads, not conclusive authorities.
- Build original minimal pairs for register, agency, aspect, focus, address terms, connective choice, repetition and sentence rhythm. Explain why a change fits its recipient and purpose instead of declaring one universal "beautiful Vietnamese."
- Keep everyday, administrative, academic, journalistic, literary, oral, regional and historical registers separate. Literary inversion and archaic diction may be excellent in a poem and distracting in a product explanation.
- Treat Hán-Việt vocabulary by function, meaning and audience, not as universally more elegant or universally inferior. Prefer precise familiar words where they carry the same meaning.
- For poetry, count tiếng/âm tiết, not tokenizer units or segmented dictionary words. Rhyme needs vowel/coda and pronunciation awareness; matching spelling endings is insufficient. Bằng/trắc checks are formal diagnostics, not proof of a good poem. Distinguish a canonical form from deliberate variants before marking an error.
- Keep quotations exact and sourced. Never invent a line then attribute it to a poet. Label original examples explicitly and do not use fabricated quotations to demonstrate a historical author's style.
- Use cross-author, cross-work and cross-source separation in evaluation. Split passages from the same poem or duplicated web copies across train/test only if leakage is explicitly intended, otherwise prohibit it.
- Add human review across northern, central, southern and diaspora usage when broad coverage is claimed. Corpus balance must be measured or honestly marked unknown, not inferred from size.
- Evaluate separately: factual fidelity, meaning preservation, naturalness, register, regional fit, rhythm, source accuracy and rights compliance. A single fluency score hides important failures.


# Contemporary Vietnamese: evidence and implementation guidance
Research cutoff: 12 November 2026. Source publication dates checked on the pages where available. Guidance below is an original synthesis, not population-wide claims about Vietnamese speakers.

## Main recommendation
Treat naturalness as matching the speaker, relationship, purpose, medium and stakes. Do not implement a “Gen Z mode” by inserting slang into every sentence. Separate receptive understanding of nonstandard writing from permission to produce it. Preserve the user's established address terms and style before applying demographic or regional defaults.

## Verified evidence and limits

1. **Nguyen, Le & Nguyen, ViLexNorm, EACL, March 2024.** The paper reports 10,467 sentence pairs from public Facebook and TikTok comments. Sampling favors engaging posts; preprocessing removes usernames, emojis and sentences below four words. Annotators were six native speakers aged 20–22. This is useful evidence of nonstandard lexical forms and normalization problems, not a representative sample of Vietnamese private conversation or appropriate assistant tone. Its short-turn and emoji exclusions are particularly important for texting evaluation. Sources: [paper](https://aclanthology.org/2024.eacl-long.85.pdf), [repository](https://github.com/ngxtnhi/ViLexNorm).

2. **ViLexNorm rights.** The repository states CC BY-NC-SA 4.0, while its abstract describes availability exclusively for research. Do not silently treat it as unrestricted commercial training material. Verify the intended use and resolve any licensing ambiguity with the rights holder before commercial incorporation. Attribution and ShareAlike conditions also need review for redistribution/adaptation. Removing usernames is not proof that original comments cannot be reidentified; the paper explicitly retains potentially offensive comments. Do not expose corpus text or use toxicity as a stylistic target. Prefer independently written examples for this skill. Same repository/paper sources as above.

3. **Nguyen, Nguyen & Nguyen, ViSoLex, COLING System Demonstrations, January 2025.** This is an open-source lexical normalization system, not an authoritative living slang dictionary or normative writing guide. Use it as a research lead, and inspect actual code/model/data licenses separately before reuse. A paper being accessible or a system being called open-source does not establish identical rights for every bundled resource. [ACL publication](https://aclanthology.org/2025.coling-demos.18/).

4. **Trinh Cam Lan, Accommodation in dialect contact, 2022, volume 6(1), pp. 86–96.** Research examines Northern-dialect speakers in Ho Chi Minh City and accommodation through sentence-final particle variants. Communicative environment and duration in the new city help explain variation. This supports context-sensitive accommodation, not rigid “Northern people say X, Southern people say Y” routing. It is not a study of all regions or of current texting. The first journal host failed; the publisher's alternate host supplied the full text. [Publisher article](https://journals.eco-vector.com/2618-9453/article/view/105391), DOI 10.54631/VS.2022.61-105391.

5. **Nguyễn Văn Đồng, Tạp chí Ngôn ngữ, issue 6 (2026), published 28 July 2026.** The abstract reports conversational fieldwork in Southwestern provinces: 3,000 dialogue pairs, with 19 sentence-final particles in 2,100 adjacency pairs. Its regional group includes nha, nghen, hen, heng, nhen, ha, nè and chớ, alongside nationally distributed particles. This establishes documented regional usage, not exclusive geographic ownership or a safe one-to-one substitution table. Only the landing-page abstract was examined. [Article](https://jol.vn/index.php/ngonngu/en/article/view/770).

6. **Sidnell & Shohet, The problem of peers in Vietnamese interaction, 2013.** Publisher search records describe how speakers negotiate peer relations through pronouns, names, kin terms, and ironic kin-term use. This is useful background against the assumption that one fixed pronoun pair fits all equal-age interlocutors. Full publisher text returned 403, so do not claim a full-text review or infer precise distributional results. [DOI](https://doi.org/10.1111/1467-9655.12053).

7. **Lê Huy, Tuổi Trẻ Online, 25 December 2025, 11:02 GMT+7.** A year-end press roundup documents expressions including “chưa có đủ wow” and “ok sốp.” Treat these as media-attested examples from 2025, not guaranteed November 2026 favorites or evidence that all young people use them. The URL contains an earlier date-like timestamp; use the actual displayed publication date. [Article](https://tuoitre.vn/moi-nha-minh-len-nui-gium-em-he-he-he-diem-danh-nhung-cum-tu-hot-khap-coi-mang-2025-20251216233706892.htm).

8. **Như Quỳnh, Tiền Phong youth section, 18 April 2026, 08:00.** Reports humorous elaborate paraphrases on Threads, including “Khả năng tiếp thu có độ trễ nhẹ.” This verifies a 2026 attestation, not national prevalence or persistence into November. The article compiles examples and engagement anecdotes rather than providing a representative corpus. Some humor is insulting or socially stereotyping; documentation does not make it appropriate assistant speech. [Article](https://svvn.tienphong.vn/gen-z-cap-nhat-ngon-ngu-moi-10-diem-tinh-te-nhung-thu-thach-hoi-nao-ca-vang-post1836261.tpo).


## Additional primary dataset cards audited in parallel

- **UD Vietnamese-VTB**: https://universaldependencies.org/treebanks/vi_vtb/index.html . Treebank annotations are declared CC BY-SA 4.0. Useful for syntactic annotation conventions, not universal literary grammar. Check source-text scope and attribution when redistributing; a treebank does not prove representative regional coverage.
- **ViDia2Std**: https://huggingface.co/datasets/Biu3010/ViDia2Std/blob/main/README.md ; paper https://ojs.aaai.org/index.php/AAAI/article/view/40247 . Card declares CC BY-NC 4.0, 13,657 pairs (10,870/1,184/1,603), real Facebook comments and three regional labels. No general commercial permission; comments retain privacy/reidentification concerns. Conversion to a standard form is a research task, not a claim that regional language is defective.
- **ViMD**: https://huggingface.co/datasets/nguyendv02/ViMD_Dataset/blob/main/README.md . Card declares CC BY-NC-ND 4.0; 102.56 hours, 18,949 news-broadcast utterances based on a historical 63-province scheme. News speech is not casual texting; regional labels are not current administrative evidence. Do not redistribute adapted audio under an assumption that research interest overrides ND.

These figures reflect the inspected cards, not independent recounts of downloaded datasets. No dataset files were incorporated into this package.
