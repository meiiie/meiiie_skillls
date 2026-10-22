// Anatomy smoke test: a plinth and a lit block that slides across it (3 s).
export default (k) => {
  const W = 960, H = 405;
  const P = k.fitProjection([[0, 0, -10], [300, 0, -10], [0, 120, -10], [300, 120, -10], [0, 0, 60], [300, 120, 60]], W, H, { pad: 20 });
  const slab = (x, y, w, d, z, h, o) => k.solidSvg(k.slabOf({ x, y, w, d, r: 2 }, z, h, P, 3, 0.4), o);
  return { width: W, height: H, seconds: 3, theme: "light", label: "smoke", poster: 3,
    frame: (t) => slab(0, 0, 300, 120, -10, 10, { tone: "lo" }) +
                  slab(20 + 200 * Math.min(t / 3, 1), 30, 60, 60, 0, 50, { lit: true }) };
};
