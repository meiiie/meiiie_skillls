"""TRÁI ĐẤT · Rơi về nhà — a 21-slide scale journey from 6 billion km to the centre of the Earth, then into deep time.
Four sub-styles (cosmos, atlas, inferno, deeptime), one signature (the altitude/depth gauge), dual compat.
python3 make_deck.py  ->  deck.json"""
import json, math, copy
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 13.333, 7.5
ORANGE = '#FF6A2B'

# ------------------------------------------------------------------ styles (each a layout grammar, see design/art-direction.md)
BASE = json.loads((Path('/workspace/skill-v4/motion-pptx-studio/assets/styles/blueprint.json')).read_text())


def style(name, label, pal, fonts, ground, roles, chrome_color):
    s = copy.deepcopy(BASE)
    s['name'], s['label'] = name, label
    s['palette'] = pal
    s['fonts'] = fonts
    s['font_files'] = [{'family': f, 'weights': '400,700'} for f in dict.fromkeys(fonts.values())]
    for k, v in roles.items():
        s['type'][k] = {**s['type'].get(k, {}), **v}
    s['grounds'] = {'main': ground}
    s['default_bg'] = 'main'
    s['chrome'] = {'over': [
        {'type': 'text', 'name': '!!folio', 'text': 'TRÁI ĐẤT · {n}/{total}', 'x': 0.6, 'y': 6.9, 'w': 3.4, 'h': 0.24, 'role': 'pageno', 'color': chrome_color}]}
    s['photo'] = {'duotone': [pal['ground'], pal['ink']], 'veil': 0.5}
    s['card'] = {**s['card'], 'fill': 'surface', 'line': 'faint'}
    return s


COSMOS = style('cosmos', 'Cosmos cinema: true black, NASA photography, hairline serif, micro mono captions, enormous empty space',
               {'ground': '#05070B', 'ground2': '#05070B', 'surface': '#0E1420', 'ink': '#E9EEF5', 'head': '#FFFFFF', 'muted': '#8A97A8',
                'faint': '#2A3342', 'accent': ORANGE, 'accent2': '#8FD8FF', 'lit': ORANGE, 'veil': '#05070B'},
               {'display': 'Fraunces', 'text': 'Be Vietnam Pro', 'label': 'JetBrains Mono'},
               {'kind': 'flat', 'base': '#05070B', 'tone': '#05070B', 'grain': 0.0, 'seed': 3},
               {'display': {'font': 'display', 'size': 150, 'bold': False, 'line': 0.86, 'spacing': -3, 'color': 'head'},
                'title': {'font': 'display', 'size': 46, 'bold': False, 'line': 0.98, 'spacing': -1, 'color': 'head'},
                'numeral': {'font': 'display', 'size': 110, 'bold': False, 'line': 0.85, 'spacing': -3, 'color': 'head'},
                'kicker': {'font': 'label', 'size': 11, 'bold': False, 'spacing': 2.5, 'caps': True, 'color': 'accent2'},
                'body': {'font': 'text', 'size': 17, 'line': 1.35, 'color': 'ink'},
                'subtitle': {'font': 'text', 'size': 20, 'line': 1.3, 'color': 'muted'},
                'label': {'font': 'label', 'size': 10, 'bold': False, 'spacing': 1.5, 'caps': True, 'color': 'muted'},
                'pageno': {'font': 'label', 'size': 9, 'bold': False, 'spacing': 1.5, 'color': 'muted'},
                'quote': {'font': 'display', 'size': 40, 'bold': False, 'line': 1.1, 'color': 'head'}}, '#8A97A8')
ATLAS = style('atlas', 'Atlas plate: warm paper, hand-built scientific illustration, ink hairlines, numbered figures, Fraunces italic captions',
              {'ground': '#EDE5D3', 'ground2': '#E4DAC4', 'surface': '#F6F0E2', 'ink': '#1E2A33', 'head': '#141C22', 'muted': '#6B6457',
               'faint': '#C9BEA6', 'accent': '#A8380A', 'accent2': '#2E6FA8', 'lit': ORANGE, 'veil': '#EDE5D3'},
              {'display': 'Fraunces', 'text': 'Be Vietnam Pro', 'label': 'JetBrains Mono'},
              {'kind': 'paper', 'base': '#EDE5D3', 'tone': '#E2D6BE', 'grain': 0.02, 'vignette': 0.25, 'seed': 41},
              {'display': {'font': 'display', 'size': 120, 'bold': False, 'line': 0.86, 'spacing': -3, 'color': 'head'},
               'title': {'font': 'display', 'size': 44, 'bold': False, 'line': 0.98, 'spacing': -1, 'color': 'head'},
               'numeral': {'font': 'display', 'size': 150, 'bold': False, 'line': 0.82, 'spacing': -4, 'color': 'head'},
               'kicker': {'font': 'label', 'size': 11, 'bold': True, 'spacing': 2.0, 'caps': True, 'color': 'accent'},
               'body': {'font': 'text', 'size': 16, 'line': 1.35, 'color': 'ink'},
               'subtitle': {'font': 'text', 'size': 19, 'line': 1.3, 'color': 'muted'},
               'label': {'font': 'label', 'size': 10, 'bold': False, 'spacing': 1.2, 'caps': True, 'color': 'muted'},
               'cardtitle': {'font': 'display', 'size': 20, 'bold': False, 'line': 1.0, 'color': 'head'},
               'pageno': {'font': 'label', 'size': 9, 'bold': False, 'spacing': 1.5, 'color': 'muted'}}, '#6B6457')
INFERNO = style('inferno', 'Inferno descent: ember-black ground, condensed poster numerals, heat gradient, concentric cut-aways',
                {'ground': '#120605', 'ground2': '#1C0906', 'surface': '#2A0E08', 'ink': '#F7E7DA', 'head': '#FFF4EA', 'muted': '#C29A86',
                 'faint': '#4A2218', 'accent': '#FFB23F', 'accent2': ORANGE, 'lit': ORANGE, 'veil': '#120605'},
                {'display': 'Anton', 'text': 'Be Vietnam Pro', 'label': 'JetBrains Mono'},
                {'kind': 'noir', 'base': '#0E0504', 'tone': '#3A1208', 'lift': [0.3, 0.75], 'grain': 0.02, 'vignette': 0.5, 'seed': 66},
                {'display': {'font': 'display', 'size': 120, 'bold': False, 'line': 0.9, 'spacing': 0, 'caps': True, 'color': 'head'},
                 'title': {'font': 'display', 'size': 48, 'bold': False, 'line': 1.0, 'spacing': 0.5, 'caps': True, 'color': 'head'},
                 'numeral': {'font': 'display', 'size': 200, 'bold': False, 'line': 0.85, 'spacing': -1, 'color': 'accent'},
                 'kicker': {'font': 'label', 'size': 11, 'bold': True, 'spacing': 2.5, 'caps': True, 'color': 'accent'},
                 'body': {'font': 'text', 'size': 17, 'line': 1.35, 'color': 'ink'},
                 'subtitle': {'font': 'text', 'size': 20, 'line': 1.3, 'color': 'muted'},
                 'label': {'font': 'label', 'size': 10, 'bold': False, 'spacing': 1.5, 'caps': True, 'color': 'muted'},
                 'pageno': {'font': 'label', 'size': 9, 'bold': False, 'spacing': 1.5, 'color': 'muted'}}, '#C29A86')
DEEP = style('deeptime', 'Deep-time instrument: midnight navy, a 24-hour dial, tabular mono numerals, one lime hand',
             {'ground': '#0A1020', 'ground2': '#0A1020', 'surface': '#111A30', 'ink': '#DCE4F2', 'head': '#FFFFFF', 'muted': '#7D8AA6',
              'faint': '#26324D', 'accent': '#C6FF4A', 'accent2': ORANGE, 'lit': ORANGE, 'veil': '#0A1020'},
             {'display': 'Fraunces', 'text': 'Be Vietnam Pro', 'label': 'JetBrains Mono'},
             {'kind': 'clean', 'base': '#0A1020', 'tone': '#0E1730', 'grid': 0.5, 'grid_alpha': 0.025, 'seed': 9},
             {'display': {'font': 'label', 'size': 120, 'bold': True, 'line': 0.9, 'spacing': -4, 'color': 'head'},
              'title': {'font': 'display', 'size': 42, 'bold': False, 'line': 1.0, 'spacing': -1, 'color': 'head'},
              'numeral': {'font': 'label', 'size': 150, 'bold': True, 'line': 0.85, 'spacing': -6, 'color': 'accent'},
              'kicker': {'font': 'label', 'size': 11, 'bold': True, 'spacing': 2.5, 'caps': True, 'color': 'accent'},
              'body': {'font': 'text', 'size': 16, 'line': 1.35, 'color': 'ink'},
              'subtitle': {'font': 'text', 'size': 19, 'line': 1.3, 'color': 'muted'},
              'label': {'font': 'label', 'size': 11, 'bold': False, 'spacing': 0.5, 'caps': False, 'color': 'ink'},
              'pageno': {'font': 'label', 'size': 9, 'bold': False, 'spacing': 1.5, 'color': 'muted'}}, '#7D8AA6')
SD = HERE / 'design' / 'styles'
SD.mkdir(parents=True, exist_ok=True)
for s in (COSMOS, ATLAS, INFERNO, DEEP):
    (SD / f"{s['name']}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding='utf-8')
ST = {k: f'design/styles/{k}.json' for k in ('cosmos', 'atlas', 'inferno', 'deeptime')}

# ------------------------------------------------------------------ the signature: an altitude/depth gauge on the right edge
GX, GTOP, GSURF, GBOT = 12.45, 1.0, 4.15, 6.45


def g_y(alt=None, depth=None):
    if depth is not None:
        return GSURF + depth / 6371 * (GBOT - GSURF)
    return GSURF - math.log10(max(alt, 1)) / 9.8 * (GSURF - GTOP)


def gauge(reading, alt=None, depth=None, rail='#2A3342', ink='#8A97A8'):
    y = g_y(alt, depth)
    sh = [
        {'type': 'line', 'name': '!!g-rail', 'x1': GX, 'y1': GTOP, 'x2': GX, 'y2': GBOT, 'color': rail, 'width': 1.0},
        {'type': 'line', 'name': '!!g-surf', 'x1': GX - 0.12, 'y1': GSURF, 'x2': GX + 0.12, 'y2': GSURF, 'color': ink, 'width': 1.0},
        {'type': 'text', 'name': '!!g-top', 'text': 'CAO', 'role': 'pageno', 'color': ink, 'x': GX - 0.35, 'y': GTOP - 0.3, 'w': 0.7, 'h': 0.22, 'align': 'c'},
        {'type': 'text', 'name': '!!g-bot', 'text': 'SÂU', 'role': 'pageno', 'color': ink, 'x': GX - 0.35, 'y': GBOT + 0.08, 'w': 0.7, 'h': 0.22, 'align': 'c'},
        {'type': 'ellipse', 'name': '!!g-dot', 'x': GX - 0.075, 'y': y - 0.075, 'w': 0.15, 'h': 0.15, 'fill': ORANGE},
        {'type': 'text', 'name': '!!g-val', 'text': reading, 'role': 'pageno', 'color': ink, 'x': GX - 1.55, 'y': y - 0.12, 'w': 1.4, 'h': 0.24, 'align': 'r'},
    ]
    return sh


GC = {'cosmos': ('#2A3342', '#8A97A8'), 'photo': ('#6E7A8C', '#D7DEE8'), 'atlas': ('#B9AD94', '#6B6457'),
      'inferno': ('#4A2218', '#C29A86'), 'deeptime': ('#26324D', '#7D8AA6')}


def G(reading, kind, alt=None, depth=None):
    r, i = GC[kind]
    return gauge(reading, alt, depth, r, i)


def appear_from(dx, dy, ms, delay=0, ease=(0, 85)):
    """Enter by travelling a motion path INTO the placed position (the render shows the end state)."""
    return [{'fx': 'appear', 'delay': delay}, {'fx': 'path', 'path': [[dx, dy], [0, 0]], 'from_offset': True, 'ms': ms, 'delay': delay, 'ease': list(ease)}]


def stars(seed, n, x0, y0, x1, y1, name, color='#C9D3E3', avoid=()):
    import random
    r = random.Random(seed)
    dots = []
    while len(dots) < n:
        s = r.choice([0.018, 0.022, 0.028, 0.035, 0.045])
        px, py = r.uniform(x0, x1), r.uniform(y0, y1)
        if any(a <= px <= c and b <= py <= d for a, b, c, d in avoid):
            continue
        dots.append({'type': 'ellipse', 'x': round(px, 3), 'y': round(py, 3), 'w': s, 'h': s, 'fill': color, 'alpha': round(r.uniform(0.35, 0.9), 2)})
    return {'type': 'group', 'name': name, 'shapes': dots}


def circle_pts(cx, cy, r, a0, a1, n=48):
    """Points of an arc (degrees, 0 = right, counter-clockwise on screen = upwards)."""
    return [[round(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), 4), round(cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), 4)] for i in range(n + 1)]


slides = []
# ================================================================== 0 · MỞ (cosmos)
DOT1 = (0.5945 * W, 0.5 * H)
slides.append({
    'id': 'dot', 'style': ST['cosmos'], 'scene': 'MỞ', 'transition': {'type': 'fade', 'ms': 1600}, 'chrome': False,
    'notes': 'Nhìn kỹ vệt sáng bên phải. Có một chấm nhỏ hơn một điểm ảnh. Ngày 14 tháng 2 năm 1990, Voyager 1 chụp nó từ khoảng 6 tỉ km. [ngừng] Chấm đó là Trái Đất. Đây là nhà.',
    'source': 'F1',
    'shapes': [
        {'type': 'image', 'name': '!!pbd', 'path': 'assets/pbd_wide.jpg', 'x': 0, 'y': 0, 'w': W, 'h': H, 'fit': 'cover',
         'anim': [{'fx': 'fade', 'ms': 2200}, {'fx': 'grow', 'scale': 1.05, 'ms': 12000, 'delay': 0}]},
        {'type': 'ellipse', 'name': '!!ring', 'x': DOT1[0] - 0.24, 'y': DOT1[1] - 0.24, 'w': 0.48, 'h': 0.48, 'line_color': ORANGE, 'line_width': 1.25,
         'anim': [{'fx': 'zoom', 'ms': 700, 'delay': 2400}, {'fx': 'pulse', 'scale': 1.35, 'ms': 1400, 'loop': True}]},
        {'type': 'line', 'name': '!!lead', 'x1': DOT1[0] + 0.26, 'y1': DOT1[1], 'x2': DOT1[0] + 1.2, 'y2': DOT1[1], 'color': ORANGE, 'width': 0.75,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 600, 'delay': 3100}},
        {'type': 'text', 'name': '!!t1', 'text': 'Đây là nhà.', 'role': 'title', 'size': 34, 'x': DOT1[0] + 1.35, 'y': DOT1[1] - 0.33, 'w': 3.6, 'h': 0.65,
         'anim': {'fx': 'type', 'ms': 600, 'step': 9, 'delay': 3600}},
        {'type': 'text', 'name': '!!k1', 'text': 'Voyager 1 · 14.02.1990 · cách khoảng 6 tỉ km', 'role': 'kicker', 'color': '#FFFFFF', 'x': 0.75, 'y': 0.6, 'w': 6.5, 'h': 0.3,
         'anim': {'fx': 'fade', 'ms': 900, 'delay': 4600}},
    ] + G('6 tỉ km', 'photo', alt=6e9)})

slides.append({
    'id': 'title', 'style': ST['cosmos'], 'scene': 'MỞ', 'transition': {'type': 'morph', 'ms': 2400}, 'chrome': False,
    'notes': 'Trong sáu phút, ta rơi một mạch từ chấm sáng ấy xuống tận tâm hành tinh, sâu 6.371 km, rồi lùi lại 4,54 tỉ năm.',
    'source': 'F1, F15',
    'shapes': [
        {'type': 'image', 'name': '!!pbd', 'path': 'assets/pbd_wide.jpg', 'x': 9.7 - 0.5945 * W * 2.6, 'y': 2.3 - 0.5 * H * 2.6, 'w': W * 2.6, 'h': H * 2.6, 'fit': 'cover'},
        {'type': 'ellipse', 'name': '!!ring', 'x': 9.7 - 0.55, 'y': 2.3 - 0.55, 'w': 1.1, 'h': 1.1, 'line_color': ORANGE, 'line_width': 1.5,
         'anim': {'fx': 'pulse', 'scale': 1.2, 'ms': 1600, 'loop': True, 'delay': 300}},
        {'type': 'text', 'name': '!!title', 'text': 'Trái Đất', 'role': 'display', 'size': 170, 'x': 0.6, 'y': 3.25, 'w': 9.6, 'h': 2.55,
         'anim': {'fx': 'wipe', 'dir': 'b', 'ms': 1100, 'delay': 600}},
        {'type': 'text', 'name': '!!sub', 'text': 'Rơi về nhà: từ 6 tỉ km xuống tâm hành tinh', 'role': 'subtitle', 'color': 'ink', 'x': 0.85, 'y': 5.85, 'w': 8.0, 'h': 0.45,
         'anim': {'fx': 'rise', 'ms': 800, 'delay': 1500}},
        {'type': 'text', 'name': '!!k1', 'text': '22 cảnh · 6 phút · một chuyến rơi', 'role': 'kicker', 'x': 0.85, 'y': 2.85, 'w': 6.5, 'h': 0.3,
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 1900}},
    ] + G('6 tỉ km', 'photo', alt=6e9)})

ROUTE = [('01', 'Không gian', '150 triệu → 400 km', 'season'), ('02', 'Khí quyển', '100 → 0 km', 'layers'),
         ('03', 'Bề mặt', '0 km', 'water'), ('04', 'Lòng đất', '0 → 6.371 km', 'xsec'), ('05', 'Thời gian sâu', '4,54 tỉ năm', 'clock')]
route = [
    {'type': 'image', 'name': '!!pbd', 'path': 'assets/pbd_wide.jpg', 'x': 0, 'y': 0, 'w': 3.9, 'h': H, 'fit': 'cover', 'focus': [0.5945, 0.5]},
    {'type': 'ellipse', 'name': '!!ring', 'x': 1.95 - 0.2, 'y': 3.75 - 0.2, 'w': 0.4, 'h': 0.4, 'line_color': ORANGE, 'line_width': 1.0},
    {'type': 'text', 'name': '!!k1', 'text': 'Lộ trình · bấm để nhảy', 'role': 'kicker', 'x': 4.75, 'y': 0.75, 'w': 5, 'h': 0.3},
    {'type': 'line', 'name': '!!route', 'x1': 6.55, 'y1': 1.35, 'x2': 6.55, 'y2': 6.55, 'color': '#2A3342', 'width': 1.25,
     'anim': {'fx': 'wipe', 'dir': 't', 'ms': 1400, 'delay': 200}},
]
for i, (n, t, km, target) in enumerate(ROUTE):
    y = 1.35 + i * 1.3
    d = 500 + i * 220
    route += [
        {'type': 'ellipse', 'name': f'!!stop{i}', 'x': 6.55 - 0.09, 'y': y - 0.09, 'w': 0.18, 'h': 0.18, 'fill': ORANGE if i == 0 else '#05070B', 'line_color': ORANGE, 'line_width': 1.25,
         'anim': {'fx': 'zoom', 'ms': 450, 'delay': d}},
        {'type': 'text', 'name': f'!!km{i}', 'text': km, 'role': 'label', 'x': 3.95, 'y': y - 0.12, 'w': 2.4, 'h': 0.26, 'align': 'r',
         'anim': {'fx': 'fade', 'ms': 500, 'delay': d + 120}},
        {'type': 'text', 'name': f'!!rn{i}', 'text': n, 'role': 'label', 'color': 'accent', 'x': 6.95, 'y': y - 0.12, 'w': 0.5, 'h': 0.26,
         'anim': {'fx': 'fade', 'ms': 400, 'delay': d + 120}},
        {'type': 'text', 'name': f'!!rt{i}', 'text': t, 'role': 'title', 'size': 40, 'x': 7.5, 'y': y - 0.36, 'w': 4.6, 'h': 0.7, 'link': target,
         'anim': {'fx': 'fly', 'dir': 'r', 'ms': 650, 'delay': d + 60}},
    ]
slides.append({
    'id': 'route', 'style': ST['cosmos'], 'scene': 'MỞ', 'transition': {'type': 'morph', 'ms': 1600},
    'notes': 'Năm chặng: không gian, khí quyển, bề mặt, lòng đất, thời gian sâu. Cột bên phải là đồng hồ độ cao: chấm cam là chúng ta.',
    'shapes': route + G('6 tỉ km', 'cosmos', alt=6e9)})

# ================================================================== 1 · KHÔNG GIAN (cosmos)
slides.append({
    'id': 'season', 'style': ST['cosmos'], 'scene': 'KHÔNG GIAN', 'transition': {'type': 'zoom', 'ms': 1200},
    'notes': 'Lùi về 150 triệu km. Trục Trái Đất nghiêng 23,4 độ và luôn chỉ một hướng. Tháng 6, bắc bán cầu ngả về Mặt Trời: mùa hè. Tháng 12 thì ngược lại. [bấm] Bất ngờ: đầu tháng 1, giữa mùa đông của ta, Trái Đất lại gần Mặt Trời nhất.',
    'source': 'F2',
    'shapes': [
        {'type': 'video', 'name': 'seasonvid', 'path': 'manim/Seasons.mp4', 'poster': 'assets/seasons.poster.png', 'x': 0, 'y': 0, 'w': W, 'h': H, 'loop': False, 'mute': True},
        {'type': 'text', 'name': '!!k1', 'text': '150 triệu km · quỹ đạo', 'role': 'kicker', 'x': 0.75, 'y': 0.6, 'w': 5, 'h': 0.3},
        {'type': 'text', 'name': '!!h1', 'text': 'Mùa đến từ độ nghiêng', 'role': 'title', 'size': 40, 'x': 0.75, 'y': 0.95, 'w': 6.4, 'h': 0.75,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 900, 'delay': 300}},
        {'type': 'text', 'name': '!!myth', 'text': [{'text': 'Đầu tháng 1', 'role': 'title', 'size': 30, 'color': 'accent'},
                                                   {'text': 'Trái Đất gần Mặt Trời nhất: 147,1 triệu km. Đầu tháng 7, xa nhất: 152,1 triệu km.', 'role': 'body', 'size': 15}],
         'x': 8.6, 'y': 4.95, 'w': 3.3, 'h': 1.85, 'anim': {'fx': 'fly', 'dir': 'r', 'ms': 700, 'click': 1}},
        {'type': 'text', 'name': '!!note', 'text': 'Sơ đồ không theo tỉ lệ · dựng bằng Manim', 'role': 'pageno', 'x': 0.75, 'y': 6.78, 'w': 4.5, 'h': 0.24},
    ] + G('150 triệu km', 'cosmos', alt=1.5e8), 'chrome': False})

slides.append({
    'id': 'epic', 'style': ST['cosmos'], 'scene': 'KHÔNG GIAN', 'transition': {'type': 'uncover', 'dir': 'l', 'ms': 1000},
    'notes': '1,5 triệu km. Tháng 7 năm 2015, DSCOVR chụp Mặt Trăng đi ngang qua Trái Đất. Đó là mặt sau của Mặt Trăng, mặt ta không bao giờ thấy từ dưới đất.',
    'source': 'F18',
    'shapes': [
        {'type': 'image', 'name': '!!epic', 'path': 'assets/epic_disc.png', 'x': 3.1, 'y': 0.95, 'w': 9.332, 'h': 5.6,
         'anim': [{'fx': 'fade', 'ms': 1400}, {'fx': 'grow', 'scale': 1.04, 'ms': 9000, 'delay': 200}]},
        {'type': 'text', 'name': '!!k1', 'text': 'DSCOVR · 16.07.2015', 'role': 'kicker', 'x': 0.75, 'y': 0.95, 'w': 3.0, 'h': 0.3},
        {'type': 'text', 'name': '!!num', 'text': '1,5', 'role': 'numeral', 'size': 130, 'x': 0.6, 'y': 1.4, 'w': 3.0, 'h': 1.9,
         'anim': {'fx': 'rise', 'ms': 900, 'delay': 500}},
        {'type': 'text', 'name': '!!unit', 'text': 'triệu km', 'role': 'title', 'size': 34, 'x': 0.75, 'y': 3.3, 'w': 3.0, 'h': 0.6,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 700, 'delay': 900}},
        {'type': 'text', 'name': '!!b1', 'text': 'Mặt Trăng đi ngang qua Trái Đất: đây là mặt sau của nó, mặt ta không bao giờ thấy từ dưới đất.', 'role': 'body', 'size': 16,
         'x': 0.75, 'y': 4.3, 'w': 2.9, 'h': 1.9, 'anim': {'fx': 'word', 'ms': 400, 'step': 40, 'delay': 1500}},
    ] + G('1,5 triệu km', 'cosmos', alt=1.5e6)})

slides.append({
    'id': 'earthrise', 'style': ST['cosmos'], 'scene': 'KHÔNG GIAN', 'transition': {'type': 'push', 'dir': 'u', 'ms': 1100},
    'notes': 'Rơi tới quỹ đạo Mặt Trăng, cách 384.400 km. Đêm Giáng sinh 1968, William Anders của Apollo 8, chuyến bay có người đầu tiên quanh Mặt Trăng, chụp Trái Đất mọc trên chân trời Mặt Trăng.',
    'source': 'F3, F4',
    'shapes': [
        stars(11, 70, 0.2, 0.2, 11.2, 4.6, '!!stars', avoid=[(0.6, 0.6, 6.4, 2.2)]) | {'anim': {'fx': 'path', 'path': [[0, 0], [-0.18, 0.04]], 'ms': 9000, 'ease': [20, 20]}},
        {'type': 'image', 'name': '!!er-earth', 'path': 'assets/er_earth.png', 'x': 8.9, 'y': 1.55, 'w': 2.0, 'h': 2.0 * 408 / 480,
         'anim': appear_from(0, 2.1, 6000, 200, (10, 80))},
        {'type': 'image', 'name': '!!er-moon', 'path': 'assets/er_moon.png', 'x': -1.0, 'y': 3.95, 'w': 15.6, 'h': 15.6 / 3.125,
         'anim': {'fx': 'path', 'path': [[0, 0], [-0.55, 0.22]], 'ms': 6000, 'delay': 200, 'ease': [10, 80]}},
        {'type': 'text', 'name': '!!num', 'text': '384.400 km', 'role': 'numeral', 'size': 96, 'color': '#05070B', 'x': 0.7, 'y': 5.45, 'w': 7.6, 'h': 1.5,
         'anim': {'fx': 'rise', 'ms': 900, 'delay': 900}},
        {'type': 'text', 'name': '!!k1', 'text': 'Apollo 8 · 24.12.1968 · William Anders', 'role': 'kicker', 'x': 0.8, 'y': 0.75, 'w': 6, 'h': 0.3,
         'anim': {'fx': 'type', 'ms': 400, 'step': 4, 'delay': 1500}},
        {'type': 'text', 'name': '!!b1', 'text': 'Những người đầu tiên bay quanh Mặt Trăng thấy Trái Đất “mọc”.', 'role': 'subtitle', 'color': 'ink',
         'x': 0.8, 'y': 1.15, 'w': 5.4, 'h': 0.9, 'anim': {'fx': 'fade', 'ms': 900, 'delay': 2300}},
    ] + G('384.400 km', 'cosmos', alt=384400)})

BM = (6.25, -1.75, 10.9)   # x, y, size of the bleeding Blue Marble disc
slides.append({
    'id': 'marble', 'style': ST['cosmos'], 'scene': 'KHÔNG GIAN', 'transition': {'type': 'fade', 'ms': 900},
    'notes': 'Bốn năm sau, Apollo 17 chụp tấm này từ khoảng 29.400 km: viên bi xanh. Châu Phi, bán đảo Ả Rập, băng Nam Cực. Một trong những bức ảnh được in lại nhiều nhất.',
    'source': 'F5',
    'shapes': [
        stars(12, 46, 0.3, 0.3, 6.0, 7.0, '!!stars', avoid=[(0.5, 1.0, 6.0, 6.8)]),
        {'type': 'image', 'name': '!!bm', 'path': 'assets/bm_disc.png', 'x': BM[0], 'y': BM[1], 'w': BM[2], 'h': BM[2],
         'anim': [*appear_from(4.5, 0.6, 1800, 0, (0, 90)), {'fx': 'spin', 'deg': 6, 'ms': 14000, 'delay': 1800}]},
        {'type': 'text', 'name': '!!num', 'text': '29.400 km', 'role': 'numeral', 'size': 80, 'rot': 270, 'x': -1.6, 'y': 3.0, 'w': 5.6, 'h': 1.3,
         'anim': {'fx': 'rise', 'ms': 900, 'delay': 900}},
        {'type': 'text', 'name': '!!k1', 'text': 'Apollo 17 · 07.12.1972', 'role': 'kicker', 'x': 2.2, 'y': 3.15, 'w': 3.6, 'h': 0.3,
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 700}},
        {'type': 'text', 'name': '!!b1', 'text': '“Viên bi xanh”: một trong những bức ảnh được in lại nhiều nhất lịch sử.', 'role': 'subtitle', 'color': 'ink',
         'x': 2.2, 'y': 3.55, 'w': 3.7, 'h': 1.45, 'anim': {'fx': 'word', 'ms': 500, 'step': 30, 'delay': 1500}},
    ] + G('29.400 km', 'cosmos', alt=29400)})

GL = 5.0   # globe diameter
GCX, GCY = 6.35, 3.85
slides.append({
    'id': 'spin', 'style': ST['cosmos'], 'scene': 'KHÔNG GIAN', 'transition': {'type': 'morph', 'ms': 1800},
    'notes': 'Rồi nó quay. Một vòng so với các vì sao mất 23 giờ 56 phút. Ở xích đạo, bạn đang lao đi khoảng 1.670 km mỗi giờ. Bên đêm, đốm vàng là đèn thành phố.',
    'source': 'F6',
    'shapes': [
        stars(12, 46, 0.3, 0.3, 6.0, 7.0, '!!stars', avoid=[(0.5, 1.0, 6.0, 6.8)]) | {'anim': {'fx': 'path', 'path': [[0, 0], [0.25, 0]], 'ms': 10000, 'ease': [30, 30]}},
        {'type': 'image', 'name': '!!bm', 'path': 'assets/bm_disc.png', 'x': GCX - GL / 2, 'y': GCY - GL / 2, 'w': GL, 'h': GL,
         'anim': {'fx': 'fadeout', 'ms': 900, 'delay': 600}},
        {'type': 'video', 'name': 'globevid', 'path': 'assets/globe.mp4', 'poster': 'assets/globe.poster.png',
         'x': GCX - GL / 0.86 / 2, 'y': GCY - GL / 0.86 / 2, 'w': GL / 0.86, 'h': GL / 0.86, 'loop': True, 'mute': True},
        {'type': 'ellipse', 'name': '!!orbit', 'x': GCX - 3.55, 'y': GCY - 0.95, 'w': 7.1, 'h': 1.9, 'line_color': '#8FD8FF', 'line_width': 0.75, 'rot': -14,
         'anim': {'fx': 'wheel', 'ms': 1400, 'delay': 900}},
        {'type': 'ellipse', 'name': '!!iss', 'x': GCX + 3.55 - 0.07, 'y': GCY - 0.07, 'w': 0.14, 'h': 0.14, 'fill': '#FFFFFF',
         'anim': [{'fx': 'appear', 'delay': 2300}, {'fx': 'orbit', 'rx': 3.55, 'ry': 0.95, 'ms': 9000, 'loop': True, 'ease': [0, 0]}]},
        {'type': 'text', 'name': '!!n1', 'text': '23 giờ 56 phút', 'role': 'title', 'size': 40, 'x': 0.7, 'y': 0.75, 'w': 4.6, 'h': 0.7,
         'anim': {'fx': 'split', 'dir': 'v', 'ms': 800, 'delay': 1200}},
        {'type': 'text', 'name': '!!n1l', 'text': 'một vòng tự quay, so với các vì sao', 'role': 'label', 'x': 0.75, 'y': 1.5, 'w': 4.6, 'h': 0.26,
         'anim': {'fx': 'fade', 'ms': 600, 'delay': 1700}},
        {'type': 'text', 'name': '!!n2', 'text': '≈ 1.670 km/h', 'role': 'title', 'size': 40, 'x': 7.2, 'y': 5.95, 'w': 4.6, 'h': 0.7, 'align': 'r',
         'anim': {'fx': 'split', 'dir': 'v', 'ms': 800, 'delay': 2600}},
        {'type': 'text', 'name': '!!n2l', 'text': 'tốc độ một điểm trên xích đạo', 'role': 'label', 'x': 7.2, 'y': 5.65, 'w': 4.6, 'h': 0.26, 'align': 'r',
         'anim': {'fx': 'fade', 'ms': 600, 'delay': 3000}},
    ] + G('29.400 km', 'cosmos', alt=29400)})

# ================================================================== 2 · KHÍ QUYỂN
slides.append({
    'id': 'limb', 'style': ST['cosmos'], 'scene': 'KHÍ QUYỂN', 'transition': {'type': 'flythrough', 'ms': 1200}, 'chrome': False,
    'notes': 'Chặng hai. Xuống độ cao trạm vũ trụ ISS, khoảng 400 km, nhìn ra rìa Trái Đất lúc hoàng hôn. Dải màu mỏng kia là cả bầu trời. Gần như toàn bộ không khí nằm dưới 100 km.',
    'source': 'F7, F8',
    'shapes': [
        {'type': 'image', 'name': '!!limb', 'path': 'assets/limb.jpg', 'x': -0.3, 'y': -0.2, 'w': W + 0.6, 'h': H + 0.4, 'fit': 'cover',
         'anim': [{'fx': 'fade', 'ms': 1200}, {'fx': 'path', 'path': [[0, 0], [0.3, 0.16]], 'ms': 10000, 'ease': [20, 20]}]},
        {'type': 'text', 'name': '!!t1', 'text': 'Cả bầu trời nằm trong dải sáng mỏng này.', 'role': 'title', 'size': 30, 'rot': 25,
         'x': 0.5, 'y': 4.45, 'w': 8.6, 'h': 0.6, 'anim': {'fx': 'word', 'ms': 500, 'step': 28, 'delay': 1000}},
        {'type': 'text', 'name': '!!k1', 'text': 'Nhìn từ ISS · khoảng 400 km', 'role': 'kicker', 'color': '#FFFFFF', 'x': 5.9, 'y': 0.85, 'w': 6.0, 'h': 0.3, 'align': 'r',
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 2600}},
        {'type': 'text', 'name': '!!k2', 'text': '99,99997% khối lượng khí quyển nằm dưới 100 km', 'role': 'label', 'color': '#D7DEE8', 'x': 4.9, 'y': 0.55, 'w': 7.0, 'h': 0.26, 'align': 'r',
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 3000}},
    ] + G('400 km', 'photo', alt=400)})

# atmosphere plate (log-ish scale, labelled as such)
def ay(h):
    return round(6.65 - math.log10(h + 1) / 4.0 * 4.75, 3)


LAY = [('Tầng đối lưu', '0–12 km', 0, 12, '#A9CBE0', 'mây, mưa, máy bay'), ('Tầng bình lưu', '12–50 km', 12, 50, '#86AFCD', 'tầng ôzôn 15–35 km'),
       ('Tầng trung lưu', '50–80 km', 50, 80, '#6286AE', 'sao băng bốc cháy'), ('Tầng nhiệt', '80–700 km', 80, 700, '#3F5A82', 'cực quang, trạm ISS'),
       ('Tầng ngoài', '700–10.000 km', 700, 10000, '#22314F', 'khí loãng dần vào không gian')]
CX0, CX1 = 0.75, 6.4
atm = []
for i, (n, rng, lo, hi, col, note) in enumerate(LAY):
    y0, y1 = ay(hi), ay(lo)
    nxt = LAY[i + 1][4] if i + 1 < len(LAY) else '#141E33'
    atm.append({'type': 'rect', 'name': f'!!lay{i}', 'x': CX0, 'y': y0, 'w': CX1 - CX0, 'h': round(y1 - y0, 3), 'fill': col,
                'gradient': [[nxt, 1.0, 0], [col, 1.0, 100]], 'angle': 90,
                'anim': {'fx': 'wipe', 'dir': 'b', 'ms': 500, 'delay': 300 + i * 260}})
    ym = (y0 + y1) / 2
    ty = min(max(ym - 0.28, 0.75 + i * 0.0), 6.2)
    atm += [
        {'type': 'line', 'name': f'!!lead{i}', 'x1': CX1 + 0.08, 'y1': round(ym, 3), 'x2': 7.25, 'y2': round(ym, 3), 'color': '#1E2A33', 'width': 0.6,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 350, 'delay': 1900 + i * 200}},
        {'type': 'text', 'name': f'!!ln{i}', 'text': [{'text': n, 'role': 'cardtitle', 'size': 19}, {'text': f'{rng} · {note}', 'role': 'label', 'size': 10}],
         'x': 7.4, 'y': round(ym - 0.3 - (0.1 if i == 2 else 0) + (0.06 if i == 1 else 0), 3), 'w': 4.5, 'h': 0.62, 'anim': {'fx': 'fly', 'dir': 'r', 'ms': 500, 'delay': 2000 + i * 200}},
    ]
# objects inside the layers, all editable shapes
cl = ay(5)
atm += [
    {'type': 'group', 'name': '!!cloud', 'shapes': [
        {'type': 'ellipse', 'x': 1.3, 'y': cl, 'w': 0.9, 'h': 0.34, 'fill': '#FFFFFF', 'alpha': 0.95},
        {'type': 'ellipse', 'x': 1.62, 'y': cl - 0.16, 'w': 0.6, 'h': 0.4, 'fill': '#FFFFFF', 'alpha': 0.95},
        {'type': 'ellipse', 'x': 1.95, 'y': cl + 0.02, 'w': 0.7, 'h': 0.3, 'fill': '#FFFFFF', 'alpha': 0.95}],
     'anim': [{'fx': 'fade', 'ms': 600, 'delay': 1700}, {'fx': 'path', 'path': [[0, 0], [0.5, 0], [0, 0]], 'ms': 9000, 'loop': True, 'ease': [30, 30]}]},
    {'type': 'poly', 'name': '!!plane', 'points': [[3.0, ay(10.5)], [3.42, ay(10.5) - 0.02], [3.48, ay(10.5) - 0.05], [3.42, ay(10.5) + 0.03], [3.0, ay(10.5) + 0.03],
                                                   [3.18, ay(10.5) + 0.02], [3.05, ay(10.5) + 0.16], [3.13, ay(10.5) + 0.16], [3.3, ay(10.5) + 0.02]],
     'fill': '#1E2A33', 'anim': [{'fx': 'appear', 'delay': 2000}, {'fx': 'path', 'path': [[0, 0], [2.4, 0]], 'ms': 7000, 'loop': True, 'ease': [0, 0]}]},
    {'type': 'rect', 'name': '!!ozone', 'x': CX0, 'y': ay(35), 'w': CX1 - CX0, 'h': round(ay(15) - ay(35), 3), 'fill': '#FFD27A', 'alpha': 0.2,
     'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 900, 'delay': 2400}},
    {'type': 'line', 'name': '!!meteor', 'x1': 4.2, 'y1': ay(78), 'x2': 4.75, 'y2': ay(78) + 0.22, 'color': '#FFE07A', 'width': 2.0, 'cap': 'round',
     'anim': [{'fx': 'appear', 'delay': 2600}, {'fx': 'path', 'path': [[0, 0], [0.7, 0.1]], 'ms': 1300, 'loop': True, 'ease': [60, 0]}]},
    {'type': 'group', 'name': '!!aurora', 'shapes': [
        {'type': 'rect', 'x': round(1.15 + k * 0.27, 3), 'y': ay(300 - 25 * (k % 3)), 'w': 0.16 + 0.05 * (k % 2), 'h': round(ay(100) - ay(300 - 25 * (k % 3)), 3),
         'gradient': [['#7CF2B0', 0.0, 0], ['#7CF2B0', 0.75, 85], ['#C9FFE0', 0.9, 100]], 'angle': 90} for k in range(8)],
     'anim': [{'fx': 'fade', 'ms': 900, 'delay': 2800}, {'fx': 'path', 'path': [[0, 0], [0.12, 0], [0, 0]], 'ms': 5200, 'loop': True, 'ease': [40, 40]}]},
    {'type': 'poly', 'name': '!!ground', 'points': [[CX0, 6.65], [1.4, 6.5], [1.9, 6.58], [2.6, 6.28], [3.1, 6.5], [3.6, 6.42], [4.3, 6.6], [4.9, 6.36], [5.5, 6.55], [CX1, 6.48], [CX1, 6.86], [CX0, 6.86]],
     'fill': '#3B4636', 'anim': {'fx': 'wipe', 'dir': 'b', 'ms': 400, 'delay': 100}},
] + [x for km in (10, 100, 1000) for x in (
    {'type': 'line', 'name': f'!!tick{km}', 'x1': CX1 - 0.14, 'y1': ay(km), 'x2': CX1, 'y2': ay(km), 'color': '#FFFFFF', 'width': 0.75},
    {'type': 'text', 'name': f'!!tk{km}', 'text': f'{km:,} km'.replace(',', '.'), 'role': 'label', 'size': 8, 'color': '#FFFFFF', 'x': CX1 - 1.2, 'y': round(ay(km) - 0.1, 3), 'w': 1.0, 'h': 0.2, 'align': 'r'})] + [

    {'type': 'group', 'name': '!!issp', 'shapes': [
        {'type': 'rect', 'x': 4.6, 'y': ay(400) - 0.04, 'w': 0.3, 'h': 0.08, 'fill': '#E9EEF5'},
        {'type': 'rect', 'x': 4.48, 'y': ay(400) - 0.11, 'w': 0.1, 'h': 0.22, 'fill': '#FFB23F'},
        {'type': 'rect', 'x': 4.92, 'y': ay(400) - 0.11, 'w': 0.1, 'h': 0.22, 'fill': '#FFB23F'}],
     'anim': [{'fx': 'appear', 'delay': 3000}, {'fx': 'path', 'path': [[0, 0], [-3.0, 0]], 'ms': 8000, 'loop': True, 'ease': [0, 0]}]},
    {'type': 'text', 'name': '!!k1', 'text': 'Hình 2 · Khí quyển', 'role': 'kicker', 'x': 7.4, 'y': 0.6, 'w': 4.6, 'h': 0.3},
    {'type': 'text', 'name': '!!h1', 'text': 'Năm tầng trời', 'role': 'title', 'size': 48, 'x': 7.4, 'y': 0.9, 'w': 4.6, 'h': 0.85,
     'anim': {'fx': 'fade', 'ms': 800, 'delay': 200}},
    {'type': 'text', 'name': '!!scale', 'text': 'thang độ cao logarit · ranh giới thay đổi theo vĩ độ và mùa', 'role': 'label', 'size': 9, 'x': 7.4, 'y': 6.5, 'w': 4.6, 'h': 0.36},
]
slides.append({
    'id': 'layers', 'style': ST['atlas'], 'scene': 'KHÍ QUYỂN', 'transition': {'type': 'wipe', 'dir': 'd', 'ms': 1000},
    'notes': 'Lớp mỏng ấy có năm tầng. Tầng đối lưu, khoảng 12 km: mây, mưa, máy bay. Tầng bình lưu giữ lớp ôzôn. Sao băng cháy ở tầng trung lưu. Cực quang và ISS ở tầng nhiệt. Rồi khí loãng dần vào không gian.',
    'source': 'F8',
    'shapes': atm + G('100 km', 'atlas', alt=100)})

# air composition strip -> zoom into the last 1%
SX0, SX1, SY, SH = 0.75, 11.95, 3.55, 1.0
SWD = SX1 - SX0
def strip(zoom):
    sh = []
    if not zoom:
        n2, o2, rest = SWD * 0.7808, SWD * 0.2095, SWD * 0.0097
        sh += [
            {'type': 'rect', 'name': '!!sN', 'x': SX0, 'y': SY, 'w': n2, 'h': SH, 'fill': '#1E2A33', 'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 1100, 'delay': 200}},
            {'type': 'rect', 'name': '!!sO', 'x': SX0 + n2, 'y': SY, 'w': o2, 'h': SH, 'fill': '#2E6FA8', 'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 500, 'delay': 1300}},
            {'type': 'rect', 'name': '!!sR', 'x': SX0 + n2 + o2, 'y': SY, 'w': rest, 'h': SH, 'fill': ORANGE, 'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 200, 'delay': 1800}},
            {'type': 'text', 'name': '!!vN', 'text': '78%', 'role': 'numeral', 'size': 150, 'x': SX0 - 0.05, 'y': 0.95, 'w': 5.5, 'h': 2.3, 'anim': appear_from(0, 0.5, 900, 300)},
            {'type': 'text', 'name': '!!lN', 'text': 'Nitơ', 'role': 'label', 'size': 11, 'color': '#FFFFFF', 'x': SX0 + 0.2, 'y': SY + 0.62, 'w': 3, 'h': 0.3},
            {'type': 'text', 'name': '!!vO', 'text': '21%', 'role': 'numeral', 'size': 72, 'color': 'accent2', 'x': SX0 + n2, 'y': 2.15, 'w': 2.6, 'h': 1.15, 'anim': appear_from(0, 0.5, 900, 1300)},
            {'type': 'text', 'name': '!!lO', 'text': 'Ôxy', 'role': 'label', 'size': 11, 'color': '#FFFFFF', 'x': SX0 + n2 + 0.15, 'y': SY + 0.62, 'w': 2, 'h': 0.3},
            {'type': 'text', 'name': '!!vR', 'text': '1%\ncòn lại', 'role': 'label', 'size': 11, 'color': 'accent', 'x': SX1 - 0.6, 'y': SY + 1.12, 'w': 1.0, 'h': 0.5, 'align': 'r',
             'anim': {'fx': 'fade', 'ms': 500, 'delay': 2000}},
            {'type': 'ellipse', 'name': '!!loupe', 'x': SX1 - 0.32, 'y': SY + 0.18, 'w': 0.64, 'h': 0.64, 'line_color': ORANGE, 'line_width': 1.5,
             'anim': [{'fx': 'zoom', 'ms': 500, 'delay': 2200}, {'fx': 'pulse', 'scale': 1.15, 'ms': 1200, 'loop': True}]},
            {'type': 'text', 'name': '!!h1', 'text': 'Hít một hơi: gần như toàn là nitơ.', 'role': 'subtitle', 'color': 'ink', 'x': SX0, 'y': 5.0, 'w': 7.5, 'h': 0.5,
             'anim': {'fx': 'fade', 'ms': 700, 'delay': 2400}},
        ]
    else:
        # the last ~1% fills the strip: argon 0.934, CO2 0.042 (422.8 ppm), others
        k = SWD / 0.0097
        ar, co2 = 0.00934 * k, 0.000423 * k
        sh += [
            {'type': 'rect', 'name': '!!sN', 'x': SX0 - 0.7808 * k - 0.2095 * k, 'y': SY, 'w': 0.7808 * k, 'h': SH, 'fill': '#1E2A33'},
            {'type': 'rect', 'name': '!!sO', 'x': SX0 - 0.2095 * k, 'y': SY, 'w': 0.2095 * k, 'h': SH, 'fill': '#2E6FA8'},
            {'type': 'rect', 'name': '!!sR', 'x': SX0, 'y': SY, 'w': SWD, 'h': SH, 'fill': '#C9BEA6'},
            {'type': 'rect', 'name': '!!sAr', 'x': SX0, 'y': SY, 'w': ar, 'h': SH, 'fill': '#5E5747', 'anim': {'fx': 'fade', 'ms': 500, 'delay': 300}},
            {'type': 'rect', 'name': '!!sC', 'x': SX0 + ar, 'y': SY, 'w': co2, 'h': SH, 'fill': ORANGE,
             'anim': [{'fx': 'zoom', 'ms': 500, 'delay': 700}, {'fx': 'pulse', 'scale': 1.25, 'ms': 1100, 'loop': True}]},
            {'type': 'text', 'name': '!!lAr', 'text': 'Argon 0,93%', 'role': 'label', 'size': 11, 'color': '#FFFFFF', 'x': SX0 + 0.2, 'y': SY + 0.62, 'w': 3, 'h': 0.3},
            {'type': 'text', 'name': '!!vN', 'text': 'CO₂', 'role': 'numeral', 'size': 150, 'color': 'accent', 'x': SX0 - 0.05, 'y': 0.95, 'w': 5.5, 'h': 2.3},
            {'type': 'text', 'name': '!!vR', 'text': '0,04%', 'role': 'label', 'size': 11, 'color': 'accent', 'x': SX0 + ar - 1.1, 'y': SY + 1.12, 'w': 1.6, 'h': 0.3, 'align': 'r'},
            {'type': 'ellipse', 'name': '!!loupe', 'x': SX0 + ar + co2 / 2 - 0.55, 'y': SY - 0.05, 'w': 1.1, 'h': 1.1, 'line_color': ORANGE, 'line_width': 1.5},
            {'type': 'text', 'name': '!!h1', 'text': 'Một vệt nhỏ, nhưng giữ nhiệt cho cả hành tinh.', 'role': 'subtitle', 'color': 'ink', 'x': SX0, 'y': 5.0, 'w': 7.5, 'h': 0.5},
            {'type': 'text', 'name': '!!ppm', 'text': [{'text': '422,8 ppm', 'role': 'title', 'size': 40, 'color': 'accent'},
                                                      {'text': 'trung bình toàn cầu năm 2024: mức cao nhất trong chuỗi đo của NOAA', 'role': 'body', 'size': 15}],
             'x': 7.9, 'y': 0.95, 'w': 4.0, 'h': 1.5, 'anim': {'fx': 'fly', 'dir': 'r', 'ms': 700, 'click': 1}},
        ]
    sh.append({'type': 'text', 'name': '!!k1', 'text': 'Hình 3 · Thành phần không khí khô' if not zoom else 'Hình 3b · Phóng to 1% còn lại', 'role': 'kicker', 'x': SX0, 'y': 0.6, 'w': 6, 'h': 0.3})
    return sh


slides.append({
    'id': 'air', 'style': ST['atlas'], 'scene': 'KHÍ QUYỂN', 'transition': {'type': 'push', 'dir': 'l', 'ms': 800},
    'notes': 'Hít một hơi. 78% là nitơ, 21% là ôxy. Mọi thứ khác gói trong 1% cuối. Ta phóng to vệt cam đó.',
    'source': 'F9', 'shapes': strip(False) + G('0 km', 'atlas', alt=1)})
slides.append({
    'id': 'air2', 'style': ST['atlas'], 'scene': 'KHÍ QUYỂN', 'transition': {'type': 'morph', 'ms': 2000},
    'notes': 'Phần lớn 1% ấy là argon. CO₂ chỉ khoảng 0,04%: một vệt nhỏ, nhưng giữ nhiệt cho cả hành tinh. [bấm] Năm 2024: 422,8 phần triệu, cao nhất từ khi NOAA đo.',
    'source': 'F9, F10', 'shapes': strip(True) + G('0 km', 'atlas', alt=1)})

# ================================================================== 3 · BỀ MẶT (atlas): the water cycle as a living diorama
SEA_Y = 5.15
wc = [
    {'type': 'ellipse', 'name': '!!sun', 'x': 0.85, 'y': 0.75, 'w': 1.2, 'h': 1.2, 'fill': '#FFB23F', 'anim': {'fx': 'zoom', 'ms': 600, 'delay': 200}},
    {'type': 'ellipse', 'name': '!!sunr', 'x': 0.55, 'y': 0.45, 'w': 1.8, 'h': 1.8, 'line_color': '#FFB23F', 'line_width': 1.0, 'line_alpha': 0.7,
     'anim': [{'fx': 'wheel', 'ms': 900, 'delay': 500}, {'fx': 'pulse', 'scale': 1.08, 'ms': 2400, 'loop': True}]},
    {'type': 'poly', 'name': '!!sea', 'points': [[0, SEA_Y]] + [[round(x * 0.35, 3), round(SEA_Y + 0.06 * math.sin(x * 1.3), 3)] for x in range(1, 22)] + [[7.6, SEA_Y + 0.1], [7.6, H], [0, H]],
     'gradient': [['#4C8DC4', 1.0, 0], ['#1D4C7A', 1.0, 100]], 'angle': 90, 'line_color': '#1E2A33', 'line_width': 0.75,
     'anim': {'fx': 'wipe', 'dir': 'b', 'ms': 700, 'delay': 100}},
    {'type': 'poly', 'name': '!!land', 'points': [[6.9, H], [7.3, SEA_Y + 0.05], [8.3, 4.3], [9.2, 3.25], [9.7, 3.55], [10.5, 2.75], [11.0, 3.55], [11.35, 4.35], [11.95, 4.7], [11.95, H]],
     'gradient': [['#A39780', 1.0, 0], ['#5E5747', 1.0, 100]], 'angle': 90, 'line_color': '#1E2A33', 'line_width': 0.9,
     'anim': {'fx': 'wipe', 'dir': 'b', 'ms': 800, 'delay': 250}},
    {'type': 'poly', 'name': '!!strata', 'points': [[7.05, 6.4], [8.4, 5.6], [9.6, 5.25], [10.8, 5.0], [11.95, 5.25], [11.95, 5.5], [10.8, 5.28], [9.6, 5.52], [8.4, 5.88], [7.0, 6.7]],
     'fill': '#4A4438', 'alpha': 0.55, 'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 700, 'delay': 700}},
    {'type': 'poly', 'name': '!!snow', 'points': [[10.12, 3.13], [10.5, 2.75], [10.9, 3.2], [10.68, 3.1], [10.5, 3.22], [10.3, 3.08]], 'fill': '#F6F0E2', 'line_color': '#1E2A33', 'line_width': 0.6,
     'anim': {'fx': 'fade', 'ms': 500, 'delay': 900}},
    {'type': 'poly', 'name': '!!river', 'points': [[10.4, 3.185], [10.026, 3.676], [9.427, 4.114], [8.724, 4.505], [8.022, 4.896], [7.42, 5.167], [7.48, 5.293], [8.078, 5.004], [8.776, 4.595], [9.473, 4.186], [10.074, 3.724], [10.44, 3.215]],
     'fill': '#8CC0E2', 'line_color': '#1E2A33', 'line_width': 0.5, 'anim': {'fx': 'wipe', 'dir': 'r', 'ms': 900, 'delay': 1700}},
    {'type': 'group', 'name': '!!cloud2', 'shapes': [
        {'type': 'ellipse', 'x': 7.3, 'y': 1.25, 'w': 1.8, 'h': 0.7, 'fill': '#FFFFFF', 'line_color': '#1E2A33', 'line_width': 0.6},
        {'type': 'ellipse', 'x': 8.0, 'y': 0.9, 'w': 1.5, 'h': 1.0, 'fill': '#FFFFFF', 'line_color': '#1E2A33', 'line_width': 0.6},
        {'type': 'ellipse', 'x': 9.0, 'y': 1.2, 'w': 1.6, 'h': 0.75, 'fill': '#FFFFFF', 'line_color': '#1E2A33', 'line_width': 0.6},
        ],
     'anim': [*appear_from(-2.2, 0.0, 1800, 900), {'fx': 'path', 'path': [[0, 0], [0.35, 0], [0, 0]], 'ms': 8000, 'loop': True, 'ease': [30, 30], 'delay': 2700}]},
    {'type': 'text', 'name': '!!t-ev', 'text': 'a · bốc hơi', 'role': 'label', 'size': 10, 'color': 'ink', 'x': 2.55, 'y': 3.0, 'w': 1.6, 'h': 0.25, 'anim': {'fx': 'fade', 'ms': 400, 'delay': 1300}},
    {'type': 'text', 'name': '!!t-ra', 'text': 'c · mưa', 'role': 'label', 'size': 10, 'color': 'ink', 'x': 10.75, 'y': 1.95, 'w': 1.15, 'h': 0.25, 'anim': {'fx': 'fade', 'ms': 400, 'delay': 1900}},
    {'type': 'text', 'name': '!!t-co', 'text': 'b · ngưng tụ thành mây', 'role': 'label', 'size': 10, 'color': 'ink', 'x': 7.3, 'y': 2.1, 'w': 1.55, 'h': 0.45, 'anim': {'fx': 'fade', 'ms': 400, 'delay': 1600}},
    {'type': 'text', 'name': '!!t-ru', 'text': 'd · dòng chảy về biển', 'role': 'label', 'size': 10, 'color': '#FFFFFF', 'x': 8.9, 'y': 6.0, 'w': 2.6, 'h': 0.25, 'anim': {'fx': 'fade', 'ms': 400, 'delay': 2200}},
]
# evaporation: droplets rise from the sea to the cloud on looping paths
for i, (x, dl) in enumerate(((3.0, 0), (3.7, 700), (4.4, 1400), (5.1, 300))):
    wc.append({'type': 'ellipse', 'name': f'!!ev{i}', 'x': x, 'y': SEA_Y - 0.2, 'w': 0.1, 'h': 0.13, 'fill': '#6FA3C4',
               'anim': [{'fx': 'appear', 'delay': 1200}, {'fx': 'path', 'path': [[0, 0], [1.2 + 0.2 * i, -3.0, 'C', 0.2, -1.0, 1.0, -2.3]], 'ms': 2600, 'loop': True, 'delay': dl, 'ease': [30, 0]}]})
# rain over the mountain
for i, x in enumerate((8.9, 9.3, 9.7, 10.1, 10.5)):
    wc.append({'type': 'line', 'name': f'!!rain{i}', 'x1': x, 'y1': 1.9, 'x2': x - 0.08, 'y2': 2.15, 'color': '#2E6FA8', 'width': 1.5,
               'anim': [{'fx': 'appear', 'delay': 1800}, {'fx': 'path', 'path': [[0, 0], [-0.15, 0.6]], 'ms': 800, 'loop': True, 'delay': 120 * i, 'ease': [60, 0]}]})
wc += [
    {'type': 'text', 'name': '!!big', 'text': '71%', 'role': 'numeral', 'size': 130, 'color': '#FFFFFF', 'x': 0.75, 'y': 5.25, 'w': 4.2, 'h': 1.75, 'anim': appear_from(0, 0.6, 900, 600)},
    {'type': 'text', 'name': '!!bigl', 'text': [{'text': 'bề mặt Trái Đất là đại dương', 'role': 'body', 'size': 15, 'color': '#FFFFFF'},
                                               {'text': 'và biển giữ khoảng 96,5% lượng nước của hành tinh', 'role': 'body', 'size': 15, 'color': '#DCE8F1'}],
     'x': 4.15, 'y': 5.95, 'w': 3.3, 'h': 1.0, 'anim': {'fx': 'fade', 'ms': 700, 'delay': 1200}},
    {'type': 'text', 'name': '!!k1', 'text': 'Hình 4 · 0 km · Đây là nhà', 'role': 'kicker', 'x': 2.6, 'y': 0.75, 'w': 4.0, 'h': 0.3},
    {'type': 'text', 'name': '!!h1', 'text': 'Hành tinh nước', 'role': 'title', 'size': 44, 'x': 2.6, 'y': 1.05, 'w': 4.3, 'h': 0.8, 'anim': {'fx': 'fade', 'ms': 700, 'delay': 300}},
]
slides.append({
    'id': 'water', 'style': ST['atlas'], 'scene': 'BỀ MẶT', 'transition': {'type': 'cover', 'dir': 'u', 'ms': 900},
    'notes': 'Chặng ba: độ cao bằng không. Ta đã về tới nhà. Đại dương phủ khoảng 71% bề mặt, giữ 96,5% lượng nước. Nắng làm nước bốc hơi, thành mây, mưa xuống núi, rồi chảy về biển.',
    'source': 'F11', 'chrome': False, 'shapes': wc + G('0 km', 'atlas', alt=1)})

slides.append({
    'id': 'plates', 'style': ST['atlas'], 'scene': 'BỀ MẶT', 'transition': {'type': 'fade', 'ms': 800},
    'notes': 'Nhưng mặt đất không đứng yên. Ở sống núi giữa Đại Tây Dương, đá nóng trào lên, đẩy hai mảng ra xa khoảng 2,5 cm mỗi năm, cỡ tốc độ móng tay mọc. Phía kia, mảng chìm xuống dưới lục địa và nuôi núi lửa.',
    'source': 'F12',
    'shapes': [
        {'type': 'video', 'name': 'platevid', 'path': 'manim/Plates.mp4', 'poster': 'assets/plates.poster.png', 'x': 0, 'y': 0, 'w': W, 'h': H, 'loop': True, 'mute': True},
        {'type': 'text', 'name': '!!k1', 'text': 'Hình 5 · Kiến tạo mảng · dựng bằng Manim', 'role': 'kicker', 'x': 0.75, 'y': 0.55, 'w': 6, 'h': 0.3},
        {'type': 'text', 'name': '!!h1', 'text': 'Mặt đất đang trôi', 'role': 'title', 'size': 48, 'x': 0.75, 'y': 0.85, 'w': 6.5, 'h': 0.85,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 900, 'delay': 300}},
        {'type': 'text', 'name': '!!b1', 'text': 'chậm cỡ móng tay mọc', 'role': 'subtitle', 'x': 0.78, 'y': 1.72, 'w': 5, 'h': 0.4,
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 900}},
    ] + G('−100 km', 'atlas', depth=100), 'chrome': False})

# ================================================================== 4 · LÒNG ĐẤT (inferno)
slides.append({
    'id': 'lava', 'style': ST['inferno'], 'scene': 'LÒNG ĐẤT', 'transition': {'type': 'split', 'dir': 'out', 'ms': 1000}, 'chrome': False,
    'notes': 'Chặng bốn. Ở Hawaii, đá nóng chảy từ dưới sâu phun lên. Đó là lời mời: ta chui xuống, qua lớp vỏ, tới lõi.',
    'source': 'F13',
    'shapes': [
        {'type': 'image', 'name': '!!lava', 'path': 'assets/lava_g.jpg', 'x': -0.4, 'y': 0, 'w': 10.3, 'h': H, 'fit': 'cover', 'focus': [0.3, 0.55],
         'anim': [{'fx': 'fade', 'ms': 900}, {'fx': 'grow', 'scale': 1.06, 'ms': 10000}]},
        {'type': 'poly', 'name': '!!cut', 'points': [[8.3, 0], [W, 0], [W, H], [6.3, H]], 'fill': '#120605',
         'anim': appear_from(3.0, 0, 1000, 300, (0, 90))},
        {'type': 'text', 'name': '!!h1', 'text': 'Xuống\nsâu\nhơn', 'role': 'display', 'size': 96, 'x': 7.3, 'y': 0.6, 'w': 3.6, 'h': 5.5, 'align': 'r',
         'anim': {'fx': 'split', 'dir': 'h', 'ms': 900, 'delay': 1100}},
        {'type': 'text', 'name': '!!b1', 'text': 'Dung nham Kīlauea, Hawaii. Ảnh: J.D. Griggs, USGS.', 'role': 'label', 'x': 5.9, 'y': 6.45, 'w': 5.0, 'h': 0.32, 'align': 'r',
         'anim': {'fx': 'fade', 'ms': 600, 'delay': 1800}},
    ] + G('−30 km', 'inferno', depth=30)})

# cross-section geometry
R0 = 3.9
XC, YC = 3.1, 4.0
RAD = [('crust', 6371, '#3A2A22'), ('mantle', 6336, '#C2502E'), ('outer', 3480, '#F2A03D'), ('inner', 1220, '#FFE07A')]


def xsec(scale=1.0, cx=XC, cy=YC, anim=False):
    sh = []
    for i, (n, r_km, col) in enumerate(RAD):
        r = R0 * r_km / 6371 * scale
        s = {'type': 'ellipse', 'name': f'!!x-{n}', 'x': round(cx - r, 3), 'y': round(cy - r, 3), 'w': round(2 * r, 3), 'h': round(2 * r, 3), 'fill': col}
        if n == 'mantle':
            s['gradient'] = [['#E07A3A', 1.0, 0], ['#8E2A14', 1.0, 100]]
            s['angle'] = 90
        if anim:
            s['anim'] = {'fx': 'wheel', 'ms': 900, 'delay': 500 + (3 - i) * 0}
        sh.append(s)
    # the uncut 3/4 of the surface (a freeform with the top-right quarter removed)
    rr = R0 * scale
    pts = [[cx, cy]] + circle_pts(cx, cy, rr, 90, 360, 72)
    sh.append({'type': 'poly', 'name': '!!x-shell', 'points': pts, 'fill': '#1B3550', 'gradient': [['#3C6E9C', 1.0, 0], ['#173252', 1.0, 55], ['#08111C', 1.0, 100]], 'angle': 45, 'line_color': '#0E1D2C', 'line_width': 0.75})
    return sh


xs = xsec(anim=False)
for s in xs:
    if s['name'] == '!!x-shell':
        s['anim'] = {'fx': 'fade', 'ms': 700, 'delay': 100}
for i, n in enumerate(('inner', 'outer', 'mantle', 'crust')):
    for s in xs:
        if s['name'] == f'!!x-{n}':
            s['anim'] = {'fx': 'wheel', 'ms': 800, 'delay': 600 + i * 350}
# draw order: crust (largest) first ... inner last, shell on top-left quarters
order = ['!!x-crust', '!!x-mantle', '!!x-outer', '!!x-inner', '!!x-shell']
xs = sorted(xs, key=lambda s: order.index(s['name']))
LBL = [('Vỏ', '6–50 km', 'đá cứng, mỏng như vỏ táo', 6371 - 20), ('Lớp phủ', 'đến 2.900 km', 'đá rắn nhưng chảy rất chậm', 4900),
       ('Lõi ngoài', 'đến 5.150 km', 'sắt và niken lỏng', 2350), ('Lõi trong', 'tâm · 6.371 km', 'sắt–niken rắn', 400)]
lab = []
for i, (n, d, desc, rkm) in enumerate(LBL):
    a = math.radians(45)
    r = R0 * rkm / 6371
    px, py = XC + r * math.cos(a), YC - r * math.sin(a)
    ly = 1.2 + i * 1.32
    lab += [
        {'type': 'line', 'name': f'!!xl{i}', 'x1': round(px, 3), 'y1': round(py, 3), 'x2': 7.55, 'y2': ly + 0.3, 'color': '#F7E7DA', 'width': 0.6,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 400, 'delay': 2200 + i * 250}},
        {'type': 'ellipse', 'name': f'!!xd{i}', 'x': round(px - 0.05, 3), 'y': round(py - 0.05, 3), 'w': 0.1, 'h': 0.1, 'fill': '#FFF4EA',
         'anim': {'fx': 'zoom', 'ms': 300, 'delay': 2100 + i * 250}},
        {'type': 'text', 'name': f'!!xt{i}', 'text': [{'text': n, 'role': 'title', 'size': 30}, {'text': f'{d} · {desc}', 'role': 'label', 'size': 10}],
         'x': 7.7, 'y': ly, 'w': 3.15, 'h': 1.05, 'anim': {'fx': 'fly', 'dir': 'r', 'ms': 500, 'delay': 2300 + i * 250}},
    ]
slides.append({
    'id': 'xsec', 'style': ST['inferno'], 'scene': 'LÒNG ĐẤT', 'transition': {'type': 'reveal', 'ms': 1200},
    'notes': 'Bổ đôi Trái Đất, đúng tỉ lệ. Vỏ chỉ dày 6 đến 50 km, gần như không thấy. Lớp phủ sâu tới khoảng 2.900 km. Rồi lõi ngoài kim loại lỏng, và lõi trong rắn ở tâm.',
    'source': 'F13',
    'shapes': xs + lab + [{'type': 'text', 'name': '!!k1', 'text': 'Mặt cắt · đúng tỉ lệ bán kính', 'role': 'kicker', 'x': 7.7, 'y': 0.6, 'w': 4.3, 'h': 0.3}]
    + G('mặt cắt', 'inferno', depth=0)})

# mantle zoom: scale x5 around a point on the 45° radius at the mantle mid-depth
def zoom_xsec(scale, fx_km, tx, ty):
    a = math.radians(45)
    r = R0 * fx_km / 6371
    px, py = XC + r * math.cos(a), YC - r * math.sin(a)
    cx = tx - (px - XC) * scale
    cy = ty - (py - YC) * scale
    return xsec(scale, cx, cy)


mz = zoom_xsec(4.2, 6371 - 300, 4.6, 1.2)
slides.append({
    'id': 'mantle', 'style': ST['inferno'], 'scene': 'LÒNG ĐẤT', 'transition': {'type': 'morph', 'ms': 2000}, 'chrome': False,
    'notes': 'Phóng vào lớp phủ. Đá nóng hơn nghìn độ, vẫn rắn, nhưng qua hàng triệu năm nó chảy rất chậm thành vòng đối lưu. Các vòng ấy kéo mảng trên mặt đất trôi đi.',
    'source': 'F13',
    'shapes': mz + [
        {'type': 'rect', 'name': '!!conv1', 'x': 1.1, 'y': 0.8, 'w': 2.3, 'h': 2.3, 'geom': 'CIRCULAR_ARROW', 'fill': '#FFF4EA', 'alpha': 0.9,
         'anim': [{'fx': 'zoom', 'ms': 600, 'delay': 900}, {'fx': 'spin', 'deg': 360, 'ms': 9000, 'loop': True}]},
        {'type': 'rect', 'name': '!!conv2', 'x': 3.9, 'y': 1.85, 'w': 1.8, 'h': 1.8, 'geom': 'CIRCULAR_ARROW', 'fill': '#FFF4EA', 'alpha': 0.75, 'rot': 180,
         'anim': [{'fx': 'zoom', 'ms': 600, 'delay': 1200}, {'fx': 'spin', 'deg': -360, 'ms': 11000, 'loop': True}]},
        {'type': 'text', 'name': '!!num', 'text': '2.900 km', 'role': 'numeral', 'size': 140, 'color': '#FFF4EA', 'x': 0.6, 'y': 4.15, 'w': 7.6, 'h': 2.7,
         'anim': {'fx': 'rise', 'ms': 900, 'delay': 600}},
        {'type': 'text', 'name': '!!b1', 'text': 'Lớp phủ: đá rắn, nóng hơn 1.000°C, chảy rất chậm thành những vòng đối lưu.', 'role': 'body', 'size': 19, 'color': '#FFF4EA',
         'x': 8.4, 'y': 2.75, 'w': 3.4, 'h': 1.35, 'anim': {'fx': 'fade', 'ms': 800, 'delay': 1300}},
        {'type': 'text', 'name': '!!k1', 'text': 'Lớp phủ', 'role': 'kicker', 'color': '#FFF4EA', 'x': 8.4, 'y': 2.35, 'w': 3.4, 'h': 0.3},
    ] + G('−2.900 km', 'inferno', depth=2900)})

CCX, CCY, CSC = 1.0, 6.7, 3.2
cz = zoom_xsec(CSC, 0, CCX, CCY)
CIR = R0 * 1220 / 6371 * CSC
slides.append({
    'id': 'core', 'style': ST['inferno'], 'scene': 'LÒNG ĐẤT', 'transition': {'type': 'morph', 'ms': 2200}, 'chrome': False,
    'notes': 'Tâm Trái Đất, sâu 6.371 km. Lõi trong là quả cầu sắt và niken rắn, khoảng 5.400 độ C, xấp xỉ bề mặt Mặt Trời. Nó rắn vì áp suất quá lớn.',
    'source': 'F14',
    'shapes': cz + [
        {'type': 'ellipse', 'name': '!!glow', 'x': round(CCX - CIR * 1.25, 3), 'y': round(CCY - CIR * 1.25, 3), 'w': round(CIR * 2.5, 3), 'h': round(CIR * 2.5, 3),
         'fill': '#FFF6C8', 'alpha': 0.3,
         'anim': [{'fx': 'fade', 'ms': 800, 'delay': 400}, {'fx': 'pulse', 'scale': 1.08, 'ms': 1800, 'loop': True}]},
        {'type': 'text', 'name': '!!num', 'text': '5.400°C', 'role': 'numeral', 'size': 170, 'color': '#2A0E08', 'x': 3.3, 'y': 0.9, 'w': 8.4, 'h': 3.05, 'align': 'r',
         'anim': {'fx': 'zoom', 'ms': 900, 'delay': 900}},
        {'type': 'text', 'name': '!!b1', 'text': 'Lõi trong: sắt–niken rắn, nóng xấp xỉ bề mặt Mặt Trời.', 'role': 'body', 'size': 19, 'color': '#2A0E08',
         'x': 6.7, 'y': 4.05, 'w': 5.0, 'h': 0.9, 'align': 'r', 'anim': {'fx': 'fade', 'ms': 800, 'delay': 1600}},
        {'type': 'text', 'name': '!!k1', 'text': 'Tâm Trái Đất · 6.371 km', 'role': 'kicker', 'color': '#2A0E08', 'x': 7.7, 'y': 0.6, 'w': 4.0, 'h': 0.3, 'align': 'r'},
    ] + G('−6.371 km', 'inferno', depth=6371)})

# ================================================================== 5 · THỜI GIAN SÂU (deeptime): a 24-hour dial
DCX, DCY, DR = 3.95, 3.85, 2.75
EV = [(0.0, '00:00', 'Trái Đất hình thành', '4,54 tỉ năm trước'), (5.5, '05:30', 'Dấu vết sự sống', '≥ 3,5 tỉ năm'),
      (11.32, '11:19', 'Ôxy tích tụ', '~2,4 tỉ năm'), (21.15, '21:09', 'Bùng nổ kỷ Cambri', '539 triệu năm'),
      (23.65, '23:39', 'Khủng long tuyệt chủng', '66 triệu năm'), (23.998, '23:59:54', 'Loài người', '300.000 năm')]
HAND_MS = 6000
EONS = [('Hỏa thành', 0.0, 24 * 0.54 / 4.54, '#3A2F4A'), ('Thái cổ', 24 * 0.54 / 4.54, 24 * 2.04 / 4.54, '#2C3D63'),
        ('Nguyên sinh', 24 * 2.04 / 4.54, 24 * (4.54 - 0.5388) / 4.54, '#3F6A8A'), ('Hiển sinh', 24 * (4.54 - 0.5388) / 4.54, 24.0, '#C6FF4A')]


def dial(scale=1.0, cx=DCX, cy=DCY, anim=True):
    sh = []
    r = DR * scale
    sh.append({'type': 'ellipse', 'name': '!!d-ring', 'x': round(cx - r, 3), 'y': round(cy - r, 3), 'w': round(2 * r, 3), 'h': round(2 * r, 3),
               'line_color': '#26324D', 'line_width': 1.25, **({'anim': {'fx': 'wheel', 'ms': 1200, 'delay': 100}} if anim else {})})
    ticks = []
    for h in range(24):
        a = math.radians(90 - h * 15)
        l = 0.22 if h % 6 == 0 else 0.1
        ticks.append({'type': 'line', 'x1': round(cx + (r - l * scale) * math.cos(a), 3), 'y1': round(cy - (r - l * scale) * math.sin(a), 3),
                      'x2': round(cx + r * math.cos(a), 3), 'y2': round(cy - r * math.sin(a), 3), 'color': '#7D8AA6', 'width': 1.0})
    sh.append({'type': 'group', 'name': '!!d-ticks', 'shapes': ticks, **({'anim': {'fx': 'fade', 'ms': 700, 'delay': 600}} if anim else {})})
    if anim:   # geologic eons as a coloured outer band, each filled when the hand reaches it
        for j, (n, h0, h1, col) in enumerate(EONS):
            a0, a1 = 90 - h0 * 15, 90 - h1 * 15
            pts = circle_pts(cx, cy, r * 1.05, a0, a1, 40) + circle_pts(cx, cy, r * 1.12, a1, a0, 40)
            sh.append({'type': 'poly', 'name': f'!!eon{j}', 'points': pts, 'fill': col,
                       'anim': {'fx': 'fade', 'ms': 500, 'delay': 1400 + int(HAND_MS * h0 / 24)}})
            am = math.radians(90 - (h0 + h1) / 2 * 15)
            sh.append({'type': 'text', 'name': f'!!eonl{j}', 'text': n, 'role': 'label', 'size': 9, 'color': '#7D8AA6', 'align': 'c',
                       'x': round(cx + r * 0.74 * math.cos(am) - 0.8, 3), 'y': round(cy - r * 0.74 * math.sin(am) - 0.11, 3), 'w': 1.6, 'h': 0.22,
                       'anim': {'fx': 'fade', 'ms': 500, 'delay': 1500 + int(HAND_MS * h0 / 24)}})
    for i, (hh, t, n, ago) in enumerate(EV):
        a = math.radians(90 - hh * 15)
        px, py = cx + r * math.cos(a), cy - r * math.sin(a)
        s = 0.16 if i < 5 else 0.22
        col = ORANGE if i == 5 else '#C6FF4A'
        e = {'type': 'ellipse', 'name': f'!!ev{i}', 'x': round(px - s / 2, 3), 'y': round(py - s / 2, 3), 'w': s, 'h': s, 'fill': col}
        if anim:
            e['anim'] = {'fx': 'zoom', 'ms': 350, 'delay': 1400 + int(HAND_MS * hh / 24)}
        sh.append(e)
    return sh


dl = dial()
# the hand: a group whose box is centred on the dial (an invisible counterweight), so spin turns it about the centre
dl.append({'type': 'group', 'name': '!!hand', 'shapes': [
    {'type': 'line', 'x1': DCX, 'y1': DCY, 'x2': DCX, 'y2': DCY - DR + 0.05, 'color': '#C6FF4A', 'width': 2.0},
    {'type': 'line', 'x1': DCX, 'y1': DCY, 'x2': DCX, 'y2': DCY + DR - 0.05, 'color': '#0A1020', 'width': 0.25, 'alpha': 0.0}],
    'anim': [{'fx': 'fade', 'ms': 300, 'delay': 1100}, {'fx': 'spin', 'deg': 360, 'ms': HAND_MS, 'delay': 1400, 'ease': [0, 0]}]})
dl.append({'type': 'ellipse', 'name': '!!hub', 'x': DCX - 0.08, 'y': DCY - 0.08, 'w': 0.16, 'h': 0.16, 'fill': '#C6FF4A', 'anim': {'fx': 'zoom', 'ms': 300, 'delay': 1000}})
rows = []
for i, (hh, t, n, ago) in enumerate(EV):
    y = 1.75 + i * 0.78
    hot = i == 5
    rows += [
        {'type': 'text', 'name': f'!!et{i}', 'text': t, 'role': 'label', 'size': 15, 'bold': True, 'color': ORANGE if hot else '#C6FF4A', 'x': 7.55, 'y': y, 'w': 1.6, 'h': 0.32,
         'anim': {'fx': 'appear', 'delay': 1450 + int(HAND_MS * hh / 24)}},
        {'type': 'text', 'name': f'!!en{i}', 'text': [{'text': n, 'role': 'body', 'size': 16, 'color': '#FFFFFF'}, {'text': ago, 'role': 'label', 'size': 10, 'color': '#7D8AA6'}],
         'x': 9.2, 'y': y - 0.04, 'w': 2.9, 'h': 0.68, 'anim': {'fx': 'fly', 'dir': 'r', 'ms': 400, 'delay': 1450 + int(HAND_MS * hh / 24)}},
    ]
slides.append({
    'id': 'clock', 'style': ST['deeptime'], 'scene': 'THỜI GIAN SÂU', 'transition': {'type': 'dissolve', 'ms': 1100},
    'notes': 'Hết chiều sâu, giờ là chiều sâu thời gian. Gói 4,54 tỉ năm vào một ngày. Sự sống có trước 6 giờ sáng. Ôxy tích tụ gần trưa. Động vật bùng nổ lúc 9 giờ tối. Khủng long biến mất lúc 23 giờ 39. Còn ta?',
    'source': 'F15, F16',
    'shapes': dl + rows + [
        {'type': 'text', 'name': '!!k1', 'text': 'Nếu 4,54 tỉ năm là một ngày', 'role': 'kicker', 'x': 7.55, 'y': 0.65, 'w': 4.6, 'h': 0.3},
        {'type': 'text', 'name': '!!h1', 'text': 'Một ngày của Trái Đất', 'role': 'title', 'size': 30, 'x': 7.55, 'y': 0.95, 'w': 4.7, 'h': 0.6,
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 200}},
    ] + G('tâm Trái Đất', 'deeptime', depth=6371)})

# last-seconds: zoom far into 12 o'clock on the same dial
ZS = 26.0
zd = dial(ZS, cx=6.2, cy=1.25 + DR * ZS, anim=False)
for s in zd:
    if s['name'] in ('!!ev5',):
        s['anim'] = [{'fx': 'pulse', 'scale': 1.4, 'ms': 1000, 'loop': True, 'delay': 1600}]
# a last-minute ruler along the top of the ring (60 s, tick each 5 s); humans = the last ~6 s
arc_r = DR * ZS
cxz, cyz = 6.2, 1.25 + DR * ZS
secs = []
for s in range(0, 61, 5):
    ang = math.radians(90 + (60 - s) / 86400 * 360 * 1.0)   # seconds before midnight (to the left of 12)
    # spread the last minute visually: 1 s = 0.17 in along the arc
    x = cxz - (60 - s) * 0.17
    secs.append({'type': 'line', 'x1': round(x, 3), 'y1': 1.62, 'x2': round(x, 3), 'y2': 1.82 if s % 15 else 1.95, 'color': '#7D8AA6', 'width': 1.0})
human = {'type': 'rect', 'name': '!!human', 'x': round(cxz - 5.7 * 0.17, 3), 'y': 1.22, 'w': round(5.7 * 0.17, 3), 'h': 0.14, 'fill': ORANGE,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 900, 'delay': 900}}
slides.append({
    'id': 'seconds', 'style': ST['deeptime'], 'scene': 'THỜI GIAN SÂU', 'transition': {'type': 'morph', 'ms': 2400},
    'notes': 'Phóng vào phút cuối trước nửa đêm. Loài người hiện đại có mặt khoảng 300.000 năm: 6 giây cuối của ngày. Toàn bộ lịch sử chữ viết: chưa tới một phần mười giây. [ngừng]',
    'source': 'F16',
    'shapes': zd + [
        {'type': 'group', 'name': '!!secs', 'shapes': secs, 'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 1200, 'delay': 300}},
        human,
        {'type': 'text', 'name': '!!m60', 'text': '23:59:00', 'role': 'label', 'size': 10, 'color': '#7D8AA6', 'x': cxz - 60 * 0.17 - 0.6, 'y': 2.05, 'w': 1.2, 'h': 0.26, 'align': 'c'},
        {'type': 'text', 'name': '!!m00', 'text': '24:00', 'role': 'label', 'size': 10, 'color': '#C6FF4A', 'x': cxz - 0.6, 'y': 2.05, 'w': 1.2, 'h': 0.26, 'align': 'c'},
        {'type': 'text', 'name': '!!num', 'text': '6 giây', 'role': 'numeral', 'size': 130, 'color': ORANGE, 'x': 0.7, 'y': 2.8, 'w': 8.0, 'h': 2.0,
         'anim': {'fx': 'type', 'ms': 500, 'step': 16, 'delay': 1300}},
        {'type': 'text', 'name': '!!b1', 'text': [{'text': 'Loài người hiện đại: 300.000 năm, tức 6 giây cuối của ngày.', 'role': 'body', 'size': 19, 'color': '#FFFFFF'},
                                                 {'text': 'Toàn bộ lịch sử chữ viết: chưa tới 0,1 giây.', 'role': 'body', 'size': 19, 'color': '#7D8AA6'}],
         'x': 0.78, 'y': 5.05, 'w': 9.6, 'h': 1.3, 'anim': {'fx': 'fade', 'ms': 800, 'delay': 2200}},
        {'type': 'text', 'name': '!!k1', 'text': 'Phút cuối cùng', 'role': 'kicker', 'x': 0.78, 'y': 2.45, 'w': 4.6, 'h': 0.3},
    ] + G('tâm Trái Đất', 'deeptime', depth=6371)})

# ================================================================== KẾT (cosmos): back to the dot, the gauge flies home
slides.append({
    'id': 'close', 'style': ST['cosmos'], 'scene': 'KẾT', 'transition': {'type': 'morph', 'ms': 2600}, 'chrome': False,
    'notes': 'Lùi ra, về lại 6 tỉ km. Carl Sagan viết về tấm ảnh này: hãy nhìn lại chấm nhỏ ấy. Đó là nơi này. Đó là nhà. [ngừng] Mọi thứ ta vừa đi qua nằm trong một điểm ảnh. Cảm ơn các bạn.',
    'source': 'F1, F17',
    'shapes': [
        {'type': 'ellipse', 'name': '!!dotshape', 'x': DOT1[0] - 0.035, 'y': DOT1[1] - 0.035, 'w': 0.07, 'h': 0.07, 'fill': '#A9CCF2',
         'anim': {'fx': 'zoom', 'ms': 500, 'delay': 1200}},
        {'type': 'ellipse', 'name': '!!ring', 'x': DOT1[0] - 0.24, 'y': DOT1[1] - 0.24, 'w': 0.48, 'h': 0.48, 'line_color': ORANGE, 'line_width': 1.25,
         'anim': [{'fx': 'zoom', 'ms': 600, 'delay': 1600}, {'fx': 'pulse', 'scale': 1.35, 'ms': 1400, 'loop': True}]},
        {'type': 'text', 'name': '!!q', 'text': '“Hãy nhìn lại chấm nhỏ ấy.\nĐó là nơi này. Đó là nhà.”', 'role': 'quote', 'size': 34, 'x': 0.75, 'y': 2.6, 'w': 6.4, 'h': 1.5,
         'anim': {'fx': 'type', 'ms': 500, 'step': 5, 'delay': 2200}},
        {'type': 'line', 'name': '!!lead', 'x1': DOT1[0] + 0.26, 'y1': DOT1[1], 'x2': DOT1[0] + 1.2, 'y2': DOT1[1], 'color': ORANGE, 'width': 0.75,
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 600, 'delay': 5600}},
        {'type': 'text', 'name': '!!t1', 'text': 'Đây là nhà.', 'role': 'title', 'size': 34, 'x': DOT1[0] + 1.35, 'y': DOT1[1] - 0.33, 'w': 3.6, 'h': 0.65,
         'anim': {'fx': 'type', 'ms': 600, 'step': 9, 'delay': 6100}},
        {'type': 'text', 'name': '!!by', 'text': 'Carl Sagan · Pale Blue Dot, 1994', 'role': 'kicker', 'x': 0.78, 'y': 4.3, 'w': 5, 'h': 0.3,
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 5200}},
    ] + G('6 tỉ km', 'photo', alt=6e9)})

SRC = ['[F1] NASA/JPL, Pale Blue Dot (PIA23645); Wikipedia "Pale Blue Dot": 14/2/1990, ~6 tỉ km, 0,12 điểm ảnh',
       '[F2] Wikipedia "Apsis": cận nhật đầu tháng 1 · 147,1 triệu km, viễn nhật đầu tháng 7 · 152,1 triệu km; trục nghiêng 23,4°',
       '[F3–F5] Wikipedia "Earthrise" (Apollo 8, 24/12/1968, W. Anders), "The Blue Marble" (Apollo 17, 7/12/1972, ~29.400 km)',
       '[F6] Wikipedia "Earth\'s rotation": 23 giờ 56 phút 4 giây; 1.670 km/h = chu vi xích đạo 40.075 km / ngày sao',
       '[F7–F9] Wikipedia "Atmosphere of Earth": tầng, Kármán 100 km, 99,99997% dưới 100 km; N₂ 78,08% · O₂ 20,95% · Ar 0,93%',
       '[F10] NOAA GML: CO₂ trung bình toàn cầu 2024 = 422,8 ppm, kỷ lục   [F11] USGS Water Science School: 71% · 96,5%',
       '[F12] USGS This Dynamic Earth: sống núi Đại Tây Dương ~2,5 cm/năm, "như móng tay mọc"   [F13] USGS: vỏ, lớp phủ ~2.900 km, lõi',
       '[F14] Wikipedia "Earth\'s inner core": ~5.700 K (5.430°C), xấp xỉ bề mặt Mặt Trời   [F15] USGS/Wikipedia "Age of Earth": 4,54 tỉ năm',
       '[F16] Wikipedia: sự sống ≥ 3,5 tỉ năm; GOE ~2,4 tỉ; Cambri 538,8 triệu; K–Pg 66 triệu; H. sapiens ~300.000 năm   [F17] C. Sagan, Pale Blue Dot (1994)   [F18] Wikipedia "DSCOVR": điểm L1 ~1,5 triệu km; Mặt Trăng đi qua 16–17/7/2015',
       'Ảnh: NASA, NASA/JPL-Caltech, NASA Earth Observatory (R. Stöckli, R. Simmon), USGS (J.D. Griggs): phạm vi công cộng · Phông: Fraunces, Be Vietnam Pro, Anton, JetBrains Mono (OFL)']
slides.append({
    'id': 'credits', 'style': ST['deeptime'], 'scene': 'NGUỒN', 'transition': {'type': 'fade', 'ms': 900},
    'notes': 'Nguồn số liệu, ảnh và phông chữ, để ai muốn kiểm tra.',
    'shapes': [{'type': 'text', 'name': '!!t', 'text': 'Nguồn', 'role': 'title', 'size': 40, 'x': 0.75, 'y': 0.6, 'w': 6, 'h': 0.75,
                'anim': {'fx': 'type', 'ms': 300, 'step': 10}}]
    + [{'type': 'text', 'name': f'!!cr{i}', 'text': c, 'role': 'label', 'size': 10.5, 'color': '#DCE4F2', 'x': 0.75, 'y': 1.55 + i * 0.5, 'w': 11.3, 'h': 0.42,
        'anim': {'fx': 'fade', 'ms': 300, 'delay': 300 + i * 120}} for i, c in enumerate(SRC)]
    + G('6 tỉ km', 'deeptime', alt=6e9)})

deck = {'style': ST['cosmos'], 'title': 'Trái Đất · Rơi về nhà', 'compat': 'dual',
        'motion': {'default_ms': 1300, 'stagger_ms': 120}, 'slides': slides}
for _s in deck['slides'] if isinstance(deck, dict) else deck:
    if _s.get('source') and _s.get('notes') and 'Nguồn:' not in _s['notes']:
        _s['notes'] += f"\n\nNguồn: {_s['source']}"
(HERE / 'deck.json').write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(slides), 'slides')
