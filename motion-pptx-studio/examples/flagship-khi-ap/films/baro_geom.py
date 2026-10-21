"""Geometry + data for film S2 "Ba khí áp kế" (three barometers). Pure python: imported by the
manimgx film (baro.py) and by the native PowerPoint fallback, so both draw the same dials.
Data (raw/ files): Fed FOMC 16 Sep 2026 raised the target range 1/4 pt to 3-3/4 - 4 %;
ECB 10 Sep 2026 raised the deposit facility rate 25 bp to 2.50 % (effective 16 Sep);
BoJ 18 Sep 2026 raised the call-rate guideline to around 1.25 % from around 1.0 %.
CPI 2026 (annual average, projection): IMF WEO Oct 2026 Table A5: US 3.6, Euro Area 3.1, Japan 2.0.
Real rate shown = policy rate (Fed: middle of the range) - IMF 2026 CPI projection. Derived, labelled so."""
import math

FW, FH = 8.0 * 2560 / 1080, 8.0
VMAX = 5.0                     # dial runs 0..5 %
A0, SWEEP = 225.0, 270.0       # degrees: 0 % at 225 (lower left), 5 % at -45 (lower right)
R = 2.3                        # dial radius, scene units
CY = 0.3

BANKS = [
    dict(key='ecb', code='ECB', name='Ngân hàng Trung ương châu Âu', x=-6.1, before=2.25, after=2.50, lo=None, hi=None,
         date='10/9', stamp='10·09·2026', country='Khu vực đồng euro', what='lãi suất tiền gửi', cpi=3.1, cpi_where='khu vực đồng euro', order=0),
    dict(key='fed', code='FED', name='Cục Dự trữ Liên bang Mỹ', x=0.0, before=3.625, after=3.875, lo=(3.50, 3.75), hi=(3.75, 4.00),
         date='16/9', stamp='16·09·2026', country='Mỹ', what='lãi suất quỹ liên bang', cpi=3.6, cpi_where='Mỹ', order=1),
    dict(key='boj', code='BOJ', name='Ngân hàng Trung ương Nhật Bản', x=6.1, before=1.00, after=1.25, lo=None, hi=None,
         date='18/9', stamp='18·09·2026', country='Nhật Bản', what='lãi suất qua đêm', cpi=2.0, cpi_where='Nhật Bản', order=2),
]
for b in BANKS:
    b['real'] = round(b['after'] - b['cpi'], 3)

def ang(v):
    """value (%) -> angle in degrees (math convention)"""
    return A0 - v / VMAX * SWEEP

def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def ticks(cx, cy=CY, r=R):
    out = []
    for i in range(0, 101):
        v = i * 0.05
        major = i % 20 == 0
        mid = (i % 5 == 0) and not major
        L = 0.30 if major else (0.18 if mid else 0.10)
        r0 = r - 0.2
        out.append(dict(v=v, kind='major' if major else ('mid' if mid else 'minor'),
                        p0=pol(cx, cy, r0, ang(v)), p1=pol(cx, cy, r0 - L, ang(v))))
    return out

def numerals(cx, cy=CY, r=R):
    return [dict(text=str(v), p=pol(cx, cy, r - 0.78, ang(v))) for v in range(0, 6)]

def needle(cx, v, cy=CY, r=R):
    """slim tapered needle polygon + tail, pointing at v"""
    a = ang(v)
    tip = pol(cx, cy, r - 0.28, a)
    tail = pol(cx, cy, 0.42, a + 180)
    w = 0.055
    l1 = pol(cx, cy, w, a + 90); l2 = pol(cx, cy, w, a - 90)
    t1 = pol(tail[0], tail[1], w * 1.6, a + 90); t2 = pol(tail[0], tail[1], w * 1.6, a - 90)
    return [tip, l1, t1, t2, l2]

def hand(cx, v, cy=CY, r=R):
    """the set hand (inflation): a hairline with a diamond at the rim"""
    a = ang(v)
    p0 = pol(cx, cy, 0.25, a); p1 = pol(cx, cy, r - 0.42, a)
    c = pol(cx, cy, r - 0.3, a)
    d = [pol(c[0], c[1], 0.12, a), pol(c[0], c[1], 0.06, a + 90), pol(c[0], c[1], 0.12, a + 180), pol(c[0], c[1], 0.06, a - 90)]
    return p0, p1, d

def gap_arc(cx, v0, v1, cy=CY, r_in=R - 1.28, r_out=R - 1.08, n=40):
    """annular band between two values (the real-rate gap)"""
    a0, a1 = ang(v0), ang(v1)
    outer = [pol(cx, cy, r_out, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    inner = [pol(cx, cy, r_in, a1 + (a0 - a1) * i / n) for i in range(n + 1)]
    return outer + inner

# the closing chart: one vertical bar per bank, under each dial, sharing a zero line
ZERO_Y = -0.6
PP = 2.6           # scene units per percentage point
BAR_W = 1.5

# ---- bezel detail (v4): a knurled outer bezel, three slotted screws, a mirror arc, a glass glint
BEZEL = 0.2          # bezel width outside the face radius R

def knurl(cx, cy=CY, r=R, n=144):
    """short radial grip marks on the bezel"""
    return [(pol(cx, cy, r + 0.05, i * 360 / n), pol(cx, cy, r + BEZEL - 0.04, i * 360 / n)) for i in range(n)]

def screws(cx, cy=CY, r=R):
    """three screw heads in the bezel ring, each (centre, slot p0, slot p1)"""
    out = []
    for k, a in enumerate((90, 210, 330)):
        c = pol(cx, cy, r + BEZEL / 2, a)
        s = 35 + k * 50
        out.append((c, pol(c[0], c[1], 0.045, s), pol(c[0], c[1], 0.045, s + 180)))
    return out

def mirror_arc(cx, cy=CY, r=R, n=80):
    """the anti-parallax mirror strip: a thin arc just inside the major ticks"""
    a0, a1 = ang(0), ang(VMAX)
    return [pol(cx, cy, r - 0.54, a0 + (a1 - a0) * i / n) for i in range(n + 1)]

def glint(cx, cy=CY, r=R, n=30):
    return [pol(cx, cy, r - 0.13, 100 + 55 * i / n) for i in range(n + 1)]
