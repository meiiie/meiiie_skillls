"""Worked example (v5.6): a genome-routed deck whose charts are `construct` drawings. Numbers are FICTIONAL.

Shows: a genome arc written as one string (split on →), chrome running head = the deck title and a
source line per slide, construct text parts coloured with "color", an open line ("closed": false), and
a lit part in navy ("lit": "accent2") because capacity is navy in this deck's colour logic.
Run build.sh (route -> genome compile -> directions -> this -> studio build)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
YEARS = ['2021', '2022', '2023', '2024', '2025']
TEU = [1.2, 1.4, 1.6, 1.9, 2.1]                       # facts 1.1-1.2 (fictional)


def bars(state=None, lit_capacity=False):
    parts = [{'id': 'base', 'kind': 'line', 'layer': 'base', 'points': [[0, 0], [10, 0]], 'line': 'faint', 'width': 1.0}]
    for i, (y, v) in enumerate(zip(YEARS, TEU)):
        x = 0.5 + i * 1.9
        parts.append({'id': f'b{i}', 'kind': 'rect', 'layer': 'structure', 'on': 'base', 'at': [x, -v * 2.2, 1.2, v * 2.2],
                      'fill': 'accent' if i == 4 and not lit_capacity else 'faint', 'lit': (i == 4) and not lit_capacity})
        parts.append({'id': f'y{i}', 'kind': 'text', 'layer': 'label', 'on': f'b{i}', 'text': y, 'at': [x, 0.15, 1.2, 0.3],
                      'role': 'label', 'color': 'muted', 'align': 'c'})
        parts.append({'id': f'v{i}', 'kind': 'text', 'layer': 'label', 'on': f'b{i}', 'text': f'{v:.1f}'.replace('.', ','),
                      'at': [x, -v * 2.2 - 0.75, 1.2, 0.35], 'role': 'cardtitle', 'color': 'head', 'align': 'c'})
    # capacity 2.4 M TEU (fact 1.3): the line the lender cares about; lit in navy on slide 3
    parts.append({'id': 'cap', 'kind': 'poly', 'layer': 'control', 'on': 'base', 'closed': False,
                  'points': [[0, -2.4 * 2.2], [10, -2.4 * 2.2]], 'line': 'muted', 'width': 2.0, 'dash': 'dash',
                  'lit': 'accent2' if lit_capacity else False})
    parts.append({'id': 'capl', 'kind': 'text', 'layer': 'label', 'on': 'cap', 'text': 'năng lực 2,4', 'at': [6.6, -2.4 * 2.2 - 0.45, 2.4, 0.35],
                  'role': 'label', 'color': 'accent2' if lit_capacity else 'muted'})
    return parts


def deck():
    title = {'shapes': [
        {'type': 'text', 'name': '!!kicker', 'role': 'kicker', 'text': 'SỐ LIỆU HƯ CẤU · VÍ DỤ V5.6', 'x': 0.9, 'y': 1.6, 'w': 8, 'h': 0.4},
        {'type': 'text', 'name': '!!title', 'role': 'title', 'text': 'Cảng Bến Mây sắp chạm trần năng lực', 'x': 0.9, 'y': 2.1, 'w': 9, 'h': 1.8},
        {'type': 'text', 'name': '!!num', 'role': 'numeral', 'text': '88%', 'x': 0.9, 'y': 4.1, 'w': 5, 'h': 2.0}]}
    chart = lambda state, lit, reveal: {'type': 'construct', 'name': 'teu', 'parts': bars(state, lit), 'x': 5.4, 'y': 1.5, 'w': 7.2,
                                        'h': 5.0, 'reveal': reveal, 'total_ms': 2600}
    s2 = {'source': 'Nguồn: số liệu hư cấu của ví dụ', 'shapes': [
        {'type': 'text', 'name': '!!title', 'role': 'title', 'text': 'Sản lượng tăng 75% sau 4 năm', 'x': 0.9, 'y': 1.0, 'w': 4.3, 'h': 2.7},
        {'type': 'text', 'name': '!!num', 'role': 'numeral', 'text': '2,1', 'x': 0.9, 'y': 3.8, 'w': 4.3, 'h': 1.9},
        {'type': 'text', 'name': '!!unit', 'role': 'caption', 'text': 'triệu TEU năm 2025', 'x': 0.9, 'y': 5.85, 'w': 4.3, 'h': 0.4},
        chart(None, False, True)]}
    s3 = {'source': 'Nguồn: số liệu hư cấu của ví dụ', 'shapes': [
        {'type': 'text', 'name': '!!title', 'role': 'title', 'text': 'Bến sắp đầy trước 2027', 'x': 0.9, 'y': 1.0, 'w': 4.3, 'h': 2.7},
        {'type': 'text', 'name': '!!num', 'role': 'numeral', 'text': '12%', 'x': 0.9, 'y': 3.8, 'w': 4.3, 'h': 1.9, 'color': 'accent2'},
        {'type': 'text', 'name': '!!unit', 'role': 'caption', 'text': 'năng lực còn trống', 'x': 0.9, 'y': 5.85, 'w': 4.3, 'h': 0.4},
        chart(None, True, ['cap', 'capl'])]}
    return {'title': 'Cảng Bến Mây (hư cấu)', 'style': 'design/style.json', 'compat': 'morph', 'slides': [
        dict(title, notes='Đây là ví dụ với số liệu hư cấu. [ngừng 1 giây] Cảng đang dùng 88% năng lực. [fact 1.4]'),
        dict(s2, notes='Sản lượng đi từ 1,2 lên 2,1 triệu TEU. [fact 1.1, 1.2]'),
        dict(s3, notes='Năng lực bến là 2,4 triệu TEU, nên chỉ còn khoảng 12% trống. [ngừng] Bến số 4 mới vào năm 2027. [fact 1.3]')]}


if __name__ == '__main__':
    (HERE / 'deck.json').write_text(json.dumps(deck(), ensure_ascii=False, indent=1), encoding='utf-8')
    print('wrote', HERE / 'deck.json')
