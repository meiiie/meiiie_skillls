"""Draw the (fictional) product's screens for the example deck.

A product deck lives or dies by its screens. When the product is real, use real screenshots
(with version labels). This example product, "Diều", does not exist, so its three screens are
drawn here in the style pack's colours and fonts, and the deck labels them as illustrations.

  python make_screens.py   -> assets/screen_live.png, screen_summary.png, screen_phone.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'scripts'))
import typeset  # noqa: E402

BG, PANEL, CARD, LINE = (13, 15, 18), (20, 23, 28), (28, 32, 38), (44, 49, 57)
INK, MUTED, AMBER, CYAN = (233, 236, 241), (142, 150, 163), (255, 176, 32), (110, 231, 249)


def font(family, size, bold=False):
    path = typeset.font_file(family, bold) or typeset.font_file('DejaVu Sans', bold)
    return ImageFont.truetype(path, size)


TEXT = lambda s, b=False: font('Be Vietnam Pro', s, b)  # noqa: E731
MONO = lambda s, b=False: font('JetBrains Mono', s, b)  # noqa: E731


def rounded(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def chrome(d, w, title):
    d.rectangle([0, 0, w, 64], fill=PANEL)
    for i, c in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse([24 + i * 30, 22, 44 + i * 30, 42], fill=c)
    d.text((w // 2, 32), title, font=TEXT(24), fill=MUTED, anchor='mm')


def sidebar(d, h, active):
    d.rectangle([0, 64, 420, h], fill=PANEL)
    d.text((40, 110), 'Diều', font=TEXT(40, True), fill=INK)
    rounded(d, [300, 108, 330, 138], 4, fill=AMBER)
    d.text((40, 190), 'CUỘC HỌP', font=MONO(20, True), fill=MUTED)
    items = ['Họp sản phẩm · 10/10', 'Giao ban thứ Hai', 'Phỏng vấn khách hàng', 'Review thiết kế', 'Kế hoạch quý 4']
    for i, it in enumerate(items):
        y = 240 + i * 78
        if i == active:
            rounded(d, [24, y - 14, 396, y + 50], 12, fill=CARD)
            d.rectangle([24, y - 14, 30, y + 50], fill=AMBER)
        d.text((48, y), it, font=TEXT(26, i == active), fill=INK if i == active else MUTED)
        d.text((48, y + 32), ['47 phút', '32 phút', '58 phút', '41 phút', '1 giờ 12 phút'][i], font=MONO(18), fill=MUTED)


def screen_live(out):
    w, h = 2400, 1500
    im = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(im)
    chrome(d, w, 'Diều — Họp sản phẩm · đang ghi')
    sidebar(d, h, 0)
    d.ellipse([470, 110, 494, 134], fill=(255, 77, 77))
    d.text((510, 104), 'ĐANG NGHE · 00:47:12', font=MONO(26, True), fill=INK)
    lines = [('Hà', '00:41:05', 'Mình chốt là bản 2.3 ra vào thứ Sáu tuần sau nhé.'),
             ('Minh', '00:41:22', 'Được, nhưng phần đồng bộ ngoại tuyến cần thêm hai ngày kiểm thử.'),
             ('Lan', '00:42:10', 'Vậy mình dời đồng bộ sang 2.4, giữ ngày phát hành.'),
             ('Hà', '00:42:31', 'Đồng ý. Minh viết lại ghi chú phát hành giúp mình.'),
             ('Tuấn', '00:44:02', 'Còn chuyện giá gói nhóm thì sao?'),
             ('Lan', '00:44:40', 'Để tuần sau, khi có số liệu dùng thử.')]
    y = 190
    for who, t, said in lines:
        d.text((480, y), who, font=TEXT(26, True), fill=CYAN if who == 'Hà' else INK)
        d.text((620, y + 4), t, font=MONO(20), fill=MUTED)
        d.text((480, y + 42), said, font=TEXT(30), fill=INK)
        y += 150
    px = 1620
    d.rectangle([px, 64, w, h], fill=PANEL)
    d.text((px + 50, 110), 'TÓM TẮT TRỰC TIẾP', font=MONO(22, True), fill=AMBER)
    items = [('QUYẾT ĐỊNH', 'Bản 2.3 phát hành thứ Sáu tuần sau'), ('QUYẾT ĐỊNH', 'Đồng bộ ngoại tuyến dời sang 2.4'),
             ('VIỆC', 'Minh: viết lại ghi chú phát hành'), ('CÒN MỞ', 'Giá gói nhóm: chờ số liệu dùng thử')]
    y = 180
    for k, txt in items:
        rounded(d, [px + 40, y, w - 40, y + 190], 16, fill=CARD, outline=AMBER if k == 'QUYẾT ĐỊNH' else LINE, width=2)
        d.text((px + 70, y + 26), k, font=MONO(20, True), fill=AMBER if k == 'QUYẾT ĐỊNH' else MUTED)
        words, line, ly = txt.split(), '', y + 70
        for wd in words:
            trial = (line + ' ' + wd).strip()
            if TEXT(30).getlength(trial) > (w - 40) - (px + 70) - 30:
                d.text((px + 70, ly), line, font=TEXT(30, True), fill=INK)
                line, ly = wd, ly + 44
            else:
                line = trial
        d.text((px + 70, ly), line, font=TEXT(30, True), fill=INK)
        y += 220
    im.save(out)


def screen_summary(out):
    w, h = 2400, 1500
    im = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(im)
    chrome(d, w, 'Diều — Biên bản')
    sidebar(d, h, 0)
    x = 520
    d.text((x, 110), 'BIÊN BẢN · 10/10 · 47 PHÚT · 5 NGƯỜI', font=MONO(22, True), fill=MUTED)
    d.text((x, 160), 'Họp sản phẩm: lịch phát hành 2.3', font=TEXT(64, True), fill=INK)
    sections = [('3 QUYẾT ĐỊNH', ['Bản 2.3 phát hành thứ Sáu tuần sau.', 'Đồng bộ ngoại tuyến dời sang bản 2.4.',
                                    'Giữ nguyên giá gói cá nhân.'], AMBER),
                ('2 VIỆC CẦN LÀM', ['Minh · viết lại ghi chú phát hành · thứ Tư', 'Lan · kế hoạch kiểm thử đồng bộ · thứ Năm'], CYAN),
                ('1 CÂU HỎI MỞ', ['Giá gói nhóm: chờ số liệu dùng thử tuần sau.'], MUTED)]
    y = 300
    for head, rows, col in sections:
        d.text((x, y), head, font=MONO(24, True), fill=col)
        y += 54
        for r in rows:
            rounded(d, [x, y, x + 34, y + 34], 8, outline=col, width=3)
            if col is AMBER:
                d.line([x + 8, y + 18, x + 15, y + 26, x + 27, y + 9], fill=AMBER, width=4)
            d.text((x + 60, y - 4), r, font=TEXT(34), fill=INK)
            y += 66
        y += 40
    rounded(d, [1880, 300, 2340, 520], 18, fill=CARD, outline=LINE)
    d.text((1910, 330), 'GỬI CHO', font=MONO(20, True), fill=MUTED)
    for i, c in enumerate(((110, 231, 249), (255, 176, 32), (167, 139, 250), (52, 211, 153), (248, 113, 113))):
        d.ellipse([1910 + i * 70, 380, 1970 + i * 70, 440], fill=c)
    rounded(d, [1910, 460, 2310, 505], 10, fill=AMBER)
    d.text((2110, 482), 'Gửi biên bản', font=TEXT(24, True), fill=BG, anchor='mm')
    im.save(out)


def screen_phone(out):
    w, h = 1170, 2532
    im = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(im)
    d.text((80, 90), '9:41', font=TEXT(44, True), fill=INK)
    d.text((80, 260), 'Hôm nay', font=TEXT(84, True), fill=INK)
    cards = [('Diều', 'Biên bản "Họp sản phẩm" đã gửi cho 5 người.', 'vừa xong'),
             ('Diều', '3 quyết định · 2 việc cần làm · 1 câu hỏi mở', 'vừa xong'),
             ('Lịch', 'Giao ban thứ Hai · 9:00', '2 giờ nữa')]
    y = 440
    for app, msg, t in cards:
        rounded(d, [60, y, w - 60, y + 300], 44, fill=CARD)
        rounded(d, [100, y + 40, 180, y + 120], 18, fill=AMBER if app == 'Diều' else LINE)
        d.text((210, y + 52), app, font=TEXT(38, True), fill=INK)
        d.text((w - 100, y + 56), t, font=TEXT(30), fill=MUTED, anchor='ra')
        words, line, ly = msg.split(), '', y + 140
        for wd in words:
            trial = (line + ' ' + wd).strip()
            if TEXT(40).getlength(trial) > w - 220:
                d.text((100, ly), line, font=TEXT(40), fill=INK)
                line, ly = wd, ly + 56
            else:
                line = trial
        d.text((100, ly), line, font=TEXT(40), fill=INK)
        y += 340
    im.save(out)


if __name__ == '__main__':
    out = HERE / 'assets'
    out.mkdir(exist_ok=True)
    screen_live(out / 'screen_live.png')
    screen_summary(out / 'screen_summary.png')
    screen_phone(out / 'screen_phone.png')
    print('screens ->', out)
