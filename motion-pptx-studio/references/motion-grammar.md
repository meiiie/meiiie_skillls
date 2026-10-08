# Motion grammar (how the deck moves)

"Có khi nhiều slide để phục vụ cho một motion hoàn chỉnh, từng frame và mọi thứ." Professional motion decks
are animated films cut into slides: each slide is a **keyframe**, and Morph interpolates between them.

## 1. Vocabulary
| Term | Meaning |
|---|---|
| Scene | one idea of the talk (Hook, Problem, Meet the hero, How it works, Proof, Close) |
| Keyframe run | 3–5 consecutive slides of one scene; same layout, objects move between them |
| `!!name` layer | a shape with exactly the same name on neighbouring slides; Morph moves, resizes, rotates and recolours it |
| `@fade3-label` | entrance effect, order 3 (fade, float or wipe); plays after the Morph, 220 ms stagger |
| `@blink2-dot` | an emphasis loop that blinks forever (cursor, live dot, "recording" light) |
| Parking | an object waiting off-slide (x 14.2 in or y -2 in) so it can fly in later via Morph |

## 2. How Morph pairs objects
- Morph pairs shapes whose **names match** (with the `!!` prefix the pairing is by name only). Shapes with
  no partner fade in or out.
- Names must be **unique per slide** (`check_deck.py` errors on duplicates) and keep the same **kind** on both
  slides (picture↔picture, text↔text; a picture that turns into a shape will not morph).
- Text morphs by characters inside a paired text box ("Ca Trù" → "2009" works when both boxes are `!!title`).
- Images morph best when they are the **same image file**: crop, scale and position change smoothly.
  A different image under the same name cross-fades.
- `!!` names that appear on only one slide are "lonely" (`check_deck.py` warns). That is fine for a deliberate
  entrance, but usually it means a name was mistyped.

## 3. Keyframe recipes (each = one scene of 3–5 slides)
| Recipe | K1 → K2 → K3 (→ K4) |
|---|---|
| Assemble | parts scattered or faded → drifting closer → locked together + title arrives |
| Push-in | full-bleed photo → 1.25× scale with an offset (crop moves) → detail + label |
| Highlight walk | 3 columns at mid opacity → column 1 lifted + bright → column 2 → column 3 (`roles.py`) |
| Counter | big number 1 → 2 → 3 (`!!count`), the background word changes each time |
| Colour bloom | muted (veil 60–70%, greyscale hero parked) → hero lands in colour with a 2 s Morph |
| Timeline walk | strings lie down into a line → a character walks node to node (`!!node1-5`, `!!hl`) |
| Book | closed cover → pages open (`!!pageL / !!pageR`) → a screen appears inside the open book |
| Zoom to detail | object whole → enlarged so one part fills the slide (+ highlight ring `!!hl`) → back out |
| Circular close | the opening keyframe again, objects return to their first positions |
Every scene should use one of these, or a variation. The 48-slide ca trù deck had 14 scenes; the 34-slide neko deck had 10.

## 4. Durations (`WORK/motion.json`)
```json
{"default_ms": 1300, "stagger_ms": 220, "dur": {"3": 2000, "12": 2000}, "keep_timing": [50]}
```
- 1300 ms default; 1500–1600 for intro keyframes; **2000 for blooms and the anchor moments**; 1000 for quick counters.
- Keys are slide **FILE** numbers (`slide12.xml` → `"12"`), not deck positions. After `ooxml.py sequence`
  they differ; `ooxml.py order DIR` prints the mapping.
- `motion.py` looks for motion.json in the unpacked folder, then its parent, then WORK (the grandparent), and prints
  which file it used. If it prints "(none, defaults)" your durations were not applied.
- `--dur 12=2000` on the command line overrides it for one run. Prefer editing motion.json so re-runs keep the value.

## 5. Entrances and loops
- Entrances are for **new information** on a keyframe (a caption, a source line, a callout). Persistent objects move with Morph; don't give them entrances.
- Order numbers run from 1 per slide. Keep it to 3 entrances per slide at most; the talk has a time budget.
- `@blink<N>-label`: use it for one living detail (a terminal cursor, a "live" dot). One per slide at most.
- Hand-made animation: list the slide file in `keep_timing` and `motion.py` leaves its `p:timing` alone (it still sets the Morph).

## 6. What motion.py guarantees
- Exactly **one** transition per slide (Morph wrapped in `mc:AlternateContent` with a fade fallback for old versions).
- It removes every older transition first, so it is **idempotent**: run it after every edit.
- `p:timing` is rebuilt from the `@` names unless the slide is in `keep_timing`.
- XML order inside `p:sld`: cSld, clrMapOvr, transition, timing, extLst.
Check: `check_deck.py` reports morph ms, entrances and shared layers per slide, and errors if a slide has 0 or 2+ transitions.

## 7. Limits (say them to the user)
LibreOffice renders static frames only: Morph, entrances and blink are visible **only in PowerPoint 365 / 2019+**
(Keynote and Google Slides ignore Morph). The render proves layout; the user must play the deck in PowerPoint.
