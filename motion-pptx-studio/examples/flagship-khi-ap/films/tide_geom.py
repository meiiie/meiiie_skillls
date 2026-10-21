"""S5 "Mực nước nợ" — general government gross debt, % of GDP, as water in seven tide-gauge stilling wells.
Data: IMF WEO Oct 2026, Table A8 (2024, 2025, 2026, 2027 and 2031; 2026+ projections). Years in between
2027 and 2031 are not shown (the film jumps, and says so). IMF Fiscal Monitor blog 14 Oct 2026: global
public debt expected to exceed 100% of global GDP by 2030, a level last reached after World War II."""
YEARS = [2024, 2025, 2026, 2027, 2031]
DEBT = {   # key: (name, values by YEARS)
    'JPN': ('Nhật Bản', [213.6, 204.8, 199.4, 196.4, 188.9]),
    'ITA': ('Ý', [134.7, 137.1, 137.9, 137.6, 135.6]),
    'USA': ('Mỹ', [122.3, 124.4, 126.8, 128.7, 145.0]),
    'FRA': ('Pháp', [112.6, 115.5, 118.5, 120.4, 123.6]),
    'GBR': ('Anh', [99.4, 102.1, 102.0, 102.5, 100.2]),
    'EA':  ('Khu vực euro', [86.3, 87.3, 88.0, 88.5, 90.4]),
    'DEU': ('Đức', [61.4, 62.7, 64.6, 66.9, 75.6]),
}
ORDER = ['JPN', 'ITA', 'USA', 'FRA', 'GBR', 'EA', 'DEU']
X0, DXW = -3.4, 2.0          # x of the first well, spacing
WW = 0.86                    # well (glass tube) width
YB = -2.75                   # inside bottom of the wells (0 %)
PPU = 0.0225                 # scene units per percentage point (0..220 %)
VMAX = 220
VAL_Y = 3.05              # fixed readout row above the wells

def x_of(i):
    return X0 + i * DXW

def y_of(v):
    return YB + v * PPU

def vn(x, d=1):
    return ('−' if x < 0 else '') + f'{abs(x):.{d}f}'.replace('.', ',')
