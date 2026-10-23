# per-slide-critic
R12: three fresh critics per deck re-invented each slide's metaphor, ordered ~22 recompositions per loop and
named photos that did not exist; medians stayed 5.5-7 and one deck got worse. Studios keep ONE art director.
- **One persistent art director per deck, up to 3 loops.** Loop 1: `scripts/critic.sh --slides renders/rN critique-1.md`
  scores the deck (`DECK x`), fixes one PLAN (signature device) and gives AT MOST 5 orders, each naming a library photo
  (or CUT, type, film). Loop 2-3: `critic.sh --slides renders/rM critique-K.md renders/rN critique-(K-1).md` - the same
  director sees its last critique and the BEFORE/AFTER of each ordered slide, marks DONE yes/partly/no, re-issues
  undone orders word for word, adds new ones only up to 5.
- **CUT = `"hidden": true`** on the slide in deck.json (build_deck drops it, the source stays); never delete or
  reorder. Render each build into a new renders/rN. An order that fails a gate: revert, mark `DONE: conflict`.
- **Do every order fully** - a recomposition, not a nudge; a missing photo is fetched into the library first.
- **Keep the better render.** If DECK falls, revert to the previous build and deliver that one.
- **Stop when a loop gains < 0.5** or after 3 loops. NOTES.md lists each loop's DECK line and DONE marks.
- Never score yourself in the critic's place; a fresh subagent with the same prompts if codex cannot start.
