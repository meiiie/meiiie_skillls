"""S5 "Mực nước nợ" — seven stilling wells fill to each economy's public debt, 2024 -> 2031 (about 17 s).
  cd design/films && manimgx render tide.py Tide -r 2560x1080 --fps 30 -o ../../assets/film/tide.mp4"""
from kit import *
import math
import tide_geom as TG

config.pixel_width, config.pixel_height = 2560, 1080
P3 = lambda x, y: np.array([x, y, 0.0])
WATER, GLASS, BRASS = '#A9B8C8', '#F7F5F0', '#C9B98F'

class Tide(Scene):
    def construct(self):
        self.camera.background_color = ds.PAPER
        fr = self.camera.frame
        lv = {k: ValueTracker(0.0) for k in TG.ORDER}
        clock = ValueTracker(0.0)
        for v in list(lv.values()) + [clock]:
            self.add(v)
        top = TG.y_of(TG.VMAX) + 0.15
        sc = ValueTracker(1.0); self.add(sc)
        AX_, AY_ = 9.1, 0.0
        def X(p):
            k = sc.get_value()
            return np.array([AX_ + (p[0] - AX_) * k, AY_ + (p[1] - AY_) * k, 0.0])
        wells = VGroup()
        for i, k in enumerate(TG.ORDER):
            x = TG.x_of(i)
            g = VGroup()
            g.add(RoundedRectangle(width=TG.WW + 0.3, height=0.3, corner_radius=0.05, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.2).move_to([x, TG.YB - 0.2, 0]))
            g.add(Rectangle(width=TG.WW + 0.5, height=0.12, fill_color=ds.INK, fill_opacity=1, stroke_width=0).move_to([x, TG.YB - 0.41, 0]))
            g.add(Rectangle(width=TG.WW, height=top - TG.YB, fill_color=GLASS, fill_opacity=1, stroke_width=0).move_to([x, (top + TG.YB) / 2, 0]))
            sx = x - TG.WW / 2 + 0.06
            for v in range(0, TG.VMAX + 1, 5):
                y = TG.y_of(v)
                L = 0.26 if v % 50 == 0 else (0.15 if v % 10 == 0 else 0.07)
                g.add(Line([sx, y, 0], [sx + L, y, 0], stroke_color=ds.INK, stroke_width=1.0 if v % 50 == 0 else 0.55))
            for v in (50, 100, 150, 200):
                g.add(T(str(v), 'micro', MONO, ds.SLATE).move_to([sx + 0.46, TG.y_of(v), 0]))
            wells.add(g)
        glass = VGroup()
        for i, k in enumerate(TG.ORDER):
            x = TG.x_of(i)
            g = VGroup(Line([x - TG.WW / 2, TG.YB - 0.05, 0], [x - TG.WW / 2, top, 0], stroke_color=ds.INK, stroke_width=1.6),
                       Line([x + TG.WW / 2, TG.YB - 0.05, 0], [x + TG.WW / 2, top, 0], stroke_color=ds.INK, stroke_width=1.6),
                       Line([x + TG.WW / 2 - 0.12, TG.YB + 0.2, 0], [x + TG.WW / 2 - 0.12, top - 0.2, 0], stroke_color='#FFFFFF', stroke_width=4, stroke_opacity=0.7),
                       RoundedRectangle(width=TG.WW + 0.22, height=0.22, corner_radius=0.04, fill_color=BRASS, fill_opacity=1, stroke_color=ds.INK, stroke_width=1.2).move_to([x, top + 0.08, 0]),
                       *[Dot([x + dx, top + 0.08, 0], radius=0.03, color=ds.INK) for dx in (-0.36, 0.36)],
                       Line([x - 0.1, top + 0.19, 0], [x - 0.1, top + 0.32, 0], stroke_color=ds.INK, stroke_width=1.2),
                       Line([x + 0.1, top + 0.19, 0], [x + 0.1, top + 0.32, 0], stroke_color=ds.INK, stroke_width=1.2),
                       Line([x - 0.2, top + 0.32, 0], [x + 0.2, top + 0.32, 0], stroke_color=ds.INK, stroke_width=1.6))
            glass.add(g)
        names = VGroup(*[T(TG.DEBT[k][0], 'label', SANS_SEMI, ds.INK).move_to([TG.x_of(i), TG.YB - 0.78, 0]) for i, k in enumerate(TG.ORDER)])
        y100 = TG.y_of(100)
        flood = DashedLine([TG.x_of(0) - 0.75, y100, 0], [TG.x_of(6) + 0.75, y100, 0], dash_length=0.14, stroke_color=ds.LOW, stroke_width=2.4)
        flab = VGroup(T('100% GDP', 'label', SANS_SEMI, ds.LOW), T('mực báo động', 'micro', SANS, ds.LOW)).arrange(DOWN, aligned_edge=RIGHT, buff=0.06)
        flab.move_to([TG.x_of(0) - 0.8, y100 + 0.1, 0], aligned_edge=DR)
        def water():
            out = VGroup()
            P3 = lambda x, y: X((x, y))
            ph = clock.get_value()
            for i, k in enumerate(TG.ORDER):
                x, v = TG.x_of(i), lv[k].get_value()
                if v <= 0.2:
                    continue
                yl = TG.y_of(v)
                xs = np.linspace(x - TG.WW / 2, x + TG.WW / 2, 18)
                surf = [P3(xx, yl + 0.025 * math.sin(ph * 5 + xx * 7 + i) + 0.035 * ((2 * (xx - x) / TG.WW) ** 2)) for xx in xs]
                ylo = TG.y_of(min(v, 100))
                if v > 100:
                    out.add(Polygon(P3(x - TG.WW / 2, TG.YB), P3(x + TG.WW / 2, TG.YB), P3(x + TG.WW / 2, ylo), P3(x - TG.WW / 2, ylo), fill_color=WATER, fill_opacity=1, stroke_width=0))
                    out.add(Polygon(*([P3(x - TG.WW / 2, ylo), P3(x + TG.WW / 2, ylo)] + surf[::-1]), fill_color=ds.LOW, fill_opacity=0.82, stroke_width=0))
                else:
                    out.add(Polygon(*([P3(x - TG.WW / 2, TG.YB), P3(x + TG.WW / 2, TG.YB)] + surf[::-1]), fill_color=WATER, fill_opacity=1, stroke_width=0))
                out.add(VMobject(stroke_color=ds.INK, stroke_width=1.6).set_points_smoothly(surf))
                for j in range(3):
                    f = (ph * 0.35 + j / 3 + i * 0.13) % 1
                    yy = TG.YB + 0.1 + f * (yl - TG.YB - 0.2)
                    if yy < yl - 0.1:
                        out.add(Circle(radius=0.035 * sc.get_value(), stroke_color='#FFFFFF', stroke_width=1.0, stroke_opacity=0.9).move_to(X((x - 0.15 + 0.15 * j + 0.04 * math.sin(ph * 3 + j), yy))))
            return out
        wat = always_redraw(water)
        cache = {}
        def lab(s, col):
            if (s, col) not in cache:
                cache[(s, col)] = halo(T(s, 'body', SERIF, col, SEMIBOLD), 6)
            return cache[(s, col)].copy()
        def values():
            out = VGroup()
            P3 = lambda x, y: X((x, y))
            for i, k in enumerate(TG.ORDER):
                v = lv[k].get_value()
                if v < 1:
                    continue
                col = ds.LOW if v > 100 else ds.INK
                m = lab(TG.vn(round(v, 1)), col)
                m.scale(sc.get_value()).move_to(X((TG.x_of(i), TG.VAL_Y)))
                x, y = TG.x_of(i) + TG.WW / 2, TG.y_of(v)
                out.add(m, Polygon(P3(x + 0.02, y), P3(x + 0.2, y + 0.09), P3(x + 0.2, y - 0.09), fill_color=col, fill_opacity=1, stroke_width=0))
            return out
        vals = always_redraw(values)
        L, TOP = -FW / 2 + 0.6, 3.62
        kick = T('NỢ CÔNG GỘP, % GDP', 'label', SANS_SEMI, ds.SLATE).move_to([L, TOP, 0], aligned_edge=UL)
        yr = {y: T(str(y), 'display', SERIF, ds.INK, SEMIBOLD).move_to([L, TOP - 0.42, 0], aligned_edge=UL) for y in TG.YEARS}
        ptag = T('dự báo', 'label', SANS_SEMI, ds.SLATE).next_to(yr[2024], DOWN, buff=0.12, aligned_edge=LEFT)
        skip = T('2028–2030 không hiển thị', 'micro', SANS, ds.SLATE).next_to(ptag, DOWN, buff=0.1, aligned_edge=LEFT)
        def go(idx, rt):
            return [lv[k].animate.set_value(TG.DEBT[k][1][idx]) for k in TG.ORDER] + [clock.animate.set_value(clock.get_value() + rt * 1.2)]
        # A. macro on the flood line in the UK well, pull back
        ig = TG.ORDER.index('GBR')
        fr.scale(0.34).move_to([TG.x_of(ig) - 0.2, y100 + 0.1, 0])
        self.add(wells, wat, glass, vals)
        for i in range(7):
            if i != ig:
                wells[i].set_opacity(0); glass[i].set_opacity(0)
        self.play(Create(flood), lv['GBR'].animate.set_value(99.4), clock.animate.set_value(1.6), run_time=1.6, rate_func=ease_out_cubic)
        self.play(fr.animate.scale(1 / 0.34).move_to(ORIGIN),
                  *[wells[i].animate.set_opacity(1) for i in range(7) if i != ig], *[glass[i].animate.set_opacity(1) for i in range(7) if i != ig],
                  *[lv[k].animate.set_value(TG.DEBT[k][1][0]) for k in TG.ORDER if k != 'GBR'], clock.animate.set_value(4.0),
                  FadeIn(names), FadeIn(flab), FadeIn(kick), FadeIn(yr[2024]), run_time=2.2, rate_func=ease_in_out_cubic)
        # B. year by year
        prev = yr[2024]
        for idx, y in enumerate(TG.YEARS[1:4], 1):
            extra = [FadeIn(ptag, shift=UP * 0.1)] if y == 2026 else []
            self.play(prev.animate.shift(UP * 0.4).set_opacity(0), FadeIn(yr[y], shift=UP * 0.4), *go(idx, 1.15), *extra, run_time=1.15, rate_func=ease_in_out_cubic)
            prev = yr[y]
        self.play(clock.animate.set_value(clock.get_value() + 0.5), run_time=0.4, rate_func=linear)
        # C. jump to 2031
        self.play(prev.animate.shift(UP * 0.4).set_opacity(0), FadeIn(yr[2031], shift=UP * 0.4), FadeIn(skip), *go(4, 2.0), run_time=2.0, rate_func=ease_in_out_cubic)
        # D. push into the US well, read the rise, pull back
        iu = TG.ORDER.index('USA'); xu = TG.x_of(iu)
        a, b = TG.y_of(122.3), TG.y_of(145.0)
        br = VGroup(Line([xu + 0.62, a, 0], [xu + 0.62, b, 0], stroke_color=ds.LOW, stroke_width=2.2),
                    Line([xu + 0.52, a, 0], [xu + 0.72, a, 0], stroke_color=ds.LOW, stroke_width=2.2),
                    Line([xu + 0.52, b, 0], [xu + 0.72, b, 0], stroke_color=ds.LOW, stroke_width=2.2))
        ghost = DashedLine([xu - TG.WW / 2, a, 0], [xu + TG.WW / 2 + 0.1, a, 0], dash_length=0.06, stroke_color=ds.INK, stroke_width=1.2)
        bl = VGroup(T('+22,7', 'sub', SERIF, ds.LOW, SEMIBOLD), T('điểm %', 'micro', SANS, ds.LOW), T('so với 2024', 'micro', SANS, ds.LOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        bl.next_to(br, RIGHT, buff=0.12)
        self.play(fr.animate.scale(0.45).move_to([xu + 0.9, (a + b) / 2 + 0.2, 0]), clock.animate.set_value(clock.get_value() + 1.2), run_time=1.2, rate_func=ease_in_out_cubic)
        self.play(Create(ghost), GrowFromEdge(br, DOWN), FadeIn(bl, shift=RIGHT * 0.15), clock.animate.set_value(clock.get_value() + 1.0), run_time=0.9)
        self.play(clock.animate.set_value(clock.get_value() + 0.7), run_time=0.6, rate_func=linear)
        self.play(fr.animate.scale(1 / 0.45).move_to(ORIGIN), clock.animate.set_value(clock.get_value() + 1.4), run_time=1.3, rate_func=ease_in_out_cubic)
        head = VGroup(*[T(s_, 'sub', SERIF, ds.INK, SEMIBOLD) for s_ in ('Nợ công toàn cầu dự kiến', 'vượt 100% GDP vào năm 2030:', 'mức chỉ từng thấy', 'sau Thế chiến II.')],
                      T('IMF, Giám sát Tài khoá 10/2026', 'micro', SANS, ds.SLATE)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        head.move_to([L, -2.9, 0], aligned_edge=DL)
        A_ = np.array([AX_, AY_, 0])
        noop = lambda m: m
        self.play(FadeOut(VGroup(br, bl, ghost)), sc.animate.set_value(0.8), wells.animate.scale(0.8, about_point=A_), UpdateFromFunc(wat, noop),
                  glass.animate.scale(0.8, about_point=A_), VGroup(names, flood, flab).animate.scale(0.8, about_point=A_), UpdateFromFunc(vals, noop),
                  clock.animate.set_value(clock.get_value() + 1.0), run_time=1.0, rate_func=ease_in_out_cubic)
        self.play(FadeIn(head, shift=UP * 0.2), clock.animate.set_value(clock.get_value() + 1.0), run_time=0.9)
        self.play(clock.animate.set_value(clock.get_value() + 1.6), run_time=1.3, rate_func=linear)
