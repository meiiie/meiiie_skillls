"""The flagship deck: "Khí áp 2026", the world economy in October 2026 (31 slides, Vietnamese).
  python3 make_deck.py && python3 $S/build_deck.py deck.json --out deck/khi-ap-2026.pptx && python3 postfix.py deck/khi-ap-2026.pptx
Every number traces to research/facts.md (IDs in the notes column of storyboard.md)."""
import json, math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'design')); sys.path.insert(0, str(ROOT / 'design' / 'films'))
import ds
import make_m1 as M
import natives as N
from make_m1 import header, film, SERIF, SANS, SANS_MED, SANS_SEMI, MONO
from shapely.geometry import shape, box as sbox

L, R = ds.MARGIN_X, ds.SLIDE_W - ds.MARGIN_X
NOTES = json.load(open(ROOT / 'script/notes.json')) if (ROOT / 'script/notes.json').exists() else {}

def T(name, s, x, y, w, h, size, font=SANS, color=ds.INK, align='l', anchor='t', anim=None, line=None, **kw):
    d = {'type': 'text', 'name': name, 'text': s, 'x': round(x, 3), 'y': round(y, 3), 'w': round(w, 3), 'h': round(h, 3),
         'font': font, 'size': size, 'color': color, 'align': align, 'anchor': anchor}
    if line:
        d['line'] = line
    if anim:
        d['anim'] = anim
    d.update(kw)
    return d

def Rc(name, x, y, w, h, fill, anim=None, **kw):
    d = dict({'type': 'rect', 'name': name, 'x': round(x, 3), 'y': round(y, 3), 'w': round(w, 3), 'h': round(h, 3), 'fill': fill}, **kw)
    if anim:
        d['anim'] = anim
    return d

def Ln(name, x1, y1, x2, y2, color=ds.INK, width=0.75, **kw):
    return dict({'type': 'line', 'name': name, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'color': color, 'width': width}, **kw)

def vn(x, d=1, plus=False):
    s = f'{abs(x):.{d}f}'.replace('.', ',')
    return ('−' if x < 0 else ('+' if plus and x > 0 else '')) + s

# ------------------------------------------------------------------ the map as a movable native object (cover, agenda, close)
G = json.load(open(ROOT / 'design/films/pressure_geom.json'))
def world_map(name, X, Y, Wd):
    """the 2026 pressure chart drawn into the window (X, Y, Wd); the same names on every slide so Morph moves it like a camera."""
    k = Wd / ds.FILM_W
    def P(q):
        return [round(X + (q[0] - ds.FILM_X) * k, 4), round(Y + (q[1] - ds.FILM_Y) * k, 4)]
    lw = lambda w: round(max(0.5, M.W(w) * max(k, 0.7)), 2)
    sh = []
    for i, r in enumerate(G['land']):
        for j, p in enumerate(M.clip_poly(r)):
            sh.append({'type': 'poly', 'name': f'{name}.land{i}_{j}', 'points': [P(q) for q in p], 'fill': ds.LAND})
    for i, c in enumerate(G['frames'][-1]):
        col = ds.LOW if c['level'] < 3.1 else ds.HIGH
        for j, seg in enumerate(M.clip_lines(c['pts'], c['closed'])):
            sh.append({'type': 'poly', 'name': f'{name}.iso{i}_{j}', 'points': [P(q) for q in seg], 'open': True,
                       'line_color': col, 'line_width': lw(1.8), 'line_alpha': 0.8})
    for i, c in enumerate(G['world_line']['2026']):
        for j, seg in enumerate(M.clip_lines(c['pts'], c['closed'])):
            sh.append({'type': 'poly', 'name': f'{name}.world{i}_{j}', 'points': [P(q) for q in seg], 'open': True,
                       'line_color': ds.INK, 'line_width': lw(4.0)})
    for ch, key, col in (('T', 'low', ds.LOW), ('C', 'high', ds.HIGH)):
        p = P(M.I(*G[key]['xy'])); s = max(18, round(58 * k)); w = s / 72 * 1.3
        sh.append({'type': 'text', 'name': f'{name}.{ch}', 'text': ch, 'x': round(p[0] - w / 2, 3), 'y': round(p[1] - w * 0.55, 3), 'w': round(w, 3), 'h': round(w, 3),
                   'font': SERIF, 'size': s, 'color': col, 'align': 'c', 'anchor': 'm'})
    return {'type': 'group', 'name': name, 'shapes': sh}

def paper_band(name, x, y, w, h):
    return Rc(name, x, y, w, h, ds.PAPER)

SRC = {
 'imf': 'Nguồn: IMF, Triển vọng Kinh tế Thế giới (WEO) 10/2026, Bảng A; số 2026–2027 là dự báo.',
 's1': M.SRC1, 's2': M.SRC2,
 'drum': 'Nguồn: IMF WEO 10/2026, Bảng A1 (tăng trưởng GDP thực thế giới, tính theo sức mua tương đương); 2026–2027 là dự báo. Nét nối các số năm, không phải số liệu theo tháng.',
 'oil': 'Nguồn: IMF WEO 10/2026, Bảng A9 (giá dầu giả định: bình quân Brent, Dubai Fateh, WTI); EIA, Triển vọng Năng lượng Ngắn hạn 6/10/2026 (Brent).',
 'cpi': 'Nguồn: IMF WEO 10/2026, trang tổng quan (lạm phát toàn cầu) và Bảng A5 (CPI bình quân năm 2026, dự báo). Mục tiêu 2%: Fed, BoJ (thông cáo 9/2026); ECB (chiến lược 2021).',
 'fm': 'Nguồn: IMF, blog Giám sát Tài khoá (Fiscal Monitor) 14/10/2026, Dabla-Norris & Valdés; IMF WEO 10/2026, Bảng A8.',
 'wto': 'Nguồn: WTO, Triển vọng và Thống kê Thương mại Toàn cầu, cập nhật 8/10/2026 (khối lượng xuất khẩu hàng hoá 2026, dự báo cập nhật).',
 'ai': 'Nguồn: WTO, cập nhật 8/10/2026. "Hàng hoá phục vụ AI": theo định nghĩa của WTO, ví dụ chip bán dẫn và máy chủ; tỷ trọng và mức tăng tính theo giá trị.',
 'chip': 'Hình minh hoạ một chuỗi điển hình, không phải nhà máy của doanh nghiệp nào. Số liệu: WTO 8/10/2026; Cục Thống kê, báo cáo 9 tháng 2026.',
 'vn': 'Nguồn: IMF WEO 10/2026 (Bảng A4); Ngân hàng Thế giới, Cập nhật Kinh tế Đông Á – Thái Bình Dương 6/10/2026; Cục Thống kê (Bộ Tài chính), báo cáo quý III và 9 tháng 2026.',
 'risk': 'Nguồn: IMF WEO 10/2026, trang tổng quan (rủi ro nghiêng về phía giảm; giả định xung đột không leo thang, thị trường năng lượng dần bình thường); OECD, báo cáo giữa kỳ 23/9/2026.',
}

def chrome_only(n, source):
    """the page chrome without the header (for full-bleed slides)"""
    return [T('!!source', source, L, 6.77, 10.9, 0.34, 10, SANS, ds.SLATE, line=1.0),
            T('!!pageno', f'{n:02d}', R - 0.8, 6.76, 0.8, 0.2, 10, MONO, ds.SLATE, 'r')]

# ================================================================== slides
S = []
def slide(id_, shapes, transition='fade', ms=900, scene=None, **kw):
    d = {'id': id_, 'scene': scene or id_, 'transition': transition, 'ms': ms, 'bg': ds.PAPER, 'shapes': shapes}
    d.update(kw)
    S.append(d)

# 01 cover
COVER_MAP = (-0.9, 0.2, 15.1)
slide('cover', [world_map('!!map', *COVER_MAP),
                paper_band('!!band', 0, 4.55, ds.SLIDE_W, 2.95),
                T('!!kicker', 'BẢN TIN KINH TẾ THẾ GIỚI · 21/10/2026', L, 4.8, 7.0, 0.3, 13, SANS_SEMI, ds.SLATE, anim={'fx': 'fade', 'ms': 500}),
                T('cover.title', 'Khí áp 2026', L - 0.04, 4.98, 7.6, 1.15, 58, SERIF, ds.INK, anim={'fx': 'type', 'by': 'letter', 'ms': 900, 'delay': 200}),
                T('cover.sub', 'Hai tâm áp, ba khí áp kế và một mực nước đang lên: kinh tế thế giới tháng 10/2026', L, 6.15, 7.6, 0.55, 17, SANS, ds.INK,
                  line=1.15, anim={'fx': 'float', 'ms': 700, 'delay': 900}),
                T('!!pageno', '01', R - 0.8, 6.76, 0.8, 0.2, 10, MONO, ds.SLATE, 'r')],
      transition='fade', ms=1200, scene='S0')

# 02 agenda: the map moves to the right like a camera; the bulletin items rise in order
AG = [('01', 'Hai tâm áp', 'tăng trưởng'), ('02', 'Nhiệt độ', 'năng lượng và lạm phát'), ('03', 'Khí áp kế', 'lãi suất'),
      ('04', 'Gió', 'thương mại và AI'), ('05', 'Mực nước', 'nợ công'), ('06', 'Việt Nam', 'trên bản đồ')]
ag = []
for i, (n, a, b) in enumerate(AG):
    y = 2.05 + i * 0.68
    ag += [T(f'ag.n{i}', n, L, y + 0.05, 0.6, 0.35, 13, MONO, ds.SLATE, anim={'fx': 'rise', 'delay': 300 + i * 140, 'ms': 500}),
           T(f'ag.a{i}', a, L + 0.65, y - 0.04, 3.2, 0.5, 23, SERIF, ds.INK, anim={'fx': 'rise', 'delay': 300 + i * 140, 'ms': 500}),
           T(f'ag.b{i}', b, L + 3.1, y + 0.04, 2.6, 0.4, 13, SANS, ds.SLATE, anim={'fx': 'rise', 'delay': 360 + i * 140, 'ms': 500}),
           Ln(f'ag.r{i}', L, y + 0.55, L + 5.6, y + 0.55, ds.RULE, 0.5, anim={'fx': 'stretch', 'delay': 250 + i * 140, 'ms': 500})]
slide('agenda', [world_map('!!map', 6.0, 1.75, 7.0)] + ag +
      [T('!!kicker', 'BẢN TIN HÔM NAY', L, 0.42, 7.0, 0.3, 13, SANS_SEMI, ds.SLATE),
       T('!!title', 'Đọc kinh tế thế giới như đọc bản đồ thời tiết', L, 0.7, ds.col_w(10), 0.6, 34, SERIF, ds.INK),
       Ln('!!rule', L, 1.5, R, 1.5, ds.INK, 0.75)] + chrome_only(2, 'Bản đồ: đường đồng mức tăng trưởng GDP 2026 nội suy từ IMF WEO 10/2026; Natural Earth.'),
      transition='morph', ms=1600, scene='S0')

# 03 the headline number
slide('hero', [world_map('!!map', 7.3, 4.25, 5.4),
               T('hero.n', '3,1%', L - 0.06, 1.6, 6.6, 2.6, 132, SERIF, ds.INK, anim={'fx': 'zoom', 'ms': 700}),
               T('hero.l', 'tăng trưởng GDP thực của thế giới năm 2026, theo dự báo của IMF', L, 4.25, 6.4, 0.9, 23, SERIF, ds.INK, line=1.1,
                 anim={'fx': 'rise', 'delay': 500, 'ms': 600}),
               T('hero.a', '2025', L, 5.3, 1.4, 0.3, 13, MONO, ds.SLATE), T('hero.av', '3,5%', L, 5.57, 1.6, 0.5, 23, SERIF, ds.INK),
               T('hero.b', '2026', L + 1.8, 5.3, 1.4, 0.3, 13, MONO, ds.LOW), T('hero.bv', '3,1%', L + 1.8, 5.57, 1.6, 0.5, 23, SERIF, ds.LOW),
               T('hero.c', '2027', L + 3.6, 5.3, 1.4, 0.3, 13, MONO, ds.SLATE), T('hero.cv', '3,4%', L + 3.6, 5.57, 1.6, 0.5, 23, SERIF, ds.INK),
               T('hero.k', 'Các nền kinh tế phát triển 2,1% · mới nổi và đang phát triển 3,7%', L, 6.15, 7.0, 0.35, 13, SANS, ds.SLATE,
                 anim={'fx': 'fade', 'delay': 1100, 'ms': 500})] +
      header('BỨC TRANH CHUNG', 'Thế giới chậm lại, nhưng chưa dừng', 'IMF hạ tăng trưởng toàn cầu năm 2026 xuống 3,1%, rồi dự báo hồi lên 3,4% năm 2027.', 3, SRC['imf']),
      transition='morph', ms=1400, scene='S0')

# 04-05 S1
slide('s1film', header('01 · HAI TÂM ÁP', M.T1[1], M.T1[2], 4, SRC['s1']) + [film('!!s1.film', 'assets/film/pressure.mp4')], transition={'type': 'push', 'dir': 'u'}, ms=900, scene='S1')
slide('s1native', header('01 · HAI TÂM ÁP · BẢN DỰNG SẴN', M.T1[1], M.T1[2], 5, SRC['s1']) + M.s1_native(), transition='fade', ms=700, scene='S1')

# 06 two forces
two = [Ln('two.mid', 6.67, 1.95, 6.67, 6.35, ds.RULE, 0.75),
       T('two.T', 'T', L, 1.6, 1.2, 1.9, 96, SERIF, ds.LOW, anim={'fx': 'drop', 'ms': 600}),
       T('two.Tk', 'LỰC THỨ NHẤT', L + 1.3, 2.0, 4.0, 0.3, 13, SANS_SEMI, ds.LOW),
       T('two.Tt', 'Giá năng lượng tăng vì chiến sự: một cú sốc cung tiêu cực', L + 1.3, 2.3, 4.6, 1.0, 23, SERIF, ds.INK, line=1.1),
       T('two.Td', 'IMF giả định giá dầu bình quân năm 2026 là 95,7 USD/thùng, cao hơn 41,3% so với 2025.', L + 1.3, 3.45, 4.6, 0.8, 13, SANS, ds.SLATE, line=1.2),
       T('two.C', 'C', 7.0, 1.6, 1.2, 1.9, 96, SERIF, ds.HIGH, anim={'fx': 'drop', 'ms': 600, 'delay': 700}),
       T('two.Ck', 'LỰC THỨ HAI', 8.3, 2.0, 4.0, 0.3, 13, SANS_SEMI, ds.HIGH, anim={'fx': 'fade', 'delay': 800}),
       T('two.Ct', 'Làn sóng công nghệ AI: một cú hích cầu tích cực', 8.3, 2.3, 4.4, 1.0, 23, SERIF, ds.INK, line=1.1, anim={'fx': 'fade', 'delay': 800}),
       T('two.Cd', 'Đài Loan (Trung Quốc) dự báo tăng 10,7%, Hàn Quốc 3,3% năm 2026, sau 8,8% và 1,1% năm 2025.', 8.3, 3.45, 4.4, 0.8, 13, SANS, ds.SLATE, line=1.2,
         anim={'fx': 'fade', 'delay': 800}),
       Rc('two.q', L, 4.75, R - L, 1.55, '#E6E2D8'),
       T('two.qt', '“Hai lực then chốt” định hình triển vọng năm nay, theo IMF: giá năng lượng tăng do chiến sự, và cơn bùng nổ công nghệ do AI dẫn dắt.',
         L + 0.3, 4.9, R - L - 0.6, 1.05, 23, SERIF, ds.INK, line=1.15, anim={'fx': 'split', 'delay': 1500, 'ms': 700}),
       T('two.qb', 'S. Tenreyro, họp báo WEO của IMF, Bangkok, 13–14/10/2026 (diễn ý)', L + 0.3, 5.98, 8.0, 0.3, 10, SANS, ds.SLATE, anim={'fx': 'fade', 'delay': 1700})]
slide('forces', header('01 · HAI TÂM ÁP', 'Hai lực kéo ngược chiều nhau', 'Một lực ghì tăng trưởng xuống, một lực đẩy lên. Năm 2026 là kết quả của cả hai.', 6,
                       'Nguồn: IMF, họp báo WEO 13–14/10/2026; IMF WEO 10/2026, Bảng A2 và A9.') + two, transition='fade', ms=900, scene='S1b')

# 07 growth by economy (lollipop bars)
ECON = [('Đài Loan (TQ)', 10.7), ('Việt Nam', 8.4), ('Ấn Độ', 7.0), ('Indonesia', 5.1), ('Trung Quốc', 4.5), ('Hàn Quốc', 3.3), ('Mỹ', 2.3), ('Brazil', 2.2),
        ('Anh', 1.3), ('Đức', 1.3), ('Khu vực euro', 1.1), ('Nhật Bản', 0.7), ('Pháp', 0.4), ('Ả Rập Xê Út', -3.3), ('Iran', -7.6), ('Qatar', -15.6),
        ('Iraq', -16.0), ('Kuwait', -16.7)]
ZX, PX = 7.65, 0.19
gr = []
for i, (n, v) in enumerate(ECON):
    y = 1.78 + i * 0.262
    col = ds.VN if n == 'Việt Nam' else (ds.HIGH if v >= 3.1 else ds.LOW)
    x0, x1 = sorted([ZX, ZX + v * PX])
    gr.append(T(f'g.n{i}', n, 1.2, y - 0.03, 2.2, 0.26, 13, SANS_MED if n == 'Việt Nam' else SANS, ds.INK, 'r'))
    an = {'fx': 'wipe', 'dir': 'l' if v > 0 else 'r', 'delay': 200 + i * 60, 'ms': 500}
    gr.append(Rc(f'g.b{i}', x0, y + 0.04, max(x1 - x0, 0.02), 0.15, col, anim=[an, {'fx': 'indicate', 'delay': 1900, 'ms': 800}] if n == 'Việt Nam' else an))
    vx = x1 + 0.08 if v > 0 else x0 - 0.68
    gr.append(T(f'g.v{i}', vn(v), vx, y - 0.04, 0.6, 0.27, 13, SANS_SEMI, col, 'l' if v > 0 else 'r', anim={'fx': 'fade', 'delay': 500 + i * 60}))
gr += [Ln('g.zero', ZX, 1.7, ZX, 6.55, ds.INK, 1.0),
       Ln('g.world', ZX + 3.1 * PX, 1.7, ZX + 3.1 * PX, 6.55, ds.INK, 0.75, dash='dash'),
       T('g.wl', 'thế giới 3,1', ZX + 3.1 * PX + 0.06, 6.38, 1.4, 0.22, 10, SANS_SEMI, ds.INK),
       T('g.note1', 'Việt Nam: IMF dự báo 8,4%; Ngân hàng Thế giới dự báo 7,4%.', 10.2, 2.1, 2.5, 0.8, 13, SANS, ds.INK, line=1.2),
       T('g.note2', 'Vùng Vịnh: sản lượng dầu khí bị gián đoạn kéo GDP của Kuwait, Iraq, Qatar giảm hơn 15%.', 10.2, 4.7, 2.5, 1.2, 13, SANS, ds.INK, line=1.2)]
slide('growth', header('01 · HAI TÂM ÁP', 'Châu Á dẫn đầu, vùng Vịnh tụt sâu', 'Tăng trưởng GDP thực năm 2026, dự báo IMF, %. Đường đứt: mức của thế giới.', 7, SRC['imf']) + gr,
      transition='fade', ms=800, scene='S1c')

# 08-09 S3 drum
T3 = ('01 · HAI TÂM ÁP · BĂNG GHI', 'Mười năm trên một băng ghi khí áp', 'Tăng trưởng thế giới 2018–2027, IMF: từ cú sập năm 2020 đến mức 3,1% năm 2026.')
slide('s3film', header(*T3, 8, SRC['drum']) + [film('!!s3.film', 'assets/film/drum.mp4')], transition={'type': 'wipe', 'dir': 'l'}, ms=800, scene='S3')
slide('s3native', header(T3[0] + ' · BẢN DỰNG SẴN', T3[1], T3[2], 9, SRC['drum']) + N.s3_native(), transition='fade', ms=700, scene='S3')

# 10-11 oil thermometer (Morph state change)
def thermo(name, x, y, h, v, vmax=140, step=10, label_every=20, merc=ds.LOW, extra=()):
    """a drawn thermometer; mercury name is fixed so Morph changes its height between slides"""
    sh = []
    bx, tw = x, 0.34
    ybot = y + h
    sh.append(Rc(f'{name}.tube', bx - tw / 2, y - 0.1, tw, h + 0.1, '#F7F5F0', line_color=ds.INK, line_width=1.0, radius=0.5))
    sh.append({'type': 'ellipse', 'name': f'{name}.bulb', 'x': bx - 0.32, 'y': ybot - 0.12, 'w': 0.64, 'h': 0.64, 'fill': merc, 'line_color': ds.INK, 'line_width': 1.0})
    mh = h * v / vmax
    sh.append(Rc(f'!!{name}.merc', bx - 0.08, ybot - mh, 0.16, mh + 0.1, merc))
    for t in range(0, vmax + 1, step):
        yy = ybot - h * t / vmax
        major = t % label_every == 0
        sh.append(Ln(f'{name}.t{t}', bx + tw / 2 + 0.02, yy, bx + tw / 2 + (0.2 if major else 0.1), yy, ds.INK, 0.75 if major else 0.5))
        if major:
            sh.append(T(f'{name}.n{t}', str(t), bx + tw / 2 + 0.24, yy - 0.11, 0.5, 0.22, 10, MONO, ds.SLATE))
    for (k, val, lab, col) in extra:
        yy = ybot - h * val / vmax
        sh.append(Ln(f'{name}.m{k}', bx - tw / 2 - 0.5, yy, bx - tw / 2 - 0.05, yy, col, 1.25))
        sh.append(T(f'{name}.ml{k}', lab, bx - tw / 2 - 3.2, yy - 0.16, 2.65, 0.32, 13, SANS_SEMI, col, 'r'))
    return sh

oil_hdr = ('02 · NHIỆT ĐỘ', 'Giá dầu: cơn sốt của năm 2026')
oil_a = thermo('oil', 4.6, 1.95, 4.3, 67.7, extra=[('a', 67.7, '2025: 67,7 USD/thùng', ds.INK)])
oil_a += [T('oil.big', '67,7', 6.1, 3.4, 4.0, 1.2, 58, SERIF, ds.INK), T('oil.bl', 'USD/thùng, giá dầu bình quân năm 2025 (IMF)', 6.1, 4.6, 5.5, 0.4, 13, SANS, ds.SLATE)]
slide('oil1', header(*oil_hdr, 'IMF giả định giá dầu bình quân của Brent, Dubai Fateh và WTI. Năm 2025: 67,7 USD/thùng.', 10, SRC['oil']) + oil_a,
      transition={'type': 'cover', 'dir': 'l'}, ms=900, scene='S4')
oil_b = thermo('oil', 4.6, 1.95, 4.3, 95.7, extra=[('a', 67.7, '2025: 67,7', ds.SLATE), ('b', 95.7, '2026: 95,7 (giả định IMF)', ds.LOW),
                                                   ('c', 114, 'Brent, bình quân tháng 9: 114', ds.INK), ('d', 131, 'Brent, đỉnh ngày 15/9: 131', ds.INK)])
oil_b += [T('oil.big', '+41,3%', 6.1, 3.4, 4.2, 1.2, 58, SERIF, ds.LOW), T('oil.bl', 'giá dầu bình quân năm 2026 so với 2025, theo giả định của IMF', 6.1, 4.6, 5.5, 0.4, 13, SANS, ds.SLATE),
          T('oil.c1', 'Sản lượng dầu thô Trung Đông bị đóng: 10,9 triệu thùng/ngày lúc đỉnh tháng 5, còn 4,8 triệu thùng/ngày trong tháng 9 (EIA).', 6.1, 5.05, 6.0, 0.6, 13, SANS, ds.INK, line=1.2,
            anim={'fx': 'rise', 'delay': 1400}),
          T('oil.c2', 'EIA dự báo Brent bình quân 105 USD/thùng trong quý IV/2026.', 6.1, 5.7, 6.0, 0.35, 13, SANS, ds.INK, anim={'fx': 'rise', 'delay': 1600})]
slide('oil2', header(*oil_hdr, 'Năm 2026, giá dầu giả định tăng 41,3%; Brent từng chạm 131 USD/thùng ngày 15/9.', 11, SRC['oil']) + oil_b, transition='morph', ms=1800, scene='S4')

# 12 inflation small multiples
CPI = [('Thế giới', 4.7, None), ('Mỹ', 3.6, 2.0), ('Khu vực euro', 3.1, 2.0), ('Nhật Bản', 2.0, 2.0), ('Mới nổi và đang phát triển', 5.7, None)]
inf = []
for i, (n, v, tgt) in enumerate(CPI):
    x = 1.6 + i * 2.45
    h, y0 = 3.2, 2.15
    ybot = y0 + h
    inf.append(Rc(f'cpi{i}.tube', x - 0.17, y0 - 0.1, 0.34, h + 0.1, '#F7F5F0', line_color=ds.INK, line_width=1.0, radius=0.5))
    inf.append({'type': 'ellipse', 'name': f'cpi{i}.bulb', 'x': x - 0.3, 'y': ybot - 0.12, 'w': 0.6, 'h': 0.6, 'fill': ds.LOW, 'line_color': ds.INK, 'line_width': 1.0})
    mh = h * v / 7.0
    inf.append(Rc(f'cpi{i}.merc', x - 0.08, ybot - mh, 0.16, mh + 0.1, ds.LOW, anim={'fx': 'wipe', 'dir': 'b', 'delay': 300 + i * 200, 'ms': 900}))
    for t in range(0, 8):
        yy = ybot - h * t / 7.0
        inf.append(Ln(f'cpi{i}.t{t}', x + 0.19, yy, x + 0.33, yy, ds.INK, 0.6))
        inf.append(T(f'cpi{i}.n{t}', str(t), x + 0.37, yy - 0.1, 0.3, 0.2, 10, MONO, ds.SLATE))
    if tgt:
        yy = ybot - h * tgt / 7.0
        inf.append(Ln(f'cpi{i}.tg', x - 0.45, yy, x + 0.17, yy, ds.HIGH, 1.5))
        inf.append(T(f'cpi{i}.tgl', 'mục tiêu 2', x - 1.25, yy - 0.12, 0.8, 0.24, 10, SANS_SEMI, ds.HIGH, 'r'))
    inf.append(T(f'cpi{i}.v', vn(v) + '%', x - 0.9, 6.0, 1.8, 0.45, 23, SERIF, ds.LOW, 'c', anim={'fx': 'zoom', 'delay': 900 + i * 200, 'ms': 400}))
    inf.append(T(f'cpi{i}.l', n, x - 1.1, 6.42, 2.2, 0.3, 13, SANS, ds.INK, 'c'))
slide('cpi', header('02 · NHIỆT ĐỘ', 'Lạm phát lại nóng lên', 'Lạm phát bình quân năm 2026, dự báo IMF, %. Vạch xanh: mục tiêu 2% của ngân hàng trung ương.', 12, SRC['cpi']) + inf,
      transition='fade', ms=800, scene='S5')

# 13-14 S2
slide('s2film', header('03 · KHÍ ÁP KẾ', M.T2[1], M.T2[2], 13, SRC['s2']) + [film('!!s2.film', 'assets/film/baro.mp4')], transition={'type': 'split', 'dir': 'out'}, ms=900, scene='S2')
slide('s2native', header('03 · KHÍ ÁP KẾ · BẢN DỰNG SẴN', M.T2[1], M.T2[2], 14, SRC['s2']) + M.s2_native(), transition='fade', ms=700, scene='S2')

# 15 yields and interest
yl = [T('y.big', '+1', L - 0.04, 1.6, 3.0, 2.6, 132, SERIF, ds.LOW, anim={'fx': 'type', 'by': 'letter', 'ms': 500}),
      T('y.unit', 'điểm %', L + 2.1, 3.0, 2.0, 0.5, 23, SERIF, ds.LOW),
      T('y.l', 'Lợi suất trái phiếu chính phủ kỳ hạn 10 năm, bình quân G7, đã tăng hơn 1 điểm % từ tháng 2 đến tháng 9/2026, lên mức cao nhất gần hai thập kỷ.',
        L, 4.3, 5.3, 1.3, 17, SANS, ds.INK, line=1.2, anim={'fx': 'rise', 'delay': 500}),
      Ln('y.mid', 6.67, 1.95, 6.67, 6.35, ds.RULE, 0.75),
      T('y.k', 'MỸ · CHI TRẢ LÃI, % GDP', 7.1, 1.95, 5.0, 0.3, 13, SANS_SEMI, ds.SLATE)]
for i, (lab, v, col) in enumerate([('trước đại dịch', 2.8, ds.SLATE), ('năm 2031 (dự báo)', 5.7, ds.LOW)]):
    y = 2.55 + i * 1.25
    yl += [T(f'y.bl{i}', lab, 7.1, y, 2.6, 0.3, 13, SANS, ds.INK),
           Rc(f'y.b{i}', 7.1, y + 0.36, v * 0.7, 0.42, col, anim={'fx': 'wipe', 'dir': 'l', 'delay': 800 + i * 500, 'ms': 800}),
           T(f'y.bv{i}', vn(v), 7.1 + v * 0.7 + 0.12, y + 0.3, 1.2, 0.5, 23, SERIF, col, anim={'fx': 'fade', 'delay': 1300 + i * 500})]
yl.append(T('y.note', 'Thâm hụt ngân sách của Mỹ năm 2026: 8,5% GDP (IMF).', 7.1, 5.25, 5.4, 0.35, 13, SANS, ds.INK))
slide('yields', header('03 · KHÍ ÁP KẾ', 'Giá của tiền vay đang lên', 'Lãi suất cao kéo theo chi phí nợ: áp lực dồn lên ngân sách các nước.', 15, SRC['fm']) + yl,
      transition='fade', ms=800, scene='S6')

# 16-17 S4 wind
T4 = ('04 · GIÓ', 'Gió mậu dịch đổi chiều', 'Khối lượng xuất khẩu hàng hoá năm 2026 theo khu vực, dự báo WTO: châu Á tăng 9,9%, Trung Đông giảm 17,2%.')
slide('s4film', header(*T4, 16, SRC['wto']) + [film('!!s4.film', 'assets/film/wind.mp4')], transition={'type': 'push', 'dir': 'u'}, ms=900, scene='S7')
slide('s4native', header(T4[0] + ' · BẢN DỰNG SẴN', T4[1], T4[2], 17, SRC['wto']) + N.s4_native(), transition='fade', ms=700, scene='S7')

# 18 waterfall of contributions
WF = [('Châu Á', 0.0, 4.0, ds.HIGH), ('Bắc Mỹ', 4.0, 4.5, ds.HIGH), ('Châu Âu', 4.5, 4.6, ds.HIGH), ('Phần còn lại của thế giới', 4.6, 3.9, ds.LOW)]
X0w, PW = 3.9, 1.45
wf = []
for i, (n, a, b, col) in enumerate(WF):
    y = 2.05 + i * 0.82
    x0, x1 = X0w + min(a, b) * PW, X0w + max(a, b) * PW
    wf += [T(f'wf.n{i}', n, L, y + 0.06, 3.1, 0.35, 13, SANS_MED, ds.INK, 'r'),
           Rc(f'wf.b{i}', x0, y, max(x1 - x0, 0.03), 0.5, col, anim={'fx': 'wipe', 'dir': 'l' if b > a else 'r', 'delay': 300 + i * 650, 'ms': 600}),
           T(f'wf.v{i}', vn(b - a, 1, True), x1 + 0.12 if b > a else x0 - 1.12, y + 0.0, 1.0, 0.5, 23, SERIF, col, 'l' if b > a else 'r', anim={'fx': 'float', 'delay': 600 + i * 650})]
    if i < 3:
        wf.append(Ln(f'wf.c{i}', X0w + b * PW, y + 0.5, X0w + b * PW, y + 0.82, ds.SLATE, 0.5, dash='dot'))
y = 2.05 + 4 * 0.82 + 0.1
wf += [Ln('wf.base', X0w, 1.85, X0w, y + 0.6, ds.INK, 1.0),
       T('wf.tn', 'Thương mại hàng hoá thế giới', L, y + 0.06, 3.1, 0.35, 13, SANS_SEMI, ds.INK, 'r'),
       Rc('wf.t', X0w, y, 3.9 * PW, 0.5, ds.INK, anim={'fx': 'wipe', 'dir': 'l', 'delay': 3000, 'ms': 700}),
       T('wf.tv', '3,9%', X0w + 3.9 * PW + 0.12, y, 1.2, 0.5, 23, SERIF, ds.INK, anim={'fx': 'fade', 'delay': 3400}),
       T('wf.note', 'Riêng châu Á đóng góp hơn 100% mức tăng; phần còn lại của thế giới cộng lại kéo xuống 0,7 điểm %.', L, 6.12, R - L, 0.4, 13, SANS, ds.INK)]
slide('waterfall', header('04 · GIÓ', 'Châu Á gánh cả mức tăng thương mại', 'Đóng góp vào mức tăng 3,9% của khối lượng thương mại hàng hoá thế giới năm 2026, điểm %.', 18, SRC['wto']) + wf,
      transition='fade', ms=800, scene='S8')

# 19 AI goods
ai = [T('ai.k1', 'TỶ TRỌNG TRONG THƯƠNG MẠI HÀNG HOÁ THẾ GIỚI, %', L, 1.9, 5.6, 0.3, 13, SANS_SEMI, ds.SLATE),
      T('ai.l1', '2016–2023', L, 2.45, 1.6, 0.3, 13, MONO, ds.SLATE),
      Rc('ai.r1', L + 1.7, 2.42, 7.0 * 0.22, 0.36, ds.ISOBAR, anim={'fx': 'wipe', 'dir': 'l', 'delay': 200}),
      Rc('ai.r1b', L + 1.7 + 7.0 * 0.22, 2.42, 1.0 * 0.22, 0.36, '#B7C2CF', anim={'fx': 'wipe', 'dir': 'l', 'delay': 500}),
      T('ai.v1', '7–8', L + 1.7 + 8.0 * 0.22 + 0.12, 2.38, 1.0, 0.45, 23, SERIF, ds.SLATE),
      T('ai.l2', '6T/2026', L, 3.15, 1.6, 0.3, 13, MONO, ds.HIGH),
      Rc('ai.r2', L + 1.7, 3.12, 14.8 * 0.22, 0.36, ds.HIGH, anim={'fx': 'wipe', 'dir': 'l', 'delay': 800, 'ms': 900}),
      T('ai.v2', '14,8', L + 1.7 + 14.8 * 0.22 + 0.12, 3.08, 1.2, 0.45, 23, SERIF, ds.HIGH, anim={'fx': 'fade', 'delay': 1500}),
      T('ai.n', 'Mười nước giao dịch nhiều nhất chiếm khoảng 85% kim ngạch xuất khẩu nhóm hàng này năm 2025.', L, 4.0, 5.6, 0.7, 13, SANS, ds.INK, line=1.2),
      Ln('ai.mid', 6.67, 1.95, 6.67, 6.35, ds.RULE, 0.75),
      T('ai.k2', 'MỨC TĂNG CỦA THƯƠNG MẠI HÀNG HOÁ PHỤC VỤ AI, %', 7.1, 1.9, 5.6, 0.3, 13, SANS_SEMI, ds.SLATE)]
for i, (lab, v) in enumerate([('2024', 16), ('2025', 31), ('6T/2026', 67)]):
    x = 7.5 + i * 1.75; base = 6.1; hh = v * 0.05
    ai += [Rc(f'ai.c{i}', x, base - hh, 1.0, hh, ds.HIGH if i == 2 else ds.ISOBAR, anim={'fx': 'wipe', 'dir': 'b', 'delay': 1800 + i * 400, 'ms': 700}),
           T(f'ai.cv{i}', str(v), x - 0.2, base - hh - 0.55, 1.4, 0.5, 23, SERIF, ds.HIGH if i == 2 else ds.INK, 'c', anim={'fx': 'drop', 'delay': 2200 + i * 400}),
           T(f'ai.cl{i}', lab, x - 0.3, base + 0.08, 1.6, 0.3, 13, MONO, ds.SLATE, 'c')]
ai.append(Ln('ai.base', 7.3, 6.1, 12.6, 6.1, ds.INK, 1.0))
ai.append(T('ai.hero', '47%', L, 4.75, 2.5, 1.15, 58, SERIF, ds.HIGH, anim={'fx': 'zoom', 'delay': 3000}))
ai.append(T('ai.herol', 'mức tăng thương mại hàng hoá toàn cầu 6 tháng đầu 2026 đến từ nhóm hàng này', L + 2.1, 5.0, 3.4, 0.8, 13, SANS, ds.INK, line=1.2, anim={'fx': 'fade', 'delay': 3200}))
slide('aigoods', header('04 · GIÓ', 'AI đã thành một mặt hàng lớn', 'Hàng hoá phục vụ AI, như chip bán dẫn và máy chủ, theo số liệu WTO (tính theo giá trị).', 19, SRC['ai']) + ai,
      transition='fade', ms=800, scene='S9')

# 20-22 S6 Anatomy
fj = json.load(open(ROOT / 'assets/film/chipline/film.json'))
ANCH = fj['anchors_in']
CHIP = json.load(open(ROOT / 'assets/film/chipline.shapes.json'))
T6 = ('04 · GIÓ · GIẢI PHẪU', 'Từ tấm wafer đến boong tàu', 'Một chuỗi điển hình của hàng hoá phục vụ AI: chế tạo, đóng gói, lắp máy chủ, xuất cảng. Hình minh hoạ.')
slide('s6film', header(*T6, 20, SRC['chip']) + [film('!!s6.film', 'assets/film/chipline.mp4')] + N.s6_labels(ANCH, anim=True, base_delay=150, period=3000),
      transition={'type': 'push', 'dir': 'u'}, ms=900, scene='S10')
cover_hdr = [Rc('!!hdrbg', 0, 0, ds.SLIDE_W, 1.56, ds.PAPER), Rc('!!ftbg', 0, 6.62, ds.SLIDE_W, 0.88, ds.PAPER)]
slide('s6native', [CHIP] + cover_hdr + header(T6[0] + ' · BẢN DỰNG SẴN', T6[1], T6[2], 21, SRC['chip']) + N.s6_labels(ANCH), transition='fade', ms=700, scene='S10')
px, py = ANCH['pkg']
zoom = N.zoom_group(CHIP, px, py + 0.35, 2.3, 4.2, 4.2)
zlab = [Rc('z.panel', 8.3, 1.56, 5.04, 5.1, ds.PAPER),
        T('z.k', 'TRẠM 2 · ĐÓNG GÓI', 8.55, 2.15, 4.0, 0.3, 13, SANS_SEMI, ds.HIGH),
        T('z.t', 'Chip tăng tốc AI và các chồng bộ nhớ HBM được gắn lên cùng một đế', 8.55, 2.5, 4.0, 1.5, 23, SERIF, ds.INK, line=1.1),
        T('z.d', 'Đây là loại hàng WTO xếp vào nhóm "phục vụ AI": chip bán dẫn, máy chủ. Năm 2025, mười nước giao dịch nhiều nhất chiếm khoảng 85% kim ngạch xuất khẩu của nhóm này.',
          8.55, 4.0, 4.0, 1.3, 13, SANS, ds.INK, line=1.2, anim={'fx': 'fade', 'delay': 1600}),
        T('z.vn', 'Việt Nam, 9 tháng 2026: nhập siêu 65,28 tỷ USD nhóm điện tử, máy tính và linh kiện.', 8.55, 5.45, 4.0, 0.8, 13, SANS_SEMI, ds.VN, line=1.2,
          anim={'fx': 'fade', 'delay': 2000})]
slide('s6zoom', [zoom] + cover_hdr + header(T6[0], 'Ống kính đẩy vào trạm đóng gói', 'Nơi chip tăng tốc và bộ nhớ được ghép thành một gói. Hình minh hoạ, không phải nhà máy thật.', 22, SRC['chip']) + zlab,
      transition='morph', ms=2000, scene='S10')

# 23-24 S5 tide
T5 = ('05 · MỰC NƯỚC', 'Mực nước nợ công', 'Nợ công gộp của bảy nền kinh tế, % GDP, IMF: 2024–2027 và năm 2031. Phần đỏ: vượt mốc 100% GDP.')
slide('s5film', header(*T5, 23, SRC['fm']) + [film('!!s5.film', 'assets/film/tide.mp4')], transition={'type': 'uncover', 'dir': 'u'}, ms=900, scene='S11')
slide('s5native', header(T5[0] + ' · BẢN DỰNG SẴN', T5[1], T5[2], 24, SRC['fm']) + N.s5_native(), transition='fade', ms=700, scene='S11')

# 25 fiscal cards
CARDS = [('3,3%', 'thâm hụt ngân sách cơ bản toàn cầu năm 2026, % GDP', 'Để giữ nợ không tăng ngay năm nay, con số cần là khoảng 2,6%.', ds.LOW),
         ('>15%', 'thu ngân sách của các nước thu nhập thấp dành để trả lãi', 'Giai đoạn 2011–2019 tỷ lệ này chỉ khoảng 9%.', ds.LOW),
         ('100%', 'nợ công toàn cầu so với GDP, dự kiến vượt vào năm 2030', 'Mức chỉ từng thấy sau Thế chiến II.', ds.INK)]
cd = []
for i, (v, a, b, col) in enumerate(CARDS):
    x = L + i * (ds.col_w(4) + ds.GUTTER)
    w = ds.col_w(4)
    an = {'fx': 'rise', 'delay': 200 + i * 300, 'ms': 600}
    cd += [Ln(f'cd.r{i}', x, 1.95, x + w, 1.95, col, 2.0),
           T(f'cd.v{i}', v, x, 2.15, w, 1.1, 58, SERIF, col, anim=an),
           T(f'cd.a{i}', a, x, 3.35, w - 0.2, 0.9, 17, SANS, ds.INK, line=1.15, anim=an),
           T(f'cd.b{i}', b, x, 4.45, w - 0.2, 0.9, 13, SANS, ds.SLATE, line=1.2, anim=an)]
cd.append(T('cd.q', '“Lợi suất trái phiếu chính phủ tăng làm ván cược tài khoá thêm lớn”: tiêu đề bài viết của IMF ngày 14/10/2026 (diễn ý).',
            L, 5.5, R - L, 0.8, 17, SERIF, ds.INK, line=1.15, anim={'fx': 'fade', 'delay': 1400}))
slide('fiscal', header('05 · MỰC NƯỚC', 'Ba vạch báo động của ngân sách', 'IMF, Giám sát Tài khoá 10/2026.', 25, SRC['fm']) + cd, transition='fade', ms=800, scene='S12')

# 26-27 Vietnam: a native map of the region, Morph moves the camera from the region to Vietnam's trade
C = json.load(open(ROOT / 'data/ne_50m_admin_0_countries.geojson'))
def region_map(name, cx, cy, s, lon0=106.0, lat0=16.0, bbox=(92, 0, 124, 30)):
    clipb = sbox(*bbox)
    k = math.cos(math.radians(lat0))
    out = []
    for f in C['features']:
        g = shape(f['geometry'])
        if not g.intersects(clipb):
            continue
        g = g.intersection(clipb)
        iso = f['properties'].get('ADM0_A3')
        polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
        for j, p in enumerate(polys):
            if p.area < 0.05:
                continue
            p = p.simplify(0.04)
            pts = [[round(cx + (x - lon0) * k * s, 4), round(cy - (y - lat0) * s, 4)] for x, y in p.exterior.coords]
            out.append({'type': 'poly', 'name': f'{name}.{iso}{j}', 'points': pts, 'fill': ds.VN if iso == 'VNM' else ds.LAND,
                        'line_color': ds.PAPER, 'line_width': 0.6})
    return {'type': 'group', 'name': name, 'shapes': out}

vn1 = [region_map('!!vnmap', 9.6, 4.1, 0.13),
       T('vn.k', 'TĂNG TRƯỞNG GDP CỦA VIỆT NAM NĂM 2026, DỰ BÁO', L, 1.9, 6.0, 0.3, 13, SANS_SEMI, ds.SLATE),
       T('vn.imf', '8,4%', L - 0.04, 2.2, 3.3, 1.1, 58, SERIF, ds.VN, anim={'fx': 'zoom', 'ms': 600}),
       T('vn.imfl', 'IMF, WEO 10/2026', L, 3.3, 3.0, 0.3, 13, SANS, ds.INK),
       T('vn.wb', '7,4%', L + 3.2, 2.2, 3.0, 1.1, 58, SERIF, ds.INK, anim={'fx': 'zoom', 'ms': 600, 'delay': 300}),
       T('vn.wbl', 'Ngân hàng Thế giới, 6/10/2026 (nâng 1,1 điểm %)', L + 3.2, 3.3, 3.2, 0.5, 13, SANS, ds.INK, line=1.15),
       Ln('vn.r', L, 4.0, 6.6, 4.0, ds.RULE, 0.75),
       T('vn.k2', 'ĐÃ ĐẠT, CỤC THỐNG KÊ', L, 4.2, 6.0, 0.3, 13, SANS_SEMI, ds.SLATE),
       T('vn.q3', '9,95%', L - 0.02, 4.5, 2.6, 0.7, 34, SERIF, ds.INK, anim={'fx': 'rise', 'delay': 900}),
       T('vn.q3l', 'GDP quý III/2026 so với cùng kỳ', L, 5.2, 2.8, 0.3, 13, SANS, ds.INK),
       T('vn.9m', '9,01%', L + 3.2, 4.5, 2.6, 0.7, 34, SERIF, ds.INK, anim={'fx': 'rise', 'delay': 1100}),
       T('vn.9ml', 'GDP 9 tháng 2026 (chưa phải số cả năm)', L + 3.2, 5.2, 3.2, 0.5, 13, SANS, ds.INK)]
slide('vn1', header('06 · VIỆT NAM', 'Việt Nam nằm trong vùng áp cao', 'Hai dự báo khác nhau một điểm %, nhưng cùng một hướng: Việt Nam thuộc nhóm tăng nhanh nhất châu Á năm 2026.', 26, SRC['vn']) + vn1,
      transition='reveal', ms=900, scene='S13')
# 27: Morph pulls the map back and left, trade arrows and a container on a path
vt = [region_map('!!vnmap', 3.6, 4.3, 0.105),
      T('vt.k', 'THƯƠNG MẠI HÀNG HOÁ 9 THÁNG 2026, TỶ USD', 6.4, 1.9, 6.3, 0.3, 13, SANS_SEMI, ds.SLATE),
      T('vt.x', '434,30', 6.4, 2.2, 3.0, 0.8, 34, SERIF, ds.HIGH), T('vt.xl', 'xuất khẩu, +24,5%', 6.4, 2.95, 3.0, 0.3, 13, SANS, ds.INK),
      T('vt.m', '453,72', 9.6, 2.2, 3.0, 0.8, 34, SERIF, ds.LOW), T('vt.ml', 'nhập khẩu, +36,7%', 9.6, 2.95, 3.0, 0.3, 13, SANS, ds.INK),
      T('vt.d', 'Nhập siêu 19,42 tỷ USD, trong đó riêng nhóm điện tử, máy tính và linh kiện nhập siêu 65,28 tỷ USD.', 6.4, 3.5, 6.2, 0.7, 13, SANS, ds.INK, line=1.2),
      Ln('vt.r', 6.4, 4.35, 12.7, 4.35, ds.RULE, 0.75),
      T('vt.us', 'Mỹ: thị trường xuất khẩu lớn nhất, 140,0 tỷ USD', 6.4, 4.55, 6.3, 0.35, 13, SANS_SEMI, ds.HIGH, anim={'fx': 'rise', 'delay': 1700}),
      T('vt.cn', 'Trung Quốc: thị trường nhập khẩu lớn nhất, 187,34 tỷ USD', 6.4, 4.95, 6.3, 0.35, 13, SANS_SEMI, ds.LOW, anim={'fx': 'rise', 'delay': 1900}),
      Ln('vt.a1', 3.95, 4.45, 6.25, 4.72, ds.HIGH, 2.25, arrow=True, anim={'fx': 'wipe', 'dir': 'l', 'delay': 1400}),
      Ln('vt.a2', 4.05, 3.0, 3.72, 3.95, ds.LOW, 2.25, arrow=True, anim={'fx': 'wipe', 'dir': 't', 'delay': 1600}),
      Rc('vt.box', 4.0, 4.45, 0.22, 0.12, ds.HIGH, anim=[{'fx': 'appear', 'delay': 2300}, {'fx': 'path', 'path': [[0, 0], [1.0, 0.12], [2.0, 0.25]], 'ms': 1600, 'delay': 2300, 'loop': True}]),
      T('vt.c', 'CPI 9 tháng tăng 4,52%; riêng tháng 9 tăng 5,08% so với cùng kỳ. IMF dự báo lạm phát năm 2026 của Việt Nam là 4,7%.', 6.4, 5.6, 6.2, 0.7, 13, SANS, ds.INK, line=1.2)]
slide('vn2', header('06 · VIỆT NAM', 'Nhập khẩu tăng nhanh hơn xuất khẩu', 'Việt Nam đứng giữa hai luồng gió: bán sang Mỹ, mua linh kiện từ Trung Quốc.', 27, SRC['vn']) + vt,
      transition='morph', ms=1800, scene='S13')

# 28 risks
RK = [('Xung đột leo thang', 'IMF giả định xung đột không leo thang thêm và thị trường năng lượng dần bình thường. Nếu sai, áp thấp sâu thêm.'),
      ('Kỳ vọng về AI bị đánh giá lại', 'Đầu tư AI ngày càng dựa vào vốn vay bên ngoài: một đợt điều chỉnh thị trường có thể bị khuếch đại (OECD).'),
      ('Căng thẳng thương mại trở lại', 'Gió mậu dịch vốn đã lệch về châu Á; thêm rào cản sẽ làm nó yếu đi.'),
      ('Ngân sách dễ tổn thương', 'Lợi suất trái phiếu và chi trả lãi tăng cùng lúc với nợ công.')]
rk = []
for i, (a, b) in enumerate(RK):
    x = L + (i % 2) * 6.17; y = 1.95 + (i // 2) * 2.25
    rk += [Rc(f'rk.bg{i}', x, y, 5.9, 2.0, '#E6E2D8', anim={'fx': 'fade', 'delay': 200 + i * 250}),
           Rc(f'rk.bar{i}', x, y, 0.08, 2.0, ds.LOW, anim={'fx': 'wipe', 'dir': 't', 'delay': 200 + i * 250}),
           T(f'rk.n{i}', f'0{i + 1}', x + 0.3, y + 0.22, 0.6, 0.3, 13, MONO, ds.LOW, anim={'fx': 'fade', 'delay': 300 + i * 250}),
           T(f'rk.a{i}', a, x + 0.9, y + 0.12, 4.8, 0.5, 23, SERIF, ds.INK, anim={'fx': 'fade', 'delay': 300 + i * 250}),
           T(f'rk.b{i}', b, x + 0.9, y + 0.7, 4.8, 1.1, 13, SANS, ds.INK, line=1.2, anim={'fx': 'fade', 'delay': 400 + i * 250})]
rk[1]['anim'] = [rk[1]['anim'], {'fx': 'pulse', 'delay': 1800, 'ms': 900}]
for j in range(4):
    rk[j * 5 + 3]['anim'] = {'fx': 'fly', 'dir': 'r', 'delay': 300 + j * 250, 'ms': 600}
slide('risks', header('CẢNH BÁO', 'Bốn cơn bão có thể đổi hướng dự báo', 'IMF đánh giá rủi ro nghiêng về phía giảm. Bốn rủi ro IMF nêu tên.', 28, SRC['risk']) + rk,
      transition={'type': 'push', 'dir': 'u'}, ms=900, scene='S14')

# 29 close (bookend: the cover map comes back)
TK = ['Tăng trưởng thế giới 3,1%: chậm lại, chưa dừng.', 'Năng lượng ghì xuống, AI đẩy lên; lãi suất và nợ là cái giá.', 'Việt Nam ở vùng áp cao, nhưng phụ thuộc cả hai luồng gió.']
cl = [world_map('!!map', *COVER_MAP), paper_band('!!band', 0, 3.85, ds.SLIDE_W, 3.65),
      T('!!kicker', 'BA ĐIỀU MANG VỀ', L, 4.05, 7.0, 0.3, 13, SANS_SEMI, ds.SLATE)]
for i, s in enumerate(TK):
    cl += [T(f'tk.n{i}', f'0{i + 1}', L, 4.45 + i * 0.66, 0.6, 0.4, 13, MONO, ds.LOW if i == 1 else ds.SLATE),
           T(f'tk.t{i}', s, L + 0.6, 4.4 + i * 0.66, 7.9, 0.55, 17, SERIF, ds.INK, anim={'fx': 'rise', 'delay': 400 + i * 450, 'ms': 600})]
cl += chrome_only(29, 'Dự báo của IMF, WTO, Ngân hàng Thế giới tháng 10/2026; số liệu Việt Nam của Cục Thống kê.')
slide('close', cl, transition='morph', ms=2000, scene='S15', bookend=True)

# 30 sources and credits
SRCS = ['IMF, World Economic Outlook 10/2026, Bảng A1–A10 và tổng quan', 'IMF, họp báo WEO, Bangkok 13–14/10/2026', 'IMF, blog Fiscal Monitor 14/10/2026',
        'OECD, Economic Outlook giữa kỳ 23/9/2026', 'WTO, Global Trade Outlook and Statistics, cập nhật 8/10/2026', 'Ngân hàng Thế giới, East Asia & Pacific Update 6/10/2026',
        'Fed 16/9/2026 · ECB 10/9/2026 · BoJ 18/9/2026 (thông cáo lãi suất)', 'EIA, Short-Term Energy Outlook 6/10/2026', 'Cục Thống kê (Bộ Tài chính), báo cáo quý III và 9 tháng 2026']
CRS = ['Bản đồ: Natural Earth (phạm vi công cộng), phép chiếu Equal Earth tâm 150°Đ', 'Phim tín hiệu: ManimGX (5 phim) và Anatomy iso-kit (MIT, 1 phim), dựng riêng cho bộ này',
       'Chữ: Source Serif Pro, IBM Plex Sans, IBM Plex Mono (SIL OFL)', 'Đường đồng mức là nội suy minh hoạ; dây chuyền chip là hình minh hoạ, không phải nhà máy thật',
       'Lãi suất thực là số suy ra (lãi suất điều hành trừ lạm phát dự báo)', 'Không dùng ảnh stock, không dùng hình do AI tạo']
sc = [T('sc.k1', 'NGUỒN SỐ LIỆU', L, 1.9, 6.0, 0.3, 13, SANS_SEMI, ds.SLATE), T('sc.k2', 'HÌNH ẢNH, CHỮ, CÔNG CỤ', 7.1, 1.9, 5.6, 0.3, 13, SANS_SEMI, ds.SLATE)]
for i, s in enumerate(SRCS):
    sc.append(T(f'sc.s{i}', s, L, 2.3 + i * 0.47, 6.1, 0.42, 13, SANS, ds.INK))
for i, s in enumerate(CRS):
    sc.append(T(f'sc.c{i}', s, 7.1, 2.3 + i * 0.6, 5.6, 0.55, 13, SANS, ds.INK, line=1.15))
slide('credits', header('NGUỒN', 'Nguồn và ghi công', 'Mọi con số trong bộ slide đều dẫn được về một trong các nguồn dưới đây.', 30, 'Bộ slide dựng ngày 21/10/2026.') + sc,
      transition='fade', ms=800, scene='S16')

def main():
    for s in S:
        if s['id'] in NOTES:
            s['notes'] = NOTES[s['id']]
    deck = {'style': str(ROOT / 'design/style.json'), 'title': 'Khí áp 2026 · Kinh tế thế giới tháng 10/2026', 'compat': 'morph', 'bg': ds.PAPER,
            'chrome': {'over': []}, 'slides': S}
    json.dump(deck, open(ROOT / 'deck.json', 'w'), ensure_ascii=False, indent=1)
    print(len(S), 'slides;', sum(len(json.dumps(s)) for s in S) // 1000, 'kB of shapes')

if __name__ == '__main__':
    main()
