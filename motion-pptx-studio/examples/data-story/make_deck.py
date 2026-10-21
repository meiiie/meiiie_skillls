"""A quarterly business review, 10 keyframes in the boardroom-data style.

The signature is the headline number itself: "+48%" opens the talk huge on the dark ground,
then shrinks into the top-right corner and stays there while the deck explains it, and
comes back at full size for the close. Bars grow, a list reveals one reason at a time, a
timeline walks the plan. "Quán Gió" is a fictional chain; every number is illustrative and
the source line says so.

  python3 make_deck.py && python3 ../../scripts/studio.py build .
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = 'Nguồn: số liệu minh hoạ cho ví dụ (Quán Gió là chuỗi giả định)'
BIG = {'type': 'stat', 'name': '!!k', 'col': [1, 7], 'y': 1.7, 'value': '+48%', 'label': 'doanh thu quý 3 so với quý 2',
       'color': 'accent2', 'label_color': '#B8C2CF'}
DARK_CHROME = {'!!source': {'color': '#8B97A8'}, '!!pageno': {'color': '#8B97A8'}, '!!foot': {'color': '#24324A'}}
CORNER = {'type': 'stat', 'name': '!!k', 'x': 10.35, 'y': 0.95, 'w': 2.1, 'value': '+48%', 'size': 30, 'label': 'quý 3',
          'color': 'accent'}
MONTHS = [{'label': 'T4', 'value': 410, 'display': '410'}, {'label': 'T5', 'value': 430, 'display': '430'},
          {'label': 'T6', 'value': 455, 'display': '455'}, {'label': 'T7', 'value': 540, 'display': '540'},
          {'label': 'T8', 'value': 640, 'display': '640'}, {'label': 'T9', 'value': 720, 'display': '720'}]
REASONS = [{'text': 'Thực đơn mùa thu', 'sub': 'Ba món mới chiếm 31% doanh thu tháng 9.'},
           {'text': 'Giao hàng trong 20 phút', 'sub': 'Đơn giao tăng gấp đôi khi bán kính giao hàng thu nhỏ.'},
           {'text': 'Thẻ thành viên', 'sub': 'Khách có thẻ quay lại 2,4 lần mỗi tháng.'}]
PLAN = [{'t': 'T10', 'label': 'Mở 2 quán', 'desc': 'Thủ Đức và Gò Vấp.'},
        {'t': 'T11', 'label': 'Ứng dụng đặt trước', 'desc': 'Bản thử với 500 thành viên.'},
        {'t': 'T12', 'label': 'Mùa lễ hội', 'desc': 'Thực đơn và quà tặng cuối năm.'}]


def head(kicker, title, col=(1, 8), y=1.0, **k):
    return {'type': 'heading', 'name': '!!h', 'col': list(col), 'y': y, 'kicker': kicker, 'title': title, **k}


slides = [
    {'id': 'open', 'scene': 'S1', 'bg': 'alt', 'ms': 1500, 'source': SRC, 'chrome_set': DARK_CHROME,
     'notes': 'Quý 3, Quán Gió tăng 48% doanh thu. [ngừng] Đây là cách chúng tôi làm được.',
     'shapes': [{**BIG, 'y': 2.0}, head('Báo cáo quý 3 · 2026', 'Quán Gió', col=(8, 5), y=2.25, sub='Một quý tăng trưởng nhanh nhất từ khi mở quán.',
                                      kick_style={'color': 'accent2'}, title_style={'color': '#FFFFFF'}, sub_style={'color': '#B8C2CF'})]},
    {'id': 'bars0', 'scene': 'S2', 'ms': 1800, 'source': SRC, 'notes': 'Doanh thu theo tháng, triệu đồng.',
     'chrome_set': {}, 'shapes': [CORNER, head('Doanh thu theo tháng', 'Tháng 7 là bước ngoặt', col=(1, 6), y=1.0,
                              body='Triệu đồng mỗi tháng, toàn chuỗi. Ba tháng cuối tăng nhanh hơn cả năm trước cộng lại.'),
                {'type': 'bars', 'name': '!!b', 'col': [7, 6], 'y': 1.85, 'h': 4.6, 'data': MONTHS, 'grow': 0.0}]},
    {'from': 'prev', 'id': 'bars1', 'ms': 1600, 'notes': 'Từ tháng 7, mỗi tháng thêm khoảng 90 triệu.',
     'set': {'!!b': {'grow': 1.0}}},
    {'from': 'prev', 'id': 'bars2', 'ms': 1300, 'notes': 'Tháng 9: 720 triệu, cao nhất từ trước đến nay.',
     'set': {'!!b': {'highlight': 5}}},
    {'id': 'why1', 'scene': 'S3', 'source': SRC, 'notes': 'Ba điều đã hiệu quả. Thứ nhất: thực đơn mùa thu.',
     'shapes': [CORNER, head('Vì sao tăng', 'Ba điều đã hiệu quả', col=(1, 6), y=1.0),
                {'type': 'stat', 'name': '!!r', 'col': [1, 5], 'y': 2.6, 'value': '31%', 'size': 120,
                 'label': 'doanh thu tháng 9 đến từ ba món mới.'},
                {'type': 'list', 'name': '!!l', 'col': [7, 6], 'y': 2.35, 'items': REASONS, 'reveal': 1, 'size': 22}]},
    {'from': 'prev', 'id': 'why2', 'morph': 'byChar', 'notes': 'Thứ hai: giao hàng nhanh hơn.',
     'set': {'!!l': {'reveal': 2, 'focus': 1}, '!!r': {'value': '2×', 'label': 'đơn giao khi bán kính giao hàng thu nhỏ.'}}},
    {'from': 'prev', 'id': 'why3', 'morph': 'byChar', 'notes': 'Thứ ba: thẻ thành viên.',
     'set': {'!!l': {'reveal': 3, 'focus': 2}, '!!r': {'value': '2,4', 'unit': 'lần', 'label': 'khách có thẻ quay lại mỗi tháng.'}}},
    {'id': 'voice', 'scene': 'S4', 'source': 'Ý kiến khách hàng, khảo sát tháng 9 (minh hoạ)', 'notes': 'Một khách quen nói thế này.',
     'shapes': [CORNER, {'type': 'quote', 'name': '!!q', 'col': [2, 9], 'y': 2.4, 'size': 40,
                         'text': 'Tôi đặt lúc bắt đầu họp, cà phê đến trước khi họp xong.', 'by': 'Chị Thu, khách hàng thân thiết'}]},
    {'id': 'plan1', 'scene': 'S5', 'source': SRC, 'notes': 'Quý 4: ba việc.',
     'shapes': [CORNER, head('Quý 4', 'Ba việc, theo thứ tự', col=(1, 8), y=1.0,
                             body='Mục tiêu: 1,1 tỷ đồng mỗi tháng vào tháng 12, giữ biên lợi nhuận như quý 3.'),
                {'type': 'timeline', 'name': '!!tl', 'x': 1.3, 'y': 4.1, 'w': 10.2, 'nodes': PLAN, 'active': 0, 'label_w': 3.2}]},
    {'from': 'prev', 'id': 'plan3', 'ms': 1600, 'notes': 'Và kết thúc năm bằng mùa lễ hội.', 'set': {'!!tl': {'active': 2}}},
    {'id': 'close', 'scene': 'S6', 'bg': 'alt', 'ms': 2000, 'source': SRC, 'chrome_set': DARK_CHROME, 'notes': 'Bốn mươi tám phần trăm. Quý sau, chúng tôi muốn giữ nhịp đó.',
     'shapes': [{**BIG, 'y': 2.0, 'label': 'và quý 4 giữ nhịp đó'},
                head('Kết', 'Cảm ơn', col=(8, 5), y=2.25, sub='Câu hỏi?', kick_style={'color': 'accent2'},
                     title_style={'color': '#FFFFFF'}, sub_style={'color': '#B8C2CF'})]},
]

deck = {'style': 'boardroom-data', 'title': 'Quán Gió · Quý 3', 'slides': slides}
(HERE / 'deck.json').write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding='utf-8')
print('deck.json:', len(slides), 'slides')
