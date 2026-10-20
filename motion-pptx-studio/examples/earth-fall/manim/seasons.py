"""Seasons: Earth's fixed 23.4° tilt on its orbit (not to scale). Hand-built for the Trái Đất deck."""
import numpy as np
import manimgx as m

BG, INK, MUTED, ICE, SUN, WARM, NIGHT = "#05070B", "#E9EEF5", "#7C8796", "#8FD8FF", "#FFC24B", "#FF6A2B", "#0A1A2E"
FONT = "Be Vietnam Pro"
RX, RY, CY = 4.9, 2.0, -0.25          # projected orbit (oblique view from above the ecliptic)
TILT = 23.4 * m.DEGREES
ER = 0.55                               # Earth radius on screen


def T(s, size=24, color=INK, weight=m.NORMAL):
    return m.Text(s, font=FONT, font_size=size, color=color, weight=weight)


class Seasons(m.Scene):
    def construct(self):
        self.camera.background_color = BG
        # stars: deterministic, faint
        rng = np.random.default_rng(7)
        stars = m.VGroup(*[m.Dot(point=[rng.uniform(-7.1, 7.1), rng.uniform(-4, 4), 0], radius=rng.uniform(0.006, 0.018),
                                 color=INK, fill_opacity=rng.uniform(0.15, 0.5)) for _ in range(140)])
        stars = m.VGroup(*[d for d in stars if not (abs(d.get_center()[1] - CY) < 1.9 and abs(d.get_center()[0]) < 5.6) and not (abs(d.get_center()[0] + 5.3) < 0.8 and d.get_center()[1] > CY + 0.5)])
        self.add(stars)
        orbit = m.Ellipse(width=2 * RX, height=2 * RY, color=ICE, stroke_width=1.6, stroke_opacity=0.55).shift(m.UP * CY)
        glow = m.VGroup(*[m.Circle(radius=0.55 + 0.16 * k, stroke_width=0, fill_color=SUN, fill_opacity=0.10 - 0.018 * k) for k in range(5)])
        sun = m.Circle(radius=0.5, stroke_width=0, fill_color=SUN, fill_opacity=1)
        sungrp = m.VGroup(glow, sun).move_to([0, CY, 0])
        self.play(m.Create(orbit), m.FadeIn(stars, lag_ratio=0.02), run_time=1.6, rate_func=m.smooth)
        self.play(m.GrowFromCenter(sungrp), run_time=0.9)

        theta = m.ValueTracker(np.pi)            # start at June solstice (Earth left of the Sun)

        def pos(th):
            return np.array([RX * np.cos(th), CY + RY * np.sin(th), 0.0])

        # Earth: a disc split by its (fixed) equator into north and south halves; a night half faces away from the Sun
        axis_dir = np.array([np.sin(TILT), np.cos(TILT), 0.0])

        def earth():
            th = theta.get_value()
            c = pos(th)
            warm_n = max(0.0, -np.cos(th))       # June: north hemisphere leans to the Sun
            warm_s = max(0.0, np.cos(th))
            north = m.Sector(radius=ER, start_angle=-TILT, angle=np.pi, stroke_width=0,
                             fill_color=m.interpolate_color(m.ManimColor("#2E6FA8"), m.ManimColor(WARM), 0.85 * warm_n), fill_opacity=1)
            south = m.Sector(radius=ER, start_angle=np.pi - TILT, angle=np.pi, stroke_width=0,
                             fill_color=m.interpolate_color(m.ManimColor("#2E6FA8"), m.ManimColor(WARM), 0.85 * warm_s), fill_opacity=1)
            away = c - np.array([0, CY, 0])
            ang = np.arctan2(away[1], away[0])
            night = m.Sector(radius=ER * 1.001, start_angle=ang - np.pi / 2, angle=np.pi, stroke_width=0,
                             fill_color=NIGHT, fill_opacity=0.72)
            eq = m.Line(-ER * np.array([np.cos(TILT), -np.sin(TILT), 0]), ER * np.array([np.cos(TILT), -np.sin(TILT), 0]),
                        stroke_width=1.2, color=INK, stroke_opacity=0.6)
            ax = m.Line(-axis_dir * ER * 1.75, axis_dir * ER * 1.75, stroke_width=2.2, color=INK)
            np_dot = m.Dot(point=axis_dir * ER * 1.75, radius=0.04, color=INK)
            g = m.VGroup(north, south, night, eq, ax, np_dot)
            g.shift(c)
            return g

        e = m.always_redraw(earth)
        self.play(m.FadeIn(e, scale=0.4), run_time=0.8)
        # tilt annotation
        c0 = pos(np.pi)
        vert = m.DashedLine(c0 + m.DOWN * 0.95, c0 + m.UP * 0.95, color=MUTED, stroke_width=1.4, dash_length=0.07)
        arc = m.Arc(radius=0.82, start_angle=np.pi / 2 - TILT, angle=TILT, color=WARM, stroke_width=2.4).shift(c0)
        tl = T("23,4°", 30, WARM, m.BOLD).next_to(arc, m.UP, buff=0.08).shift(m.LEFT * 1.05)
        self.play(m.Create(vert), m.Create(arc), m.FadeIn(tl, shift=m.UP * 0.15), run_time=0.9)
        jun = T("Tháng 6 · Hạ chí", 22, INK).next_to(c0 + m.RIGHT * ER, m.RIGHT, buff=0.3).shift(m.UP * 0.2)
        jun2 = T("Bắc bán cầu ngả về Mặt Trời", 17, MUTED).next_to(jun, m.DOWN, buff=0.08, aligned_edge=m.LEFT)
        self.play(m.FadeIn(jun, shift=m.UP * 0.1), m.FadeIn(jun2, shift=m.UP * 0.1), run_time=0.6)
        self.wait(0.6)
        self.play(m.FadeOut(vert), m.FadeOut(arc), m.FadeOut(tl), run_time=0.4)

        # the year: June -> Sept -> Dec -> March -> June (counter-clockwise seen from the north)
        labels = {
            3 * np.pi / 2: ("Tháng 9 · Thu phân", None, m.DOWN * 0.95),
            0.0 + 2 * np.pi: ("Tháng 12 · Đông chí", "Nam bán cầu ngả về Mặt Trời", "in"),
            np.pi / 2 + 2 * np.pi: ("Tháng 3 · Xuân phân", None, m.UP * 0.55 + m.RIGHT * 2.6),
        }
        seg = [(np.pi, 3 * np.pi / 2), (3 * np.pi / 2, 2 * np.pi), (2 * np.pi, 5 * np.pi / 2), (5 * np.pi / 2, 3 * np.pi)]
        trail = m.TracedPath(lambda: pos(theta.get_value()), stroke_color=WARM, stroke_width=2.2, stroke_opacity=0.9)
        self.add(trail)
        for a, b in seg:
            self.play(theta.animate.set_value(b), run_time=2.1, rate_func=m.linear)
            key = b
            if key in labels:
                s, sub, off = labels[key]
                p = pos(b)
                if isinstance(off, str):   # inside the orbit, right-aligned toward the sun
                    lab = T(s, 22, INK).next_to(p + m.LEFT * ER, m.LEFT, buff=0.3).shift(m.UP * 0.2)
                else:
                    lab = T(s, 22, INK).move_to(p + off)
                grp = [lab]
                if sub:
                    grp.append(T(sub, 17, MUTED).next_to(lab, m.DOWN, buff=0.08, aligned_edge=m.RIGHT))
                self.play(*[m.FadeIn(x, shift=m.UP * 0.1) for x in grp], run_time=0.45)

        self.wait(2.0)
