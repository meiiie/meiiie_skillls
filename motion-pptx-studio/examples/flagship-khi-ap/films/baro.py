"""S2 "Ba khí áp kế" — three central banks raise rates within nine days; only the Fed ends above
inflation (about 17 s).
  cd design/films && manimgx render baro.py Baro -r 2560x1080 --fps 30 -o ../../assets/film/baro.mp4
Data and geometry: baro_geom.py (shared with the native fallback)."""
from kit import *
import baro_geom as B

config.pixel_width, config.pixel_height = 2560, 1080
CY, R = B.CY, B.R

def vn(x, d=2, plus=False):
    s = f'{abs(x):.{d}f}'.replace('.', ',')
    return ('−' if x < 0 else ('+' if plus and x > 0 else '')) + s

def P(p):
    return np.array([p[0], p[1], 0.0])

def dial(b):
    cx = b['x']
    bez = Circle(radius=R + B.BEZEL, fill_color='#D8D2C4', fill_opacity=1, stroke_color=ds.INK, stroke_width=1.4).move_to([cx, CY, 0])
    kn = VGroup(*[Line(P(a), P(c), stroke_color=ds.SLATE, stroke_width=0.6, stroke_opacity=0.8) for a, c in B.knurl(cx)])
    sc = VGroup()
    for c, a, e in B.screws(cx):
        sc.add(Circle(radius=0.07, fill_color=ds.LAND, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.9).move_to(P(c)),
               Line(P(a), P(e), stroke_color=ds.INK, stroke_width=1.1))
    face = Circle(radius=R, fill_color=ds.PAPER, fill_opacity=1, stroke_color=ds.INK, stroke_width=2.0).move_to([cx, CY, 0])
    mirror = VMobject(stroke_color=ds.SLATE, stroke_width=0.7).set_points_smoothly([P(p) for p in B.mirror_arc(cx)])
    gl = VMobject(stroke_color='#FFFFFF', stroke_width=5, stroke_opacity=0.55).set_points_smoothly([P(p) for p in B.glint(cx)])
    ring = Circle(radius=R - 0.09, stroke_color=ds.INK, stroke_width=1.0).move_to([cx, CY, 0])
    shade = Circle(radius=R - 0.09, fill_color=ds.LAND, fill_opacity=0.35, stroke_width=0).move_to([cx, CY, 0])
    track = Arc(radius=R - 0.2, start_angle=np.radians(B.ang(B.VMAX)), angle=np.radians(B.SWEEP),
                stroke_color=ds.INK, stroke_width=1.4).move_arc_center_to([cx, CY, 0])
    tk = VGroup()
    for t in B.ticks(cx):
        w = {'major': 2.4, 'mid': 1.5, 'minor': 0.9}[t['kind']]
        c = ds.INK if t['kind'] != 'minor' else ds.SLATE
        tk.add(Line(P(t['p0']), P(t['p1']), stroke_color=c, stroke_width=w))
    nums = VGroup(*[T(n['text'], 'label', MONO, ds.HIGH if n['text'] == '2' else ds.INK, MEDIUM if n['text'] == '2' else NORMAL).move_to(P(n['p'])) for n in B.numerals(cx)])
    code = T(b['code'], 'sub', SERIF, ds.INK, SEMIBOLD).move_to([cx, CY - 0.78, 0])
    name = T(b['stamp'], 'micro', MONO, ds.SLATE).next_to(code, DOWN, buff=0.1)
    inner = Circle(radius=0.62, stroke_color=ds.RULE, stroke_width=1.0).move_to([cx, CY, 0])
    unit = T('%/năm', 'micro', MONO, ds.SLATE).move_to([cx, CY + 0.72, 0])
    a2 = np.radians(B.ang(2.0))
    p2 = np.array([cx, CY, 0]) + (R - 0.2) * np.array([np.cos(a2), np.sin(a2), 0])
    tgt = Line(p2, p2 - 0.42 * np.array([np.cos(a2), np.sin(a2), 0]), stroke_color=ds.HIGH, stroke_width=3.2)
    tl = T('mục tiêu', 'micro', SANS_MED, ds.HIGH).next_to(nums[2], DOWN, buff=0.08)
    return dict(face=face, ring=ring, shade=shade, track=track, ticks=tk, nums=nums, code=code, name=name, unit=unit,
                bez=VGroup(bez, kn, sc), mirror=mirror, glint=gl,
                all=VGroup(bez, kn, sc, face, shade, ring, inner, track, mirror, tk, nums, unit, code, name, tgt, tl, gl), tgt=VGroup(tgt, tl))

def needle_mob(cx, v):
    pts = [P(p) for p in B.needle(cx, v)]
    n = Polygon(*pts, fill_color=ds.INK, fill_opacity=1, stroke_width=0)
    sh = Polygon(*[p + np.array([0.05, -0.06, 0]) for p in pts], fill_color=ds.INK, fill_opacity=0.14, stroke_width=0)
    hub = VGroup(Circle(radius=0.13, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([cx, CY, 0]),
                 Circle(radius=0.045, fill_color=ds.PAPER, fill_opacity=1, stroke_width=0).move_to([cx, CY, 0]))
    return VGroup(sh, n, hub)

def band_mob(cx, lo, hi):
    pts = [P(p) for p in B.gap_arc(cx, lo, hi, r_in=R - 0.36, r_out=R - 0.22, n=12)]
    return Polygon(*pts, fill_color=ds.INK, fill_opacity=0.9, stroke_width=0)

def hand_mob(cx, v):
    p0, p1, d = B.hand(cx, v)
    return VGroup(Line(P(p0), P(p1), stroke_color=ds.LOW, stroke_width=2.2),
                  Polygon(*[P(q) for q in d], fill_color=ds.LOW, fill_opacity=1, stroke_width=0))

def gap_mob(cx, v0, v1):
    col = ds.HIGH if v0 > v1 else ds.LOW
    return Polygon(*[P(p) for p in B.gap_arc(cx, v0, v1)], fill_color=col, fill_opacity=1, stroke_width=0)

class Baro(Scene):
    def construct(self):
        self.camera.background_color = ds.PAPER
        fr = self.camera.frame
        fr.scale(1 / 2.6).move_to([0.0, CY + 1.05, 0])
        D = {b['key']: dial(b) for b in B.BANKS}
        order = [D['ecb'], D['fed'], D['boj']]

        # ---------- A. build the instruments, the camera pulls back --------------------------
        fed = D['fed']
        def build(d, lag):
            return [FadeIn(d['bez'][0]), LaggedStart(*[Create(k) for k in d['bez'][1]], lag_ratio=0.004), FadeIn(d['bez'][2], scale=1.6),
                    DrawBorderThenFill(d['face']), FadeIn(d['shade']), Create(d['ring']), Create(d['all'][6]), Create(d['track']), Create(d['mirror']),
                    LaggedStart(*[Create(t) for t in d['ticks']], lag_ratio=lag)]
        self.play(*build(fed, 0.012), run_time=1.6)
        others = [D['ecb'], D['boj']]
        self.play(fr.animate.scale(2.6).move_to(ORIGIN),
                  LaggedStart(*[FadeIn(n, scale=0.8) for n in fed['nums']], lag_ratio=0.1),
                  *[AnimationGroup(*build(d, 0.01), LaggedStart(*[FadeIn(n) for n in d['nums']], lag_ratio=0.1)) for d in others],
                  run_time=2.0, rate_func=ease_in_out_cubic)
        self.play(*[FadeIn(VGroup(d['code'], d['name'], d['unit']), shift=UP * 0.1) for d in order], *[FadeIn(d['tgt']) for d in order],
                  *[FadeIn(d['glint']) for d in order], run_time=0.5)

        # ---------- HUD ---------------------------------------------------------------------
        L, TOP = -FW / 2 + 0.6, 3.62
        kick = T('LÃI SUẤT ĐIỀU HÀNH VÀ LẠM PHÁT · THÁNG 9/2026, %', 'label', SANS_SEMI, ds.SLATE).move_to([L, TOP, 0], aligned_edge=UL)
        ln = VGroup(Polygon(*[np.array(p) for p in [[0, 0.04, 0], [0.5, 0, 0], [0, -0.04, 0]]], fill_color=ds.INK, fill_opacity=1, stroke_width=0),
                    T('lãi suất điều hành', 'micro', SANS, ds.SLATE),
                    VGroup(Line(ORIGIN, RIGHT * 0.42, stroke_color=ds.LOW, stroke_width=2.2),
                           Polygon(*[np.array(p) for p in [[0.42, 0.06, 0], [0.54, 0, 0], [0.42, -0.06, 0], [0.30, 0, 0]]], fill_color=ds.LOW, fill_opacity=1, stroke_width=0)),
                    T('lạm phát 2026, dự báo IMF', 'micro', SANS, ds.SLATE)).arrange(RIGHT, buff=0.14)
        ln[2].shift(RIGHT * 0.3); ln[3].shift(RIGHT * 0.3)
        ln.move_to([FW / 2 - 0.6, TOP - 0.07, 0], aligned_edge=UR)
        self.play(FadeIn(kick, shift=RIGHT * 0.2), FadeIn(ln), run_time=0.5)

        # ---------- B. needles at the old rates ------------------------------------------------
        trk = {b['key']: ValueTracker(b['before']) for b in B.BANKS}
        num = {b['key']: ValueTracker(b['before']) for b in B.BANKS}
        for v in list(trk.values()) + list(num.values()):
            self.add(v)
        needles = {b['key']: always_redraw(lambda b=b: needle_mob(b['x'], trk[b['key']].get_value())) for b in B.BANKS}
        band = always_redraw(lambda: band_mob(0.0, trk['fed'].get_value() - 0.125, trk['fed'].get_value() + 0.125))
        def readout(b):
            def mk():
                v = num[b['key']].get_value()
                s = f"{vn(v - 0.125)}–{vn(v + 0.125)}%" if b['key'] == 'fed' else f"{vn(v)}%"
                return T(s, 'title', SERIF, ds.INK, SEMIBOLD).move_to([b['x'], CY - R - 0.5, 0])
            return always_redraw(mk)
        reads = {b['key']: readout(b) for b in B.BANKS}
        whats = {b['key']: T(b['country'] + ' · ' + b['what'], 'label', SANS, ds.SLATE).move_to([b['x'], CY - R - 1.0, 0]) for b in B.BANKS}
        self.play(*[FadeIn(needles[k]) for k in needles], FadeIn(band), *[FadeIn(reads[k]) for k in reads],
                  *[FadeIn(whats[k]) for k in whats], run_time=0.6)

        # ---------- C. the three hikes, in date order -----------------------------------------
        chips = {}
        for b in B.BANKS:
            chip = VGroup(T(b['date'], 'sub', SERIF, ds.INK, SEMIBOLD), T('+0,25 điểm %', 'label', SANS_SEMI, ds.HIGH)).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
            chip.move_to([b['x'], CY + R + 0.42, 0])
            chips[b['key']] = chip
        anims = []
        for i, b in enumerate(B.BANKS):
            k = b['key']
            anims.append(Succession(Wait(i * 0.75),
                                    AnimationGroup(FadeIn(chips[k], shift=DOWN * 0.25, run_time=0.45),
                                                   trk[k].animate(run_time=1.1, rate_func=ease_out_back).set_value(b['after']),
                                                   num[k].animate(run_time=0.8, rate_func=smooth).set_value(b['after']))))
        self.play(*anims, run_time=2.6)
        self.wait(0.2)

        # ---------- D. inflation hands and the real-rate gap -----------------------------------
        cpi = {b['key']: ValueTracker(0.0) for b in B.BANKS}
        for v in cpi.values():
            self.add(v)
        hands = {b['key']: always_redraw(lambda b=b: hand_mob(b['x'], cpi[b['key']].get_value())) for b in B.BANKS}
        cpl = {b['key']: T(f"lạm phát {vn(b['cpi'], 1)}%", 'label', SANS_SEMI, ds.LOW).move_to([b['x'], CY - R - 1.4, 0]) for b in B.BANKS}
        self.add(*hands.values())
        self.play(*[cpi[b['key']].animate.set_value(b['cpi']) for b in B.BANKS], *[FadeIn(cpl[k], shift=UP * 0.1) for k in cpl],
                  run_time=1.2, rate_func=ease_out_cubic)
        gaps = {b['key']: gap_mob(b['x'], b['after'], b['cpi']) for b in B.BANKS}
        self.play(*[FadeIn(g, scale=0.9) for g in gaps.values()], run_time=0.7)
        self.wait(0.5)

        # ---------- E. the gaps fall out of the dials and become a chart -----------------------
        for k in needles:
            needles[k].clear_updaters(); hands[k].clear_updaters(); reads[k].clear_updaters()
        band.clear_updaters()
        S, NY = 0.6, 1.9
        instr = {b['key']: VGroup(D[b['key']]['all'], needles[b['key']], hands[b['key']]) for b in B.BANKS}
        instr['fed'].add(band)
        moves = [instr[b['key']].animate.scale(S).move_to([b['x'], NY, 0]) for b in B.BANKS]
        zero = Line([-FW / 2 + 0.6, B.ZERO_Y, 0], [FW / 2 - 0.6, B.ZERO_Y, 0], stroke_color=ds.INK, stroke_width=2.0)
        zl = T('0', 'label', MONO, ds.SLATE).next_to(zero, LEFT, buff=0.12)
        bars, vals = {}, {}
        for b in B.BANKS:
            h = b['real'] * B.PP
            r = Rectangle(width=B.BAR_W, height=abs(h), fill_color=ds.HIGH if h > 0 else ds.LOW, fill_opacity=0.9, stroke_width=0)
            r.move_to([b['x'], B.ZERO_Y + h / 2, 0])
            bars[b['key']] = r
            disp = {'fed': '+0,3', 'ecb': '−0,6', 'boj': '−0,8'}[b['key']]
            v = T(disp, 'title', SERIF, ds.HIGH if h > 0 else ds.LOW, SEMIBOLD)
            v.next_to(r, RIGHT, buff=0.22)
            v.align_to(r, UP if h > 0 else DOWN)
            vals[b['key']] = v
        ylab = T('lãi suất thực, điểm %', 'label', SANS_MED, ds.INK).move_to([-FW / 2 + 0.6, B.ZERO_Y + 0.42, 0], aligned_edge=LEFT)
        # E1 push into the Fed's gap arc
        gc = gaps['fed'].get_center()
        Z = 0.42
        self.play(fr.animate.scale(Z).move_to(gc + np.array([0.0, -0.35, 0])),
                  *[FadeOut(x) for x in list(reads.values()) + list(whats.values()) + list(cpl.values()) + list(chips.values())],
                  FadeOut(ln), FadeOut(kick), run_time=1.3, rate_func=ease_in_out_cubic)
        # E2 track the gap down: the dials rise and shrink, the Fed gap falls out and becomes its bar
        self.play(*moves, ReplacementTransform(gaps['fed'], bars['fed']), Create(zero),
                  fr.animate.move_to([0.0, B.ZERO_Y + 0.55, 0]), run_time=1.4, rate_func=ease_in_out_cubic)
        # E3 pull back: the other two gaps fall into theirs
        self.play(fr.animate.scale(1 / Z).move_to(ORIGIN), FadeIn(zl), FadeIn(ylab), FadeIn(kick),
                  *[ReplacementTransform(gaps[k], bars[k]) for k in ('ecb', 'boj')], run_time=1.5, rate_func=ease_in_out_cubic)
        self.play(LaggedStart(*[FadeIn(vals[k], shift=RIGHT * 0.2) for k in ['ecb', 'fed', 'boj']], lag_ratio=0.2), run_time=0.8)
        head = VGroup(T('Ba lần tăng lãi suất trong chín ngày.', 'sub', SERIF, ds.INK, SEMIBOLD),
                      T('Chỉ ở Mỹ, lãi suất đứng trên lạm phát.', 'sub', SERIF, ds.HIGH, SEMIBOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        head.move_to([L, -2.62, 0], aligned_edge=UL)
        self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.2) for h in head], lag_ratio=0.35), run_time=0.9)
        self.wait(1.3)
