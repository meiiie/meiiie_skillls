"""Plate motion in cross-section: a mid-ocean ridge pushes new crust out, the plate sinks under a continent (not to scale)."""
import numpy as np
import manimgx as m

PAPER, INK, MUTED = "#EDE5D3", "#1E2A33", "#6B6457"
SEA, SEA2 = "#9CC3D9", "#6FA3C4"
CRUST_A, CRUST_B = "#3F4A55", "#7C8894"       # alternating magnetic stripes
CONT, CONT2 = "#B8A27A", "#9C8660"
MANTLE_T, MANTLE_B = "#E9A46A", "#C2502E"
MAGMA = "#FF6A2B"
FONT = "Be Vietnam Pro"

RIDGE_X, TRENCH_X = -2.2, 2.6
TOP, THICK = 0.2, 0.42          # plate top y, plate thickness
DIP = 32 * m.DEGREES
SP = 0.42                        # stripe length
V = 0.32                         # spreading speed (units / s)


def T(s, size=22, color=INK, weight=m.NORMAL):
    return m.Text(s, font=FONT, font_size=size, color=color, weight=weight)


class Plates(m.Scene):
    def construct(self):
        self.camera.background_color = PAPER
        # mantle with horizontal gradient bands
        bands = m.VGroup(*[m.Rectangle(width=14.4, height=0.42, stroke_width=0,
                                       fill_color=m.interpolate_color(m.ManimColor(MANTLE_T), m.ManimColor(MANTLE_B), k / 9), fill_opacity=1)
                           .move_to([0, TOP - THICK - 0.21 - 0.42 * k, 0]) for k in range(10)])
        sea = m.Polygon([-7.2, TOP + 1.25, 0], [TRENCH_X + 0.55, TOP + 1.25, 0], [TRENCH_X + 0.55, TOP - 0.05, 0], [-7.2, TOP - 0.05, 0],
                        stroke_width=0, fill_color=SEA, fill_opacity=1)
        surf = m.Line([-7.2, TOP + 1.25, 0], [TRENCH_X + 0.9, TOP + 1.25, 0], color=SEA2, stroke_width=3)
        self.play(m.FadeIn(bands, lag_ratio=0.08), run_time=1.0)
        self.play(m.GrowFromEdge(sea, m.DOWN), m.Create(surf), run_time=0.8)

        t = m.ValueTracker(0)
        # left plate path: ridge -> left; right plate path: ridge -> trench -> dipping down
        def right_point(s):
            L1 = TRENCH_X - RIDGE_X
            if s <= L1:
                return np.array([RIDGE_X + s, TOP, 0]), 0.0
            d = s - L1
            return np.array([TRENCH_X + d * np.cos(DIP), TOP - d * np.sin(DIP), 0]), -DIP

        def base():
            L1 = TRENCH_X - RIDGE_X
            left = m.Rectangle(width=RIDGE_X + 7.4 - 0.04, height=THICK, stroke_width=0, fill_color=CRUST_B, fill_opacity=1)
            left.move_to([(RIDGE_X - 0.04 - 7.4) / 2, TOP - THICK / 2, 0])
            p1 = [RIDGE_X + 0.04, TOP, 0]; p2 = [TRENCH_X, TOP, 0]
            d = 6.0
            p3 = [TRENCH_X + d * np.cos(DIP), TOP - d * np.sin(DIP), 0]
            q3 = [p3[0] + THICK * np.sin(DIP), p3[1] - THICK * np.cos(DIP), 0]
            q2 = [TRENCH_X + THICK * np.tan(DIP / 2), TOP - THICK, 0]
            q1 = [RIDGE_X + 0.04, TOP - THICK, 0]
            right = m.Polygon(p1, p2, p3, q3, q2, q1, stroke_width=0, fill_color=CRUST_B, fill_opacity=1)
            return m.VGroup(left, right)

        def plates():
            g = m.VGroup()
            off = (t.get_value() * V) % (2 * SP)
            for side in (-1, 1):
                for i in range(0, 14):
                    s = 2 * i * SP + off - SP
                    if s < 0.04:
                        w = SP + s - 0.04
                        if w <= 0.02:
                            continue
                        s0 = 0.04
                    else:
                        w, s0 = SP, s
                    if side < 0:
                        x = RIDGE_X - s0
                        if x - w < -7.6:
                            continue
                        r = m.Rectangle(width=w, height=THICK, stroke_width=0, fill_color=CRUST_A, fill_opacity=1)
                        r.move_to([x - w / 2, TOP - THICK / 2, 0])
                    else:
                        p, ang = right_point(s0 + w / 2)
                        if p[1] < -4.2:
                            continue
                        r = m.Rectangle(width=w, height=THICK, stroke_width=0, fill_color=CRUST_A, fill_opacity=1)
                        r.rotate(ang)
                        r.move_to(p - np.array([-np.sin(ang), np.cos(ang), 0]) * THICK / 2)
                    g.add(r)
            return g

        bs = base()
        pl = m.always_redraw(plates)
        # continent on the right, over the dipping plate
        cont = m.Polygon([TRENCH_X + 0.35, TOP + 0.05, 0], [TRENCH_X + 1.2, TOP + 1.45, 0], [TRENCH_X + 2.3, TOP + 1.7, 0], [3.4 + 2.6, TOP + 1.8, 0],
                         [7.3, TOP + 1.8, 0], [7.3, TOP - 1.9, 0], [TRENCH_X + 3.2, TOP - 1.9, 0],
                         stroke_width=0, fill_color=CONT, fill_opacity=1)
        volcano = m.Polygon([4.05, TOP + 1.45, 0], [4.85, TOP + 2.65, 0], [5.15, TOP + 2.65, 0], [5.95, TOP + 1.5, 0],
                            stroke_width=0, fill_color=CONT2, fill_opacity=1)
        # magma at the ridge
        magma = m.Polygon([RIDGE_X - 0.9, TOP - THICK - 1.3, 0], [RIDGE_X - 0.25, TOP - THICK - 0.2, 0], [RIDGE_X - 0.05, TOP + 0.02, 0], [RIDGE_X + 0.05, TOP + 0.02, 0],
                          [RIDGE_X + 0.25, TOP - THICK - 0.2, 0], [RIDGE_X + 0.9, TOP - THICK - 1.3, 0], stroke_width=0, fill_color=MAGMA, fill_opacity=1)
        self.play(m.GrowFromEdge(magma, m.DOWN), run_time=0.6)
        self.add(bs, pl)
        self.play(m.FadeIn(bs), m.FadeIn(pl), m.FadeIn(volcano), m.FadeIn(cont, shift=m.LEFT * 0.3), run_time=1.0)

        # convection arrows under each plate
        def loop_arrow(cx, cw):
            a = m.CurvedArrow([cx + 1.1 * cw, -2.6, 0], [cx - 1.1 * cw, -2.6, 0], angle=-cw * 2.6, color=INK, stroke_width=2.2)
            return a
        conv = m.VGroup(m.CurvedArrow([RIDGE_X - 0.35, -2.6, 0], [RIDGE_X - 3.0, -1.05, 0], angle=-1.2, color=INK, stroke_width=2.4),
                        m.CurvedArrow([RIDGE_X + 0.35, -2.6, 0], [RIDGE_X + 3.0, -1.05, 0], angle=1.2, color=INK, stroke_width=2.4))
        lab_r = T("Sống núi giữa đại dương", 22, "#FFFFFF", m.BOLD).move_to([RIDGE_X, TOP + 0.85, 0])
        lab_r2 = T("đá nóng chảy trào lên, tạo vỏ mới", 17, "#FFFFFF").next_to(lab_r, m.DOWN, buff=0.08)
        lab_t = T("Hút chìm", 22, INK, m.BOLD).move_to([TRENCH_X - 0.6, -2.3, 0])
        lab_t2 = T("mảng chìm xuống dưới lục địa", 17, INK).next_to(lab_t, m.DOWN, buff=0.08)
        lab_v = T("Núi lửa", 17, INK, m.BOLD).move_to([3.75, TOP + 2.3, 0])
        tick = m.Line([RIDGE_X, TOP + 0.3, 0], [RIDGE_X, TOP + 0.12, 0], color='#FFFFFF', stroke_width=1.5)
        self.play(m.Create(tick), m.FadeIn(lab_r, shift=m.DOWN * 0.1), m.FadeIn(lab_r2), t.animate.set_value(2.0), run_time=2.0, rate_func=m.linear)
        self.play(m.GrowArrow(conv[0]), m.GrowArrow(conv[1]), m.FadeIn(lab_t), m.FadeIn(lab_t2), m.FadeIn(lab_v),
                  t.animate.set_value(4.0), run_time=2.0, rate_func=m.linear)
        # speed callout
        sp = T("≈ 2,5 cm mỗi năm", 32, "#FFFFFF", m.BOLD).move_to([-4.6, -3.05, 0])
        sp2 = T("tốc độ tách giãn ở sống núi Đại Tây Dương", 17, "#FFFFFF").next_to(sp, m.DOWN, buff=0.08)
        arr = m.Arrow([-3.2, TOP - THICK / 2, 0], [-5.4, TOP - THICK / 2, 0], color="#FFFFFF", stroke_width=4, buff=0, max_tip_length_to_length_ratio=0.18)
        self.play(m.FadeIn(sp, shift=m.UP * 0.1), m.FadeIn(sp2), m.GrowArrow(arr), t.animate.set_value(7.0), run_time=3.0, rate_func=m.linear)
        self.play(t.animate.set_value(12.0), run_time=5.0, rate_func=m.linear)
        rise = m.Line([4.9, -1.45, 0], [5.0, TOP + 2.6, 0], color=MAGMA, stroke_width=5)
        plume = m.VGroup(*[m.Circle(radius=0.16 + 0.07 * k, stroke_width=0, fill_color='#8A8070', fill_opacity=0.55 - 0.08 * k).move_to([5.0 + 0.12 * k, TOP + 2.9 + 0.28 * k, 0]) for k in range(4)])
        self.play(m.Create(rise), m.FadeIn(plume, lag_ratio=0.3, shift=m.UP * 0.2), t.animate.set_value(13.5), run_time=1.2, rate_func=m.linear)
        note = T("Sơ đồ không theo tỉ lệ", 14, INK).to_corner(m.DR, buff=0.3).shift(m.LEFT * 1.5)
        self.play(m.FadeIn(note), t.animate.set_value(14.5), run_time=1.0, rate_func=m.linear)
