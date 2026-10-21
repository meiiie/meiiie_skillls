"""S3 "Băng ghi khí áp" — a barograph writes world growth 2018-2027 on its turning drum, then the paper
unrolls into the chart (about 17 s).
  cd design/films && manimgx render drum.py Drum -r 2560x1080 --fps 30 -o ../../assets/film/drum.mp4
Data and mappings: drum_geom.py (shared with the native fallback)."""
from kit import *
import drum_geom as D
import math

config.pixel_width, config.pixel_height = 2560, 1080
P3 = lambda x, y: np.array([x, y, 0.0])
CASE = '#D8D2C4'; BRASS = '#C9B98F'; PAPERD = '#F6F3EC'

class Drum(Scene):
    def construct(self):
        self.camera.background_color = ds.PAPER
        fr = self.camera.frame
        tau, flat = ValueTracker(2017.55), ValueTracker(0.0)
        self.add(tau, flat)
        e = lambda: smooth(flat.get_value())
        M = lambda u, g: D.mix(u, g, tau.get_value(), e())

        # ---------------- the instrument (static parts) ----------------
        x0, x1 = D.DCX - D.RD, D.DCX + D.RD
        yb, yt = D.DCY - D.HD / 2, D.DCY + D.HD / 2
        base = VGroup(
            RoundedRectangle(width=13.4, height=0.95, corner_radius=0.08, fill_color=CASE, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.6).move_to([0.2, -2.72, 0]),
            Line([-6.4, -2.38, 0], [6.8, -2.38, 0], stroke_color=ds.INK, stroke_width=0.8),
            Line([-6.4, -3.06, 0], [6.8, -3.06, 0], stroke_color=ds.SLATE, stroke_width=0.6),
            RoundedRectangle(width=4.6, height=0.52, corner_radius=0.06, fill_color='#BDB5A4', fill_opacity=1, stroke_color=ds.INK, stroke_width=1.0).move_to([D.DCX, -2.72, 0]),
            *[RoundedRectangle(width=0.7, height=0.2, corner_radius=0.05, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([x, -3.28, 0]) for x in (-5.9, -2.0, 2.4, 6.3)],
            *[VGroup(Circle(radius=0.07, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.8), Line([-0.05, 0, 0], [0.05, 0, 0], stroke_color=ds.INK, stroke_width=0.9)).move_to([x, -2.72, 0]) for x in (-6.05, -4.75, 0.35, 6.5)],
            # pen lifter
            Line([4.4, -2.38, 0], [4.75, -1.95, 0], stroke_color=ds.INK, stroke_width=2.0),
            Circle(radius=0.09, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([4.75, -1.95, 0]))
        # clockwork: four gears turning with the drum, seen through the window in the base
        def gear(r, n, phase):
            pts = []
            for i in range(n * 4):
                a = phase + 2 * math.pi * i / (n * 4)
                rr = r if (i % 4) in (0, 1) else r * 0.84
                pts.append(P3(rr * math.cos(a), rr * math.sin(a)))
            return Polygon(*pts, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.8)
        GEARS = [(-3.9, 0.21, 18, 1.0), (-3.25, 0.15, 12, -1.5), (-2.65, 0.22, 20, 0.9), (-1.95, 0.13, 10, -1.8), (-1.4, 0.2, 16, 1.1), (-0.75, 0.16, 12, -1.4)]
        def gears():
            g = VGroup()
            for gx, r, n, k in GEARS:
                ph = k * (tau.get_value() - 2017.55) * 3.0
                gg = gear(r, n, ph).move_to([gx, -2.72, 0])
                g.add(gg, Circle(radius=r * 0.35, fill_color=CASE, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.7).move_to([gx, -2.72, 0]),
                      Dot([gx, -2.72, 0], radius=0.025, color=ds.INK),
                      Line([gx, -2.72, 0], [gx + r * 0.3 * math.cos(ph), -2.72 + r * 0.3 * math.sin(ph), 0], stroke_color=ds.INK, stroke_width=0.8))
            return g
        gearm = always_redraw(gears)
        # clock spindle plate and drum flanges
        flanges = VGroup(
            Rectangle(width=2 * D.RD + 0.34, height=0.2, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.4).move_to([D.DCX, yt + 0.1, 0]),
            Rectangle(width=2 * D.RD + 0.34, height=0.2, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.4).move_to([D.DCX, yb - 0.1, 0]),
            Rectangle(width=0.5, height=0.14, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([D.DCX, yt + 0.27, 0]),
            Rectangle(width=1.2, height=0.36, fill_color=CASE, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.2).move_to([D.DCX, yb - 0.38, 0]))
        # brass knurl on flanges
        for yy in (yt + 0.1, yb - 0.1):
            for i in range(48):
                xx = D.DCX + D.RD * math.sin(-math.pi / 2 + math.pi * (i + 0.5) / 48)
                flanges.add(Line([xx, yy - 0.08, 0], [xx, yy + 0.08, 0], stroke_color=ds.INK, stroke_width=0.5, stroke_opacity=0.6))
        drum = Rectangle(width=2 * D.RD, height=D.HD, fill_color=PAPERD, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.4).move_to([D.DCX, D.DCY, 0])
        shade = VGroup()
        for i in range(24):           # cylinder shading: darker toward both edges
            a0 = -math.pi / 2 + math.pi * i / 24; a1 = a0 + math.pi / 24
            xa, xb = D.DCX + D.RD * math.sin(a0), D.DCX + D.RD * math.sin(a1)
            op = 0.20 * (1 - math.cos((a0 + a1) / 2)) ** 1.2
            shade.add(Rectangle(width=xb - xa + 0.004, height=D.HD, fill_color=ds.INK, fill_opacity=op, stroke_width=0).move_to([(xa + xb) / 2, D.DCY, 0]))
        hl = Rectangle(width=0.18, height=D.HD - 0.1, fill_color='#FFFFFF', fill_opacity=0.35, stroke_width=0).move_to([D.DCX - D.RD * 0.42, D.DCY, 0])
        # aneroid stack, pillar, pen arm
        AX, PX, PY = 3.4, 5.4, 0.7
        pillar = VGroup(Rectangle(width=0.24, height=PY + 2.25, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.2).move_to([PX, (PY - 2.25) / 2, 0]),
                        Circle(radius=0.16, fill_color=CASE, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.4).move_to([PX, PY, 0]),
                        Circle(radius=0.05, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([PX, PY, 0]))
        post = VGroup(Rectangle(width=0.5, height=0.22, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([AX, -2.13, 0]),
                    Rectangle(width=2.1, height=0.08, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.8).move_to([AX, -2.3, 0]))
        def nib_y():
            return D.DCY + (D.gval(min(tau.get_value(), 2027.0)) - D.GMID) * D.PPY_D
        def arm_y(x):
            yn = nib_y()
            return PY + (yn - PY) * (PX - x) / (PX - D.DCX)
        def mech():
            yn = nib_y()
            g = VGroup()
            top = arm_y(AX) - 0.42
            n = 8
            for i in range(n):          # aneroid capsules: corrugated discs that breathe with the pen
                yy = -2.02 + (top + 2.02) * (i + 0.5) / n
                h = (top + 2.02) / n * 0.62
                g.add(Ellipse(width=1.7, height=h, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.0).move_to([AX, yy, 0]))
                g.add(Line([AX - 0.72, yy, 0], [AX + 0.72, yy, 0], stroke_color=ds.INK, stroke_width=0.5, stroke_opacity=0.55))
            g.add(Line([AX, -2.02, 0], [AX, top, 0], stroke_color=ds.INK, stroke_width=1.6))
            g.add(Line([AX, top, 0], [AX, arm_y(AX), 0], stroke_color=ds.INK, stroke_width=2.2))
            nut = VGroup(Rectangle(width=0.34, height=0.14, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.8).move_to([AX, top + 0.07, 0]),
                         *[Line([AX - 0.15 + 0.05 * j, top + 0.01, 0], [AX - 0.15 + 0.05 * j, top + 0.13, 0], stroke_color=ds.INK, stroke_width=0.5) for j in range(7)])
            g.add(nut)
            g.add(Circle(radius=0.06, fill_color=ds.PAPER, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.0).move_to([AX, arm_y(AX), 0]))
            # arm, counterweight, nib
            g.add(Line([D.DCX + 0.05, yn, 0], [PX + 0.75, arm_y(PX + 0.75), 0], stroke_color=ds.INK, stroke_width=2.4))
            g.add(Circle(radius=0.2, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([PX + 0.75, arm_y(PX + 0.75), 0]))
            g.add(Polygon(P3(D.DCX, yn), P3(D.DCX + 0.34, yn + 0.09), P3(D.DCX + 0.34, yn - 0.09), fill_color=ds.LOW, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.8))
            g.add(Circle(radius=0.08, fill_color=ds.LOW, fill_opacity=1, stroke_color=ds.INK, stroke_width=0.8).move_to([D.DCX + 0.42, yn, 0]))
            return g
        case = VGroup(RoundedRectangle(width=13.0, height=6.15, corner_radius=0.35, stroke_color=ds.SLATE, stroke_width=1.0).move_to([0.2, 0.83, 0]),
                      Line([-5.9, 3.55, 0], [-4.6, 3.55, 0], stroke_color='#FFFFFF', stroke_width=4, stroke_opacity=0.8),
                      Line([6.55, 2.6, 0], [6.55, 1.4, 0], stroke_color='#FFFFFF', stroke_width=4, stroke_opacity=0.8))

        # ---------------- the paper (everything mapped through D.mix every frame) ----------------
        def paper():
            t, ee = tau.get_value(), e()
            hu = math.pi / 2 * D.RD / D.SPD
            ua = (t - hu) + (2017.5 - (t - hu)) * ee
            ub = (t + hu) + (2027.5 - (t + hu)) * ee
            out = VGroup()
            us = np.linspace(ua, ub, 46)
            # projection band
            pa, pb = max(ua, 2025.5), min(ub, 2027.5)
            if pb > pa:
                uu = np.linspace(pa, pb, 16)
                pts = [P3(*M(u, 7.0)[:2]) for u in uu] + [P3(*M(u, -3.0)[:2]) for u in uu[::-1]]
                out.add(Polygon(*pts, fill_color=ds.LAND, fill_opacity=0.75, stroke_width=0))
            for gl in range(-3, 8):
                pts = [P3(*M(u, gl)[:2]) for u in us]
                w = 1.1 if gl == 0 else (0.8 if gl % 2 == 0 else 0.5)
                out.add(VMobject(stroke_color=ds.INK if gl == 0 else ds.ISOBAR, stroke_width=w, stroke_opacity=0.9 if gl == 0 else 0.6).set_points_as_corners(pts))
            for k in range(int(math.ceil(ua - 0.5)), int(math.floor(ub - 0.5)) + 1):
                u = k + 0.5
                a, b = M(u, -3.0), M(u, 7.0)
                out.add(Line(P3(*a[:2]), P3(*b[:2]), stroke_color=ds.ISOBAR, stroke_width=0.6, stroke_opacity=0.5 * a[2]))
            for k in range(int(math.ceil(ua * 4)), int(math.floor(ub * 4)) + 1):
                u = k / 4
                if k % 4 == 2:
                    continue
                a, b = M(u, -3.0), M(u, 7.0)
                out.add(Line(P3(*a[:2]), P3(*b[:2]), stroke_color=ds.ISOBAR, stroke_width=0.35, stroke_opacity=0.35 * a[2]))
            uc = 2017.25
            if ee < 0.05 and abs((uc - t) * D.SPD / D.RD) < math.pi / 2 * 0.97:
                a, b = M(uc, -3.4), M(uc, 7.4)
                out.add(Line(P3(*a[:2]), P3(*b[:2]), stroke_color=BRASS, stroke_width=7 * a[2] + 1))
                out.add(Line(P3(*a[:2]), P3(*b[:2]), stroke_color=ds.INK, stroke_width=0.6))
            # trace: actual (solid), projection (dashed)
            end = min(t, 2027.0)
            if end > 2018.0:
                st = max(2018.0, (t - hu * 0.96) + (2018.0 - (t - hu * 0.96)) * ee) if ee < 1 else 2018.0
                st = min(st, min(end, 2025.0))
                ua2 = np.linspace(st, min(end, 2025.0), max(2, int((min(end, 2025.0) - st) * 14) + 2))
                out.add(VMobject(stroke_color=ds.INK, stroke_width=3.2).set_points_as_corners([P3(*M(u, D.gval(u))[:2]) for u in ua2]))
            if end > 2025.0:
                u = max(2025.0, (t - hu * 0.96) * (1 - ee) + 2025.0 * ee)
                while u < end:
                    v = min(u + 0.11, end)
                    seg = [P3(*M(w, D.gval(w))[:2]) for w in np.linspace(u, v, 4)]
                    out.add(VMobject(stroke_color=ds.INK, stroke_width=3.2).set_points_as_corners(seg))
                    u += 0.2
            return out
        pap = always_redraw(paper)

        # value marks that ride on the paper
        marks = VGroup()
        for y, g in zip(D.YEARS, D.G):
            col = ds.LOW if g < D.AVG else ds.INK
            dot = Dot(radius=0.06, color=ds.INK).set_stroke(PAPERD, 2, background=True)
            lab = halo(T(D.vn(g), 'body', SERIF, ds.LOW if y == 2026 else (ds.LOW if g < 0 else ds.INK), SEMIBOLD), 6, PAPERD)
            yl = halo(T(str(y), 'micro', MONO, ds.SLATE), 4, PAPERD)
            m = VGroup(dot, lab, yl)
            def upd(mm, y=y, g=g):
                x, yy, c = M(y, g)
                op = 0.0 if tau.get_value() < y - 0.02 else float(np.clip(c * 1.6 - 0.5, 0, 1))
                mm[0].move_to([x, yy, 0]); mm[1].move_to([x, yy + 0.34, 0] if g >= 0 else [x - 0.5, yy + 0.02, 0])
                bx, by, _ = M(y, -3.0)
                mm[2].move_to([bx, by - 0.24, 0])
                for sub in mm:
                    sub.set_opacity(op)
            m.add_updater(upd)
            marks.add(m)

        # ---------------- HUD ----------------
        L, TOP = -FW / 2 + 0.6, 3.62
        kick = T('TĂNG TRƯỞNG GDP THỰC THẾ GIỚI, %', 'label', SANS_SEMI, ds.SLATE).move_to([L, TOP, 0], aligned_edge=UL)
        yrs = VGroup(*[T(str(y), 'display', SERIF, ds.INK, SEMIBOLD).move_to([L, TOP - 0.42, 0], aligned_edge=UL) for y in D.YEARS])
        tag = T('dự báo', 'label', SANS_SEMI, ds.LOW).next_to(yrs[0], DOWN, buff=0.14, aligned_edge=LEFT)
        def yr_upd(g):
            k = int(np.clip(round(tau.get_value() - 2018 + 0.0), 0, 9)) if tau.get_value() >= 2018 else -1
            for i, m in enumerate(g):
                m.set_opacity(1.0 if i == k else 0.0)
        yrs.add_updater(yr_upd)

        # ---------------- A. build, macro on the nib ----------------
        fr.scale(0.36).move_to([D.DCX + 1.4, nib_y() + 0.2, 0])
        mob_mech = always_redraw(mech)
        self.add(drum, shade, hl, pap)
        self.play(FadeIn(drum), FadeIn(shade), Create(pillar), FadeIn(mob_mech), run_time=1.2)
        self.play(fr.animate.scale(1 / 0.36).move_to(ORIGIN), FadeIn(flanges), FadeIn(base), FadeIn(post), FadeIn(gearm), Create(case[0]), FadeIn(case[1:]),
                  tau.animate.set_value(2018.0), run_time=2.0, rate_func=ease_in_out_cubic)
        self.add(marks, yrs)
        self.play(FadeIn(kick, shift=RIGHT * 0.2), run_time=0.4)
        # ---------------- B. the drum turns: 2018 -> 2025 ----------------
        self.play(tau.animate.set_value(2025.0), run_time=6.0, rate_func=linear)
        # ---------------- C. projection ----------------
        self.play(tau.animate.set_value(2027.0), FadeIn(tag, shift=UP * 0.1), run_time=1.8, rate_func=linear)
        self.wait(0.3)
        # ---------------- D. the paper comes off the drum and lies flat ----------------
        mob_mech.clear_updaters(); gearm.clear_updaters()
        instr = VGroup(mob_mech, gearm, pillar, post, flanges, base, case, shade, hl)
        self.play(flat.animate.set_value(1.0), FadeOut(instr, shift=DOWN * 0.4), FadeOut(drum), FadeOut(tag), FadeOut(yrs), run_time=2.2, rate_func=linear)
        ax, ay = D.chart_xy(2017.45, D.AVG)
        bx, _ = D.chart_xy(2027.55, D.AVG)
        avg = DashedLine([ax, ay, 0], [bx, ay, 0], dash_length=0.12, stroke_color=ds.HIGH, stroke_width=2.0)
        avl = VGroup(T('bình quân', 'label', SANS_SEMI, ds.HIGH), T('2008–2017: 3,3', 'label', SANS_SEMI, ds.HIGH)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        avl.move_to([bx + 0.2, ay, 0], aligned_edge=LEFT)
        px, py = D.chart_xy(2026.5, 7.0)
        ptag = T('DỰ BÁO', 'micro', SANS_SEMI, ds.SLATE).move_to([px, py + 0.18, 0])
        ticks = VGroup(*[T(D.vn(g, 0), 'micro', MONO, ds.SLATE).move_to([D.chart_xy(2017.5, g)[0] - 0.28, D.chart_xy(2017.5, g)[1], 0]) for g in (-2, 0, 2, 4, 6)])
        self.play(Create(avg), FadeIn(avl), FadeIn(ptag), FadeIn(ticks), run_time=0.9)
        head = T('2026: tăng 3,1%, dưới mức bình quân 2008–2017.', 'sub', SERIF, ds.INK, SEMIBOLD).move_to([L, -3.3, 0], aligned_edge=DL)
        k26 = marks[8]
        self.play(FadeIn(head, shift=UP * 0.2), Indicate(k26[1], scale_factor=1.25, color=ds.LOW), run_time=1.0)
        self.wait(1.4)
