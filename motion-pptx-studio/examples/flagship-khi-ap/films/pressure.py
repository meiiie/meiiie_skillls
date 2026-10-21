"""S1 "Hai tâm áp" — the 2026 world economy as a pressure chart (about 20 s).
  cd design/films && manimgx render pressure.py Pressure -r 2560x1080 --fps 30 -o ../../assets/film/pressure.mp4
Numbers: IMF WEO Oct 2026 Table A (real GDP growth 2025/2026 by economy, world 3.5 -> 3.1);
WTO press release 8 Oct 2026 (AI-enabling goods = 47% of global merchandise trade growth H1 2026;
Middle East crude exports about -24%, LNG -47%, H1 2026); IMF oil assumption 95.7 USD/bbl (2026).
Isobars: contour lines of growth interpolated between the IMF economies (pressure_geom.py)."""
from kit import *

G = json.load(open(HERE / 'pressure_geom.json'))
E = {e['key']: e for e in G['econ']}
config.pixel_width, config.pixel_height = 2560, 1080

def vn(x, d=1):
    return ('−' if x < 0 else '') + f'{abs(x):.{d}f}'.replace('.', ',')

def xy(k):
    return np.array(E[k]['xy'])

def aim(world_pt, screen_pt, z):
    """camera centre that puts world_pt at screen_pt at zoom z"""
    return np.array(world_pt) - np.array(screen_pt) / z

def ledger(rows, title, x, y, color, width=4.3, note=None):
    """an FT-style ledger: title rule, then name ........ value rows"""
    g = VGroup()
    head = halo(T(title, 'label', SANS_SEMI, ds.SLATE), 6).move_to([x, y, 0], aligned_edge=UL)
    rule = Line([x, y - 0.36, 0], [x + width, y - 0.36, 0], stroke_color=ds.INK, stroke_width=1.6)
    g.add(head, rule)
    items = []
    yy = y - 0.62
    for name, val, col, sub in rows:
        n = halo(T(name, 'body', SANS, ds.INK), 6).move_to([x, yy, 0], aligned_edge=LEFT)
        v = halo(T(val, 'sub', SERIF, col, SEMIBOLD), 6).move_to([x + width, yy, 0], aligned_edge=RIGHT)
        row = VGroup(n, v)
        if sub:
            s = halo(T(sub, 'micro', MONO, ds.SLATE), 5).next_to(n, RIGHT, buff=0.18)
            row.add(s)
        hair = Line([x, yy - 0.27, 0], [x + width, yy - 0.27, 0], stroke_color=ds.RULE, stroke_width=1.0)
        row.add(hair)
        items.append(row)
        g.add(row)
        yy -= 0.56
    return g, head, rule, items

def panel(x0, y0, x1, y1):
    r = Rectangle(width=x1 - x0, height=y0 - y1, fill_color=ds.PAPER, fill_opacity=0.94, stroke_width=0)
    return r.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])

class Pressure(Scene):
    def construct(self):
        self.camera.background_color = ds.PAPER
        V = View(self, 0.0, 0.0, 0.92)

        # ---------- base chart --------------------------------------------------------
        grat = VGroup(*[poly(g['pts'], stroke_color=ds.RULE, stroke_width=0.9) for g in G['graticule']])
        land = VGroup(*[poly(r, True, fill_color=ds.LAND, fill_opacity=1, stroke_width=0) for r in G['land']])
        coast = VGroup(*[poly(r, True, stroke_color='#CCC6B8', stroke_width=0.9) for r in G['land']])
        bord = VGroup(*[poly(b, stroke_color=ds.PAPER, stroke_width=1.2) for b in G['borders']])
        for grp in (grat, land, coast, bord):
            V.follow(grp)

        # ---------- isobars: rebuilt every frame from the precomputed contour frames -----------
        t = ValueTracker(0.0)
        self.add(t)
        nfr = len(G['frames'])
        def build_isobars():
            k = int(round(t.get_value() * (nfr - 1)))
            c, z = V.state()
            world = 3.5 + (3.1 - 3.5) * t.get_value()
            out = VGroup()
            for cc in G['frames'][k]:
                pts = (np.array(cc['pts']) - c[:2]) * z
                col = ds.LOW if cc['level'] < world else ds.HIGH
                out.add(poly(pts, cc['closed'], stroke_color=col, stroke_width=1.8, stroke_opacity=0.8))
            for cc in G['world_line']['2025' if t.get_value() < 0.5 else '2026']:
                pts = (np.array(cc['pts']) - c[:2]) * z
                out.add(poly(pts, cc['closed'], stroke_color=ds.INK, stroke_width=4.0))
            return out

        # ---------- HUD (fixed to the screen) ----------------------------------------------
        L, TOP = -FW / 2 + 0.6, 3.5
        kick = halo(T('TĂNG TRƯỞNG GDP THỰC · ĐƯỜNG ĐỒNG MỨC, %', 'label', SANS_SEMI, ds.SLATE), 6)
        kick.move_to([L, TOP, 0], aligned_edge=UL)
        y202 = halo(T('202', 'display', SERIF, ds.INK, SEMIBOLD), 10)
        y202.move_to([L, TOP - 0.42, 0], aligned_edge=UL)
        d5 = halo(T('5', 'display', SERIF, ds.INK, SEMIBOLD), 10).next_to(y202, RIGHT, buff=0.03).align_to(y202, DOWN)
        d6 = halo(T('6', 'display', SERIF, ds.INK, SEMIBOLD), 10).move_to(d5).align_to(y202, DOWN)
        sw = Line([0, 0, 0], [0.5, 0, 0], stroke_color=ds.INK, stroke_width=4.0)
        wlab = halo(T('thế giới', 'label', SANS, ds.SLATE), 6)
        w35 = halo(T('3,5%', 'sub', SERIF, ds.INK, SEMIBOLD), 8)
        w31 = halo(T('3,1%', 'sub', SERIF, ds.INK, SEMIBOLD), 8)
        sw.move_to([L, TOP - 1.72, 0], aligned_edge=LEFT)
        w35.next_to(sw, RIGHT, buff=0.16).shift(DOWN * 0.0)
        w35.align_to(sw, DOWN).shift(DOWN * 0.13)
        w31.move_to(w35, aligned_edge=LEFT)
        wlab.next_to(w35, RIGHT, buff=0.14).align_to(w35, DOWN)
        leg = VGroup(
            Line([0, 0, 0], [0.42, 0, 0], stroke_color=ds.HIGH, stroke_width=2.4),
            halo(T('trên mức thế giới', 'micro', SANS, ds.SLATE), 5),
            Line([0, 0, 0], [0.42, 0, 0], stroke_color=ds.LOW, stroke_width=2.4),
            halo(T('dưới mức thế giới', 'micro', SANS, ds.SLATE), 5)).arrange(RIGHT, buff=0.14)
        leg[2].shift(RIGHT * 0.25); leg[3].shift(RIGHT * 0.25)
        leg.move_to([L, -3.5, 0], aligned_edge=DL)
        src = halo(T('Nguồn: IMF WEO 10/2026 (Bảng A); WTO 8/10/2026. Đường đồng mức nội suy giữa các nền kinh tế IMF công bố, minh hoạ không gian.', 'micro', SANS, ds.SLATE), 5)
        src.move_to([L, -3.62, 0], aligned_edge=DL)

        # ---------- A. the chart assembles ------------------------------------------------
        self.play(LaggedStart(*[Create(g) for g in grat], lag_ratio=0.04),
                  FadeIn(land, run_time=1.4), V.z.animate.set_value(1.0), run_time=1.6, rate_func=ease_out_cubic)
        self.add(coast, bord)
        # ---------- B. 2025 -----------------------------------------------------------------
        iso0 = build_isobars()
        self.play(LaggedStart(*[Create(p) for p in iso0], lag_ratio=0.1, run_time=1.4),
                  FadeIn(kick, shift=RIGHT * 0.25), FadeIn(VGroup(y202, d5), shift=UP * 0.2),
                  Create(sw), FadeIn(wlab), FadeIn(w35), FadeIn(leg), run_time=1.4)
        self.remove(iso0, *iso0)
        iso = always_redraw(build_isobars)
        self.add(iso)
        self.bring_to_front(kick, y202, d5, sw, wlab, w35, leg)

        # ---------- C. morph to 2026 ----------------------------------------------------------
        lo, hi = G['low']['xy'], G['high']['xy']
        def marker(ch, word, col):
            a = halo(T(ch, 'display', SERIF, col, SEMIBOLD), 12)
            b = halo(T(word, 'micro', SANS_SEMI, col), 6)
            return VGroup(a, b).arrange(DOWN, buff=0.06)
        Tm, Cm = marker('T', 'ÁP THẤP', ds.LOW), marker('C', 'ÁP CAO', ds.HIGH)
        V.pin(Tm, lo); V.pin(Cm, hi)
        self.play(t.animate.set_value(1.0), run_time=2.4, rate_func=ease_in_out_cubic)
        self.play(d5.animate.shift(UP * 0.5).set_opacity(0), FadeIn(d6, shift=UP * 0.5),
                  w35.animate.shift(UP * 0.3).set_opacity(0), FadeIn(w31, shift=UP * 0.3),
                  GrowFromCenter(Tm), GrowFromCenter(Cm), run_time=0.7, rate_func=ease_out_back)
        self.remove(d5, w35)

        # ---------- D. into the Gulf ----------------------------------------------------------
        zg = 2.6
        gulf = (xy('KWT') + xy('QAT') + xy('IRQ')) / 3
        cg = aim(gulf, (-4.6, 0.1), zg)
        pan1 = panel(0.55, 3.0, 5.85, -3.2)
        self.play(V.go(cg[0], cg[1], zg), FadeOut(leg), FadeOut(Tm), FadeOut(Cm), run_time=1.4, rate_func=ease_in_out_cubic)
        self.play(FadeIn(pan1), run_time=0.3)
        # numbered callouts (FT style): a numbered ring on the map, the same number in a ranked ledger, no leaders
        rows = sorted([('Iraq', 'IRQ'), ('Iran', 'IRN'), ('Kuwait', 'KWT'), ('Qatar', 'QAT'), ('UAE', 'ARE'), ('Ả Rập Xê Út', 'SAU')],
                      key=lambda r: E[r[1]]['g2026'])
        lg, head, rule, items = ledger([(n, vn(E[k]['g2026']), ds.LOW, None) for n, k in rows],
                                       'TRUNG ĐÔNG · TĂNG TRƯỞNG 2026, %', 1.45, 2.6, ds.LOW, 4.1)
        def badge(i, fill, ink):
            c = Circle(radius=0.15, fill_color=fill, fill_opacity=1, stroke_color=ds.LOW, stroke_width=1.6)
            return VGroup(c, T(str(i), 'micro', MONO, ink, MEDIUM).move_to(c))
        dots, keys = VGroup(), VGroup()
        for i, ((n, k), row) in enumerate(zip(rows, items), 1):
            d = halo(badge(i, ds.PAPER, ds.LOW), 4)
            V.pin(d, xy(k)); dots.add(d)
            kb = badge(i, ds.LOW, ds.PAPER).scale(0.92).move_to(row[0].get_left() + LEFT * 0.36)
            row.add(kb); keys.add(kb)
        leads = VGroup()
        self.play(FadeIn(head, shift=DOWN * 0.1), Create(rule), LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(r, shift=LEFT * 0.25) for r in items], lag_ratio=0.12),
                  LaggedStart(*[Indicate(d, scale_factor=1.25, color=ds.LOW) for d in dots], lag_ratio=0.12), run_time=1.5)
        oil = VGroup(
            VGroup(halo(T('−24%', 'display', SERIF, ds.LOW, SEMIBOLD), 10), halo(T('xuất khẩu dầu thô', 'label', SANS, ds.INK), 6)).arrange(DOWN, aligned_edge=LEFT, buff=0.12),
            VGroup(halo(T('−47%', 'display', SERIF, ds.LOW, SEMIBOLD), 10), halo(T('xuất khẩu LNG', 'label', SANS, ds.INK), 6)).arrange(DOWN, aligned_edge=LEFT, buff=0.12),
        ).arrange(RIGHT, buff=0.7, aligned_edge=UP)
        oil.move_to([1.1, -1.25, 0], aligned_edge=UL)
        oilsrc = halo(T('Trung Đông, 6 tháng đầu 2026 · WTO', 'micro', SANS, ds.SLATE), 5).next_to(oil, DOWN, buff=0.16, aligned_edge=LEFT)
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.3) for o in oil], lag_ratio=0.25), FadeIn(oilsrc), run_time=1.0, rate_func=ease_out_cubic)
        self.wait(0.35)

        # ---------- E. across to East Asia and the Pacific -----------------------------------
        self.play(FadeOut(VGroup(lg, leads, oil, oilsrc, pan1)), FadeOut(dots), run_time=0.4)
        za = 1.9
        asia = np.array([-2.05, 0.68])
        ca = aim(asia, (-4.4, -0.6), za)
        self.play(V.go(ca[0], ca[1], za), run_time=1.4, rate_func=ease_in_out_cubic)
        pan2 = panel(0.1, 3.0, 9.0, -3.25)
        pan2 = panel(1.2, 3.0, 9.0, -1.15)
        LAB = [('Đài Loan', 'TWN', 'r'), ('Hàn Quốc', 'KOR', 'u'), ('Nhật Bản', 'JPN', 'r'), ('Việt Nam', 'VNM', 'l'),
               ('Trung Quốc', 'CHN', 'l')]     # five economies of the AI chain; India and Indonesia cut (density)
        dots2, labs2 = VGroup(), VGroup()
        for n, k, side in LAB:
            col = ds.VN if k == 'VNM' else (ds.HIGH if E[k]['g2026'] >= 3.1 else ds.LOW)
            d = Dot(radius=0.06, color=col).set_stroke(ds.PAPER, 2.5, background=True)
            V.pin(d, xy(k)); dots2.add(d)
            nm = halo(T(n, 'label', SANS_MED, ds.INK), 6)
            val = halo(T(vn(E[k]['g2026']), 'sub', SERIF, col, SEMIBOLD), 8)
            g = VGroup(nm, val).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
            if k == 'VNM':
                g = VGroup(g, halo(T('IMF; World Bank: 7,4', 'micro', SANS, ds.SLATE), 5)).arrange(DOWN, aligned_edge=RIGHT, buff=0.08)
            p = d.get_center()
            if side == 'r':
                g.next_to(p, RIGHT, buff=0.16)
            elif side == 'l':
                g.next_to(p, LEFT, buff=0.16)
            else:
                g.next_to(p, UP, buff=0.14)
            labs2.add(g)
        # AI flows across the Pacific
        flows = VGroup()
        for f in G['flows']:
            a, b, c2 = [np.array([p[0], p[1], 0.0]) for p in f]
            flows.add(VMobject(stroke_color=ds.HIGH, stroke_width=1.6, stroke_opacity=0.55).set_points_smoothly([a, b, c2]))
        V.follow(flows)
        clock = ValueTracker(0.0)
        self.add(clock)
        parts = VGroup()
        for i, fl in enumerate(flows):
            for j in range(5):
                p = Dot(radius=0.045, color=ds.HIGH)
                off = j / 5 + i * 0.07
                p.add_updater(lambda m_, fl=fl, off=off: m_.move_to(fl.point_from_proportion((clock.get_value() * 0.32 + off) % 1)))
                parts.add(p)
        hero = halo(T('47%', 'hero', SERIF, ds.HIGH, SEMIBOLD), 14)
        hero.move_to([1.65, 2.45, 0], aligned_edge=UL)
        cap = VGroup(T('mức tăng thương mại hàng hoá toàn cầu', 'body', SANS, ds.INK),
                     T('6 tháng đầu 2026 đến từ hàng hoá phục vụ AI', 'body', SANS, ds.INK),
                     T('chip bán dẫn, máy chủ… · WTO, 8/10/2026', 'micro', SANS, ds.SLATE)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        cap.next_to(hero, DOWN, buff=0.3, aligned_edge=LEFT).shift(RIGHT * 0.08)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots2], lag_ratio=0.08), clock.animate.set_value(0.5), run_time=0.5, rate_func=linear)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.12) for l in labs2], lag_ratio=0.12),
                  LaggedStart(*[Create(f) for f in flows], lag_ratio=0.2), clock.animate.set_value(1.9), run_time=1.3, rate_func=linear)
        self.add(parts)
        self.add(pan2)
        self.play(FadeIn(pan2), FadeIn(hero, scale=0.92), LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in cap], lag_ratio=0.15),
                  clock.animate.set_value(3.2), run_time=1.0, rate_func=linear)
        self.play(clock.animate.set_value(4.0), run_time=0.7, rate_func=linear)

        # ---------- F. pull back: the two forces ----------------------------------------------
        self.play(FadeOut(VGroup(labs2, hero, cap, pan2)), FadeOut(dots2), clock.animate.set_value(4.4), run_time=0.35, rate_func=linear)
        self.play(V.go(0.0, 0.0, 1.0), clock.animate.set_value(6.2), FadeIn(leg), FadeIn(Tm), FadeIn(Cm), run_time=1.4, rate_func=ease_in_out_cubic)
        end = VGroup(halo(T('Một vùng áp thấp năng lượng, một vùng áp cao AI.', 'sub', SERIF, ds.INK, SEMIBOLD), 10)).move_to([L, -2.85, 0], aligned_edge=DL)
        self.play(FadeIn(end, shift=UP * 0.2), Indicate(Tm, scale_factor=1.12, color=ds.LOW), Indicate(Cm, scale_factor=1.12, color=ds.HIGH),
                  clock.animate.set_value(7.4), run_time=0.9, rate_func=linear)
        self.play(clock.animate.set_value(8.2), run_time=0.8, rate_func=linear)
