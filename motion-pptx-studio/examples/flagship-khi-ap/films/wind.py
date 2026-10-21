"""S4 "Gió mậu dịch" — export winds of 2026 by region, then the stations fly into a ranked chart (about 17 s).
  cd design/films && manimgx render wind.py Wind -r 2560x1080 --fps 30 -o ../../assets/film/wind.mp4"""
from kit import *
import math
import wind_geom as WG

config.pixel_width, config.pixel_height = 2560, 1080
G = json.load(open(HERE / 'pressure_geom.json'))
XY = WG.station_xy()

class Wind(Scene):
    def construct(self):
        self.camera.background_color = ds.PAPER
        V = View(self, -3.6, 1.2, 1.45)
        grat = VGroup(*[poly(g['pts'], stroke_color=ds.RULE, stroke_width=0.9) for g in G['graticule']])
        land = VGroup(*[poly(r, True, fill_color=ds.LAND, fill_opacity=1, stroke_width=0) for r in G['land']])
        bord = VGroup(*[poly(b, stroke_color=ds.PAPER, stroke_width=1.2) for b in G['borders']])
        iso = VGroup(*[poly(c['pts'], c['closed'], stroke_color=ds.LOW if c['level'] < 3.1 else ds.HIGH, stroke_width=1.4, stroke_opacity=0.22) for c in G['frames'][-1]])
        for g in (grat, land, bord, iso):
            V.follow(g)
        # streamlines + comet particles
        lines, comets = VGroup(), VGroup()
        clock = ValueTracker(0.0); self.add(clock)
        meta = []
        for k, n, v, _ in WG.REG:
            col = ds.HIGH if v > 0.5 else (ds.SLATE if v > -1 else ds.LOW)
            for pts in WG.streams(XY[k], v):
                ln = poly(pts, stroke_color=col, stroke_width=1.0, stroke_opacity=0.3)
                lines.add(ln); meta.append((ln, v, col))
        V.follow(lines)
        for i, (ln, v, col) in enumerate(meta):
            sp = 0.08 + 0.05 * abs(v) / 5
            for j in range(3):
                c = VMobject(stroke_color=col, stroke_width=3.6)
                def upd(m_, ln=ln, sp=sp, off=j / 3 + i * 0.17):
                    f = (clock.get_value() * sp + off) % 1
                    a, b = max(0.0, f - 0.16), max(0.001, f)
                    m_.set_points_as_corners([ln.point_from_proportion(a + (b - a) * q / 4) for q in range(5)])
                    m_.set_stroke(opacity=min(1.0, 4 * min(f, 1 - f) + 0.1))
                c.add_updater(upd)
                comets.add(c)
        # stations
        st, labs = {}, {}
        for k, n, v, _ in WG.REG:
            col = ds.HIGH if v > 0.5 else (ds.SLATE if v > -1 else ds.LOW)
            ring = VGroup(Circle(radius=0.17, fill_color=ds.PAPER, fill_opacity=1, stroke_color=col, stroke_width=2.2),
                          Dot(radius=0.06, color=col))
            V.pin(ring, XY[k]); st[k] = ring
            lb = VGroup(halo(T(n if k != 'sa' else 'Nam & Trung Mỹ', 'label', SANS_MED, ds.INK), 6), halo(T(WG.vn(v) + '%', 'sub', SERIF, col, SEMIBOLD), 8)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            V.pin(lb, XY[k], offset=(0.0, -0.62)); labs[k] = lb
        # HUD
        L, TOP = -FW / 2 + 0.6, 3.62
        kick = halo(T('XUẤT KHẨU HÀNG HOÁ 2026 THEO KHU VỰC · KHỐI LƯỢNG, %', 'label', SANS_SEMI, ds.SLATE), 6).move_to([L, TOP, 0], aligned_edge=UL)
        leg = VGroup(Line(ORIGIN, RIGHT * 0.42, stroke_color=ds.HIGH, stroke_width=3.2), halo(T('gió thổi ra: xuất khẩu tăng', 'micro', SANS, ds.SLATE), 5),
                     Line(ORIGIN, RIGHT * 0.42, stroke_color=ds.LOW, stroke_width=3.2), halo(T('gió hút vào: xuất khẩu giảm', 'micro', SANS, ds.SLATE), 5)).arrange(RIGHT, buff=0.14)
        leg[2].shift(RIGHT * 0.25); leg[3].shift(RIGHT * 0.25)
        leg.move_to([L, TOP - 0.5, 0], aligned_edge=UL)
        # A. the map, Old World first
        self.play(LaggedStart(*[Create(g) for g in grat], lag_ratio=0.03), FadeIn(land), FadeIn(bord), FadeIn(iso), FadeIn(kick), run_time=1.4)
        order_a = ['eu', 'af', 'me', 'cis', 'asia']
        self.add(lines, comets)
        self.play(LaggedStart(*[GrowFromCenter(st[k]) for k in order_a], lag_ratio=0.15), LaggedStart(*[FadeIn(labs[k], shift=UP * 0.1) for k in order_a], lag_ratio=0.15),
                  FadeIn(leg), clock.animate.set_value(2.0), run_time=1.6, rate_func=linear)
        self.play(clock.animate.set_value(4.0), V.go(-4.4, 1.0, 1.55), run_time=1.6, rate_func=linear)
        # B. pan east across the Pacific to the Americas
        self.play(V.go(1.5, 0.6, 1.25), clock.animate.set_value(7.5), LaggedStart(*[AnimationGroup(GrowFromCenter(st[k]), FadeIn(labs[k])) for k in ('na', 'sa')], lag_ratio=0.4),
                  run_time=2.6, rate_func=ease_in_out_cubic)
        self.play(V.go(0.0, 0.0, 1.0), clock.animate.set_value(9.5), run_time=1.4, rate_func=ease_in_out_cubic)
        # C. stations fly into a ranked chart
        rows = WG.bar_rows()
        for k in st:
            st[k].clear_updaters(); labs[k].clear_updaters()
        dim = Rectangle(width=FW, height=FH, fill_color=ds.PAPER, fill_opacity=0.82, stroke_width=0)
        zero = Line([WG.ZX, WG.ROW0 + 0.45, 0], [WG.ZX, WG.ROW0 - 6 * WG.DROW - 0.45, 0], stroke_color=ds.INK, stroke_width=2.0)
        wx = WG.ZX + WG.WORLD * WG.PPU
        wl = DashedLine([wx, WG.ROW0 + 0.45, 0], [wx, WG.ROW0 - 6 * WG.DROW - 0.45, 0], dash_length=0.1, stroke_color=ds.INK, stroke_width=1.4)
        wlab = T('thương mại hàng hoá thế giới +3,9', 'micro', SANS_SEMI, ds.INK).next_to(wl, UP, buff=0.06)
        flights, bars, names, vals = [], [], [], []
        for r in rows:
            k, v, y = r['key'], r['v'], r['y']
            col = ds.HIGH if v > 0.5 else (ds.SLATE if v > -1 else ds.LOW)
            flights.append(st[k].animate(path_arc=-0.6).scale(0.7).move_to([WG.ZX, y, 0]))
            w = max(abs(r['x1'] - r['x0']), 0.03)
            bar = Rectangle(width=w, height=0.4, fill_color=col, fill_opacity=0.92, stroke_width=0).move_to([(r['x0'] + r['x1']) / 2 if v != 0 else WG.ZX, y, 0])
            bars.append((bar, LEFT if v > 0 else RIGHT))
            nm = T(r['name'], 'label', SANS_MED, ds.INK)
            vl = T(WG.vn(v), 'sub', SERIF, col, SEMIBOLD)
            if v > 0:
                nm.move_to([WG.ZX - 0.3, y, 0], aligned_edge=RIGHT); vl.move_to([r['x1'] + 0.18, y, 0], aligned_edge=LEFT)
            else:
                nm.move_to([WG.ZX + 0.3, y, 0], aligned_edge=LEFT); vl.move_to([r['x1'] - 0.18, y, 0], aligned_edge=RIGHT)
            names.append(nm); vals.append(vl)
        self.add(dim); self.bring_to_front(*st.values(), kick)
        self.play(FadeIn(dim), FadeOut(VGroup(*labs.values())), FadeOut(leg), *flights, clock.animate.set_value(11.0), run_time=1.6, rate_func=ease_in_out_cubic)
        self.play(Create(zero), *[GrowFromEdge(b, e) for b, e in bars], *[FadeOut(s) for s in st.values()], FadeOut(comets), FadeOut(lines),
                  LaggedStart(*[FadeIn(n, shift=RIGHT * 0.1) for n in names], lag_ratio=0.08), run_time=1.3, rate_func=ease_out_cubic)
        self.play(LaggedStart(*[FadeIn(v, shift=RIGHT * 0.15) for v in vals], lag_ratio=0.08), Create(wl), FadeIn(wlab), run_time=1.0)
        head = VGroup(T('Châu Á góp 4,0 điểm % trong mức tăng 3,9%', 'sub', SERIF, ds.INK, SEMIBOLD),
                      T('của thương mại hàng hoá thế giới.', 'sub', SERIF, ds.INK, SEMIBOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        head.move_to([L, -3.55, 0], aligned_edge=DL)
        self.play(FadeIn(head, shift=UP * 0.2), Indicate(vals[0], scale_factor=1.2, color=ds.HIGH), run_time=1.0)
        self.wait(1.5)
