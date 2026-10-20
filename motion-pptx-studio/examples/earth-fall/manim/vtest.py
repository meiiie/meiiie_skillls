import manimgx as m
class V(m.Scene):
    def construct(self):
        self.camera.background_color = "#05070B"
        t = m.Text("Hạ chí · Đông chí · 23,4° · Bắc bán cầu", font="Be Vietnam Pro", font_size=40, color="#E9EEF5")
        e = m.Ellipse(width=10, height=3.4, color="#8FD8FF", stroke_width=2).shift(m.DOWN*0.3)
        d = m.Dot(color="#FF6A2B")
        tr = m.ValueTracker(0)
        d.add_updater(lambda o: o.move_to(e.point_from_proportion(tr.get_value() % 1)))
        self.add(e, d, t.to_edge(m.UP))
        self.play(tr.animate.set_value(1), run_time=2, rate_func=m.linear)
