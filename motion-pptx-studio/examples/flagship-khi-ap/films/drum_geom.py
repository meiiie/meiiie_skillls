"""S3 "Băng ghi khí áp" geometry + data, shared by the film (drum.py) and the native fallback.
Data: IMF WEO Oct 2026, Table A1, world real GDP growth (%): 2018 3.6, 2019 3.0, 2020 -2.7, 2021 6.7,
2022 3.8, 2023 3.3, 2024 3.5, 2025 3.5, 2026 3.1 (projection), 2027 3.4 (projection); 2008-17 average 3.3.
The trace joins the annual values with straight lines (no invented monthly path)."""
import math
YEARS = list(range(2018, 2028))
G = [3.6, 3.0, -2.7, 6.7, 3.8, 3.3, 3.5, 3.5, 3.1, 3.4]
AVG = 3.3
PROJ_FROM = 2026          # 2026 and 2027 are projections
# drum (front elevation of a barograph)
DCX, DCY, RD, HD = -2.2, 0.55, 3.0, 4.7
GMID, PPY_D = 2.0, 0.4    # g=-3..7 -> y -1.45..2.55
SPD = 1.05                # paper speed: scene units of arc per year
# flat chart (end state)
CX0, DX = -7.9, 1.55      # x of 2018, units per year
CY0, PPY_C = -0.55, 0.42  # y of g=0, units per point

def gval(u):
    if u <= YEARS[0]:
        return G[0]
    if u >= YEARS[-1]:
        return G[-1]
    i = int(math.floor(u - YEARS[0])); f = u - YEARS[0] - i
    return G[i] + (G[i + 1] - G[i]) * f

def drum_xy(u, g, tau):
    a = max(-math.pi / 2, min(math.pi / 2, (u - tau) * SPD / RD))
    return DCX + RD * math.sin(a), DCY + (g - GMID) * PPY_D, math.cos(a)

def chart_xy(u, g):
    return CX0 + (u - YEARS[0]) * DX, CY0 + g * PPY_C

def mix(u, g, tau, e):
    x0, y0, c = drum_xy(u, g, tau)
    x1, y1 = chart_xy(u, g)
    return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e, c + (1 - c) * e

def vn(x, d=1):
    return ('−' if x < 0 else '') + f'{abs(x):.{d}f}'.replace('.', ',')
