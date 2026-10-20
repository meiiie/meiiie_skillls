# Motion library (v5): beyond Morph

Morph is one tool. The slidewppt.vn decks we measured (6 public decks, `research/REPORT.md`) use Morph on a
minority of slides; they lean on Fade/Push transitions, Fly/Float/Fade entrances, motion paths, letter-by-letter
text, hyperlink menus and GIF/audio. Award-level decks pick **2–4 signature techniques per deck** and repeat them
with intent. Write them under `## Motion vocabulary` in `design/art-direction.md` (Gate 3).

## 1. Transitions (`"transition"` on a slide; `python motion.py --list`)
`"transition": "push"` or `{"type": "push", "dir": "l", "ms": 800}`; default `morph` (byObject; `"morph": "byChar"`).

| Family | Names | XML | Plays in |
|---|---|---|---|
| core | fade, cut, push, wipe, split, cover, uncover, shape, diamond, zoombox, dissolve, blinds, checker, randombars, clock, comb | ECMA-376 `p:` | PowerPoint all, LibreOffice (imported), Keynote (most), Google Slides (fade/slide/flip family; others become fade or none) |
| Office 2010 | reveal, flash, ripple, honeycomb, glitter, vortex, shred, switch, flip, gallery, cube, doors, window, zoom, pan, ferris, conveyor, rotate, orbit, flythrough | `p14:` in `mc:AlternateContent`, fade fallback | PowerPoint 2010+; LibreOffice imports some; others fall back to fade |
| Office 2013 | fallover, drape, curtains, wind, prestige, fracture, crush, peeloff, pagecurl, airplane, origami | `p15:prstTrans` | PowerPoint 2013+ / 365 only; LibreOffice: none/approximate |
| Morph | morph (byObject/byWord/byChar) | `p159:morph` | PowerPoint 2019 / 365 / web (plays in 2016 C2R); fade elsewhere |

## 2. Effects (`"anim"` on any top-level shape or component)
`"anim": {"fx": "fly", "dir": "l", "ms": 600, "delay": 200}` or a list. Keys: `delay` (ms in its click group),
`ms`, `click` (0 = after the transition, 1, 2 … = per click), `trigger` (the `!!name` that is clicked),
`loop`, `reverse`, `ease` ([accel %, decel %]), `step` (letters/words % of ms), `scale`, `deg`, `path`
([[dx, dy] …] inches, `"C"` for curves), `rx`/`ry` (orbit). On a component the effect is applied to every
part with `"stagger"` ms between them.

| Class | fx | Notes |
|---|---|---|
| entrance | appear, fade, fly (dir l/r/t/b), drop, float/rise, wipe (dir), split (h/v), zoom, wheel, type (letters), word | `type`/`word` write `p:iterate`; only text shapes iterate |
| emphasis | pulse (auto-reverse), grow, spin (deg), teeter, blink | `loop: true` = `repeatCount="indefinite"` |
| exit | fadeout, flyout, zoomout, wipeout | |
| path | path, orbit | `animMotion`, relative, in slide fractions |
| media | (automatic for `video` shapes) | autoplay + loop + mute by default; `"loop": false` for a one-shot scene |

PowerPoint animates only top-level shapes: an `anim` inside a group is ignored (build_deck warns). The legacy
name grammar (`@fade1-x`, `@blink2-x`, now also `@fly`, `@zoom`, `@split`, `@type`, `@word`, `@pulse`, `@spin`,
`@wheel`, `@drop`, `@rise` with an optional direction letter) still works.

## 3. Recipes that read as "designed"
- **Typed hook**: two lines of `type`, the second 0.9 s later in the accent; a dot `drop`s and loops a `path`.
- **Camera pan on a rail** (heritage timelines): every year's numeral lives on one long strip; each keyframe
  shifts the strip so the active year sits at the left (Morph), the others off-slide; the right column changes.
- **Assemble → explode** (anatomy): parts `drop` in, then Morph to the exploded view, callouts `wipe` in.
- **Diagram film**: `diagram_video.py` MP4 (pipes draw on, dots flow), then the same diagram as editable shapes
  with native `zoom`/`wipe`/looping `path` effects.
- **Unit grid**: 10 row groups `wipe` in 90 ms apart. **Slope chart**: one line `wipe`s, Morph to the second.
- **Sticker poster**: tilted photos `drop`, tags `fly`, a sticker `teeter`s on click (`trigger`).
- **Click recipe**: step blocks per click (`click`: 1, 2, 3).
- **Hyperlink menu**: `"link": "<slide id>"` on menu items (a hand-made Summary Zoom that also works in 2016).
- **Looping background**: a `video` shape full-bleed under the content (a procedural MP4, ≤ 10 MB).

## 4. Not authored (PowerPoint UI only) and their fallbacks
Summary/Slide/Section **Zoom** (365/2019+; 2016 plays them as links; web none) → `link` menu. **3-D model
animations** (Arrive, Turntable; subscriber 365) → a rendered MP4 turntable. **Cameo**, **ink replay** → none.
**Lottie** (LottieFiles add-in inserts a GIF) → a GIF/MP4. Write these in the hand-off message if the user wants them.

## 4b. No-Morph safe mode (`"compat"`, v5.1)
Morph plays only in PowerPoint 365/2019+. PowerPoint 2016 and older, Google Slides, Keynote and LibreOffice read
the `mc:Fallback`, so a Morph scene becomes a fade where every shared `!!` shape jumps. Ask the brief's
**players** question (venue PC, Google Slides, Mac Keynote?) and set `deck.json` `"compat"`:

| compat | Morph slides become | Pick it when |
|---|---|---|
| `morph` (default) | Morph, fade fallback | the deck plays on PowerPoint 365/2019+ only |
| `dual` | Morph + a classic fallback (push/wipe by the main move direction, else fade); new `!!` shapes fade in | the deck travels: 365 gets Morph, everyone else gets a clean directional cut |
| `safe` | a core transition (`"safe_transition"`, default fade ≤ 800 ms) + rebuilt motion: moved `!!` shape → appear (zoom if resized) + motion path from its old place; resized only → zoom; changed text → type (byChar) / word (byWord) / fade; new `!!` → fade | the player is unknown or not PowerPoint 365, or the user says "không có Morph" |

How pros do it without Morph: one classic transition per chapter (push/wipe/cover), and inside a scene the
change is carried by entrances in reading order, a motion path for the one object that travels, a grow/pulse
for the number that matters, letter/word text. `safe` writes exactly that; still review it — hand-authored
`anim` on a shape always wins (shapes with an authored entrance or path are left alone).
Support: Keynote and LibreOffice play paths, zoom, fade, fly, wipe, letter-by-letter; **Google Slides keeps
fade/fly/zoom/spin and drops motion paths** (the shape then simply appears at its end place, which still reads).
Build: `python make_deck.py safe` → `deck-safe.json` → `studio.py build WORK --deck deck-safe.json`
(see `examples/phin-multistyle/build-safe.sh`).

## 5. Verify
- `check_deck.py`: transition per slide, effect census, ERROR on effects that target missing shapes or repeat
  timing ids, WARN on motion monotony (≥ 12 slides, > 85% Morph, no other effect family).
- `check_deck.py --compat safe|dual [--nomorph-render DIR --renders R]` (auto from motion.json): no-Morph gate,
  ERROR on Morph left in `safe` or a Morph-authored shared shape that moves with no path/entrance; renders a
  Morph-stripped copy and compares every slide's end state with the intended render (`studio.py` does this).
- `verify_motion.py DECK.pptx`: LibreOffice round trip (pptx → odp) counts imported effects per slide.
- `preview_motion.py DECK.pptx --out preview.mp4`: a labelled SIMULATION video (sprites per shape + the parsed
  timing). The real proof is PowerPoint 365: play it, or File › Export › Create a Video.
