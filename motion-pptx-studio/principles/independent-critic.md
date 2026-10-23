# independent-critic
A builder grades its own deck 8-9 when an outside eye says 6-7. Self-scores do not count.
- **After the first full build, a fresh critic looks.** `scripts/critic.sh renders/rN` starts a new session
  that never saw your plans, shows it the yardsticks (examples/yardsticks, credited) beside your contact
  sheets and writes critique.md: a harsh score, the 8 weakest slides with a redesign order each, one deck-wide order and a repetition list.
- **One redesign loop is mandatory.** Apply the deck-wide order to EVERY slide, break every repetition, carry out every order (or write why one is wrong, with the image
  that proves it), rebuild, render, and put before/after of those slides in one compare image.
- **If codex cannot start** (a sandboxed agent), give references/critic-prompt.md and the same images to a
  fresh subagent or new chat. If none exists, say so in NOTES.md; never fill the score in yourself.
- **Report both scores** in NOTES.md: the critic's, then yours after the loop, each with one line why.
- The critic judges what it SEES at 1x: empty fields, small subjects, clip-art, lists, missing photographs.
