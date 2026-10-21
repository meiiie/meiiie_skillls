# Critique log: Milestone 1 (times Asia/Saigon, UTC+7, 21 Oct 2026)

Method: render, take a contact sheet (`design/films/sheet.py`, frame-index grabs because manimgx writes VFR), then look at each frame against the reference set (FT/Bloomberg map graphics, Economist charts, synoptic charts). Score out of 10 (8 = would ship in a professional briefing), fix, and re-render. Final stills are in `stills/`.

## S1 "Hai tâm áp" (pressure map), assets/film/pressure.mp4, 20.1 s, 2560×1080
| v | Problem seen | Fix | Score |
|---|---|---|---|
| v1 | Strokes thickened 2.6× on camera zoom (manimgx scales stroke with the frame); labels grew with the zoom | Wrote `kit.View`, a 2-D camera that moves/scales groups and pins labels at constant size | 5 |
| v2 | Asia ledger table duplicated the map and cluttered it; hero "47%" and caption ran out of frame | Replaced the ledger with direct map labels; hero inside a paper panel, caption below | 6 |
| v3 | Gulf leader lines crossed; rows were in random order | Rows ordered by latitude, with a common elbow | 6.5 |
| v4 | Stale 2025 isobars stayed under the morphing 2026 set; the duration was 22 s | Removed iso0 after the hand-off to always_redraw; tightened timings to 20.1 s | 7 |
| v5 (final) | HUD world value and legend collided with the T marker in the final wide view; the in-film source duplicated the slide source | Value moved under the year, legend to bottom-left, in-film source removed, end caption at y −2.85 | **7.5** |

Remaining weaknesses:
- the Gulf leaders still fan slightly;
- the Asia frame is dense (7 labels plus the hero);
- the ocean contours are interpolation, flagged in the source;
- the AI-flow particles go slightly off-frame at the top right (intentional bleed, but the renderer warns).

## S2 "Ba khí áp kế" (barometers), assets/film/baro.mp4, 16.1 s, 2560×1080
| v | Problem seen | Fix | Score |
|---|---|---|---|
| v1 | The follow-updater zoom conflicted with Create, so ticks drew in the wrong place | Used a real camera-frame macro zoom for the intro only | 5 |
| v2 | Bank names overlapped numerals; the final bar chart was tiny, with a lot of whitespace | Mono date stamp on the dial, country on the readout; PP 2.6 and zero line at −0.6 | 6 |
| v3 (final) | Fed bar touched the dial; hike chips misaligned | Re-spaced; chips "10/9 +0,25 điểm %" with ease_out_back; target-2% tick and "mục tiêu" in blue | **7** |

Remaining weaknesses:
- it is flatter than S1, without the "wow" camera move after the intro;
- the small dials in the final state read as icons;
- the arc→bar morph is clear but plain.
Next iteration idea: a continuous camera dolly from the Fed dial face into the bar, and a brass/engraved bezel detail pass.

## Deck (deck/m1.pptx, renders/m1_v2)
| v | Problem | Fix |
|---|---|---|
| v1 | LibreOffice drew grey bands under every hairline and shape | Found that build_deck autoshapes keep `<p:style>` with effectRef idx=2 (theme shadow); `postfix.py` strips 841 refs, giving a clean render. **Skill bug to fix upstream.** |
| v1 | Title wrapped; source outside the safe area | Shorter titles over 8 columns; film window up to y 1.62; source at 6.76 |
| v2 | Slide 2 standfirst ran 4 lines, past the header rule | Shortened the standfirst to 3 lines |
| v2 | 16 build_deck overlap warnings remain | Checked visually: they are generous text boxes on the native map/dials (code vs stamp, year vs kicker), with no visible collision in the render |

Slide scores: s1film 8, s1native 7.5, s2film 7.5, s2native 7.5 (the native dials are fully editable and match the film's end state).

---
# Critique log: Milestone 2 (polish + 4 films + full deck), 21 Oct 2026, 20:11–21:51 UTC+7
Scale 1–10 against the bar (FT / Bloomberg / Economist graphics desk, Pentagram data work): concept, data
honesty, composition, type, motion, detail density. Redo until ≥ 8; where it stayed below, it says so.

## S1 pressure v6 (assets/film/pressure.mp4, 20.2 s) — 8
- v5 → 7.5: Gulf leaders fanned into a knot over the Arabian peninsula; Asia labels too dense (9 codes).
- v6: Gulf rows ranked by 2026 growth in a ledger at the left, numbered badge rings on the map and the same
  number filled in each ledger row (no leaders crossing the map), Indicate pulse per row; Asia cut to TWN, KOR,
  JPN, VNM, CHN; VN sub-label "IMF; World Bank: 7,4". Old version kept: assets/film/old/pressure_v5.mp4.
- Remaining: the end frame's isobars around Japan are still busy at the HIGH; acceptable.

## S2 baro v4 (baro.mp4, 17.6 s) — 8
- v3 → 7.5: the bar chart appeared by crossfade, breaking the instrument metaphor; bezels thin and toy-like.
- v4: bezel ring (case colour), 144 knurl marks, 3 slotted screws, anti-parallax mirror arc, glass glint; phase
  E is one continuous camera move: push 0.42× onto the Fed gap, the dials shrink and rise while the Fed gap
  ReplacementTransforms into its bar on a zero line, pull back, ECB/BoJ gaps become bars. The native fallback
  (slide 14) now carries the same bezel, knurl (96), screws and mirror arc.

## S3 drum (drum.mp4, 17.2 s) — 8
- v1 → 6: a plain cylinder and a pen; trace had a vertical artifact at the cylinder edge; gears hidden.
- v2 → 7: clockwork window with 6 gears, aneroid capsule stack breathing with the pen, pen lifter, glass case,
  clip strip; trace starts in the visible range (hu·0.96); −2,7 label left of its dot.
- v3 → 8: the paper unrolls into a flat chart with the 2008–2017 average (3,3) dashed and labelled outside the
  right edge, DỰ BÁO band, headline at the bottom. Data: IMF A1 (2018–2027).

## S4 wind (wind.mp4, 15.0 s) — 7.5–8
- v1 → 6: winds too sparse to read as weather. v2: 6 longer streamlines per station, 3 comets each, thicker;
  station kicks lifted above the dim layer. v3: stations fly on arcs into a ranked diverging bar chart, world
  line "+3,9", headline on Asia's 4,0 pp. Below 8 because the pan's first two seconds are mostly empty ocean.

## S5 tide (tide.mp4, 16.85 s) — 8
- v1 → 6: values collided with staff numbers; v2: fixed readout row + pointer triangles; v3: headline collided
  with the tubes → wells scale to 0.8 at the end; v4: water vanished after the scale (play re-adds z-order) →
  UpdateFromFunc noop re-raise. US +22,7 bracket; "2028–2030 không hiển thị" stated on the year roll.

## S6 chipline (Anatomy, chipline.mp4, 12 s, 3936 native shapes) — 7.5 (film) / 8 (slide 20 with synced labels)
- v1 → 6: faces too pale (contrast 1.2); v2: darker shade tokens, max-shapes budget kept by fewer rollers;
  v3: server trays slide in during station 2 and out the back during 3 (they protruded oddly in v2); poster at
  8.9 s (rack full). Audit: 226 solids, 94% width, edges 10.7:1, faces 1.38:1.
- Honest gap: the port end (crane, ship) reads less clearly than the fab; no water plane. Slide 22 (Morph push
  into the packaging station on the native shapes) is the strongest moment of this chapter (8.5).

## Deck (deck/khi-ap-2026.pptx, 30 slides)
- all-1 → 7: chip zoom empty (film.json `anchors` are pixels; `anchors_in` are inches); growth chart values
  collided with names; close/cover paper band cut the map on the left only; AI value crossed the divider.
- all-2 → 7.5: check_deck variety: 9 effect techniques, 3 transition types, fade 37%; labels 2/3 overlapped on
  the chipline; the zoom slide's foot band hid the source line.
- all-3: transitions push/cover/wipe/split/uncover/reveal/fade/morph; effects + drop, float, split, stretch,
  indicate, fly; pkg label narrowed; foot band moved under the header. Scores below (filled after the look).
- final-2 (deck/final.pptx) — deck 8 overall. check_deck PASS (0 errors, 26 warnings), gate 6 PASS.
  - Strongest (8.5): 1 cover, 2 agenda (Morph map camera), 14 dials with bezels, 20 + 22 (Anatomy line, then a
    native Morph push into the packaging station), 26 Vietnam, 29 bookend close.
  - Solid (8): 3, 6, 7, 8, 11, 16–19, 23–25, 27, 28.
  - Weakest (7): 10 (oil 2025 thermometer is a deliberate set-up for the Morph to 11 but sparse alone), 12
    (inflation thermometers read as five equal columns), 15 (yields: big "+1" plus two bars, plain), 30 (credits).
  - Fixed on the way: a film_audit false positive (the ring that samples the page around a film crossed the
    1.5 in rule and the source line; it now uses the dominant ring colour, skill v5.7).
  - Remaining warnings, accepted: composition 10 signatures / 24 cuts (the film + native pairs repeat by design),
    flat ground (paper colour is the concept: a synoptic chart), labels on slide 20 without a chip (on plain paper).
