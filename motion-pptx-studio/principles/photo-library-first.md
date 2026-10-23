# photo-library-first
The best decks (8-8.5) were image-led: the photo came first, the slide was built around it.
- **Right after facts + concept, before samples:** 12-15 real candidates per chapter in library/CH/ (Commons,
  Openverse, Unsplash, Pexels, NASA/ESA, archives, press kits; fetch_commons.py, Vietnamese AND English). library.json
  entry: file, url, licence, author, subject (plain noun phrase), job.
- **Hero quality:** each chapter's hero is a real photo >= 1600 px long side (the original, not a thumbnail).
- **4+ different subjects per chapter:** place, object, people, detail, archive. Eight server halls are one subject.
- **No photo of the exact thing** (unreleased product, concept): real comparable objects and contexts (a real
  e-bike of the class, the dock, the commuter street, the battery cell, a hand on the bar) plus a ManimGX/Anatomy
  render of it lit like a photo. Never flat vector drawings.
- **Abstract: concept -> physical thing first** (inflation -> a price board; privacy -> a phone in a hand), mapped
  in library/README.md, then searched.
- **Board, look, pick:** `photo_library.py board` -> board-CH.jpg; jobs hero, detail, wide, sequence; rest "candidate".
- **Write slides FROM the library** via design/hero-plan.md; samples use different picks.
- **Gate:** `photo_library.py check ... --deck --pptx` (build.py): >= 8 real candidates, hero >= 1600 px, hero + 3
  jobs, licence + url, >= 2 slides/chapter from picks, photos on >= half the slides, one photo on <= 2 slides.
- Graded or cropped copies (assets/img/sNN.jpg) name their library file in the slide's `"photo_from": ["library/..."]`;
  the LIB gate matches through it.
