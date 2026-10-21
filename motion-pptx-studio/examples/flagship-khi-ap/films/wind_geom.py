"""S4 "Gió mậu dịch" data + geometry (film wind.py and the native fallback).
WTO Global Trade Outlook, 8 Oct 2026, Table 1: merchandise EXPORT volume growth 2026 (updated forecast):
North America 5.7, South and Central America and the Caribbean 3.4, Europe -0.1, CIS -3.9, Africa 5.6,
Middle East -17.2, Asia 9.9; world merchandise trade volume 3.9 (average of exports and imports).
Asia accounts for 4.0 percentage points of the 3.9% world growth (WTO text)."""
import math, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
REG = [  # key, Vietnamese name, export growth 2026 %, (lon, lat) of the station
    ('asia', 'Châu Á', 9.9, (112, 28)),
    ('na', 'Bắc Mỹ', 5.7, (-98, 42)),
    ('af', 'Châu Phi', 5.6, (20, 4)),
    ('sa', 'Nam, Trung Mỹ và Caribe', 3.4, (-60, -14)),
    ('eu', 'Châu Âu', -0.1, (14, 50)),
    ('cis', 'CIS', -3.9, (68, 52)),
    ('me', 'Trung Đông', -17.2, (47, 26)),
]
WORLD = 3.9
ZX, PPU, ROW0, DROW = 1.4, 0.40, 2.25, 0.66   # bar chart (screen units at the end view)

def station_xy():
    """projected station points (Equal Earth, 150E), precomputed by: python3 -c "import wind_geom as W; W.write_xy()" """
    f = HERE / 'wind_xy.json'
    if f.exists():
        return json.load(open(f))
    import pressure_geom as pg
    return {k: pg.P(lon, lat) for k, n, v, (lon, lat) in REG}

def write_xy():
    import pressure_geom as pg
    json.dump({k: pg.P(lon, lat) for k, n, v, (lon, lat) in REG}, open(HERE / 'wind_xy.json', 'w'), indent=1)

def streams(xy, v, n=6):
    """n streamlines per station; positive: blow outward to the east, negative: drawn in toward the station"""
    out = []
    L = 0.9 + 0.13 * min(abs(v), 12)
    for j in range(n):
        off = (j - (n - 1) / 2) * 0.2
        x0, y0 = xy[0] + 0.15, xy[1] + off
        pts = []
        for i in range(13):
            s = i / 12
            ang = math.radians(6 * (j - (n - 1) / 2) + 16 * math.sin(s * math.pi) * (1 if j % 2 else -0.6))
            pts.append((x0 + L * s * math.cos(ang), y0 + L * s * math.sin(ang) + 0.06 * math.sin(s * math.pi * 2 + j)))
        if v < 0:
            pts = [(2 * xy[0] - p[0] + 0.3 * 0, p[1]) for p in pts][::-1]   # mirror to the west and reverse: flows inward
        out.append(pts)
    return out

def bar_rows():
    rows = sorted(REG, key=lambda r: -r[2])
    out = []
    for i, (k, n, v, _) in enumerate(rows):
        out.append(dict(key=k, name=n, v=v, y=ROW0 - i * DROW, x0=ZX, x1=ZX + v * PPU))
    return out

def vn(x, d=1, plus=True):
    s = f'{abs(x):.{d}f}'.replace('.', ',')
    return ('−' if x < 0 else ('+' if plus and x > 0 else '')) + s
