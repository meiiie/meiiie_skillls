"""Copy to WORK/design/films/kit.py (it imports WORK/design/ds.py and reads fonts from WORK/fonts/).
Shared film kit (manimgx): type in slide points, a 2-D camera that keeps strokes and type
at screen size, pins and ledgers. Every film is 2560x1080 (64:27) and sits on the slide in the
film window ds.FILM_* so a 13 pt label in a film reads as 13 pt on the slide."""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ds
from manimgx import *

FONTS = [str(HERE.parents[1] / 'fonts')]
FW, FH = 8.0 * 2560 / 1080, 8.0
UPI = FW / ds.FILM_W                    # scene units per slide inch

# Families come from YOUR ds.py (chosen per topic); the fallbacks are neutral ManimGX-shipped faces, not a style.
# Typst reads typographic families: a "Barlow Condensed" file is family 'Barlow' (+ weight); test-render first.
SERIF = SERIF_SEMI = getattr(ds, 'FILM_SERIF', 'Libertinus Serif')
SANS = SANS_MED = SANS_SEMI = getattr(ds, 'FILM_SANS', 'Noto Sans')
MONO = getattr(ds, 'FILM_MONO', 'DejaVu Sans Mono')

def fs(pt):
    """Text font_size whose capital is as tall as a pt-point capital on the slide."""
    cap_units = pt / 72 * 0.69 * UPI
    return 48 * cap_units / 0.449

def T(s, size='label', font=SANS, color=ds.INK, weight=NORMAL, slant=NORMAL, **kw):
    pt = ds.SIZES[size] if isinstance(size, str) else size
    return Text(s, font=font, font_size=fs(pt), color=color, weight=weight, slant=slant, font_paths=FONTS, **kw)

def halo(mob, width=6, color=ds.PAPER):
    mob.set_stroke(color, width=width, background=True)
    return mob

def poly(pts, closed=False, **style):
    v = VMobject(**style)
    p = np.array([[x, y, 0] for x, y in pts])
    if closed and not np.allclose(p[0], p[-1]):
        p = np.vstack([p, p[:1]])
    v.set_points_as_corners(p)
    return v

class View:
    """2-D camera: screen = (world - C) * Z. Groups registered with follow() are moved and
    scaled with the view (their strokes stay put), pins are only moved."""
    def __init__(self, scene, cx=0.0, cy=0.0, z=1.0):
        self.cx, self.cy, self.z = ValueTracker(cx), ValueTracker(cy), ValueTracker(z)
        scene.add(self.cx, self.cy, self.z)

    def state(self):
        return np.array([self.cx.get_value(), self.cy.get_value(), 0.0]), self.z.get_value()

    def S(self, w):
        c, z = self.state()
        return (np.array([w[0], w[1], 0.0]) - c) * z

    def follow(self, group):
        c0, z0 = self.state()
        group.apply_function(lambda p: (p - c0) * z0)
        last = {'c': c0, 'z': z0}
        def upd(g):
            c, z = self.state()
            if np.allclose(c, last['c']) and abs(z - last['z']) < 1e-9:
                return
            k = z / last['z']
            g.scale(k, about_point=ORIGIN)
            g.shift((last['c'] - c) * z)
            last['c'], last['z'] = c, z
        group.add_updater(upd)
        return group

    def pin(self, mob, w, offset=(0, 0)):
        off = np.array([offset[0], offset[1], 0.0])
        mob.move_to(self.S(w) + off)
        mob.add_updater(lambda m_: m_.move_to(self.S(w) + off))
        return mob

    def go(self, cx, cy, z, **kw):
        return AnimationGroup(self.cx.animate.set_value(cx), self.cy.animate.set_value(cy), self.z.animate.set_value(z), **kw)
