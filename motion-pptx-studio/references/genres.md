# Genres: what changes from one kind of deck to another

The system (craft.md), the engine and the motion grammar are the same for every deck. What changes is
the story arc, the signature, the evidence, the research depth and the traps. `gates.py init --kind`
sets the research and imagery minimums listed here.

| Kind | Style pack to start from | Facts / domains | Kept images / real | Typical length |
|---|---|---|---|---|
| heritage (culture, history, craft, ceremony) | lacquer-heritage | 15 / 3 | 12 / 6 | 8-15 min, 30-50 slides |
| product (launch, demo, developer tool, app) | noir-product | 12 / 2 | 6 / 1 | 5-10 min, 20-35 slides |
| pitch (investors, contest, grant) | noir-product or boardroom-data | 12 / 3 | 6 / 1 | 3-8 min, 15-30 slides |
| business (review, report, consulting, finance) | boardroom-data or paper-editorial | 10 / 2 | 4 / 0 | 10-20 min, 15-35 slides |
| education (lecture, science, explainer, workshop) | paper-editorial or studio-pop | 12 / 3 | 8 / 3 | 10-30 min |
| event (festival, campaign, community, launch party) | studio-pop | 6 / 2 | 6 / 2 | 3-8 min |
| other | the closest pack | 10 / 2 | 6 / 2 | |

A pack is a starting point. Change its palette to the subject's own colours (sourced), keep its roles.

## Heritage and culture
- **Arc**: a sense, not a title (one sound, one object in darkness) → the object assembles → the
  problem (a date, a list, a fading practice) → the true parts (who, what, where) → the turn (the
  hero, the project) → what was made → what comes next → the close returns to the opening object.
- **Signature**: an object of the practice drawn in parts (the instrument's strings, a tool, a pattern
  from the real material). Never a generic national symbol.
- **Evidence**: the UNESCO file or the national institute, museum records, scholars; the practice's
  own vocabulary in the on-slide language.
- **Research**: `cultural-visual-accuracy.md` in full: TRUE and WRONG motifs, an anatomy checklist,
  an audit of the user's media frame by frame.
- **Traps**: neighbouring art forms in "matching" photos, foreign script in temple photos, terms with
  a loaded history, AI pictures that invent anatomy (four pegs, two drumsticks).
- **Example**: `examples/catru-mini` (7 keyframes) and the reference deck (`assets/reference/`).

## Product launch and demo
- **Arc**: the moment before the product (a typed question, an empty field) → the problem in one
  number → the reveal (the product lands in the frame) → how it works in 3 steps beside the screen →
  why people keep it (3 reasons, one lit) → what it costs or how to start → the close returns to the
  opening moment, now solved.
- **Signature**: the product's own primitive: the cursor, the icon, the notification dot, a light
  beam that scans each screen.
- **Evidence**: real screenshots with a version label, the repo, release notes, the pricing page,
  measured results with their conditions. Status words exactly as true: shipped, beta, designed, planned.
- **Research**: README, CHANGELOG, releases, the site, issues (for honest limits), the brand board.
  Never redraw a logo. Label drawn screens as illustrations.
- **Traps**: "playable" for a design, a benchmark without its conditions, a competitor's logo, a
  screenshot of another product's UI.
- **Example**: `examples/product-launch` (11 keyframes, a fictional product with drawn screens).

## Pitch (investors, contest juries, grants)
- **Arc**: the problem as a scene (a person, a cost, a moment) → why now → the solution (a reveal) →
  proof (traction, pilots, quotes) → the market in one number → the model → the team → the ask →
  the close returns to the person from the opening.
- **Signature**: the person or the object of the problem (an empty chair, a queue, a meter).
- **Evidence**: every number sourced and dated; projections labelled as projections.
- **Traps**: TAM/SAM/SOM slides with no sources, logos of "partners" who only had a meeting, a
  roadmap that reads as delivered.

## Business review and report
- **Arc**: the headline number (the answer first) → what drove it (2-3 reasons, revealed one by one)
  → where it fell short → what we will do (a roadmap rail) → the ask or decision → the number again.
- **Signature**: the headline number that shrinks into a corner and stays; or one line that becomes
  the horizon of every chart.
- **Evidence**: the company's own data with its period and definition; a source line on every
  data slide (boardroom-data puts `{source}` in the chrome).
- **Traps**: tables pasted from Excel, eight-colour pie charts, a chart whose title only names the
  axis, numbers with no period.
- **Example**: `examples/data-story` (11 keyframes, a fictional chain, illustrative numbers).

## Education, science, explainer
- **Arc**: a question the audience cannot answer yet → a model built step by step (each keyframe
  adds one part) → a worked example → a common mistake → the question again, now answerable.
- **Signature**: the model itself (an atom, a cell, a lever, a graph axis) or the teacher's mark (a
  chalk dot, a pencil line).
- **Evidence**: textbooks, papers, institutions; diagrams redrawn, credited, and checked for the
  conventions of the field (units, symbols, orientation).
- **Traps**: simplifications that become false, diagrams copied from a site with no licence,
  too much text because "students need notes" (give a handout instead).

## Event, campaign, community
- **Arc**: the feeling (a sound, a crowd, a colour) → what, when, where → who it is for → the
  programme (a rail of the day) → how to join → the feeling again.
- **Signature**: the event's object (a ticket, a lantern, a stage light, a sticker) that bounces from
  slide to slide.
- **Evidence**: dates, venue, partners as confirmed in writing; photos of the real place or past
  editions with permission.
- **Traps**: partner logos without permission, dates that changed, photos of strangers' faces
  without consent.
