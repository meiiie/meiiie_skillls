"""Milestone-1 deck: two signature scenes, each as (a) the film on its slide and (b) an editable,
native-shape version of the same picture drawn from the same geometry (one geometry, two renderers).
  python3 make_m1.py && python3 <skill>/scripts/build_deck.py deck/m1.json --out deck/m1.pptx"""
import json, math, sys
from pathlib import Path
from shapely.geometry import LineString, Polygon as SPoly, box
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'design')); sys.path.insert(0, str(ROOT / 'design' / 'films'))
import ds
import baro_geom as B

FW, FH = 8.0 * 2560 / 1080, 8.0
UPI = FW / ds.FILM_W
SERIF, SANS, SANS_MED, SANS_SEMI, MONO = 'Source Serif Pro Semibold', 'IBM Plex Sans', 'IBM Plex Sans Medm', 'IBM Plex Sans SmBld', 'IBM Plex Mono'
FRAME = box(-FW / 2, -FH / 2, FW / 2, FH / 2)

def I(x, y):
    """scene units -> slide inches inside the film window"""
    return [round(ds.FILM_X + (x + FW / 2) / FW * ds.FILM_W, 4), round(ds.FILM_Y + (FH / 2 - y) / FH * ds.FILM_H, 4)]

def W(sw):
    """manimgx stroke width (hundredths of a unit) -> points"""
    return round(sw * 0.01 / UPI * 72, 2)

def text(name, s, cx, cy, size, font=SANS, color=ds.INK, align='c', w=None, h=None, anchor='m'):
    w = w or max(0.4, len(s) * size / 72 * 0.56 + 0.2)
    h = h or size / 72 * 1.5
    x, y = I(cx, cy)
    if align == 'c':
        x -= w / 2
    elif align == 'r':
        x -= w
    return {'type': 'text', 'name': name, 'text': s, 'x': round(x, 3), 'y': round(y - h / 2, 3), 'w': round(w, 3), 'h': round(h, 3),
            'font': font, 'size': size, 'color': color, 'align': align[0], 'anchor': anchor}

def clip_lines(pts, closed=False):
    g = LineString(pts + ([pts[0]] if closed else []))
    g = g.intersection(FRAME)
    out = []
    for part in ([g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))):
        if part.geom_type == 'LineString' and len(part.coords) >= 2:
            out.append([I(*c) for c in part.coords])
    return out

def clip_poly(pts):
    p = SPoly(pts).buffer(0).intersection(FRAME)
    out = []
    for part in ([p] if p.geom_type == 'Polygon' else list(getattr(p, 'geoms', []))):
        if part.geom_type == 'Polygon' and part.area > 1e-4:
            out.append([I(*c) for c in part.exterior.coords])
    return out

def header(kicker, title, stand, n, source):
    L = ds.MARGIN_X
    return [
        {'type': 'text', 'name': '!!kicker', 'text': kicker, 'x': L, 'y': 0.42, 'w': 7.0, 'h': 0.3, 'role': 'kicker'},
        {'type': 'text', 'name': '!!title', 'text': title, 'x': L, 'y': 0.7, 'w': ds.col_w(8), 'h': 0.6, 'role': 'title'},
        {'type': 'text', 'name': '!!stand', 'text': stand, 'x': ds.col_x(8), 'y': 0.46, 'w': ds.col_w(4), 'h': 0.95, 'font': SANS,
         'size': 13, 'color': ds.SLATE, 'line': 1.25},
        {'type': 'line', 'name': '!!rule', 'x1': L, 'y1': 1.5, 'x2': ds.SLIDE_W - L, 'y2': 1.5, 'color': ds.INK, 'width': 0.75},
        {'type': 'text', 'name': '!!source', 'text': source, 'x': L, 'y': 6.77, 'w': 10.9, 'h': 0.34, 'font': SANS, 'size': 10, 'color': ds.SLATE, 'line': 1.0},
        {'type': 'text', 'name': '!!pageno', 'text': f'{n:02d}', 'x': ds.SLIDE_W - L - 0.8, 'y': 6.76, 'w': 0.8, 'h': 0.2, 'font': MONO, 'size': 10, 'color': ds.SLATE, 'align': 'r'},
    ]

# ------------------------------------------------------------------ S1 native (final state of the film)
def s1_native():
    G = json.load(open(ROOT / 'design/films/pressure_geom.json'))
    sh = []
    for i, g in enumerate(G['graticule']):
        for j, seg in enumerate(clip_lines(g['pts'])):
            sh.append({'type': 'poly', 'name': f'grat{i}_{j}', 'points': seg, 'open': True, 'line_color': ds.RULE, 'line_width': W(0.9)})
    for i, r in enumerate(G['land']):
        for j, p in enumerate(clip_poly(r)):
            sh.append({'type': 'poly', 'name': f'land{i}_{j}', 'points': p, 'fill': ds.LAND})
    for i, b in enumerate(G['borders']):
        for j, seg in enumerate(clip_lines(b)):
            sh.append({'type': 'poly', 'name': f'bord{i}_{j}', 'points': seg, 'open': True, 'line_color': ds.PAPER, 'line_width': W(1.2)})
    for i, c in enumerate(G['frames'][-1]):
        col = ds.LOW if c['level'] < 3.1 else ds.HIGH
        for j, seg in enumerate(clip_lines(c['pts'], c['closed'])):
            sh.append({'type': 'poly', 'name': f'iso{i}_{j}', 'points': seg, 'open': True, 'line_color': col, 'line_width': W(1.8), 'line_alpha': 0.8})
    for i, c in enumerate(G['world_line']['2026']):
        for j, seg in enumerate(clip_lines(c['pts'], c['closed'])):
            sh.append({'type': 'poly', 'name': f'world{i}_{j}', 'points': seg, 'open': True, 'line_color': ds.INK, 'line_width': W(4.0)})
    lo, hi = G['low']['xy'], G['high']['xy']
    sh.append(text('mark.T', 'T', lo[0], lo[1] + 0.12, 58, SERIF, ds.LOW))
    sh.append(text('mark.Tl', 'ÁP THẤP', lo[0], lo[1] - 0.5, 10, SANS_SEMI, ds.LOW))
    sh.append(text('mark.C', 'C', hi[0], hi[1] + 0.12, 58, SERIF, ds.HIGH))
    sh.append(text('mark.Cl', 'ÁP CAO', hi[0], hi[1] - 0.5, 10, SANS_SEMI, ds.HIGH))
    L = -FW / 2 + 0.6
    sh.append(text('hud.kick', 'TĂNG TRƯỞNG GDP THỰC · ĐƯỜNG ĐỒNG MỨC, %', L, 3.36, 13, SANS_SEMI, ds.SLATE, 'l', w=5.0))
    sh.append(text('hud.year', '2026', L - 0.04, 2.6, 58, SERIF, ds.INK, 'l', w=2.2))
    x0 = I(L, 1.78)
    sh.append({'type': 'line', 'name': 'hud.sw', 'x1': x0[0], 'y1': x0[1], 'x2': x0[0] + 0.32, 'y2': x0[1], 'color': ds.INK, 'width': W(4.0)})
    sh.append(text('hud.w', '3,1%', L + 0.66, 1.8, 23, SERIF, ds.INK, 'l', w=1.0))
    sh.append(text('hud.wl', 'thế giới', L + 1.86, 1.76, 13, SANS, ds.SLATE, 'l', w=1.0))
    ly = -3.38
    for k, (col, lab, dx) in enumerate([(ds.HIGH, 'trên mức thế giới', 0.0), (ds.LOW, 'dưới mức thế giới', 2.55)]):
        a = I(L + dx, ly)
        sh.append({'type': 'line', 'name': f'leg{k}', 'x1': a[0], 'y1': a[1], 'x2': a[0] + 0.27, 'y2': a[1], 'color': col, 'width': W(2.4)})
        sh.append(text(f'leg{k}t', lab, L + dx + 0.58, ly, 10, SANS, ds.SLATE, 'l', w=1.6))
    sh.append(text('end', 'Một vùng áp thấp năng lượng, một vùng áp cao AI.', L, -2.6, 23, SERIF, ds.INK, 'l', w=7.5))
    return [{'type': 'group', 'name': '!!s1', 'shapes': sh}]

# ------------------------------------------------------------------ S2 native (the dials after the hikes)
def s2_native():
    sh = []
    CY, R = B.CY, B.R
    for b in B.BANKS:
        cx, k = b['x'], b['key']
        def circ(name, r, **st):
            a = I(cx - r, CY + r); c = I(cx + r, CY - r)
            return dict({'type': 'ellipse', 'name': name, 'x': a[0], 'y': a[1], 'w': round(c[0] - a[0], 4), 'h': round(c[1] - a[1], 4)}, **st)
        sh.append(circ(f'{k}.bezel', R + B.BEZEL, fill='#D8D2C4', line_color=ds.INK, line_width=W(2.0)))
        for i, (p0, p1) in enumerate(B.knurl(cx, n=96)):
            a, c = I(*p0), I(*p1)
            sh.append({'type': 'line', 'name': f'{k}.kn{i}', 'x1': a[0], 'y1': a[1], 'x2': c[0], 'y2': c[1], 'color': '#B3AB9A', 'width': W(0.8)})
        for i, (c0, s0, s1) in enumerate(B.screws(cx)):
            a = I(c0[0] - 0.06, c0[1] + 0.06); c = I(c0[0] + 0.06, c0[1] - 0.06)
            sh.append({'type': 'ellipse', 'name': f'{k}.sc{i}', 'x': a[0], 'y': a[1], 'w': round(c[0] - a[0], 4), 'h': round(c[1] - a[1], 4),
                       'fill': '#C9B98F', 'line_color': ds.SLATE, 'line_width': W(0.6)})
            a, c = I(*s0), I(*s1)
            sh.append({'type': 'line', 'name': f'{k}.ss{i}', 'x1': a[0], 'y1': a[1], 'x2': c[0], 'y2': c[1], 'color': ds.SLATE, 'width': W(0.8)})
        sh.append(circ(f'{k}.face', R, fill=ds.PAPER, line_color=ds.INK, line_width=W(3.2)))
        sh.append(circ(f'{k}.shade', R - 0.09, fill='#E9E6DD'))
        sh.append(circ(f'{k}.ring', R - 0.09, line_color=ds.INK, line_width=W(1.0)))
        sh.append(circ(f'{k}.inner', 0.62, line_color=ds.RULE, line_width=W(1.0)))
        sh.append({'type': 'poly', 'name': f'{k}.mirror', 'points': [I(*q) for q in B.mirror_arc(cx)], 'open': True, 'line_color': '#C9B98F', 'line_width': W(2.4)})
        track = [I(*B.pol(cx, CY, R - 0.2, B.ang(v / 20))) for v in range(0, 101)]
        sh.append({'type': 'poly', 'name': f'{k}.track', 'points': track, 'open': True, 'line_color': ds.INK, 'line_width': W(1.4)})
        for i, t in enumerate(B.ticks(cx)):
            a, c = I(*t['p0']), I(*t['p1'])
            w = {'major': 2.4, 'mid': 1.5, 'minor': 0.9}[t['kind']]
            sh.append({'type': 'line', 'name': f'{k}.tick{i}', 'x1': a[0], 'y1': a[1], 'x2': c[0], 'y2': c[1],
                       'color': ds.INK if t['kind'] != 'minor' else ds.SLATE, 'width': W(w)})
        for n in B.numerals(cx):
            sh.append(text(f"{k}.n{n['text']}", n['text'], n['p'][0], n['p'][1], 13, MONO, ds.HIGH if n['text'] == '2' else ds.INK, w=0.4))
        p2 = B.pol(cx, CY, R - 0.2, B.ang(2.0)); p3 = B.pol(cx, CY, R - 0.62, B.ang(2.0))
        a, c = I(*p2), I(*p3)
        sh.append({'type': 'line', 'name': f'{k}.target', 'x1': a[0], 'y1': a[1], 'x2': c[0], 'y2': c[1], 'color': ds.HIGH, 'width': W(3.2)})
        n2 = B.numerals(cx)[2]['p']
        sh.append(text(f'{k}.tl', 'mục tiêu', n2[0], n2[1] - 0.27, 10, SANS_MED, ds.HIGH, w=0.9))
        sh.append(text(f'{k}.unit', '%/năm', cx, CY + 0.72, 10, MONO, ds.SLATE, w=0.8))
        sh.append(text(f'{k}.code', b['code'], cx, CY - 0.78, 23, SERIF, ds.INK, w=1.2))
        sh.append(text(f'{k}.stamp', b['stamp'], cx, CY - 1.13, 10, MONO, ds.SLATE, w=1.3))
        if b['hi']:
            band = [I(*p) for p in B.gap_arc(cx, b['hi'][0], b['hi'][1], r_in=R - 0.36, r_out=R - 0.22, n=12)]
            sh.append({'type': 'poly', 'name': f'{k}.band', 'points': band, 'fill': ds.INK, 'alpha': 0.9})
        gap = [I(*p) for p in B.gap_arc(cx, b['after'], b['cpi'])]
        sh.append({'type': 'poly', 'name': f'{k}.gap', 'points': gap, 'fill': ds.HIGH if b['after'] > b['cpi'] else ds.LOW})
        p0, p1, d = B.hand(cx, b['cpi'])
        a, c = I(*p0), I(*p1)
        sh.append({'type': 'line', 'name': f'{k}.hand', 'x1': a[0], 'y1': a[1], 'x2': c[0], 'y2': c[1], 'color': ds.LOW, 'width': W(2.2)})
        sh.append({'type': 'poly', 'name': f'{k}.handtip', 'points': [I(*q) for q in d], 'fill': ds.LOW})
        nd = B.needle(cx, b['after'])
        sh.append({'type': 'poly', 'name': f'{k}.needle', 'points': [I(*q) for q in nd], 'fill': ds.INK})
        sh.append(circ(f'{k}.hub', 0.13, fill=ds.INK))
        sh.append(circ(f'{k}.hub2', 0.045, fill=ds.PAPER))
        # chip, readout, inflation, real rate
        sh.append(text(f'{k}.date', b['date'], cx - 0.12, CY + R + 0.45, 23, SERIF, ds.INK, 'r', w=0.9))
        sh.append(text(f'{k}.hike', '+0,25 điểm %', cx + 0.05, CY + R + 0.4, 13, SANS_SEMI, ds.HIGH, 'l', w=1.3))
        val = '3,75–4,00%' if k == 'fed' else f"{b['after']:.2f}%".replace('.', ',')
        sh.append(text(f'{k}.rate', val, cx, CY - R - 0.5, 34, SERIF, ds.INK, w=3.6))
        sh.append(text(f'{k}.what', b['country'] + ' · ' + b['what'], cx, CY - R - 1.06, 13, SANS, ds.SLATE, w=4.2))
        real = {'fed': '+0,3', 'ecb': '−0,6', 'boj': '−0,8'}[k]
        sh.append(text(f'{k}.cpi', f"lạm phát {b['cpi']:.1f}%".replace('.', ',') + f'  ·  lãi suất thực {real}', cx, CY - R - 1.46, 13, SANS_SEMI,
                       ds.HIGH if b['after'] > b['cpi'] else ds.LOW, w=4.4))
    L = -FW / 2 + 0.6
    sh.append(text('hud.kick', 'LÃI SUẤT ĐIỀU HÀNH VÀ LẠM PHÁT · THÁNG 9/2026, %', L, 3.5, 13, SANS_SEMI, ds.SLATE, 'l', w=6.0))
    return [{'type': 'group', 'name': '!!s2', 'shapes': sh}]

SRC1 = ('Nguồn: IMF WEO 10/2026, Bảng A (tăng trưởng GDP thực 2025–2026); WTO, thông cáo 8/10/2026. Đường đồng mức nội suy từ số liệu '
        'từng nền kinh tế (một số nước dùng số bình quân khu vực của IMF): minh hoạ không gian, không phải số đo. Bản đồ: Natural Earth.')
SRC2 = ('Nguồn: Fed 16/9/2026; ECB 10/9/2026; BoJ 18/9/2026; IMF WEO 10/2026 (lạm phát CPI bình quân 2026, dự báo). Lãi suất thực = '
        'lãi suất điều hành (Fed: giữa khoảng 3,75–4,00%) − lạm phát dự báo năm 2026: số suy ra, làm tròn một chữ số.')
T1 = ('BỨC TRANH CHUNG', 'Hai tâm áp của kinh tế thế giới',
      'Cú sốc năng lượng ở vùng Vịnh và cú hích đầu tư AI ở Đông Á. Thế giới tăng 3,1%, từ 3,5% năm 2025.')
T2 = ('LÃI SUẤT', 'Chín ngày, ba lần tăng lãi suất',
      'ECB, Fed và BoJ cùng nâng lãi suất 0,25 điểm % từ ngày 10 đến 18/9. Chỉ ở Mỹ, lãi suất điều hành cao hơn lạm phát dự báo năm 2026.')

def film(name, path):
    return {'type': 'video', 'name': name, 'path': path, 'poster': path.replace('.mp4', '.poster.png'),
            'x': ds.FILM_X, 'y': ds.FILM_Y, 'w': ds.FILM_W, 'h': ds.FILM_H, 'loop': False, 'mute': True, 'autoplay': True}

def main():
    deck = {
        'style': str(ROOT / 'design/style.json'), 'title': 'Kinh tế thế giới · tháng 10/2026', 'compat': 'morph', 'bg': ds.PAPER,
        'chrome': {'over': []},
        'slides': [
            {'id': 's1film', 'scene': 'S1', 'transition': 'fade', 'ms': 900, 'bg': ds.PAPER,
             'shapes': header(*T1[:1], T1[1], T1[2], 1, SRC1) + [film('!!s1.film', 'assets/film/pressure.mp4')]},
            {'id': 's1native', 'scene': 'S1', 'transition': 'fade', 'ms': 900, 'bg': ds.PAPER,
             'shapes': header(T1[0] + ' · BẢN DỰNG SẴN (CHỈNH SỬA ĐƯỢC)', T1[1], T1[2], 2, SRC1) + s1_native()},
            {'id': 's2film', 'scene': 'S2', 'transition': 'fade', 'ms': 900, 'bg': ds.PAPER,
             'shapes': header(T2[0], T2[1], T2[2], 3, SRC2) + [film('!!s2.film', 'assets/film/baro.mp4')]},
            {'id': 's2native', 'scene': 'S2', 'transition': 'fade', 'ms': 900, 'bg': ds.PAPER,
             'shapes': header(T2[0] + ' · BẢN DỰNG SẴN (CHỈNH SỬA ĐƯỢC)', T2[1], T2[2], 4, SRC2) + s2_native()},
        ]}
    notes = json.load(open(ROOT / 'script/notes_m1.json')) if (ROOT / 'script/notes_m1.json').exists() else {}
    for s in deck['slides']:
        if s['id'] in notes:
            s['notes'] = notes[s['id']]
    (ROOT / 'deck').mkdir(exist_ok=True)
    json.dump(deck, open(ROOT / 'm1.json', 'w'), ensure_ascii=False, indent=1)
    print('shapes', [sum(1 for _ in json.dumps(s)) for s in deck['slides']])

if __name__ == '__main__':
    main()
