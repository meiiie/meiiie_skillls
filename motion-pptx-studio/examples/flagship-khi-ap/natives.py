"""Editable native versions of films S3-S6 (end state of each film, same geometry modules as the films)
and the drawn objects of the data slides (thermometers, waterfall, Vietnam map)."""
import json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'design')); sys.path.insert(0, str(ROOT / 'design' / 'films'))
import ds
from make_m1 import I, W, text, clip_lines, clip_poly, FW, FH, SERIF, SANS, SANS_MED, SANS_SEMI, MONO
import drum_geom as DG, tide_geom as TG, wind_geom as WG

def ln(name, a, b, color, w, dash=None):
    d = {'type': 'line', 'name': name, 'x1': a[0], 'y1': a[1], 'x2': b[0], 'y2': b[1], 'color': color, 'width': w}
    if dash:
        d['dash'] = dash
    return d

def rect_s(name, x0, y0, x1, y1, fill, **kw):
    """rectangle from two scene-unit corners"""
    a, b = I(x0, max(y0, y1)), I(x1, min(y0, y1))
    return dict({'type': 'rect', 'name': name, 'x': a[0], 'y': a[1], 'w': round(b[0] - a[0], 4), 'h': round(b[1] - a[1], 4), 'fill': fill}, **kw)

def hud(kick, L=-FW / 2 + 0.6):
    return text('hud.kick', kick, L, 3.62 - 0.12, 13, SANS_SEMI, ds.SLATE, 'l', w=7.0)

# ------------------------------------------------------------------ S3 drum: the flat chart
def s3_native():
    sh = [hud('TĂNG TRƯỞNG GDP THỰC THẾ GIỚI, %')]
    C = DG.chart_xy
    x0, _ = C(2017.5, 0); x1, _ = C(2027.5, 0)
    px0, _ = C(2025.5, 0)
    sh.append(rect_s('proj', px0, C(0, -3)[1], x1, C(0, 7)[1], ds.LAND))
    for g in range(-3, 8):
        y = C(0, g)[1]
        sh.append(ln(f'h{g}', I(x0, y), I(x1, y), ds.INK if g == 0 else ds.ISOBAR, W(1.1 if g == 0 else 0.6)))
    for k in range(2017, 2028):
        x = C(k + 0.5, 0)[0]
        sh.append(ln(f'v{k}', I(x, C(0, -3)[1]), I(x, C(0, 7)[1]), ds.ISOBAR, W(0.5)))
    pts = [I(*C(y, g)) for y, g in zip(DG.YEARS, DG.G)]
    sh.append({'type': 'poly', 'name': 'trace', 'points': pts[:8], 'open': True, 'line_color': ds.INK, 'line_width': W(3.2)})
    for i in (7, 8):
        a, b = pts[i], pts[i + 1]
        sh.append(ln(f'proj{i}', a, b, ds.INK, W(3.2), 'dash'))
    for (y, g), p in zip(zip(DG.YEARS, DG.G), pts):
        sh.append({'type': 'ellipse', 'name': f'dot{y}', 'x': p[0] - 0.035, 'y': p[1] - 0.035, 'w': 0.07, 'h': 0.07, 'fill': ds.INK})
        cx, cy = C(y, g)
        col = ds.LOW if (y == 2026 or g < 0) else ds.INK
        if g >= 0:
            sh.append(text(f'val{y}', DG.vn(g), cx, cy + 0.36, 17, SERIF, col, w=0.7))
        else:
            sh.append(text(f'val{y}', DG.vn(g), cx - 0.55, cy + 0.02, 17, SERIF, col, w=0.8))
        sh.append(text(f'yr{y}', str(y), cx, C(0, -3)[1] - 0.26, 10, MONO, ds.SLATE, w=0.6))
    for g in (-2, 0, 2, 4, 6):
        sh.append(text(f'tk{g}', DG.vn(g, 0), x0 - 0.3, C(0, g)[1], 10, MONO, ds.SLATE, w=0.4))
    ay = C(0, DG.AVG)[1]
    sh.append(ln('avg', I(x0, ay), I(x1, ay), ds.HIGH, W(2.0), 'dash'))
    sh.append(text('avg.l', 'bình quân', x1 + 0.2, ay + 0.15, 13, SANS_SEMI, ds.HIGH, 'l', w=1.6))
    sh.append(text('avg.l2', '2008–2017: 3,3', x1 + 0.2, ay - 0.17, 13, SANS_SEMI, ds.HIGH, 'l', w=1.6))
    sh.append(text('ptag', 'DỰ BÁO', C(2026.5, 0)[0], C(0, 7)[1] + 0.2, 10, SANS_SEMI, ds.SLATE, w=0.9))
    sh.append(text('head', '2026: tăng 3,1%, dưới mức bình quân 2008–2017.', -FW / 2 + 0.6, -3.08, 23, SERIF, ds.INK, 'l', w=8.0))
    return [{'type': 'group', 'name': '!!s3', 'shapes': sh}]

# ------------------------------------------------------------------ S4 wind: the ranked chart over the faded map
def s4_native():
    G = json.load(open(ROOT / 'design/films/pressure_geom.json'))
    sh = []
    for i, r in enumerate(G['land']):
        for j, p in enumerate(clip_poly(r)):
            sh.append({'type': 'poly', 'name': f'land{i}_{j}', 'points': p, 'fill': '#E8E5DC'})
    sh.append(hud('XUẤT KHẨU HÀNG HOÁ 2026 THEO KHU VỰC · KHỐI LƯỢNG, %'))
    rows = WG.bar_rows()
    top, bot = WG.ROW0 + 0.45, WG.ROW0 - 6 * WG.DROW - 0.45
    for r in rows:
        v, y = r['v'], r['y']
        col = ds.HIGH if v > 0.5 else (ds.SLATE if v > -1 else ds.LOW)
        xa, xb = sorted([r['x0'], r['x1']])
        if xb - xa < 0.03:
            xb = xa + 0.03
        sh.append(rect_s(f"bar.{r['key']}", xa, y - 0.2, xb, y + 0.2, col))
        if v > 0:
            sh.append(text(f"nm.{r['key']}", r['name'], WG.ZX - 0.3, y, 13, SANS_MED, ds.INK, 'r', w=3.6))
            sh.append(text(f"v.{r['key']}", WG.vn(v), r['x1'] + 0.18, y, 23, SERIF, col, 'l', w=1.1))
        else:
            sh.append(text(f"nm.{r['key']}", r['name'], WG.ZX + 0.3, y, 13, SANS_MED, ds.INK, 'l', w=2.0))
            sh.append(text(f"v.{r['key']}", WG.vn(v), r['x1'] - 0.18, y, 23, SERIF, col, 'r', w=1.1))
    sh.append(ln('zero', I(WG.ZX, top), I(WG.ZX, bot), ds.INK, W(2.0)))
    wx = WG.ZX + WG.WORLD * WG.PPU
    sh.append(ln('world', I(wx, top), I(wx, bot), ds.INK, W(1.4), 'dash'))
    sh.append(text('world.l', 'thương mại hàng hoá thế giới +3,9', wx, top + 0.16, 10, SANS_SEMI, ds.INK, w=3.2))
    sh.append(text('head', 'Châu Á góp 4,0 điểm % trong mức tăng 3,9%', -FW / 2 + 0.6, -2.95, 23, SERIF, ds.INK, 'l', w=8.5))
    sh.append(text('head2', 'của thương mại hàng hoá thế giới.', -FW / 2 + 0.6, -3.42, 23, SERIF, ds.INK, 'l', w=8.5))
    return [{'type': 'group', 'name': '!!s4', 'shapes': sh}]

# ------------------------------------------------------------------ S5 tide: wells at 2031 (end of the film)
def s5_native(k=0.8, idx=4):
    AX, AY = 9.1, 0.0
    X = lambda x, y: (AX + (x - AX) * k, AY + (y - AY) * k)
    top = TG.y_of(TG.VMAX) + 0.15
    sh = [hud('NỢ CÔNG GỘP, % GDP')]
    L = -FW / 2 + 0.6
    year = TG.YEARS[idx]
    sh.append(text('hud.year', str(year), L - 0.04, 2.83, 58, SERIF, ds.INK, 'l', w=2.4))
    if year >= 2026:
        sh.append(text('hud.proj', 'dự báo', L, 2.12, 13, SANS_SEMI, ds.SLATE, 'l', w=1.2))
    if year == 2031:
        sh.append(text('hud.skip', '2028–2030 không hiển thị', L, 1.84, 10, SANS, ds.SLATE, 'l', w=2.6))
    for i, key in enumerate(TG.ORDER):
        x = TG.x_of(i)
        v = TG.DEBT[key][1][idx]
        hw = TG.WW / 2
        def R(nm, x0, y0, x1, y1, fill, **kw):
            a, b = X(x0, y0), X(x1, y1)
            return rect_s(f'{key}.{nm}', a[0], a[1], b[0], b[1], fill, **kw)
        sh.append(R('base', x - hw - 0.15, TG.YB - 0.35, x + hw + 0.15, TG.YB - 0.05, '#C9B98F', line_color=ds.INK, line_width=W(1.2)))
        sh.append(R('foot', x - hw - 0.25, TG.YB - 0.47, x + hw + 0.25, TG.YB - 0.35, ds.INK))
        sh.append(R('glass', x - hw, TG.YB, x + hw, top, '#F7F5F0'))
        sh.append(R('water', x - hw, TG.YB, x + hw, TG.y_of(min(v, 100)), '#A9B8C8'))
        if v > 100:
            sh.append(R('over', x - hw, TG.y_of(100), x + hw, TG.y_of(v), ds.LOW, alpha=0.82))
        sx = x - hw + 0.06
        for t in range(0, TG.VMAX + 1, 10):
            Lt = 0.26 if t % 50 == 0 else 0.15
            sh.append(ln(f'{key}.t{t}', I(*X(sx, TG.y_of(t))), I(*X(sx + Lt, TG.y_of(t))), ds.INK, W(1.0 if t % 50 == 0 else 0.55) * k))
        for t in (50, 100, 150, 200):
            p = X(sx + 0.46, TG.y_of(t))
            sh.append(text(f'{key}.n{t}', str(t), p[0], p[1], 10, MONO, ds.SLATE, w=0.4))
        for side in (-1, 1):
            sh.append(ln(f'{key}.side{side}', I(*X(x + side * hw, TG.YB)), I(*X(x + side * hw, top)), ds.INK, W(1.6) * k))
        sh.append(R('cap', x - hw - 0.11, top - 0.03, x + hw + 0.11, top + 0.19, '#C9B98F', line_color=ds.INK, line_width=W(1.2)))
        col = ds.LOW if v > 100 else ds.INK
        p = X(x + hw, TG.y_of(v))
        a, b, c = I(p[0] + 0.02 * k, p[1]), I(p[0] + 0.2 * k, p[1] + 0.09 * k), I(p[0] + 0.2 * k, p[1] - 0.09 * k)
        sh.append({'type': 'poly', 'name': f'{key}.mark', 'points': [a, b, c], 'fill': col})
        q = X(x, TG.VAL_Y)
        sh.append(text(f'{key}.val', TG.vn(v), q[0], q[1], 17, SERIF, col, w=1.0))
        q = X(x, TG.YB - 0.78)
        sh.append(text(f'{key}.name', TG.DEBT[key][0], q[0], q[1], 13, SANS_SEMI, ds.INK, w=1.6))
    y100 = TG.y_of(100)
    a, b = X(TG.x_of(0) - 0.75, y100), X(TG.x_of(6) + 0.75, y100)
    sh.append(ln('flood', I(*a), I(*b), ds.LOW, W(2.4), 'dash'))
    sh.append(text('flood.l', '100% GDP', a[0] - 0.05, a[1] + 0.32, 13, SANS_SEMI, ds.LOW, 'r', w=1.4))
    sh.append(text('flood.l2', 'mực báo động', a[0] - 0.05, a[1] + 0.12, 10, SANS, ds.LOW, 'r', w=1.4))
    if idx == 4:
        for j, s in enumerate(('Nợ công toàn cầu dự kiến', 'vượt 100% GDP vào năm 2030:', 'mức chỉ từng thấy', 'sau Thế chiến II.')):
            sh.append(text(f'head{j}', s, L, -0.75 - j * 0.5, 23, SERIF, ds.INK, 'l', w=5.6))
        sh.append(text('head.src', 'IMF, Giám sát Tài khoá 10/2026', L, -2.75, 10, SANS, ds.SLATE, 'l', w=3.0))
    return [{'type': 'group', 'name': '!!s5', 'shapes': sh}]

# ------------------------------------------------------------------ S6 labels at the Anatomy anchors
S6_LABELS = [('fab', '1', 'Chế tạo tấm wafer', 'phòng sạch, quạt lọc, ray treo chở hộp wafer'),
             ('pkg', '2', 'Đóng gói chip', 'chip tăng tốc + chồng bộ nhớ HBM'),
             ('rack', '3', 'Lắp máy chủ', 'khay máy chủ vào tủ rack'),
             ('port', '4', 'Cảng container', 'cẩu bờ xếp hàng lên tàu')]

def s6_labels(anchors, anim=False, base_delay=0, period=3000):
    out = []
    for i, (k, n, a, b) in enumerate(S6_LABELS):
        x, y = anchors[k]
        y0 = max(1.75, y - 0.95)
        grp = [ln(f'lab.{k}.lead', [x, y], [x, y0 + 0.42], ds.HIGH, 0.9),
               {'type': 'ellipse', 'name': f'lab.{k}.dot', 'x': x - 0.04, 'y': y - 0.04, 'w': 0.08, 'h': 0.08, 'fill': ds.HIGH},
               {'type': 'ellipse', 'name': f'lab.{k}.ring', 'x': x - 0.13, 'y': y0 - 0.03, 'w': 0.26, 'h': 0.26, 'fill': ds.HIGH},
               {'type': 'text', 'name': f'lab.{k}.n', 'text': n, 'x': x - 0.13, 'y': y0 - 0.03, 'w': 0.26, 'h': 0.26, 'font': MONO, 'size': 10, 'color': ds.PAPER, 'align': 'c', 'anchor': 'm'},
               {'type': 'text', 'name': f'lab.{k}.t', 'text': a, 'x': x + 0.2, 'y': y0 - 0.06, 'w': 2.3, 'h': 0.3, 'font': SANS_SEMI, 'size': 13, 'color': ds.INK},
               {'type': 'text', 'name': f'lab.{k}.d', 'text': b, 'x': x + 0.2, 'y': y0 + 0.2, 'w': 2.3, 'h': 0.4, 'font': SANS, 'size': 10, 'color': ds.SLATE}]
        if k == 'pkg':       # keep clear of the rack label to its right
            for g in grp[4:]:
                g['w'] = 1.3
        if k == 'port':      # keep the last label inside the margin
            for g in grp[4:]:
                g['x'] = x - 2.5; g['align'] = 'r'
        g = {'type': 'group', 'name': f'lab.{k}', 'shapes': grp}
        if anim:
            g['anim'] = {'fx': 'rise', 'delay': base_delay + i * period, 'ms': 600}
        out.append(g)
    return out

def zoom_group(group, fx, fy, k, tx, ty):
    """camera push on a native group: scale every point by k about (fx, fy) and put that point at (tx, ty)."""
    def P(p):
        return [round(tx + (p[0] - fx) * k, 4), round(ty + (p[1] - fy) * k, 4)]
    out = {'type': 'group', 'name': group['name'], 'shapes': []}
    for s in group['shapes']:
        s2 = dict(s)
        if 'points' in s2:
            s2['points'] = [P(p) for p in s2['points']]
        elif s2.get('type') in ('ellipse', 'rect', 'text'):
            a = P([s2['x'], s2['y']])
            s2['x'], s2['y'] = a
            s2['w'] = round(s2['w'] * k, 4); s2['h'] = round(s2['h'] * k, 4)
        elif s2.get('type') == 'line':
            a, b = P([s2['x1'], s2['y1']]), P([s2['x2'], s2['y2']])
            s2['x1'], s2['y1'], s2['x2'], s2['y2'] = a + b
        out['shapes'].append(s2)
    return out
