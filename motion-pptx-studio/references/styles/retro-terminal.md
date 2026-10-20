# retro-terminal — phosphor on CRT black

**Use for** credits, developer stories, security, game and computing history; a one-slide palate cleanser.
**Palette** CRT `#040B06` with scanlines (`make_assets.py` ground `scanline`), phosphor `#A6FFA6`, head `#D4FFD4`,
amber cursor `#FFB000`.
**Fonts** VT323 (display, labels) · IBM Plex Mono (text). Both pass Vietnamese.

## Layout grammar
- A prompt line in the chrome (`~/credits $`), a command as the title (`cat sources.txt`), output lines left-aligned
  in mono at 13–16 pt, one per fact/licence.
- No boxes; a code block is just indentation and the amber cursor.

## Signature motion
- The command types letter by letter (`type`, `step` 10%), output lines `appear` 180 ms apart; the cursor `blink`s.
- Transition `dissolve` or `randombars` as a screen glitch.

## Avoid
Green on green below 4.5:1, long paragraphs, "matrix rain" clip-art.
