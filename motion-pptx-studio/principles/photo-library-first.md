# photo-library-first
The 8.5 decks were image-led: the photo came first and the slide was built around it. Text-led decks fall
back to cards and repeated drawings. So collect the pictures before you write a single slide.
- **Right after facts + concept, before samples:** per chapter 8-15 real photo candidates in
  library/CH/, from Commons, Openverse, Unsplash, Pexels, NASA/ESA, government and museum archives, press
  kits (fetch_commons.py search ... in Vietnamese AND English). Each entry in library/library.json:
  file, url, licence, author, subject (what it physically shows, a plain noun phrase), job.
- **4+ different subjects per chapter.** Eight server halls are one subject. Mix place, object, people, detail,
  document/archive. `check` fails a chapter with < 4 distinct subjects or > 1/3 look-alike candidate pairs.
- **Abstract topics: map each concept to a physical thing first** (inflation -> a market price board, a
  wallet; privacy -> a phone in a hand, a CCTV mast, a server hall; blockchain -> a ledger book, a mining
  rig, a Bitcoin ATM). Write that map in library/README.md, then photograph-search it.
- **Board, look, pick:** `photo_library.py board library/library.json` -> board-CH.jpg. Pick per chapter
  a hero (full-bleed), a detail or texture (macro), a wide (context) and, where it tells a process, a
  sequence; set those jobs, leave the rest "candidate".
- **Write slides FROM the library:** each slide names its pick and the job it does; text goes in the
  quiet area. Sample chapters use DIFFERENT picks from the same library, so the samples test directions,
  not photos. Drawings and diagrams fill in only where no photo can show it.
- **Gate:** `photo_library.py check library/library.json --deck deck.json --pptx deck.pptx` (build.py runs it
  for decks over 8 slides): >= 8 real candidates/chapter, hero + 3 jobs, licence + url, >= 2 slides per
  chapter from its picks, real photos on >= half the slides, one photo or drawing on <= 2 slides.
