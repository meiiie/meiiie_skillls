"""Sample deck for motion-pptx-studio v5: "Một giọt cà phê phin" (16 slides, 5 styles, one per chapter)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
brew = json.loads((HERE / 'design' / 'brew-shapes.json').read_text(encoding='utf-8'))

SRC_FAO = 'Nguồn: FAOSTAT qua Wikipedia "Coffee production in Vietnam" [F3]'
SRC_EXP = 'Nguồn: Business Recorder / Bộ NN&PTNT (agro.gov.vn), số liệu xuất khẩu 2023–2024 [F4]'


# ------------------------------------------------------------- the phin, drawn (blueprint chapter)
BP = {'line': '#E8F1FF', 'fill': '#123A66', 'lit': '#FFB627', 'coffee': '#3B2416', 'milk': '#F2E3C6'}


def phin(cx, y_lid, y_press, y_ch, y_plate, y_cup, lit_press=False):
    """Five top-level groups (so each can morph and animate on its own)."""
    L = {'line_color': BP['line'], 'line_width': 1.5}
    lid = {'type': 'group', 'name': '!!lid', 'shapes': [
        {'type': 'rect', 'x': cx - 1.0, 'y': y_lid + 0.12, 'w': 2.0, 'h': 0.2, 'fill': BP['fill'], 'radius': 0.3, **L},
        {'type': 'rect', 'x': cx - 0.22, 'y': y_lid, 'w': 0.44, 'h': 0.14, 'fill': BP['fill'], 'radius': 0.2, **L}]}
    pc = BP['lit'] if lit_press else BP['fill']
    press = {'type': 'group', 'name': '!!press', 'shapes': [
        {'type': 'rect', 'x': cx - 0.07, 'y': y_press, 'w': 0.14, 'h': 0.42, 'fill': pc, **L},
        {'type': 'rect', 'x': cx - 0.82, 'y': y_press + 0.42, 'w': 1.64, 'h': 0.1, 'fill': pc, 'radius': 0.3, **L}]}
    holes = [{'type': 'ellipse', 'x': cx - 0.55 + i * 0.22, 'y': y_ch + 1.12, 'w': 0.06, 'h': 0.06, 'fill': BP['line']} for i in range(6)]
    chamber = {'type': 'group', 'name': '!!chamber', 'shapes': [
        {'type': 'poly', 'points': [[cx - 0.98, y_ch], [cx + 0.98, y_ch], [cx + 0.82, y_ch + 1.25], [cx - 0.82, y_ch + 1.25]],
         'fill': BP['fill'], **L},
        {'type': 'line', 'x1': cx - 0.86, 'y1': y_ch + 1.05, 'x2': cx + 0.86, 'y2': y_ch + 1.05, 'color': BP['line'], 'width': 0.75, 'dash': 'dash'}] + holes}
    plate = {'type': 'group', 'name': '!!plate', 'shapes': [
        {'type': 'rect', 'x': cx - 1.45, 'y': y_plate, 'w': 2.9, 'h': 0.12, 'fill': BP['fill'], 'radius': 0.4, **L},
        {'type': 'rect', 'x': cx - 0.7, 'y': y_plate + 0.12, 'w': 1.4, 'h': 0.08, 'fill': BP['fill'], **L}]}
    cup = {'type': 'group', 'name': '!!cup', 'shapes': [
        {'type': 'poly', 'points': [[cx - 0.85, y_cup + 1.05], [cx + 0.85, y_cup + 1.05], [cx + 0.75, y_cup + 1.4], [cx - 0.75, y_cup + 1.4]],
         'fill': BP['milk'], 'alpha': 0.9},
        {'type': 'poly', 'points': [[cx - 0.97, y_cup + 0.45], [cx + 0.97, y_cup + 0.45], [cx + 0.85, y_cup + 1.05], [cx - 0.85, y_cup + 1.05]],
         'fill': BP['coffee']},
        {'type': 'poly', 'points': [[cx - 1.1, y_cup], [cx + 1.1, y_cup], [cx + 0.75, y_cup + 1.4], [cx - 0.75, y_cup + 1.4]],
         'line_color': BP['line'], 'line_width': 1.5}]}
    return [lid, press, chamber, plate, cup]


def callout(name, x1, y, label, sub, delay):
    return [
        {'type': 'line', 'name': f'!!co-{name}', 'x1': x1, 'y1': y, 'x2': 7.05, 'y2': y, 'color': '#B4CAE8', 'width': 0.75, 'dash': 'dot',
         'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 450, 'delay': delay}},
        {'type': 'text', 'name': f'!!cl-{name}', 'text': [{'text': label, 'role': 'cardtitle'}, {'text': sub, 'color': 'muted'}], 'x': 7.2, 'y': y - 0.3, 'w': 5.2, 'h': 0.88, 'role': 'body',
         'anim': {'fx': 'fly', 'dir': 'r', 'ms': 500, 'delay': delay + 150}}]


slides = []

# =========================== CHAPTER 0 — kinetic type (hook)
slides.append({
    'id': 'cover', 'style': 'kinetic-type', 'scene': 'MỞ', 'transition': {'type': 'fade', 'ms': 900},
    'notes': 'Mỗi sáng, hàng triệu người Việt ngồi chờ một thứ rất chậm: những giọt cà phê rơi qua chiếc phin nhôm. '
             'Hôm nay mình kể câu chuyện của một giọt cà phê, từ năm 1857 đến ly sữa đá trên bàn bạn.',
    'chrome': False,
    'shapes': [
        {'type': 'text', 'name': '!!w1', 'text': 'Một giọt', 'role': 'display', 'size': 128, 'x': 0.9, 'y': 0.7, 'w': 11.5, 'h': 2.35,
         'anim': {'fx': 'type', 'ms': 500, 'step': 14}},
        {'type': 'text', 'name': '!!w2', 'text': 'cà phê phin', 'role': 'display', 'size': 128, 'color': 'accent', 'x': 0.9, 'y': 3.0, 'w': 11.5, 'h': 2.35,
         'anim': {'fx': 'type', 'ms': 500, 'step': 14, 'delay': 900}},
        {'type': 'text', 'name': '!!sub', 'text': 'Chuyện chậm rãi nhất trong ngày của người Việt — kể bằng sáu phong cách slide.',
         'role': 'subtitle', 'x': 0.9, 'y': 5.5, 'w': 8.2, 'h': 1.0, 'anim': {'fx': 'rise', 'delay': 2200}},
        {'type': 'ellipse', 'name': '!!drop', 'x': 11.6, 'y': 1.0, 'w': 0.42, 'h': 0.42, 'fill': 'accent',
         'anim': [{'fx': 'drop', 'ms': 700, 'delay': 2600}, {'fx': 'path', 'path': [[0, 0], [0, 4.6]], 'ms': 1600, 'loop': True, 'delay': 3400}]},
    ]})
slides.append({
    'id': 'y1857', 'style': 'kinetic-type', 'scene': 'MỞ', 'transition': {'type': 'cut'},
    'notes': 'Năm 1857. Đó là năm các nhà truyền giáo Pháp mang những cây cà phê đầu tiên vào Việt Nam [F1]. '
             'Hơn một thế kỷ rưỡi sau, Việt Nam đứng thứ hai thế giới về sản lượng [F3].',
    'source': 'Nguồn: Wikipedia "Coffee production in Vietnam" [F1]',
    'shapes': [
        {'type': 'text', 'name': '!!num', 'text': '1857', 'role': 'numeral', 'size': 240, 'x': 0.7, 'y': 0.5, 'w': 9.0, 'h': 4.0,
         'anim': {'fx': 'zoom', 'ms': 650}},
        {'type': 'text', 'name': '!!line', 'text': 'Năm những cây cà phê đầu tiên theo chân các nhà truyền giáo Pháp tới Việt Nam.',
         'role': 'subtitle', 'color': 'ink', 'x': 0.9, 'y': 4.75, 'w': 7.8, 'h': 1.0, 'anim': {'fx': 'word', 'ms': 400, 'step': 30, 'delay': 700}},
        {'type': 'rect', 'name': '!!bar', 'x': 0.9, 'y': 4.55, 'w': 2.2, 'h': 0.08, 'fill': 'accent', 'anim': {'fx': 'wipe', 'dir': 'l', 'delay': 400}},
    ]})
menu_items = [('01', 'Lịch sử', 'hist'), ('02', 'Giải phẫu chiếc phin', 'anat'), ('03', 'Những con số', 'num'), ('04', 'Ba ly đặc sản', 'rec')]
menu = []
for i, (n, t, target) in enumerate(menu_items):
    y = 1.55 + i * 1.22
    menu += [
        {'type': 'text', 'name': f'!!mn{i}', 'text': n, 'role': 'title', 'size': 54, 'color': 'accent', 'x': 0.9, 'y': y, 'w': 1.6, 'h': 1.1,
         'anim': {'fx': 'fly', 'dir': 'l', 'ms': 500, 'delay': i * 160}},
        {'type': 'text', 'name': f'!!mt{i}', 'text': t, 'role': 'title', 'size': 54, 'x': 2.6, 'y': y, 'w': 9.6, 'h': 1.1, 'link': target,
         'anim': {'fx': 'fly', 'dir': 'l', 'ms': 500, 'delay': i * 160 + 80}}]
slides.append({
    'id': 'menu', 'style': 'kinetic-type', 'scene': 'MỤC LỤC', 'transition': {'type': 'push', 'dir': 'u', 'ms': 700},
    'notes': 'Bốn chặng: lịch sử, giải phẫu chiếc phin, những con số, và ba ly đặc sản. Mỗi chặng một phong cách — '
             'bấm vào tên chặng là nhảy thẳng tới đó.',
    'shapes': [{'type': 'text', 'name': '!!k', 'text': 'Bốn chặng · bấm để nhảy', 'role': 'kicker', 'x': 0.9, 'y': 0.85, 'w': 6, 'h': 0.35}] + menu})

# =========================== CHAPTER 1 — lacquer heritage (history): a camera pan along a gold rail, 3 keyframes
YEARS = [('1857', 'Theo chân nhà truyền giáo', 'Những cây cà phê đầu tiên được các nhà truyền giáo Pháp mang vào Việt Nam.'),
         ('1888', 'Đồn điền đầu tiên', 'Ninh Bình, Quảng Bình.'),
         ('1920s', 'Lên cao nguyên', 'Đất đỏ Đắk Lắk thành vùng trồng lớn — ngày nay là thủ phủ cà phê.'),
         ('1946', 'Một ly thay sữa', 'Hà Nội thiếu sữa tươi; ông Nguyễn Văn Giảng đánh lòng đỏ trứng thay sữa: cà phê trứng.')]
STEP = 3.1        # rail spacing between years (in)
GOLD = '#C9A45C'


def hist_frame(k):
    sh = []
    off = 1.0 - k * STEP          # active year sits at x = 1.0
    sh.append({'type': 'line', 'name': '!!rail', 'x1': -1.0 + off - 1.0, 'y1': 6.05, 'x2': off + STEP * 4 + 2.0, 'y2': 6.05, 'color': GOLD, 'width': 0.75})
    for i, (y, t, d) in enumerate(YEARS):
        x = off + i * STEP
        on = i == k
        sh.append({'type': 'ellipse', 'name': f'!!knot{i}', 'x': x - (0.09 if on else 0.05), 'y': 6.05 - (0.09 if on else 0.05),
                   'w': 0.18 if on else 0.1, 'h': 0.18 if on else 0.1, 'fill': GOLD if (on or i < k) else '#140B08', 'line_color': GOLD, 'line_width': 0.75})
        sh.append({'type': 'text', 'name': f'!!yr{i}', 'text': y, 'role': 'label', 'x': x - 0.05, 'y': 6.22, 'w': 1.6, 'h': 0.32,
                   'color': GOLD if on else '#8C7A5E'})
        # the big numeral travels with the rail (a pan), only the active one is on stage
        sh.append({'type': 'text', 'name': f'!!big{i}', 'text': y, 'role': 'numeral', 'size': 210, 'color': GOLD,
                   'x': 0.75 + (i - k) * 13.0, 'y': 1.05, 'w': 6.4, 'h': 3.2, 'alpha': 1.0 if on else 0.0})
    y, t, d = YEARS[k]
    sh += [
        {'type': 'line', 'name': '!!div', 'x1': 7.55, 'y1': 1.35, 'x2': 7.55, 'y2': 4.9, 'color': GOLD, 'width': 0.5},
        {'type': 'text', 'name': '!!kick', 'text': 'Chặng 01 · Lịch sử', 'role': 'kicker', 'x': 7.95, 'y': 1.35, 'w': 4.6, 'h': 0.3},
        {'type': 'text', 'name': '!!tt', 'text': t, 'role': 'title', 'x': 7.95, 'y': 1.8, 'w': 4.6, 'h': 1.65},
        {'type': 'text', 'name': '!!dd', 'text': d, 'role': 'body', 'x': 7.95, 'y': 3.6, 'w': 4.4, 'h': 1.2,
         'anim': {'fx': 'fade', 'ms': 700, 'delay': 200}},
    ]
    return sh


HIST_NOTES = ['Hạt cà phê đi một đường dài. 1857: nó đến cùng các nhà truyền giáo Pháp [F1].',
              'Năm 1888 có những đồn điền đầu tiên ở Ninh Bình, Quảng Bình; đến những năm 1920 nó lên Tây Nguyên, Đắk Lắk — '
              'nơi bây giờ là thủ phủ cà phê [F1].',
              'Và 1946, giữa Hà Nội thiếu sữa, ông Nguyễn Văn Giảng đánh lòng đỏ trứng thay sữa: cà phê trứng ra đời [F5].']
for j, k in enumerate((0, 2, 3)):
    s = {'id': 'hist' if j == 0 else f'hist{j}', 'style': 'lacquer-heritage', 'scene': 'LỊCH SỬ',
         'transition': {'type': 'curtains', 'ms': 1800} if j == 0 else {'type': 'morph', 'ms': 1700},
         'notes': HIST_NOTES[j], 'source': 'Nguồn: Wikipedia "Coffee production in Vietnam" [F1], "Egg coffee" [F5]',
         'shapes': hist_frame(k)}
    if k == 2:
        s['shapes'][-1]['text'] = 'Đồn điền đầu tiên năm 1888 ở Ninh Bình, Quảng Bình; rồi đất đỏ Đắk Lắk thành thủ phủ cà phê.'
    slides.append(s)
slides.append({
    'id': 'milk', 'style': 'lacquer-heritage', 'scene': 'LỊCH SỬ', 'transition': {'type': 'fade', 'ms': 1200},
    'notes': 'Vì sao lại là sữa đặc? Vì ở xứ nhiệt đới thời đó sữa tươi hiếm và mau hỏng; sữa đặc có đường để được lâu [F2]. '
             'Một thứ thay thế bất đắc dĩ thành ra bản sắc.',
    'source': 'Nguồn: Wikipedia "Vietnamese iced coffee" [F2] · ảnh: Phương Huy, CC0',
    'chrome_set': {'!!pageno': {'color': '#FFFFFF'}},
    'shapes': [
        {'type': 'image', 'name': '!!photo', 'path': 'assets/phin_quochung.jpg', 'x': 6.9, 'y': 0.0, 'w': 6.433, 'h': 7.5, 'fit': 'cover',
         'focus': [0.5, 0.35], 'anim': [{'fx': 'fade', 'ms': 1000}, {'fx': 'grow', 'scale': 1.05, 'ms': 6000}]},
        {'type': 'line', 'name': '!!div', 'x1': 6.6, 'y1': 1.35, 'x2': 6.6, 'y2': 6.1, 'color': GOLD, 'width': 0.5},
        {'type': 'text', 'name': '!!kick', 'text': 'Vì sao sữa đặc?', 'role': 'kicker', 'x': 1.0, 'y': 1.35, 'w': 5.2, 'h': 0.3},
        {'type': 'text', 'name': '!!q', 'text': 'Thiếu sữa tươi, thừa sáng tạo.', 'role': 'display', 'size': 64, 'x': 1.0, 'y': 1.8, 'w': 5.3, 'h': 2.4,
         'anim': {'fx': 'word', 'ms': 600, 'step': 35, 'delay': 300}},
        {'type': 'text', 'name': '!!dd', 'text': 'Sữa tươi hiếm và mau hỏng ở xứ nóng; sữa đặc có đường để được lâu. Một lựa chọn bất đắc dĩ thành ra hương vị của cả nước.',
         'role': 'body', 'x': 1.0, 'y': 4.45, 'w': 4.9, 'h': 1.5, 'anim': {'fx': 'fade', 'ms': 800, 'delay': 1500}},
    ]})

# =========================== CHAPTER 2 — blueprint (anatomy, architecture animation)
asm = phin(3.6, 1.95, 2.05, 2.35, 3.62, 3.78)
for k, g in enumerate(asm):
    g['anim'] = {'fx': 'drop', 'ms': 600, 'delay': (4 - k) * 220}
slides.append({
    'id': 'anat', 'style': 'blueprint', 'scene': 'GIẢI PHẪU', 'transition': {'type': 'wipe', 'dir': 'r', 'ms': 900},
    'notes': 'Chiếc phin trông đơn giản: năm mảnh nhôm hay inox. Nhưng mỗi mảnh có một việc. Ta tháo nó ra.',
    'shapes': asm + [
        {'type': 'heading', 'name': '!!h', 'x': 7.0, 'y': 1.5, 'w': 5.4, 'kicker': 'Chặng 02 · Giải phẫu', 'title': 'Năm mảnh kim loại',
         'sub': 'Không điện, không áp suất: chỉ trọng lực và thời gian.', 'anim': {'fx': 'fade', 'ms': 700, 'delay': 1300}, 'stagger': 150},
        {'type': 'ellipse', 'name': 'drip', 'x': 3.55, 'y': 3.9, 'w': 0.1, 'h': 0.14, 'fill': '#FFB627',
         'anim': [{'fx': 'appear', 'delay': 1600}, {'fx': 'path', 'path': [[0, 0], [0, 0.75]], 'ms': 900, 'loop': True}]},
    ]})
exp = phin(3.6, 0.8, 1.55, 2.6, 4.3, 4.85, lit_press=True)
exp[1]['anim'] = {'fx': 'pulse', 'scale': 1.06, 'loop': True, 'delay': 1600}
slides.append({
    'id': 'anat2', 'style': 'blueprint', 'scene': 'GIẢI PHẪU', 'transition': {'type': 'morph', 'ms': 1600},
    'notes': 'Nắp giữ nhiệt. Nắp nén — mảnh quan trọng nhất — ép nhẹ lớp bột để nước thấm đều chứ không chảy tuột. '
             'Buồng lọc đục lỗ nhỏ, đĩa đế gác lên miệng ly, và dưới cùng là lớp sữa đặc chờ sẵn.',
    'shapes': exp + [
        {'type': 'text', 'name': '!!k', 'text': 'Tách lớp · mảnh vàng quyết định', 'role': 'kicker', 'x': 0.9, 'y': 6.62, 'w': 6, 'h': 0.3},
    ] + callout('lid', 4.75, 0.98, 'Nắp', 'giữ nhiệt trong lúc ủ', 300)
      + callout('press', 4.45, 2.02, 'Nắp nén', 'ép lớp bột, nước thấm đều', 500)
      + callout('ch', 4.65, 3.22, 'Buồng lọc', 'đáy đục lỗ, giữ bột lại', 700)
      + callout('plate', 5.1, 4.36, 'Đĩa đế', 'gác vững trên miệng ly', 900)
      + callout('cup', 4.6, 5.55, 'Ly', 'sữa đặc nằm sẵn dưới đáy', 1100)})
slides.append({
    'id': 'brew', 'style': 'blueprint', 'scene': 'GIẢI PHẪU', 'transition': {'type': 'fade', 'ms': 800},
    'notes': 'Đây là cả quy trình dưới dạng sơ đồ. Bột và nước gặp nhau trong phin, giọt cốt rơi xuống, gặp sữa đặc, thêm đá. '
             'Phần chuyển động này là một video dựng từ chính sơ đồ — slide sau là bản chỉnh sửa được.',
    'shapes': [
        {'type': 'heading', 'name': '!!h', 'col': [1, 10], 'y': 0.85, 'kicker': 'Sơ đồ quy trình · video', 'title': 'Một ly, sáu bước'},
        {'type': 'video', 'name': 'brewvid', 'path': 'assets/brew.mp4', 'poster': 'assets/brew.poster.png',
         'x': 0.9, 'y': 2.05, 'w': 11.533, 'h': 4.45, 'loop': False, 'mute': True},
    ]})
slides.append({
    'id': 'brew2', 'style': 'blueprint', 'scene': 'GIẢI PHẪU', 'transition': {'type': 'fade', 'ms': 600},
    'notes': 'Cùng sơ đồ đó, nhưng bằng hình khối thật trong PowerPoint: sửa chữ, đổi màu, kéo khối thoải mái. '
             'Những chấm vàng là đường đi của nước.',
    'shapes': [{'type': 'heading', 'name': '!!h', 'col': [1, 10], 'y': 0.85, 'kicker': 'Cùng sơ đồ · bản chỉnh sửa được', 'title': 'Một ly, sáu bước'}] + brew})

# =========================== CHAPTER 3 — swiss white-blue (numbers): cobalt field, a 10x10 unit grid, an index slope chart
COB, INK, FAINT, MUTE = '#1F4BFF', '#0B1B3F', '#D5DEF2', '#3F4B72'
grid_rows = []
for r in range(10):
    cells = []
    for c in range(10):
        idx = r * 10 + c
        filled = idx < 97
        cells.append({'type': 'rect', 'x': 7.6 + c * 0.38, 'y': 2.45 + r * 0.38, 'w': 0.29, 'h': 0.29,
                      'fill': COB if filled else '#FFFFFF', 'line_color': None if filled else MUTE, 'line_width': 1.0})
    grid_rows.append({'type': 'group', 'name': f'!!row{r}', 'shapes': cells, 'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 350, 'delay': 900 + r * 90}})
slides.append({
    'id': 'num', 'style': 'swiss-blue', 'scene': 'CON SỐ', 'transition': {'type': 'push', 'dir': 'l', 'ms': 800},
    'notes': 'Chuyển sang con số. Việt Nam là nước sản xuất cà phê lớn thứ hai thế giới, chỉ sau Brazil [F3]. '
             'Và gần như toàn bộ là Robusta — khoảng 97 trên 100 hạt [F3]: đắng, đậm, nhiều caffeine, rất hợp với sữa đặc.',
    'source': SRC_FAO, 'chrome': ['!!pageno'],
    'shapes': [
        {'type': 'rect', 'name': '!!field', 'x': 0, 'y': 0, 'w': 5.6, 'h': 7.5, 'fill': COB, 'anim': {'fx': 'wipe', 'dir': 't', 'ms': 600}},
        {'type': 'text', 'name': '!!k2', 'text': 'HẠNG THẾ GIỚI', 'role': 'kicker', 'color': '#FFFFFF', 'x': 0.9, 'y': 0.85, 'w': 4, 'h': 0.3},
        {'type': 'text', 'name': '!!two', 'text': '2', 'role': 'numeral', 'size': 380, 'color': '#FFFFFF', 'x': 0.6, 'y': 0.9, 'w': 4.6, 'h': 5.0,
         'anim': {'fx': 'fly', 'dir': 'b', 'ms': 800, 'delay': 300}},
        {'type': 'text', 'name': '!!twol', 'text': 'nước sản xuất cà phê lớn nhất, chỉ sau Brazil', 'role': 'subtitle', 'color': '#FFFFFF',
         'x': 0.9, 'y': 5.9, 'w': 4.2, 'h': 0.9, 'anim': {'fx': 'fade', 'delay': 700}},
        {'type': 'text', 'name': '!!k3', 'text': '100 hạt cà phê Việt Nam', 'role': 'kicker', 'x': 7.6, 'y': 0.85, 'w': 4.5, 'h': 0.3},
        {'type': 'text', 'name': '!!t3', 'text': '97 hạt là Robusta', 'role': 'title', 'size': 40, 'x': 7.6, 'y': 1.25, 'w': 5.3, 'h': 0.8},
    ] + grid_rows + [
        {'type': 'rect', 'name': '!!lg1', 'x': 7.6, 'y': 6.62, 'w': 0.18, 'h': 0.18, 'fill': COB},
        {'type': 'text', 'name': '!!lg1t', 'text': 'Robusta', 'role': 'caption', 'x': 7.85, 'y': 6.55, 'w': 1.6, 'h': 0.3},
        {'type': 'rect', 'name': '!!lg2', 'x': 9.5, 'y': 6.62, 'w': 0.18, 'h': 0.18, 'fill': '#FFFFFF', 'line_color': MUTE, 'line_width': 1.0},
        {'type': 'text', 'name': '!!lg2t', 'text': 'Arabica và loại khác', 'role': 'caption', 'x': 9.75, 'y': 6.55, 'w': 2.6, 'h': 0.3},
    ]})


def yv(v):  # index value -> y (in): 70 at 6.0, 140 at 1.9
    return round(6.0 - (v - 70) / 70 * 4.1, 3)


X1, X2 = 1.4, 7.9


def slope(show_usd):
    sh = [
        {'type': 'text', 'name': '!!k4', 'text': 'Xuất khẩu · chỉ số 2023 = 100', 'role': 'kicker', 'x': 0.9, 'y': 0.85, 'w': 6, 'h': 0.3},
        {'type': 'text', 'name': '!!t4', 'text': '…mà thu nhiều tiền hơn' if show_usd else 'Bán ít hạt hơn…', 'role': 'title',
         'x': 0.9, 'y': 1.2, 'w': 8, 'h': 0.85},
        {'type': 'line', 'name': '!!base', 'x1': X1 - 0.3, 'y1': yv(100), 'x2': X2 + 0.3, 'y2': yv(100), 'color': FAINT, 'width': 0.75, 'dash': 'dash'},
        {'type': 'text', 'name': '!!b100', 'text': '100', 'role': 'caption', 'x': 0.5, 'y': yv(100) - 0.15, 'w': 0.6, 'h': 0.3, 'align': 'r'},
        {'type': 'line', 'name': '!!ax1', 'x1': X1, 'y1': 2.3, 'x2': X1, 'y2': 6.25, 'color': FAINT, 'width': 0.75},
        {'type': 'line', 'name': '!!ax2', 'x1': X2, 'y1': 2.3, 'x2': X2, 'y2': 6.25, 'color': FAINT, 'width': 0.75},
        {'type': 'text', 'name': '!!xa', 'text': '2023', 'role': 'label', 'x': X1 - 0.5, 'y': 6.35, 'w': 1.0, 'h': 0.3, 'align': 'c'},
        {'type': 'text', 'name': '!!xb', 'text': '2024', 'role': 'label', 'x': X2 - 0.5, 'y': 6.35, 'w': 1.0, 'h': 0.3, 'align': 'c'},
        # tonnes: 1.62 -> 1.34 Mt = 82.7
        {'type': 'line', 'name': '!!lt', 'x1': X1, 'y1': yv(100), 'x2': X2, 'y2': yv(82.7), 'color': MUTE if show_usd else INK, 'width': 3.0,
         **({} if show_usd else {'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 900, 'delay': 300}})},
        {'type': 'ellipse', 'name': '!!dt', 'x': X2 - 0.11, 'y': yv(82.7) - 0.11, 'w': 0.22, 'h': 0.22, 'fill': MUTE if show_usd else INK},
        {'type': 'text', 'name': '!!vt', 'text': '−17%', 'role': 'numeral', 'size': 88, 'color': MUTE if show_usd else INK,
         'x': 8.6, 'y': yv(82.7) - 0.75, 'w': 3.9, 'h': 1.2, **({} if show_usd else {'anim': {'fx': 'zoom', 'delay': 1100}})},
        {'type': 'text', 'name': '!!vtl', 'text': 'khối lượng: 1,62 → 1,34 triệu tấn', 'role': 'caption', 'x': 8.65, 'y': yv(82.7) + 0.45, 'w': 3.9, 'h': 0.3},
    ]
    if show_usd:  # value: 4.24 -> 5.6 bn USD = 132
        sh += [
            {'type': 'line', 'name': '!!lu', 'x1': X1, 'y1': yv(100), 'x2': X2, 'y2': yv(132), 'color': COB, 'width': 4.5,
             'anim': {'fx': 'wipe', 'dir': 'l', 'ms': 900, 'delay': 200}},
            {'type': 'ellipse', 'name': '!!du', 'x': X2 - 0.14, 'y': yv(132) - 0.14, 'w': 0.28, 'h': 0.28, 'fill': COB,
             'anim': [{'fx': 'zoom', 'delay': 1000}, {'fx': 'pulse', 'scale': 1.35, 'loop': True}]},
            {'type': 'text', 'name': '!!vu', 'text': '+32%', 'role': 'numeral', 'size': 88, 'color': COB, 'x': 8.6, 'y': yv(132) - 0.75, 'w': 3.9, 'h': 1.2,
             'anim': {'fx': 'fly', 'dir': 'r', 'ms': 700, 'delay': 1100}},
            {'type': 'text', 'name': '!!vul', 'text': 'kim ngạch: 4,24 → 5,6 tỷ USD, kỷ lục', 'role': 'caption', 'x': 8.65, 'y': yv(132) + 0.45, 'w': 3.9, 'h': 0.3,
             'anim': {'fx': 'fade', 'delay': 1400}},
        ]
    return sh


slides.append({
    'id': 'exp0', 'style': 'swiss-blue', 'scene': 'CON SỐ', 'transition': {'type': 'wipe', 'dir': 'l', 'ms': 700},
    'notes': 'Năm 2024 có một nghịch lý. Lượng xuất khẩu giảm, từ 1,62 xuống 1,34 triệu tấn — giảm khoảng 17% [F4].',
    'source': SRC_EXP, 'shapes': slope(False)})
slides.append({
    'id': 'exp1', 'style': 'swiss-blue', 'scene': 'CON SỐ', 'transition': {'type': 'morph', 'ms': 1400},
    'notes': '…nhưng thu về nhiều tiền hơn bao giờ hết: kỷ lục 5,6 tỷ đô la, so với 4,24 tỷ năm trước — tăng khoảng 32% [F4]. '
             'Hai đường đi ngược chiều nhau: ít hạt hơn, giá cao hơn.',
    'source': SRC_EXP, 'shapes': slope(True)})

# =========================== CHAPTER 4 — neo-brutal (recipes): a sticker poster, then a numbered recipe card
TAG = lambda name, text, x, y, rot, delay, fill='#111111', color='#F3EEE3': [
    {'type': 'group', 'name': name, 'rot': rot, 'shapes': [
        {'type': 'rect', 'x': x, 'y': y, 'w': 2.6, 'h': 0.46, 'fill': fill},
        {'type': 'text', 'text': text, 'role': 'label', 'color': color, 'x': x, 'y': y + 0.06, 'w': 2.6, 'h': 0.34, 'align': 'c'}],
     'anim': {'fx': 'fly', 'dir': 'r', 'ms': 450, 'delay': delay}}]
poster = [
    {'type': 'text', 'name': '!!three', 'text': '3', 'role': 'display', 'size': 230, 'color': 'ink', 'x': 0.7, 'y': 0.6, 'w': 3.4, 'h': 3.3,
     'anim': {'fx': 'zoom', 'ms': 500}},
    {'type': 'text', 'name': '!!three-t', 'text': ['ly cà phê,', 'ba thành phố'], 'role': 'title', 'size': 30, 'color': '#D9431F', 'x': 0.9, 'y': 4.0, 'w': 3.6, 'h': 1.2,
     'anim': {'fx': 'fly', 'dir': 'l', 'delay': 300}},
    {'type': 'text', 'name': '!!three-k', 'text': 'Chặng 04 · Đặc sản', 'role': 'kicker', 'x': 0.9, 'y': 5.45, 'w': 3.4, 'h': 0.3},
    {'type': 'image', 'name': '!!pegg', 'path': 'assets/egg_coffee.jpg', 'x': 4.55, 'y': 0.95, 'w': 3.4, 'h': 4.3, 'fit': 'cover', 'focus': [0.5, 0.5],
     'rot': -5, 'line_color': 'ink', 'line_width': 3.0, 'shadow': {'blur': 0, 'dist': 9, 'dir': 45, 'color': '#111111', 'alpha': 1.0},
     'anim': {'fx': 'drop', 'ms': 600, 'delay': 500}},
    {'type': 'image', 'name': '!!pbac', 'path': 'assets/bac_xiu.jpg', 'x': 8.45, 'y': 1.75, 'w': 3.2, 'h': 4.3, 'fit': 'cover', 'focus': [0.5, 0.45],
     'rot': 4, 'line_color': 'ink', 'line_width': 3.0, 'shadow': {'blur': 0, 'dist': 9, 'dir': 45, 'color': '#111111', 'alpha': 1.0},
     'anim': {'fx': 'drop', 'ms': 600, 'delay': 800}},
    {'type': 'group', 'name': '!!salt', 'rot': -3, 'shapes': [
        {'type': 'rect', 'x': 5.6, 'y': 5.2, 'w': 3.3, 'h': 1.55, 'fill': '#C5F25A', 'line_color': 'ink', 'line_width': 3.0,
         'shadow': {'blur': 0, 'dist': 8, 'dir': 45, 'color': '#111111', 'alpha': 1.0}},
        {'type': 'text', 'text': 'MUỐI?!', 'role': 'display', 'size': 46, 'x': 5.6, 'y': 5.3, 'w': 3.3, 'h': 0.85, 'align': 'c'},
        {'type': 'text', 'text': 'cà phê muối · Huế · 2010', 'role': 'label', 'color': 'ink', 'x': 5.6, 'y': 6.17, 'w': 3.3, 'h': 0.3, 'align': 'c'}],
     'anim': [{'fx': 'zoom', 'ms': 450, 'delay': 1400}, {'fx': 'teeter', 'ms': 900, 'trigger': '!!salt'}]},
] + TAG('!!tegg', 'HÀ NỘI · 1946 · TRỨNG', 4.3, 0.6, -5, 1100) + TAG('!!tbac', 'CHỢ LỚN · BẠC XỈU', 9.2, 1.35, 4, 1250, '#FF5A36', '#111111')
slides.append({
    'id': 'rec', 'style': 'neo-brutal', 'scene': 'ĐẶC SẢN', 'transition': {'type': 'cover', 'dir': 'l', 'ms': 800}, 'chrome': ['!!badge', '!!pageno'],
    'notes': 'Chặng cuối: ba ly đặc sản. Cà phê trứng của Hà Nội, 1946 [F5]. Bạc xỉu của người Hoa Chợ Lớn — nhiều sữa, ít cà phê [F6]. '
             'Và cà phê muối của Huế, mới từ 2010 [F6]. Bấm vào ô muối, nó sẽ lắc — vì ai nghe lần đầu cũng lắc đầu.',
    'source': 'Nguồn: Wikipedia "Egg coffee" [F5], "Vietnamese iced coffee" [F6] · ảnh: Souradeep Dasgupta CC BY 4.0; Phương Huy CC BY-SA 4.0',
    'shapes': poster})
steps = [('Cốt', 'Pha một phin cốt thật đặc, giữ nóng.'), ('Đánh', 'Lòng đỏ trứng + sữa đặc, đánh đến khi bông và sánh.'),
         ('Ủ', 'Rót cốt vào tách, đặt tách trong bát nước nóng.'), ('Phủ', 'Phủ kem trứng lên trên. Ăn bằng thìa trước, uống sau.')]
st = [{'type': 'text', 'name': '!!rk', 'text': 'Công thức · cà phê trứng', 'role': 'kicker', 'x': 0.9, 'y': 0.85, 'w': 5, 'h': 0.3},
      {'type': 'text', 'name': '!!rt', 'text': 'Bốn bước, mười phút.', 'role': 'display', 'size': 60, 'x': 0.9, 'y': 1.2, 'w': 11.5, 'h': 1.3},
      {'type': 'line', 'name': '!!rr', 'x1': 0.9, 'y1': 2.65, 'x2': 12.433, 'y2': 2.65, 'color': 'ink', 'width': 2.5}]
for i, (verb, s) in enumerate(steps):
    x = 0.9 + i * 2.95
    hot = i == 3
    clk = i  # first step plays on arrival, then one click per step
    st += [{'type': 'group', 'name': f'!!step{i}', 'shapes': [
               {'type': 'rect', 'x': x, 'y': 3.0, 'w': 2.65, 'h': 3.85, 'fill': '#FF5A36' if hot else '#FFFFFF', 'line_color': 'ink', 'line_width': 2.5,
                'shadow': {'blur': 0, 'dist': 7, 'dir': 45, 'color': '#111111', 'alpha': 1.0}},
               {'type': 'text', 'text': f'0{i + 1}', 'role': 'display', 'size': 60, 'x': x + 0.2, 'y': 3.0, 'w': 2.3, 'h': 1.3},
               {'type': 'text', 'text': verb, 'role': 'title', 'size': 28, 'x': x + 0.22, 'y': 4.3, 'w': 2.3, 'h': 0.62},
               {'type': 'text', 'text': s, 'role': 'body', 'size': 15, 'x': x + 0.22, 'y': 5.05, 'w': 2.25, 'h': 1.7}],
            'anim': {'fx': 'drop', 'ms': 500, 'click': clk, 'delay': 200}}]
slides.append({
    'id': 'egg', 'style': 'neo-brutal', 'scene': 'ĐẶC SẢN', 'transition': {'type': 'push', 'dir': 'u', 'ms': 700},
    'notes': 'Muốn thử ở nhà? Bốn bước, mỗi cú bấm một bước. Phin cốt đặc. Đánh trứng với sữa đặc. Giữ tách nóng. Phủ kem — ăn bằng thìa trước. '
             'Đây là cách làm phổ biến; tỷ lệ mỗi quán một khác.',
    'bg': 'alt', 'shapes': st})

# =========================== CLOSE — kinetic again (circular)
slides.append({
    'id': 'close', 'style': 'kinetic-type', 'scene': 'KẾT', 'transition': {'type': 'fallover', 'ms': 1500},
    'notes': 'Một ly cà phê phin không vội được. Có lẽ đó là điều nó dạy ta: chậm lại, và đợi giọt cuối cùng. Cảm ơn các bạn.',
    'chrome': False,
    'shapes': [
        {'type': 'image', 'name': '!!bgp', 'path': 'assets/phin_hot.jpg', 'x': 0, 'y': 0, 'w': 13.333, 'h': 7.5, 'fit': 'cover', 'focus': [0.5, 0.42],
         'duotone': ['#070707', '#6B5E55'], 'anim': [{'fx': 'fade', 'ms': 1200}, {'fx': 'grow', 'scale': 1.04, 'ms': 7000}]},
        {'type': 'text', 'name': '!!w1', 'text': 'Chậm lại.', 'role': 'display', 'size': 128, 'x': 0.9, 'y': 0.7, 'w': 11.5, 'h': 2.35,
         'anim': {'fx': 'type', 'ms': 500, 'step': 14}},
        {'type': 'text', 'name': '!!w2', 'text': 'Đợi giọt cuối.', 'role': 'display', 'size': 128, 'color': 'accent', 'x': 0.9, 'y': 3.0, 'w': 11.5, 'h': 2.35,
         'anim': {'fx': 'type', 'ms': 500, 'step': 14, 'delay': 1100}},
        {'type': 'ellipse', 'name': '!!drop', 'x': 11.6, 'y': 5.45, 'w': 0.42, 'h': 0.42, 'fill': 'accent',
         'anim': [{'fx': 'zoom', 'delay': 2300}, {'fx': 'pulse', 'scale': 1.25, 'loop': True}]},
        {'type': 'text', 'name': '!!sub', 'text': 'Cảm ơn bạn đã ngồi chờ cùng.', 'role': 'subtitle', 'x': 0.9, 'y': 5.5, 'w': 8, 'h': 0.6,
         'anim': {'fx': 'fade', 'delay': 2600}},
    ]})
credits = ['[F1] Wikipedia, "Coffee production in Vietnam" — 1857, 1888, Tây Nguyên 1920s',
           '[F2] Wikipedia, "Vietnamese iced coffee" — sữa đặc thay sữa tươi',
           '[F3] FAOSTAT qua Wikipedia — hạng 2 thế giới, Robusta ~97%',
           '[F4] Business Recorder 40341258; agro.gov.vn — xuất khẩu 2023/2024',
           '[F5] Wikipedia, "Egg coffee" — Nguyễn Văn Giảng (1946 theo bài "Vietnamese iced coffee")',
           '[F6] Wikipedia, "Vietnamese iced coffee" — bạc xỉu, cà phê muối Huế 2010',
           'Ảnh: Phương Huy (CC0; CC BY-SA 4.0), Souradeep Dasgupta (CC BY 4.0), via Wikimedia Commons',
           'Phông chữ: 12 họ phông Google Fonts, tất cả SIL OFL (danh sách trong fonts/)']
slides.append({
    'id': 'credits', 'style': 'retro-terminal', 'scene': 'credits', 'transition': {'type': 'dissolve', 'ms': 900},
    'notes': 'Nguồn và giấy phép ảnh, phông chữ.',
    'shapes': [{'type': 'text', 'name': '!!t', 'text': 'cat sources.txt', 'role': 'title', 'size': 44, 'x': 0.9, 'y': 0.95, 'w': 8, 'h': 0.8,
                'anim': {'fx': 'type', 'ms': 300, 'step': 10}}]
              + [{'type': 'text', 'name': f'!!cr{i}', 'text': c, 'role': 'body', 'size': 13, 'x': 0.9, 'y': 1.95 + i * 0.6, 'w': 11.6, 'h': 0.52,
                  'anim': {'fx': 'appear', 'delay': 700 + i * 180}} for i, c in enumerate(credits)]})

deck = {'style': 'kinetic-type', 'title': 'Một giọt cà phê phin', 'motion': {'default_ms': 1100, 'stagger_ms': 140}, 'slides': slides}
# python make_deck.py safe|dual  -> deck-safe.json / deck-dual.json (no-Morph safe mode, compat.py)
import sys  # noqa: E402
COMPAT = sys.argv[1] if len(sys.argv) > 1 else 'morph'
if COMPAT != 'morph':
    deck['compat'] = COMPAT
(HERE / ('deck.json' if COMPAT == 'morph' else f'deck-{COMPAT}.json')).write_text(json.dumps(deck, ensure_ascii=False, indent=1), encoding='utf-8')
print(len(slides), 'slides')
