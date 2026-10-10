"""Ca trù, seven keyframes rebuilt with the v4 engine and the lacquer-heritage style pack.

Why a script and not hand-written JSON: the three strings are live lines locked to the
neck of the drawn instrument, so their coordinates are computed from the instrument box.
Change one number (where the instrument stands) and the strings follow on every slide.

  python make_deck.py            -> deck.json (then: python ../../scripts/studio.py build .)
Assets: python ../../scripts/make_assets_example.py --out assets (the gold-foil drawings).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NECK = (0.475, 0.5, 0.525)          # string x positions on the 600 x 2400 instrument canvas
TOP, BOTTOM = 284 / 2400, 2240 / 2400
WIDTHS = (2.0, 1.4, 0.9)            # graduated, as measured in the reference deck


def instrument(x, y, h, alpha=None):
    w = h / 4
    parts = [{'type': 'image', 'name': f'!!dd{p.title()}', 'path': f'assets/dd_{p}.png', 'x': x, 'y': y, 'w': w, 'h': h,
              'fit': 'stretch', **({'alpha': alpha} if alpha else {})} for p in ('body', 'neck', 'head')]
    return parts


def strings(xs, y1, y2, scale=1.0, color='lit', alpha=0.9):
    out = [{'type': 'line', 'name': f'!!str{i + 1}', 'x1': x, 'y1': y1, 'x2': x, 'y2': y2, 'color': color,
            'width': round(WIDTHS[i] * scale, 2), 'alpha': alpha} for i, x in enumerate(xs)]
    d = 0.14 * max(0.6, scale)
    out.append({'type': 'ellipse', 'name': '!!peg', 'x': round(xs[1] - d / 2, 3), 'y': round(y1 - d / 2, 3), 'w': d, 'h': d,
                'fill': color})
    return out


def strings_on(x, y, h):
    w = h / 4
    return strings([round(x + w * f, 3) for f in NECK], round(y + h * TOP, 3), round(y + h * BOTTOM, 3), scale=min(1.0, h / 5.8))


def medallion(x, y, s, alpha=None):
    return [{'type': 'image', 'name': f'!!med{k}', 'path': f'assets/med_{n}.png', 'x': x, 'y': y, 'w': s, 'h': s, 'fit': 'stretch',
             **({'alpha': alpha} if alpha else {})} for k, n in (('W', 'weave'), ('T', 'tally'), ('C', 'core'))]


PARK_DD = instrument(14.2, 0.6, 6.2)
PARK_MED = medallion(13.5, 3.1, 1.2)
MARGIN = strings([0.8, 0.93, 1.06], 0.95, 6.55)


def card(name, col, title, kicker, desc, icon, state='rest', dy=0.0):
    return {'type': 'card', 'name': name, 'col': col, 'y': round(2.75 + dy, 3), 'h': 3.95, 'title': title, 'kicker': kicker,
            'desc': desc, 'icon': icon, 'icon_h': 1.6, 'state': state}


CARDS = [
    ('!!role1', [1, 4], 'Ca nương', 'PHÁCH', 'Nữ, hát chính, tự gõ phách giữ nhịp.', 'assets/phach.png'),
    ('!!role2', [5, 4], 'Kép đàn', 'ĐÀN ĐÁY', 'Nam, đệm đàn đáy, đối đáp với giọng hát.', 'assets/dd_full.png'),
    ('!!role3', [9, 4], 'Quan viên', 'TRỐNG CHẦU', 'Người nghe, khen chê bằng tiếng trống chầu.', 'assets/trong_chau.png'),
]

slides = [
    {'id': 'k1', 'scene': 'S1', 'ms': 1500, 'notes': 'Có một âm thanh... [ngừng 2 giây]',
     'shapes': PARK_MED + PARK_DD + strings([6.667] * 3, 0.75, 5.95) + [
         {'type': 'text', 'name': '!!kick', 'role': 'kicker', 'text': 'Nghe thử một tiếng đàn', 'x': 3.67, 'y': 6.45, 'w': 6.0,
          'h': 0.32, 'align': 'c'}]},
    {'id': 'k2', 'scene': 'S1', 'ms': 1500, 'notes': 'Ba sợi dây. Một cây đàn.',
     'shapes': PARK_MED + PARK_DD + strings([6.53, 6.667, 6.80], 0.95, 5.95) + [
         {'type': 'text', 'name': '!!kick', 'role': 'kicker', 'text': 'Ba dây · một cây đàn', 'x': 3.67, 'y': 6.45, 'w': 6.0,
          'h': 0.32, 'align': 'c'}]},
    {'id': 'k3', 'scene': 'S1', 'ms': 2000, 'notes': 'Đó là đàn đáy, cây đàn của ca trù.',
     'shapes': medallion(9.15, 2.55, 3.0, alpha=0.6) + instrument(9.9, 0.75, 6.0) + strings_on(9.9, 0.75, 6.0) + [
         {'type': 'heading', 'name': '!!h', 'col': [1, 7], 'y': 1.6, 'kicker': 'Tiếng đàn đáy', 'title': 'Ca trù',
          'title_role': 'display', 'sub': 'Bạn đã từng nghe chưa?'}]},
    {'id': 'u1', 'scene': 'S2', 'bg': 'alt', 'ms': 1800,
     'notes': 'Năm 2009, UNESCO ghi danh ca trù vào Danh sách di sản văn hoá phi vật thể cần được bảo vệ khẩn cấp. '
              '(Nguồn: UNESCO, quyết định 4.COM 14.12, Abu Dhabi, 1/10/2009)',
     'shapes': medallion(7.35, 1.0, 5.3, alpha=0.9) + PARK_DD + MARGIN + [
         {'type': 'heading', 'name': '!!h', 'col': [1, 6], 'y': 1.25, 'kicker': 'UNESCO', 'title': '2009',
          'title_role': 'numeral', 'sub': 'Ca trù được ghi danh',
          'body': 'Vào Danh sách di sản văn hoá phi vật thể cần được bảo vệ khẩn cấp.'}]},
    {'id': 'r1', 'scene': 'S3', 'notes': 'Một buổi ca trù có ba thành phần.',
     'shapes': PARK_MED + PARK_DD + MARGIN + [
         {'type': 'heading', 'name': '!!h', 'col': [1, 12], 'y': 0.9, 'kicker': 'Ba thành phần biểu diễn',
          'title': 'Một tiếng hát, hai nhạc cụ đệm'}] + [card(*c) for c in CARDS]},
    {'id': 'r2', 'scene': 'S3', 'notes': 'Kép đàn: tiếng đàn đáy đối đáp với giọng hát.',
     'shapes': PARK_MED + PARK_DD + MARGIN + [
         {'type': 'heading', 'name': '!!h', 'col': [1, 12], 'y': 0.9, 'kicker': 'Vai 2 · kép đàn',
          'title': 'Tiếng đàn đáy đối đáp giọng hát'}]
     + [card(*CARDS[0], state='dim'), card(*CARDS[1], state='lit', dy=-0.25), card(*CARDS[2], state='dim')]},
    {'id': 'close', 'scene': 'S4', 'ms': 2000, 'notes': 'Nghe thì lạ, hiểu rồi thương. [ngừng]',
     'shapes': PARK_MED + PARK_DD + strings([6.667] * 3, 0.75, 5.35) + [
         {'type': 'text', 'name': '!!kick', 'role': 'quote', 'text': 'Nghe thì lạ, hiểu rồi thương', 'x': 2.67, 'y': 5.7, 'w': 8.0,
          'h': 0.75, 'align': 'c'}]},
]

deck = {'style': 'lacquer-heritage', 'title': 'Ca trù', 'slides': slides}
(HERE / 'deck.json').write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding='utf-8')
print('deck.json:', len(slides), 'slides')
