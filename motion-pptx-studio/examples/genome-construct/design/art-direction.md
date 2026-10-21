# Art direction (compiled from design/genome.json; edit the genome, not this file)
<!-- genome -->

- style: design/style.json (genome "ben-may", family boardroom-data)
- label: Cool paper, deep teal, navy for capacity: numbers as heroes, bars that are the berths

## Style choice
- chosen: boardroom-data (fit 0.772) as the starting family, then re-decided axis by axis in the genome; why: highest fit 0.77: covers economy, business (subject 1.00), register near analytical, calm, precise (tone 1.00), no kept pictures yet (material 0.35)
- rejected: desktop-os, a fictional desktop makes official statistics look like a game; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: heritage-collage, collage softness, tilted prints and a script accent make figures look approximate; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: kinetic-type, a type-only show of one huge word per slide cannot carry many sourced figures; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: lacquer-heritage, gold-on-lacquer ceremony makes a data briefing look like a ritual object; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: neo-brutal, sticker shadows and lime blocks make inflation and debt look like a joke; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: papercut-collage, craft paper and torn edges make figures look homemade; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: retro-terminal, a hacker-terminal register speaks to the wrong audience; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: studio-pop, cartoon outlines and sun yellow trivialise inflation and debt; this deck is about economy (1.00: declared, cảng, sản lượng, container), which needs figures that read exact at a glance, daylight legibility for dense numbers and a source on every one
- rejected: blueprint, fit 0.38 < 0.40, weakest on subject (0.00): its subjects ['engineering', 'aerospace', 'technology'] do not cover what this deck is about ['economy', 'business']
- rejected: direction:C, fit 0.38 < 0.40, weakest on subject (0.00): its subjects ['engineering', 'aerospace', 'technology'] do not cover what this deck is about ['economy', 'business']
- rejected: glass-tech, fit 0.28 < 0.40, weakest on tone (0.00): its register (bold, cinematic) is far from this deck's (analytical, calm, precise)
- rejected: noir-product, fit 0.39 < 0.40, weakest on subject (0.19): its subjects ['technology', 'aerospace', 'engineering'] do not cover what this deck is about ['economy', 'business']

## Palette (every hex with where it comes from)
- ground #F5F7FA: a cool flat ground: nothing competes with the figures (explicit in the genome)
- ground2 #E6E8EB: second ground for alternating scenes (derived: the ground moved 6% toward black)
- surface #DCDEE1: card and panel fill (derived: the ground moved 10% toward black)
- ink #0F1722: body text, held at 7:1+ against the ground as it renders (explicit in the genome)
- accent #0E7C6B: teal for the measured throughput (explicit in the genome)
- accent2 #1F3A5F: navy for capacity, the lit bar on the capacity slide (explicit in the genome)
- muted #595E66: labels and sources, 5:1 against the darkest rendered ground (derived: ink mixed 38% into the ground, held at 5:1)

## Colour arc
- S1 title on ground → S2 bars on ground → S3 capacity in navy

## Motifs and textures
- flat ground (grain 0.0)
- photographs as found

## Layered objects (Morph)
- the berth bar that splits into the new berth

## Signature
- the berth bar that splits into the new berth

## Motion vocabulary
- grammar: bars grow from the baseline (how a quantity is made), the line is drawn along its stroke
- tempo 1100 ms, stagger 120 ms; transitions morph
- grow: stretch from the contact edge (GrowFromEdge)
- create: wipe along the stroke (Manim Create)
- write: letter-by-letter type (Write)

## Type and grid
- type: one sans family pair, numbers at display size
- grid: 12 columns, figure left, chart right
- composition: one figure + one drawn chart per slide
