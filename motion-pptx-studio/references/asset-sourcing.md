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
| Google Fonts / OFL | typefaces | github.com/google/fonts (see art-direction.md) |
| Generate yourself | textures, ornaments, diagrams | `make_assets_example.py`, numpy or PIL, SVG with cairosvg: CC0 by you |

Avoid: Pinterest, random Google Images, stock sites with unclear licences, AI images of the cultural
subject itself (they invent anatomy). AI or procedural **textures** (paper, lacquer, grain) are fine.

## 2. Search properly
```bash
python $S/fetch_commons.py search "ca trù"  --out WORK/assets/candidates
python $S/fetch_commons.py search "đàn đáy" --out WORK/assets/candidates   # appends; adds the ASCII-folded query
python $S/fetch_commons.py search "Ca tru singing" --source openverse --out WORK/assets/candidates
```
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
python $S/fetch_commons.py keep "commons:Ca trù performance.jpg" --as 01_catru_trio.jpg \
  --subject "Ca trù on stage: 2 ca nương, kép đàn đáy" \
  --why "female singers + đàn đáy player (facts 2.1); trống chầu not visible: don't caption as the full trio" \
  --dest WORK/assets --credits WORK/assets/CREDITS.md --candidates WORK/assets/candidates/candidates.json
```
- `--why` cites the fact ID and states the limits honestly (the test caught itself claiming a trống chầu that was not in the photo).
- TIFF and WebP are converted to JPEG automatically.
- Unverified subject? Add `--uncertain` (goes to `_uncertain/`, used as atmosphere only, never captioned).
- Write the **rejected** candidates and reasons under "Rejected during research" in CREDITS.md.
- Then: `python $S/contact_sheet.py WORK/assets --out WORK/assets/contact.jpg` and look at the kept set once more.

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
| Museum object on white, to place on a dark slide | `python $S/cutout.py in.jpg out.png` (flood fill from the corners; `--rembg` for busy backgrounds) |
| Han characters or other text inside a photo | `python $S/inpaint_text.py in.jpg out.jpg --box x0,y0,x1,y1 --vblur 61 --preview p.png` |
| Frames from a video | `python $S/video_frames.py v.mp4 --out frames --every 5 --sheet` (or `--scene 0.35`) |
| Duotone / sepia versions for a muted opening | `python $S/make_assets_example.py --photo path\|name` (duo_ and col_ versions) |
| Procedural textures and gold-leaf motifs | `python $S/make_assets_example.py --out WORK/assets/gen` (adapt it to your TRUE list) |
| Layered object for Morph | draw or cut each part (head, neck, body) onto **one shared canvas size** so the parts line up when stacked |
Keep originals in `WORK/media_orig/`. Every derivative gets its own CREDITS row ("same as 01, pillar text
inpainted", with the source URL and "(đã chỉnh sửa)"). Look at each result on a dark background before use.

## 7. Quantities that reproduced the reference decks
- Heritage, 10–15 min: about 40 candidates reviewed, 16 kept, 2 uncertain, 7 rejected with reasons.
- Product, 6–8 min: the official logo, 1 real screenshot (version labelled), 1 demo poster, a brand-board grid
  background and a mascot, all from the repo, with the AI-made mascot labelled as such.
`gates.py` enforces minimums (12 kept for heritage, 6 for product, scaled down for talks under 5 minutes).
