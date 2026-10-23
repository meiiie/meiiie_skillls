# hero-plan
R13 first builds scored 4.5-5 with the critic: the look was decided slide by slide while coding, so explanation
slides fell back to cream diagrams and number cards. Plan every slide's visual before writing make_deck.py.
- **design/hero-plan.md, after the library and the pick, before code:** one row per slide
  `| slide | chapter | purpose | visual | source |`. visual = photo, bleed, cutout, pair, sequence, mask, object,
  poster, 3d, film or diagram; source = a library file, a film script or `type`.
- **Every chapter opens on a hero** (bleed, cutout, film or 3-D still) with a real source, chosen for the signature device.
- **Explain with things, not boxes.** A mechanism is shown by a photo of the thing working, a cut-out object with
  2-3 leader labels, a lit ManimGX 3-D still or a film. A flat diagram only when nothing physical shows it:
  max(2, slides/8) per deck, never a chapter opener, drawn in the deck's treatment (unity).
- **Numbers sit on their object** (data-as-object): 250 pt on the photo of the thing counted, not on a cream card.
- **Gate:** `scripts/photo_library.py plan design/hero-plan.md` (build.py runs it): fails missing sources, a chapter
  without a hero, a diagram opener, too many diagrams, "drawing"/"card" visuals.
- Build only what the plan names; change the plan first, then the code.
