"""Geometry for film S1 "Hai tâm áp" (the pressure chart of 2026).
One geometry, two renderers: this script writes pressure_geom.json, read by the manimgx film
(pressure.py) and by the native PowerPoint fallback (deck builder) so both draw the same map.

Data: IMF WEO Oct 2026, Table A, real GDP growth 2025 and 2026 (raw/imf_weo_oct2026_tableA_excerpt.txt).
The isobars are contour lines of growth interpolated between the 25 economies IMF lists (Gaussian
kernel, sigma 7 deg); far from any economy the field is masked, so no line is drawn where there is
no data. They are a spatial illustration of 25 national numbers, not a measured field.
Projection: Equal Earth, central meridian 150E (an Asia-centred chart, Viet Nam near the middle).
Run with system python3 (needs numpy, matplotlib, shapely)."""
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString, MultiLineString
from shapely import affinity

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / 'data'
LON0 = 150.0
FW, FH = 8.0 * 2560 / 1080, 8.0           # scene frame (units)
SCALE, YSHIFT = 3.45, -0.44

# (key, name_vi, lon, lat, g2025, g2026)   IMF WEO Oct 2026 Table A1/A2/A4
ECON = [
    ('USA', 'Mỹ', -98, 39, 2.3, 2.3), ('CAN', 'Canada', -106, 56, 1.9, 1.1), ('MEX', 'Mexico', -102, 23, 0.5, 1.5),
    ('BRA', 'Brazil', -50, -11, 2.3, 2.2), ('DEU', 'Đức', 10, 51, 0.2, 1.3), ('FRA', 'Pháp', 2.5, 46.5, 0.9, 0.4),
    ('GBR', 'Anh', -2, 53, 1.2, 1.3), ('RUS', 'Nga', 50, 56, 1.0, 0.9), ('SAU', 'Ả Rập Xê Út', 45, 24, 4.6, -3.3),
    ('IRN', 'Iran', 53.5, 32.5, -0.9, -7.6), ('QAT', 'Qatar', 51.2, 25.3, 1.8, -15.6), ('KWT', 'Kuwait', 47.7, 29.3, 2.7, -16.7),
    ('IRQ', 'Iraq', 43.7, 33.2, -0.4, -16.0), ('ARE', 'UAE', 54.3, 24.0, 6.2, -3.9), ('CHN', 'Trung Quốc', 112, 32, 5.0, 4.5),
    ('IND', 'Ấn Độ', 79, 22, 7.8, 7.0), ('IDN', 'Indonesia', 112, -3, 5.1, 5.1), ('VNM', 'Việt Nam', 106, 16, 8.0, 8.4),
    ('THA', 'Thái Lan', 101, 15, 2.4, 2.1), ('PHL', 'Philippines', 122, 12, 4.4, 3.4), ('MYS', 'Malaysia', 102, 4, 5.2, 5.2),
    ('SGP', 'Singapore', 103.8, 1.35, 5.0, 5.0), ('KOR', 'Hàn Quốc', 127.8, 36.3, 1.1, 3.3), ('TWN', 'Đài Loan', 121, 23.7, 8.8, 10.7),
    ('JPN', 'Nhật Bản', 138, 36.5, 1.2, 0.7),
]
WORLD = {2025: 3.5, 2026: 3.1}
# Countries IMF Table A gives only as a regional aggregate: the aggregate is used as a proxy,
# at reduced kernel weight (0.6), and this is disclosed on the slide.
EA_REST = ['AUT', 'BEL', 'HRV', 'CYP', 'EST', 'FIN', 'GRC', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'PRT', 'SVK', 'SVN', 'ESP', 'BGR']
EME = ['ALB', 'BIH', 'BLR', 'HUN', 'KOS', 'MDA', 'MNE', 'MKD', 'POL', 'ROU', 'SRB', 'TUR', 'UKR']
PROXY = [('Euro Area', EA_REST, 1.2, 1.1), ('Emerging & Developing Europe', EME, 2.0, 1.7),
         ('Sub-Saharan Africa', 'Sub-Saharan Africa', 4.5, 4.5), ('Latin America & Caribbean', 'Latin America & Caribbean', 2.5, 2.3)]
LEVELS = None  # set after STEP

A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2

def wrap(lon):
    return ((lon - LON0 + 180) % 360) - 180

def proj(lon_rel, lat):
    """Equal Earth for lon already relative to LON0 (deg). Returns scene units."""
    lam, phi = np.radians(lon_rel), np.radians(lat)
    th = np.arcsin(M * np.sin(phi))
    x = 2 * math.sqrt(3) * lam * np.cos(th) / (3 * (A1 + 3 * A2 * th**2 + 7 * A3 * th**6 + 9 * A4 * th**8))
    y = A1 * th + A2 * th**3 + A3 * th**7 + A4 * th**9
    return x * SCALE, y * SCALE + YSHIFT

def P(lon, lat):
    x, y = proj(wrap(lon), lat)
    return [round(float(x), 4), round(float(y), 4)]

def shift_geom(g):
    """real lon -> lon relative to LON0, splitting at the seam."""
    out = []
    win = box(-180, -90, 180, 90)
    for k in (-360, 0, 360):
        gg = affinity.translate(g, xoff=-LON0 + k)
        inter = gg.intersection(win)
        if not inter.is_empty:
            out.append(inter)
    return out

def rings(geom, min_area=0.0):
    polys = []
    def add(p):
        if p.geom_type == 'Polygon':
            if p.area >= min_area:
                polys.append(p)
        elif hasattr(p, 'geoms'):
            for q in p.geoms:
                add(q)
    add(geom)
    return polys

def project_ring(coords, lat_clip=(-58, 84)):
    pts = []
    for lon, lat in coords:
        lat = max(lat_clip[0], min(lat_clip[1], lat))
        x, y = proj(lon, lat)
        pts.append([round(float(x), 4), round(float(y), 4)])
    return pts

def densify(coords, step=1.0):
    """add points along long straight edges so the projected outline curves (seam edges)."""
    out = []
    for (a, b), (c, d) in zip(coords[:-1], coords[1:]):
        n = max(1, int(math.hypot(c - a, d - b) / step))
        for i in range(n):
            out.append((a + (c - a) * i / n, b + (d - b) * i / n))
    out.append(coords[-1])
    return out

def land():
    gj = json.load(open(DATA / 'ne_50m_land.geojson'))
    out = []
    for f in gj['features']:
        for g in shift_geom(shape(f['geometry'])):
            for p in rings(g, min_area=0.6):
                ext = densify(list(p.exterior.coords))
                if max(c[1] for c in ext) < -58:
                    continue  # Antarctica
                out.append(project_ring(ext))
    return out

def borders():
    gj = json.load(open(DATA / 'ne_50m_admin_0_boundary_lines_land.geojson'))
    out = []
    for f in gj['features']:
        for g in shift_geom(shape(f['geometry'])):
            lines = [g] if g.geom_type == 'LineString' else [l for l in getattr(g, 'geoms', []) if l.geom_type == 'LineString']
            for l in lines:
                c = list(l.coords)
                if len(c) >= 2 and l.length > 0.8:
                    out.append(project_ring(c))
    return out

def graticule():
    out = []
    for lon in range(-180, 181, 30):
        lon_rel = wrap(lon) if lon != LON0 + 180 else 180
        pts = [proj(lon_rel, lat) for lat in np.linspace(-58, 84, 60)]
        out.append({'kind': 'meridian', 'lon': lon, 'pts': [[round(float(x), 4), round(float(y), 4)] for x, y in pts]})
    for lat in range(-45, 76, 15):
        pts = [proj(l, lat) for l in np.linspace(-180, 180, 120)]
        out.append({'kind': 'parallel', 'lat': lat, 'pts': [[round(float(x), 4), round(float(y), 4)] for x, y in pts]})
    return out

# ---- the field ----------------------------------------------------------------------
GLON = np.linspace(-180, 180, 721)        # relative lon
GLAT = np.linspace(-58, 80, 277)
LONR, LATG = np.meshgrid(GLON, GLAT)
LONA = LONR + LON0                       # absolute lon
import os
SIGDIV, SIGMIN, SIGMAX = [float(x) for x in os.environ.get('PG_SIG', '1.0,10,24').split(',')]
STEP = float(os.environ.get('PG_STEP', '1.0'))


def countries():
    gj = json.load(open(DATA / 'ne_50m_admin_0_countries.geojson'))
    c = {}
    for f in gj['features']:
        p = f['properties']
        a3 = p['ADM0_A3'] if p['ADM0_A3'] != 'SDS' else 'SSD'
        c[a3] = dict(lon=p['LABEL_X'], lat=p['LABEL_Y'], area=shape(f['geometry']).area, region=p['REGION_WB'], a3=a3)
    return c

C = countries()
ALIAS = {'KOR': 'KOR', 'TWN': 'TWN'}
POINTS = []   # lon, lat, g2025, g2026, sigma, weight, source
for k, n, lon, lat, a, b in ECON:
    area = C.get(k, {}).get('area', 4.0)
    POINTS.append((lon, lat, a, b, float(np.clip(math.sqrt(area) / SIGDIV, SIGMIN, SIGMAX)), 1.0, k))
listed = {e[0] for e in ECON}
for name, members, a, b in PROXY:
    for a3, c in C.items():
        hit = (a3 in members) if isinstance(members, list) else (c['region'] == members)
        if hit and a3 not in listed and c['area'] > 0.5:
            POINTS.append((c['lon'], c['lat'], a, b, float(np.clip(math.sqrt(c['area']) / SIGDIV, SIGMIN, SIGMAX)), 0.6, name))

def kernel():
    W = []
    for lon, lat, a, b, sig, wt, src in POINTS:
        dlon = ((LONA - lon + 180) % 360) - 180
        dx = dlon * np.cos(np.radians((LATG + lat) / 2))
        dy = LATG - lat
        W.append(wt * np.exp(-(dx**2 + dy**2) / (2 * sig**2)))
    return np.array(W)

KW = kernel()
LEVELS = [round(x * STEP, 2) for x in range(int(-16 / STEP), int(11 / STEP) + 1) if abs(x * STEP - 3.1) > 0.45 and abs(x * STEP - 3.5) > 0.45]
SUMW = KW.sum(0)
MASK = SUMW < float(os.environ.get('PG_MASK', '0.22'))          # no economy within reach: draw nothing

def field(t):
    """t=0 -> 2025, t=1 -> 2026 (linear blend of the two IMF columns)"""
    v = np.array([a + (b - a) * t for lon, lat, a, b, *_ in POINTS])
    w0 = 0.02
    wv = WORLD[2025] + (WORLD[2026] - WORLD[2025]) * t
    f = (np.tensordot(v, KW, 1) + w0 * wv) / (SUMW + w0)
    return np.where(MASK, np.nan, f)

def chaikin(pts, n=2, closed=False):
    p = np.asarray(pts)
    for _ in range(n):
        if len(p) < 3:
            break
        q = p[:-1] * 0.75 + p[1:] * 0.25
        r = p[:-1] * 0.25 + p[1:] * 0.75
        mid = np.empty((len(q) * 2, 2)); mid[0::2] = q; mid[1::2] = r
        p = np.vstack([p[:1], mid, p[-1:]]) if not closed else mid
    return p

def contours(t, levels=None, extra=None):
    levels = LEVELS if levels is None else levels
    f = field(t)
    fig = plt.figure()
    lv = sorted(set(levels + ([extra] if extra is not None else [])))
    cs = plt.contour(GLON, GLAT, f, levels=lv)
    out = []
    for lev, segs in zip(cs.levels, cs.allsegs):
        for s in segs:
            if len(s) < 6:
                continue
            closed = np.allclose(s[0], s[-1])
            s = chaikin(s, 2, closed)
            x, y = proj(s[:, 0], s[:, 1])
            pts = np.stack([x, y], 1)
            # drop near-duplicate points
            keep = [0]
            for i in range(1, len(pts)):
                if np.hypot(*(pts[i] - pts[keep[-1]])) > 0.025:
                    keep.append(i)
            pts = pts[keep]
            if len(pts) >= 4:
                out.append({'level': float(lev), 'closed': bool(closed), 'pts': np.round(pts, 4).tolist()})
    plt.close(fig)
    return out

def extremum(t, lo=True, region=None):
    f = field(t)
    g = np.where(np.isnan(f), np.inf if lo else -np.inf, f)
    if region:
        (a, b), (c, d) = region
        sel = (LONA % 360 >= a % 360) & (LONA % 360 <= b % 360) & (LATG >= c) & (LATG <= d)
        g = np.where(sel, g, np.inf if lo else -np.inf)
    i = np.unravel_index(np.argmin(g) if lo else np.argmax(g), g.shape)
    return P(float(LONA[i]), float(LATG[i])), float(f[i])

def main():
    frames = 90
    out = {
        'frame': [FW, FH], 'lon0': LON0, 'scale': SCALE, 'yshift': YSHIFT,
        'source': 'IMF WEO Oct 2026 Table A (real GDP growth 2025, 2026); Natural Earth 1:50m (public domain)',
        'land': land(), 'borders': borders(), 'graticule': graticule(),
        'levels': LEVELS, 'world': WORLD,
        'econ': [{'key': k, 'name': n, 'lon': lon, 'lat': lat, 'g2025': a, 'g2026': b, 'xy': P(lon, lat)} for k, n, lon, lat, a, b in ECON],
        'frames': [contours(i / (frames - 1)) for i in range(frames)],
        'world_line': {'2025': contours(0, [WORLD[2025]]), '2026': contours(1, [WORLD[2026]])},
    }
    lo, lov = extremum(1, True, ((30, 70), (15, 40)))
    hi, hiv = extremum(1, False, ((95, 135), (0, 40)))
    out['low'] = {'xy': lo, 'value': round(lov, 1)}
    out['high'] = {'xy': hi, 'value': round(hiv, 1)}
    # the energy front: from the Gulf low west-north-west across the Levant to Europe (illustrative path)
    out['front'] = [P(lon, lat) for lon, lat in [(49, 29), (42, 32.5), (35, 35.5), (27, 38.5), (19, 42), (11, 45.5), (4, 47.5)]]
    # AI flow arcs: Taiwan/Korea -> North America across the Pacific (WTO: Asia export volume +9.9%)
    def arc(a, b, bulge):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + bulge
        return [[x1, y1], [mx, my], [x2, y2]]
    out['flows'] = [arc((121.5, 24), (-118, 34), 1.1), arc((127, 36), (-122, 38), 1.5), arc((121, 23), (-97, 30), 0.7)]
    json.dump(out, open(HERE / 'pressure_geom.json', 'w'), ensure_ascii=False)
    n = sum(len(f) for f in out['frames'])
    print('land', len(out['land']), 'borders', len(out['borders']), 'contour paths total', n, 'low', out['low'], 'high', out['high'])
    # quick look
    fig, ax = plt.subplots(figsize=(19, 8), dpi=80)
    for r in out['land']:
        a = np.array(r); ax.fill(a[:, 0], a[:, 1], color='#E0DCD1', lw=0)
    for c in out['frames'][-1]:
        a = np.array(c['pts']); ax.plot(a[:, 0], a[:, 1], color='#C0391F' if c['level'] < 3.1 else '#1F4F8F', lw=0.8)
    for c in out['world_line']['2026']:
        a = np.array(c['pts']); ax.plot(a[:, 0], a[:, 1], color='k', lw=2)
    ax.set_xlim(-FW / 2, FW / 2); ax.set_ylim(-4, 4); ax.set_aspect('equal'); ax.axis('off')
    fig.savefig(HERE / os.environ.get('PG_PREV', 'pressure_geom.preview.png'), bbox_inches='tight', facecolor='#EEEBE3')

if __name__ == '__main__':
    main()
