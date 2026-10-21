"""storyboard.md from deck.json + the per-slide direction table below (the intent, not the build)."""
import json, re
from pathlib import Path
HERE = Path(__file__).parent
d = json.loads((HERE / 'deck.json').read_text(encoding='utf-8'))
SCENE = {'dot': 'S1 Mở', 'title': 'S1 Mở', 'route': 'S1 Mở', 'season': 'S2 Quỹ đạo', 'epic': 'S2 Quỹ đạo', 'earthrise': 'S3 Về gần', 'marble': 'S3 Về gần',
         'spin': 'S3 Về gần', 'limb': 'S4 Bầu trời', 'layers': 'S4 Bầu trời', 'air': 'S4 Bầu trời', 'air2': 'S4 Bầu trời',
         'water': 'S5 Mặt đất', 'plates': 'S5 Mặt đất', 'lava': 'S6 Lòng đất', 'xsec': 'S6 Lòng đất', 'mantle': 'S6 Lòng đất',
         'core': 'S6 Lòng đất', 'clock': 'S7 Thời gian và về nhà', 'seconds': 'S7 Thời gian và về nhà', 'close': 'S7 Thời gian và về nhà',
         'credits': 'S8 Nguồn'}
DIR = {  # id: (keyframe role, layout / composition, visual, choreography)
 'dot': ('K1 hook: a dot you cannot see', 'void + tiny focal point (90% empty)', 'pale_blue_dot.png', 'slow grow (Ken Burns) → ring zoom + pulse loop → leader wipe → letters'),
 'title': ('K2 push-in ×2.6 on the dot', 'giant type bleeding low-left, dot top-right', 'pale_blue_dot.png', 'Morph push-in; title wipe up; ring pulse loop'),
 'route': ('K3 crop-morph into a vertical slice = the route', 'vertical rail + menu (hyperlinks)', 'pale_blue_dot.png', 'Morph crop; rail wipe; stops zoom (stagger 120 ms); titles fly'),
 'season': ('K1 150 million km: the orbit', 'full-bleed diagram film, title top-left', 'frame:seasons.poster.png', 'zoom transition; Manim film; title wipe; myth on click (fly)'),
 'epic': ('K2 1.5 million km: the Moon crosses Earth', 'small-in-void: tall numeral column left, disc centre-right', 'epic_moon.jpg', 'uncover left; slow grow; numeral rise; unit wipe; words'),
 'earthrise': ('K2 384,400 km: Earth rises', 'horizon at bottom third, parallax 3 planes', 'earthrise.jpg', 'push up; stars drift (far), Earth rises (mid), Moon slides (near): parallax'),
 'marble': ('K3 29,400 km: the whole disc', 'disc bleeding off the right edge, numeral left', 'blue_marble.jpg', 'fly-in + spin settle; numeral rise; word reveal'),
 'spin': ('K4 the day: the globe turns', 'centred globe film + orbit ring', 'frame:globe.poster.png', 'Morph shrink of the photo → looping globe film; orbit wheel; ISS orbit path loop; split numerals'),
 'limb': ('K1 400 km: the thin line', 'diagonal: type rotated 25° along the limb', 'limb_sunset.jpg', 'flythrough; slow drift path; word-by-word text'),
 'layers': ('K2 five layers (Hình 2)', 'scientific plate left, label column right', 'drawn:atmosphere-plate', 'strata wipe up staggered; leaders wipe; plane/ISS/meteor paths; aurora sway'),
 'air': ('K3 one breath: 78/21/1', 'proportional strip, numerals as typography', 'drawn:air-strip', 'push; strip wipes in proportion; numerals rise; loupe zoom + pulse'),
 'air2': ('K4 zoom into the last 1%', 'same strip ×100 (Morph scale)', 'drawn:air-strip', 'Morph zoom; CO₂ sliver zoom + pulse loop; 422,8 ppm on click'),
 'water': ('K1 0 km: the water cycle (Hình 4)', 'diorama: sea low-left, land right, numeral in the sea', 'drawn:water-cycle', 'cover up; sea/land wipe; droplets on curved looping paths; rain loops; cloud drift'),
 'plates': ('K2 the ground drifts (Hình 5)', 'full-bleed diagram film', 'frame:plates.poster.png', 'fade; looping Manim film; title wipe'),
 'lava': ('K1 go deeper: the cut', 'diagonal split: photo left, poster type right', 'lava.jpg', 'split transition; photo grow; diagonal plate path-in; type split'),
 'xsec': ('K2 the cut-away, to scale', 'quarter cut-away bleeding left, labels right', 'drawn:cross-section', 'reveal; shells wheel in from the core out; leaders wipe; labels fly'),
 'mantle': ('K3 zoom ×4.2 into the mantle', 'macro: one curved surface fills the frame', 'drawn:cross-section', 'Morph zoom; convection arrows spin loops; numeral rise'),
 'core': ('K4 the centre', 'quarter-disc in the corner, numeral top-right', 'drawn:cross-section', 'Morph zoom; core glow pulse loop; numeral zoom'),
 'clock': ('K1 4.54 Ga as one day', 'dial left, ledger right', 'drawn:24h-dial', 'dissolve; hand spins 6 s; eon bands, dots and rows land exactly when the hand passes'),
 'seconds': ('K2 the last minute ×26', 'dial edge as horizon, giant numeral', 'drawn:24h-dial', 'Morph zoom; ticks wipe; letters "6 giây"'),
 'close': ('K3 back to the dot', 'void + dot, quote left (bookend of slide 1)', 'drawn:dot', 'Morph; dot zoom; ring pulse; quote letters'),
 'credits': ('appendix: sources', 'ledger', 'drawn:ledger', 'fade; rows letter-in'),
}
def txt(s):
    t = s.get('text')
    if isinstance(t, list):
        return ' '.join(r.get('text', '') for r in t)
    return t or ''
def walk(shs):
    for s in shs:
        yield s
        if s.get('type') == 'group':
            yield from walk(s.get('shapes', []))
rows = []
for i, sl in enumerate(d['slides'], 1):
    role, lay, vis, mot = DIR[sl['id']]
    shs = list(walk(sl['shapes']))
    on = ' '.join(txt(s).replace('\n', ' ') for s in shs if s.get('type') == 'text' and not (s.get('name') or '').startswith(('!!g-', '!!folio')))
    on = re.sub(r'\s+', ' ', on).strip()
    if len(on) > 400:
        on = on[:397] + '…'
    layers = ' '.join(sorted({s['name'] for s in shs if (s.get('name') or '').startswith('!!') and not s['name'].startswith('!!g-')})[:4]) + ' !!g-dot'
    notes = sl.get('notes', '').split('\n\nNguồn:')[0]
    words = len(notes.split())
    tr = sl['transition']
    ms = tr.get('ms', '') if tr['type'] == 'morph' else f"{tr['type']} {tr.get('ms', '')}"
    rows.append(f"| {i} | {SCENE[sl['id']]} | {role} | {lay} | {layers} | {vis} | {on.replace('|', '/')} | {mot} | {sl.get('source', '—')} | {words} | {ms} |")
total = sum(int(r.split('|')[10]) for r in rows)
head = f"""# Storyboard (Gate 4)
- target: 6 min · budget: ~850 words (words_budget measure: {total} spoken words → 5:42-6:34)
- anchor: "Đây là nhà" (on-slide: slide 1 setup, slide 12 middle at 0 km, slide 20 close)
- colour arc: S1-S3 #05070B (cosmos black) → S4-S5 #EDE5D3 (atlas paper; the limb photo is the hinge) → S6 #120605 (inferno ember) → S7 #0A1020 (deeptime navy) → close #05070B
- circular close: slide 20 returns to the opening dot at the same position (DOT1), the gauge flies back to 6 tỉ km

The signature: an altitude/depth gauge (!!g-rail, !!g-dot, !!g-val ...) on every slide; it is log-scale above the surface and
linear below, so the orange dot falls monotonically for 17 slides and returns to the top in the close.

| # | scene | keyframe role | layout | layers | visual | on-slide text | motion | source | words | morph ms |
|---|---|---|---|---|---|---|---|---|---|---|
"""
(HERE / 'storyboard.md').write_text(head + '\n'.join(rows) + '\n', encoding='utf-8')
print(total, 'words')
