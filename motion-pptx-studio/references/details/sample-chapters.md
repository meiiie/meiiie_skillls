# sample-chapters.md - details (moved from principles/ in v6.22)
- **Sandboxed (critic.sh cannot start):** spawn a fresh subagent with references/critic-pick-prompt.md and the
  images; it ends pick.md with `<!-- signed: critic.sh subagent -->`. Never edit build.py or copy it to pass the gate.
- **Hard stop, not skippable (v6.22).** build.py refuses any full deck until samples/ holds >= 3 built chapters and a
  critic-signed pick.md newer than them, inside this project. If the
  critic cannot start, END YOUR TURN: tell the user the three samples are ready for an independent pick.
  Writing or signing pick.md yourself is forbidden.
- Samples build with `--min-films 0` (build.py does this automatically under a samples/ folder); films start with the full deck.
