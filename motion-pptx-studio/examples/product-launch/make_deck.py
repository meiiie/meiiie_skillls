"""Product launch, 11 keyframes in the noir-product style: the cursor is the signature.

The amber block cursor opens the talk (a typed line), grows into a panel, becomes the frame
of the product, walks the three steps beside the screen and shrinks back into a cursor at the
end (a circular close). "Diều" is a fictional product; its numbers are illustrative and the
deck says so.

  python make_screens.py && python make_deck.py && python ../../scripts/studio.py build .
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CURSOR_REST = {'type': 'rect', 'name': '!!cursor', 'x': 12.05, 'y': 0.95, 'w': 0.16, 'h': 0.3, 'fill': 'accent'}
SCREEN_BOX = {'x': 6.55, 'y': 1.45, 'w': 5.9, 'h': 3.85}


def cursor(**k):
    return {**CURSOR_REST, **k}


def screen(img, device='browser', **box):
    b = {**SCREEN_BOX, **box}
    return {'type': 'screen', 'name': '!!screen', 'device': device, 'image': f'assets/{img}', 'url': 'dieu.example', **b}


PARK_SCREEN = screen('screen_live.png', x=14.0, y=1.45)
STEPS = [{'t': '01', 'label': 'Nghe', 'desc': 'Ghi lại cả cuộc họp, nhận ra ai đang nói.'},
         {'t': '02', 'label': 'Hiểu', 'desc': 'Tách quyết định, việc cần làm, câu hỏi mở.'},
         {'t': '03', 'label': 'Gửi', 'desc': 'Biên bản đến đúng người trước khi họ rời phòng.'}]
CARDS = [('!!f1', [1, 4], 'Tiếng Việt trước tiên', 'NGÔN NGỮ', 'Hiểu giọng ba miền và từ chuyên ngành của đội bạn.'),
         ('!!f2', [5, 4], 'Riêng tư mặc định', 'DỮ LIỆU', 'Bản ghi âm xoá sau 24 giờ, chỉ giữ biên bản.'),
         ('!!f3', [9, 4], 'Gửi đúng chỗ', 'TÍCH HỢP', 'Email, lịch và công cụ quản lý việc của đội.')]


def cards(lit=None):
    out = []
    for i, (n, col, t, k, d) in enumerate(CARDS):
        st = 'rest' if lit is None else ('lit' if i == lit else 'dim')
        out.append({'type': 'card', 'name': n, 'col': col, 'y': 3.05 - (0.2 if i == lit else 0), 'h': 3.2, 'title': t,
                    'kicker': k, 'desc': d, 'state': st})
    return out


ILLUS = 'Sản phẩm và số liệu minh hoạ cho ví dụ'
DATA = [{'label': 'Ghi tay', 'value': 38, 'display': '38 phút'}, {'label': 'Với Diều', 'value': 2, 'display': '2 phút'}]

slides = [
    {'id': 'type', 'scene': 'S1', 'ms': 1400, 'notes': 'Cuộc họp vừa kết thúc. [ngừng] Ai đang giữ biên bản?',
     'shapes': [cursor(x=8.32, y=3.42, w=0.22, h=0.5), PARK_SCREEN,
                {'type': 'text', 'name': '!!line', 'role': 'title', 'text': 'Cuộc họp vừa kết thúc.', 'x': 1.0, 'y': 3.3,
                 'w': 7.2, 'h': 0.75, 'align': 'r'}]},
    {'id': 'panel', 'scene': 'S1', 'ms': 1600, 'notes': '47 phút, ba quyết định, và không ai ghi lại.',
     'shapes': [cursor(**SCREEN_BOX, fill='surface', line_color='accent', line_width=1.5, radius=0.04), PARK_SCREEN,
                {'type': 'heading', 'name': '!!h', 'col': [1, 5], 'y': 1.6, 'kicker': '47 phút · 5 người',
                 'title': 'Ai đang giữ biên bản?', 'body': '3 quyết định. 2 việc cần làm. 0 dòng ghi chép.'}]},
    {'id': 'reveal', 'scene': 'S1', 'ms': 1800, 'notes': 'Diều viết biên bản ngay trong lúc mọi người nói.',
     'shapes': [cursor(x=6.55, y=1.1, w=0.16, h=0.16), screen('screen_live.png'),
                {'type': 'heading', 'name': '!!h', 'col': [1, 5], 'y': 1.6, 'kicker': 'Giới thiệu', 'title': 'Diều',
                 'title_role': 'display', 'sub': 'Biên bản họp tự viết, ngay trong lúc bạn nói.'}]},
    {'id': 'cost0', 'scene': 'S2', 'notes': 'Mỗi tuần, một trưởng nhóm mất khoảng năm giờ để ghi và gửi biên bản. (minh hoạ)',
     'shapes': [cursor(), screen('screen_live.png', x=14.0),
                {'type': 'stat', 'name': '!!k', 'col': [1, 5], 'y': 1.45, 'value': '5', 'unit': 'giờ / tuần',
                 'label': 'để ghi, chép lại và gửi biên bản họp.', 'src': ILLUS},
                {'type': 'bars', 'name': '!!b', 'col': [7, 5], 'y': 1.3, 'h': 4.9, 'data': DATA, 'grow': 0.0}]},
    {'from': 'prev', 'id': 'cost1', 'ms': 1500, 'notes': 'Ghi tay mất 38 phút mỗi cuộc họp. Với Diều: hai phút để đọc lại.',
     'set': {'!!b': {'grow': 1.0, 'highlight': 1}}},
    {'id': 'how1', 'scene': 'S3', 'notes': 'Bước một: Diều nghe.',
     'shapes': [cursor(x=6.55, y=1.1, w=0.16, h=0.16), screen('screen_live.png'),
                {'type': 'heading', 'name': '!!h', 'col': [1, 5], 'y': 1.45, 'kicker': 'Cách hoạt động',
                 'title': 'Ba bước, không ai phải ghi'},
                {'type': 'timeline', 'name': '!!tl', 'x': 1.05, 'y': 4.35, 'w': 4.1, 'nodes': STEPS, 'active': 0, 'label_w': 1.75}]},
    {'from': 'prev', 'id': 'how2', 'notes': 'Bước hai: Diều hiểu điều gì đã được quyết định.',
     'set': {'!!tl': {'active': 1}, '!!screen': {'image': 'assets/screen_summary.png'}}},
    {'from': 'prev', 'id': 'how3', 'ms': 1600, 'notes': 'Bước ba: biên bản đến điện thoại của mọi người.',
     'set': {'!!tl': {'active': 2}, '!!screen': {'image': 'assets/screen_phone.png', 'device': 'phone',
                                                 'x': 8.6, 'y': 0.95, 'w': 2.55, 'h': 5.5}},
     'add': []},
    {'id': 'why1', 'scene': 'S4', 'notes': 'Vì sao các đội giữ Diều lại.',
     'shapes': [cursor(), screen('screen_phone.png', device='phone', x=14.0, y=0.95, w=2.55, h=5.5),
                {'type': 'heading', 'name': '!!h', 'col': [1, 12], 'y': 1.2, 'kicker': 'Vì sao giữ lại',
                 'title': 'Viết cho đội Việt, giữ kín điều cần kín'}] + cards()},
    {'from': 'prev', 'id': 'why2', 'notes': 'Riêng tư là điều đầu tiên khách hàng hỏi.',
     'set': {'!!f1': {'state': 'dim'}, '!!f2': {'state': 'lit', 'y': 2.85}, '!!f3': {'state': 'dim'}}},
    {'id': 'close', 'scene': 'S5', 'ms': 2000, 'notes': 'Cuộc họp tiếp theo, để Diều ghi. [ngừng] Cảm ơn.',
     'shapes': [cursor(x=9.55, y=3.42, w=0.22, h=0.5), screen('screen_phone.png', device='phone', x=14.0, y=0.95, w=2.55, h=5.5),
                {'type': 'text', 'name': '!!line', 'role': 'title', 'text': 'Lần họp tới, để Diều ghi.', 'x': 0.9,
                 'y': 3.3, 'w': 8.55, 'h': 0.75, 'align': 'r'}]},
]

deck = {'style': 'noir-product', 'title': 'Diều', 'slides': slides}
(HERE / 'deck.json').write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding='utf-8')
print('deck.json:', len(slides), 'slides')
