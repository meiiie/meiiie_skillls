# Asset sourcing (Phase 2 → Gate 2)

Goal: a folder of **real, verified, licensed** images and objects, plus a CREDITS file that proves it.
A deck made from 3 stock icons and a gradient fails this skill even if it is pretty.

## 1. Where to search (in order)
| Source | Good for | How |
|---|---|---|
| The user's own material | product screenshots, team photos, logos, video frames | ask once; `video_frames.py` for videos |
| Official product assets | logos, brand board, screenshots, demo posters | repo `assets/`, site `og:image`, press kit; never redraw a logo |
| Wikimedia Commons | heritage photos, instruments, places, historic photos | `fetch_commons.py search` (licence metadata included) |
| Openverse | Flickr CC, museum collections | `fetch_commons.py search --source openverse` |
| Museum open access | objects on clean backgrounds | Smithsonian Open Access, The Met OA, Rijksmuseum, Europeana, national museum sites: check each record's licence |
| Google Fonts / OFL | typefaces | `fetch_fonts.py` (npm `@expo-google-fonts`, then github.com/google/fonts) |
| Generate yourself | grounds, foil objects, layered parts, patterns, drawn screens | `make_assets.py` (ground, foil, layers, photo, glow, pattern); your own SVG drawings of TRUE-list objects: own work |

Avoid: Pinterest, random Google Images, stock sites with unclear licences, AI images of the cultural
subject itself (they invent anatomy). AI or procedural **textures** (paper, lacquer, grain) are fine.

## 2. Search properly
```bash
python3 $S/fetch_commons.py search "ca trù"  --out WORK/assets/candidates
python3 $S/fetch_commons.py search "đàn đáy" --out WORK/assets/candidates   # appends; adds the ASCII-folded query
python3 $S/fetch_commons.py search "Ca tru singing" --source commons,openverse --out WORK/assets/candidates   # Openverse is opt-in (v5.3)
```
- **Commons is the default source.** Openverse is opt-in: from many cloud hosts it hangs; v5.3 gives it a
  12 s timeout and one retry, then moves on.
- **Writing queries that return something** (v5.3, from the VinFast test): quoted multi-word queries
  are exact-phrase, so "VinFast VF 3" returned nothing while `VinFast VF3` and `VinFast` + browsing the
  category worked. Try: the brand alone; the model with and without the space; the place in the local
  language and in English ("Hải Phòng", "Hai Phong"); `--loose`; then open the Commons **category**
  page of the best hit and take neighbours from it. A short coined name ("V-Green") matches unrelated
  words (birds, cricket): add the parent brand or skip it.
- Multi-word Commons queries are quoted automatically (unquoted "ca trù" returned unrelated houses).
- Each search writes `candidates.json`, `candidates.tsv` (captions) and `contact*.jpg` with licence, author and use tag
  (full-bleed / half-panel / inset-icon only, decided by size).
- NC/ND images are skipped unless you pass `--allow-nc`. Don't pass it for contests, TV or commercial work.

## 3. Review: look, compare, decide
Open every contact sheet. For each promising image, compare it with `research/accuracy.md`:
- Is it the right instrument, the right place, the right technique? Count strings and pegs.
- Is there foreign script, a watermark, a modern logo, or a recognisable private person?
- Is the resolution enough for its use (full-bleed ≥ 1920 px wide; half panel ≥ 1000 px; inset smaller)?
Real false positives seen in this skill's own test: string quartets ("dan" matched a name), a North Carolina
road sign ("NC CA TRU"), and an Openverse "Ca Tru" set that showed đàn tranh and sáo.

## 4. Keep (writes CREDITS automatically)
```bash
python3 $S/fetch_commons.py keep "commons:Ca trù performance.jpg" --as 01_catru_trio.jpg \
  --subject "Ca trù on stage: 2 ca nương, kép đàn đáy" \
  --why "female singers + đàn đáy player (facts 2.1); trống chầu not visible: don't caption as the full trio" \
  --dest WORK/assets --credits WORK/assets/CREDITS.md --candidates WORK/assets/candidates/candidates.json
```
- `--why` cites the fact ID and states the limits honestly (the test caught itself claiming a trống chầu that was not in the photo).
- TIFF and WebP are converted to JPEG automatically.
- Unverified subject? Add `--uncertain` (goes to `_uncertain/`, used as atmosphere only, never captioned).
- Write the **rejected** candidates and reasons under "Rejected during research" in CREDITS.md.
- Then: `python3 $S/contact_sheet.py WORK/assets --out WORK/assets/contact.jpg` and look at the kept set once more.

## 5. Licences
| Licence | Use? | Credit |
|---|---|---|
| CC0, Public Domain, PDM | yes | not required; credit anyway |
| CC BY x.0 | yes | author, title, licence, source on the credits slide |
| CC BY-SA x.0 | yes | as BY, and edits stay BY-SA: "(đã chỉnh sửa / edited)" |
| CC BY-NC / NC-SA / ND | **no** by default | only for clearly private, non-commercial, unedited use |
| "All rights reserved", unknown | no | ask the owner or skip it |
| Official logos and screenshots of the user's own product | yes (owner) | note "© owner, used with permission" |
Put a short credit on the slide where the image appears (for example "Ảnh: Michael Coghlan, CC BY-SA 2.0") and the
full list on a credits slide near the end.

## 6. Prepare assets
| Need | Tool |
|---|---|
| Museum object on white (or a craft on black space), to place on a page | `python3 $S/cutout.py in.jpg out.png` (v5.4: border-connected background with an edge-detail test, so dark parts of the object such as solar panels or lacquer stay; holes closed and filled; `--defringe 6` un-mixes the old background from the outline; `--bridge 40` also closes wide dark bays that open to the edge, at the cost of filling real gaps; `--tol`, `--close`, `--edge`; EXIF-rotated phone photos come out upright; `--rembg` for busy backgrounds). LOOK at it on a light and a dark page. |
| Han characters or other text inside a photo | `python3 $S/inpaint_text.py in.jpg out.jpg --box x0,y0,x1,y1 --vblur 61 --preview p.png` |
| Frames from a video | `python3 $S/video_frames.py v.mp4 --out frames --every 5 --sheet` (or `--scene 0.35`) |
| Duotone / sepia / mono + colour pair for a muted opening and a bloom | `python3 $S/make_assets.py photo in.jpg --mode duotone --colors "#140B08,#E2BE7C" --aspect 16:9 --pair --out WORK/assets/x.jpg` |
| A material ground (lacquer, paper, noir, clean grid, halftone, flat) | `python3 $S/make_assets.py ground --style <pack> --name main --out …` or `--kind … --base … --tone …` |
| A drawn object in one finish (gold, silver, copper, bronze, ink, chalk, neon, metal) | `python3 $S/make_assets.py foil object.svg --finish gold --out WORK/assets/object.png` |
| Layered object for Morph | one SVG, one top-level `<g id="part">` per moving part on the same canvas: `python3 $S/make_assets.py layers object.svg --finish gold --out-dir WORK/assets/object` |
| Bands and tiles (woven mat, dots, stripes, hatch, chevron, grid) | `python3 $S/make_assets.py pattern --kind woven --finish gold --size 2400x300 --out …` |
| The ca trù drawings of the reference deck | `python3 $S/make_assets_example.py --out WORK/assets/gen` (a worked example of drawings in SVG) |
Keep originals in `WORK/media_orig/`. Every derivative gets its own CREDITS row ("same as 01, pillar text
inpainted", with the source URL and "(đã chỉnh sửa)"). Look at each result on a dark background before use.

## 6b. Generated assets (Codex image gen, v5.3)

The second source after licensed photos. Use it for what a photo cannot give you and what claims
nothing: **textures** (brushed aluminium, pressed steel, wet asphalt), **abstract backgrounds**
(drafting paper, light trails), **object renders** of a generic thing (a prismatic cell, a busbar), and
**scene plates** (a misty plain at dawn, an empty test track). Never: clichés (books, scales, lightbulbs,
handshakes, robots, globes in hands, puzzles, rockets), logos or badges, real people, anything that looks
like a news/documentary photo of a real event, place or product, charts or maps, text in the image.

```bash
python3 $S/gen_assets_codex.py probe                       # is codex logged in and able to make images?
python3 $S/gen_assets_codex.py lint --spec WORK/design/codex-assets.json
python3 $S/gen_assets_codex.py run WORK --spec WORK/design/codex-assets.json --jobs 3
```

Spec: `{"brands": ["VinFast", ...], "items": [{"name": "tex-alu-whiteblue", "kind": "texture",
"aspect": "16:9", "prompt": "brushed aluminium sheet, cool white light, faint blue reflections..."}]}`.
The linter rejects banned subjects and brand names before anything runs (negations such as "no logos"
are fine), and every prompt gets a suffix: no text, no logos, no people, not a photo of a real event.
Each file lands in `assets/gen/<name>.jpg` (≤ 2560 px, EXIF-normalised) with `<name>.json` (prompt, model,
session) and a CREDITS row whose licence reads **"AI-generated (no third-party rights claimed; label as
AI)"**. Gate 2 fails a file in assets/gen without that label or sidecar. On the slide, an AI plate behind
a real fact is a ground, never evidence; if a viewer could take it for a photo of the subject, add
"ảnh minh họa AI" / "AI illustration" in the caption.

How it works: `codex exec` (Codex CLI ≥ 0.16, logged in; no API key needed) runs its built-in image
tool, which writes to `$CODEX_HOME/generated_images/<session>/`; the script picks the new file of that
session. 25–60 s per image. **Fallback** when `probe` exits 2 (no codex, not logged in, no image tool):
procedural grounds (`make_assets.py`), drawn SVG motifs, or `asset_scarcity`. Never fill the gap with
unlicensed web images.

## 6c. Third-party logos and brand marks
When the subject is a company that is not the user's: use a licensed photo of the real sign or a file from
the company's press kit, unaltered, with a trademark note in CREDITS; never redraw, recolour or generate a
logo. Product names in type are fine; the mark is not decoration.

## 7. Quantities that reproduced the reference decks
- Heritage, 10–15 min: about 40 candidates reviewed, 16 kept, 2 uncertain, 7 rejected with reasons.
- Product, 6–8 min: the official logo, 1 real screenshot (version labelled), 1 demo poster, a brand-board grid
  background and a mascot, all from the repo, with the AI-made mascot labelled as such.
`gates.py` reports these as **advisory** habits since v5.3 (WARN, not FAIL): 12 kept for heritage, 6 for
product, 2× as many candidates looked at as files kept (one rule for every kind). What stays hard: every
image under assets/ and assets/gen/ has a CREDITS row with a licence, a source and a reason.
`fetch_commons.py keep` now applies EXIF rotation, turns MPO/TIFF/WebP into JPEG/PNG and downsizes to
2560 px at keep time (the original goes to media_orig/full/), so the 25 MB limit is not met for the first
time at Phase 5. `contact_sheet.py` writes a manifest next to the sheet; gate 2 compares names and sizes,
not file times.
Gate 2 also reads the storyboard once it has 3 or more rows: distinct visuals ≥ scenes, and no file or `drawn:` motif on more than 4 rows. Gate 4 checks the same thing even if you run it before Gate 2.

## 8. When there is nothing you may use (asset scarcity)
Some subjects have no openly licensed image: a commercial game's art, a living designer's unpublished drawings, a logo you were not given. Stretching one official screenshot across a whole scene is the failure mode (one Mondstadt frame on six slides of a 23-slide deck). Do one of these, and say which:

1. **Illustrate from the TRUE list.** Build procedural or drawn assets (`make_assets_example.py`, or your own drawing) of motifs that `research/accuracy.md` marks TRUE. Label them as illustrations on the slide and in CREDITS (licence `drawn` or `own work`, your name, why the motif is accurate, a source URL for the motif even though the pixels are yours). `drawn:<motif>` in the storyboard counts as a visual.
2. **Shrink.** Set `asset_scarcity: <one sentence on why no licensed images exist>` in `brief.md`, tell the user in the next message, and plan only as many scenes as you have distinct visuals (Gate 4 lowers the scene minimum to that count, never below 2). The real-photo minimum at Gate 2 becomes 0. The kept-file minimum does not: every illustration still needs a CREDITS row. Distinct visuals ≥ scenes and the 4-row cap still apply.

Do not caption a game screenshot as if you photographed it, and do not duplicate one file under several names to clear the distinct-image count.
