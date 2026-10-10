# The reference bar

The quality bar is a real, accepted deck: *Hành Trình Tái Sinh Nghệ Thuật Ca Trù Của Cậu Đàn Đáy*
(NEKO CORE, 48 slides, 14 scenes, PptxGenJS + Morph). Its renders are in
`assets/reference/catru-contact-1.jpg` and `-2.jpg`. Look at them before Phase 3, and put every
sample and group render next to them (`studio.py compare`). The case study of how it was made is
`examples/case-catru-heritage.md`; the seven-keyframe rebuild with this engine is `examples/catru-mini`.

## 1. What was measured from the file

| Decision | Measured | Why it works |
|---|---|---|
| Ground | full-slide image grounds on 48/48: dark lacquer (mean RGB 28,14,10 with brush streaks and vignette), red crackle lacquer for the UNESCO and video scenes | a material, so the dark is rich and the red is an event |
| Frame | `!!frame` on 48/48: 0.75 pt gold #D9B26A at 65%, inset 0.28 in | the film's frame; never moves, so everything else visibly does |
| Signature | `!!str1-3` + `!!peg` on 48/48: three graduated lines (2.0 / 1.4 / 0.9 pt) and a dot | one string in darkness opens the talk, the strings lock onto the instrument's neck, lie down into the timeline, and return for the close |
| Layered hero | đàn đáy as `!!ddHead/Neck/Body` on one 600 × 2400 canvas, parked off-slide at x 14.2 in between appearances | Morph assembles and flies the instrument |
| Medallion | `!!medW/T/C`, three rings, parked at x 13.3 in | a second recurring object that blooms in the turn |
| Type | Cormorant (titles 54 pt bold, line 0.88; display 66-150) and Josefin Sans (kicker 13 pt bold, tracked +5 pt; body 16-17 pt, line 1.25) | a calligraphic serif against a geometric label; two families only |
| Grid | kicker x 1.45 in, title x 1.35 in on every text slide; page number at (12.15, 6.78) | the same verticals on 48 slides |
| Motion | one Morph per slide (1300 ms; 1500 intro; 2000 for the quiet string, the bloom and the close); entrances fade/wipe 700-800 ms, 220 ms stagger, ≤ 3 per slide | calm, and every move means something |
| Scenes | 14 scenes, 48 keyframes; highlight walks (3 roles, 3 reasons), a timeline walk (5 nodes), a book that opens, list reveals | each idea gets a camera move, not a slide |
| Photos | 9 distinct, sepia/duotone under a 62% veil, colour arrives with the narrator | a colour arc: muted past, bloom at the turn |
| Words | anchor phrase on 4 slides; sources on a credits slide and in the notes, not on content slides | the slide shows; the speaker tells |

## 2. What the audit says about it

`check_deck.py` on the reference: PASS. Warnings: one hold beat (31→32, the "which instrument is
missing?" question held while the bubble changes), 31 distinct text sizes (the scale drifted),
8 text boxes near the edge, one title that runs into its body text on slide 14. A real deck has
small flaws; the bar is the system, the signature and the motion, not zero warnings.

`tests/test_audit.py::test_reference_deck_passes` keeps it that way: any change to the audits that
fails this deck is a wrong change (`MOTION_REF_DECK=/path/NEKO_CORE_CaTru_motion.pptx pytest tests`).

## 3. Comparing your deck with the bar

```bash
python $S/studio.py compare WORK WORK/renders/g2-1            # writes WORK/design/compare-N.jpg
python $S/studio.py compare WORK WORK/renders/g2-1 --ref assets/reference/styles-gallery.jpg
```
Answer in `notes/<group>.md`:
1. At thumbnail size, does the deck read as one piece? (ground, chrome, signature, type)
2. Is there a signature, and does it do something in this group?
3. Is each slide as specific as the reference (real objects of the subject, real numbers), or generic?
4. Are there slides with nothing to find at 4×? Slides with too much?
5. Does every scene have a camera move (keyframes that change), or are some slides alone?

The reference is a heritage deck. For other kinds, compare the system and the motion, not the
lacquer: `examples/product-launch` and `examples/data-story` show the same bar in other styles.
