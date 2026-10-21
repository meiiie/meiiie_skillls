// S6 "Giải phẫu chuỗi chip": an illustrative isometric line from wafer fab to container ship.
// Generic mechanism (minh hoạ), not any company's plant. No words in the drawing: labels are slide text at the anchors.
export default (k) => {
  const W = 1600, H = 675, T = 12, PH = 3;          // 4 stations x 3 s
  const pts = [[-10, -10, -20], [1190, -10, -20], [-10, 210, -20], [1190, 210, -20], [0, 0, 175], [1190, 210, 175], [0, 210, 175]];
  const P = k.fitProjection(pts, W, H, { pad: 14, azimuth: 66 });
  const D = (p) => k.depthOf(p, P);
  const at = (p) => k.iso(p, P);
  const parts = [];
  const add = (depth, svg) => parts.push([depth, svg]);
  const box = (x, y, w, d, z, h, o = {}) => add(D([x + w / 2, y + d / 2, z + h / 2]) + (o.bias || 0),
      k.solidSvg(k.slabOf({ x, y, w, d, r: o.r ?? 1.2 }, z, h, P, 3, 0.4), { tone: o.tone || 'hi', lit: !!o.lit, crease: o.crease || 'faint' }));
  const cyl = (cx, cy, r, z, h, o = {}) => add(D([cx, cy, z + h / 2]) + (o.bias || 0),
      k.solidSvg(k.cylinder(cx, cy, r, z, h, P, 20, 0.3), { tone: o.tone || 'hi', lit: !!o.lit }));
  const line = (a, b, o = {}) => add(D(b) + (o.bias || 0.5), k.lineSvg(k.pathOf([at(a), at(b)]), { tone: o.tone || 'mid', dashed: o.dashed, flow: o.flow }));
  const ease = (u) => u < 0 ? 0 : u > 1 ? 1 : u * u * (3 - 2 * u);

  function frame(t) {
    parts.length = 0;
    const st = Math.floor((t % T) / PH), u = ((t % T) % PH) / PH;
    // ---------------- ground: plinths, apron, water ----------------
    box(-6, 0, 250, 200, -6, 6, { tone: 'lo', bias: -1e4 });
    box(262, 0, 430, 200, -6, 6, { tone: 'lo', bias: -1e4 });
    box(704, 0, 290, 200, -6, 6, { tone: 'lo', bias: -1e4 });
    box(994, -4, 196, 214, -20, 8, { tone: 'faint', bias: -1e4 });
    for (let i = 0; i < 9; i++) line([1000 + i * 21, 6, -12], [1006 + i * 21, 200, -12], { tone: 'faint', bias: -9e3 });
    // ---------------- 1 FAB ----------------
    const fab = st === 0;
    box(14, 34, 196, 132, 0, 92, { lit: fab });
    for (const z of [26, 52, 74]) add(D([210, 100, z]) + 1, k.lineSvg(k.sideSeam({ x: 14, y: 34, w: 196, d: 132, r: 1.2 }, z, P, 3), { tone: 'lo' }));
    box(4, 120, 12, 40, 0, 40, {});                                   // utility annex
    for (let i = 0; i < 5; i++) for (let j = 0; j < 4; j++) {          // fan filter units on the roof
      const cx = 36 + i * 38, cy = 52 + j * 32;
      cyl(cx, cy, 9, 92, 5, { lit: fab && (i + j + Math.floor(t * 4)) % 5 === 0 });
      add(D([cx, cy, 98]) + 0.2, k.dotsSvg([at([cx, cy, 97.2])], { size: 1.2, tone: 'hi' }));
    }
    cyl(190, 150, 11, 92, 34, {}); cyl(190, 150, 13, 124, 3, {});
    cyl(168, 150, 8, 92, 26, {}); cyl(168, 150, 10, 116, 3, {});
    for (let i = 0; i < 7; i++) box(214, 40 + i * 17, 6, 10, 10, 30, { tone: 'mid' });   // loading doors / louvres
    // overhead hoist rail to packaging, with FOUP pods
    for (const x of [228, 262, 296]) box(x, 96, 5, 5, 0, 70, {});
    box(206, 95, 120, 7, 70, 4, { tone: 'hi' });
    for (let i = 0; i < 4; i++) {
      const x = 206 + ((t * 28 + i * 31) % 116);
      box(x, 92, 13, 13, 54, 14, { lit: fab || st === 1 });
      line([x + 6.5, 98, 68], [x + 6.5, 98, 70], { tone: 'hi' });
    }
    // ---------------- 2 PACKAGING ----------------
    const pk = st === 1;
    for (const [x, y] of [[300, 46], [478, 46], [300, 158], [478, 158]]) box(x, y, 7, 7, 0, 40, { tone: 'mid' });
    box(296, 42, 192, 126, 40, 6, {});
    box(330, 62, 120, 86, 46, 2, { tone: 'mid' });                    // carrier tray
    box(352, 72, 82, 66, 48, 3, { lit: pk });                         // substrate
    box(362, 80, 62, 50, 51, 2, {});                                  // interposer
    box(381, 92, 24, 26, 53, 5, { lit: pk });                         // accelerator die
    for (let s = 0; s < 6; s++) {                                     // HBM stacks: 4 dies each, dropping in during step 2
      const sx = s < 3 ? 366 : 410, sy = 84 + (s % 3) * 15;
      const drop = pk ? (1 - ease(u * 1.6 - s * 0.12)) * 34 : (st > 1 ? 0 : 34);
      for (let l = 0; l < 4; l++) box(sx, sy, 10, 11, 53 + l * 2.4 + drop * (1 + l * 0.35), 1.8, { lit: pk && drop > 0.5 });
    }
    for (let i = 0; i < 10; i++) box(338 + i * 11, 142, 6, 4, 48, 3, { tone: 'mid' });   // passives along the edge
    // pick-and-place gantry
    box(306, 40, 8, 8, 46, 76, {}); box(470, 40, 8, 8, 46, 76, {});
    box(306, 40, 172, 8, 122, 8, {});
    const gx = pk ? 360 + 60 * Math.sin(u * Math.PI * 2) : 392;
    box(gx - 9, 34, 18, 20, 106, 18, { lit: pk });
    cyl(gx, 52, 2.5, 74 + (pk ? 10 * Math.abs(Math.sin(u * Math.PI * 4)) : 0), 32, { tone: 'hi' });
    // ---------------- 3 SERVERS ----------------
    const sv = st === 2;
    for (const [x, y] of [[540, 54], [640, 54], [540, 140], [640, 140]]) box(x, y, 6, 6, 0, 160, {});
    box(540, 54, 106, 92, 160, 6, {}); box(540, 54, 106, 92, 0, 6, { tone: 'mid' });
    for (let i = 0; i < 12; i++) {
      const z = 10 + i * 12.4;
      // trays slide in from the front during step 3, leave through the back during step 4, the rack is empty before
      let slide;
      if (sv) slide = (1 - ease(u * 2.2 - i * 0.1)) * 70;
      else if (st === 3) slide = -90 * ease(u * 2.0 - (11 - i) * 0.07);
      else continue;
      if (slide < -86) continue;
      box(546, 58 + slide, 94, 80, z, 9, { lit: sv && slide > 1 });
      const fy = 138 + slide;
      add(D([593, fy, z + 4.5]) + 0.3, k.dotsSvg([0, 1, 2, 3, 4, 5, 6, 7].map((q) => at([552 + q * 5, fy, z + 4.5])), { size: 0.9, tone: 'hi' }));
      add(D([620, fy, z + 4.5]) + 0.3, k.lineSvg(k.pathOf([at([606, fy, z + 3]), at([634, fy, z + 3])]), { tone: 'mid' }));
    }
    add(D([480, 100, 120]), k.wireSvg(at([474, 46, 128]), at([543, 58, 150]), { via: [at([500, 50, 150])], tone: 'mid', flow: true }));
    box(660, 70, 30, 60, 0, 60, { tone: 'mid' });                     // power shelf
    for (let i = 0; i < 4; i++) add(D([690, 80 + i * 14, 40]) + 0.4, k.dotsSvg([at([690, 80 + i * 14, 40])], { size: 1.6, tone: 'hi' }));
    // ---------------- 4 PORT ----------------
    const pt = st === 3;
    for (let c = 0; c < 3; c++) for (let r = 0; r < 4; r++) for (let l = 0; l < 2; l++) {
      if (c === 2 && r === 0 && l === 1) continue;
      box(720 + c * 46, 14 + r * 22, 42, 18, l * 19, 18, { lit: pt && c === 0 && r === 3 && l === 1, tone: (c + r + l) % 3 ? 'hi' : 'mid' });
    }
    // AGV carries a container from the racks to the yard during step 3/4
    const ax = st >= 2 ? 650 + 210 * ease(st === 2 ? u : 1) : 650;
    box(ax, 168, 46, 22, 0, 8, { tone: 'mid' });
    for (const dx of [6, 36]) for (const dy of [168, 190]) cyl(ax + dx, dy, 4, 0, 3, { tone: 'hi' });
    if (st >= 2) box(ax + 2, 170, 42, 18, 8, 18, { lit: st === 2 });
    // quay crane
    for (const [x, y] of [[884, 30], [884, 150], [930, 30], [930, 150]]) box(x, y, 7, 7, 0, 150, {});
    box(884, 30, 53, 127, 150, 6, {});
    box(870, 86, 280, 10, 156, 8, { lit: pt });                       // boom over the ship
    box(884, 80, 20, 22, 164, 16, {});                                // machinery house
    for (let i = 0; i < 6; i++) line([905 + i * 40, 91, 164], [905 + (i + 1) * 40, 91, 156], { tone: 'lo' });
    line([890, 91, 180], [1140, 91, 164], { tone: 'mid' }); line([890, 91, 180], [970, 91, 164], { tone: 'mid' });
    const tx = pt ? 960 + 140 * ease(u * 1.3) : 960;
    const hz = pt ? 110 - 70 * Math.sin(Math.min(1, u * 1.3) * Math.PI) * 0.6 : 110;
    box(tx - 10, 84, 20, 14, 148, 8, { tone: 'hi' });
    line([tx, 91, 148], [tx, 91, hz + 20], { tone: 'hi', bias: 2 });
    box(tx - 22, 82, 44, 18, hz + 18, 3, { tone: 'hi', bias: 2 });     // spreader
    box(tx - 21, 82, 42, 18, hz, 18, { lit: pt, bias: 2 });           // the container on the hook
    // ship
    box(1004, 24, 176, 140, -14, 30, {});
    box(1004, 24, 176, 140, 16, 3, { tone: 'mid' });
    box(1150, 40, 28, 108, 19, 52, {}); box(1152, 56, 24, 76, 71, 10, { tone: 'mid' });
    for (let i = 0; i < 6; i++) box(1153, 50 + i * 15, 2, 8, 50, 12, { tone: 'lo' });
    for (let c = 0; c < 3; c++) for (let r = 0; r < 5; r++) for (let l = 0; l < 2; l++) {
      if (l === 1 && (c + r) % 3 === 0) continue;
      box(1010 + c * 45, 30 + r * 25, 42, 20, 19 + l * 19, 18, { tone: (c * 5 + r + l) % 4 ? 'hi' : 'mid' });
    }
    // ---------------- connective tissue: pipe rack, conveyor, masts, waves ----------------
    for (const x of [40, 90, 140, 190]) box(x, 172, 4, 4, 0, 36, { tone: 'mid' });
    for (let q = 0; q < 3; q++) add(D([120, 174 + q * 0, 36 + q * 5]) + 0.6, k.solidSvg(k.slabOf({ x: 30, y: 172 + q * 0.5, w: 175, d: 4, r: 1.8 }, 36 + q * 5, 3.6, P, 6, 0.2), { tone: 'hi' }));
    box(560, 182, 300, 10, 0, 10, { tone: 'mid' });                   // conveyor bed
    for (let i = 0; i < 15; i++) cyl(568 + i * 20, 187, 3.5, 10, 2, { tone: 'lo' });
    for (let i = 0; i < 4; i++) {
      const cx = 560 + ((t * 40 + i * 75) % 300);
      box(cx, 180, 22, 14, 12, 10, { lit: st === 2 && i === 1 });
    }
    for (const [x, y] of [[712, 6], [860, 196], [1000, 12]]) { box(x, y, 3, 3, 0, 120, { tone: 'mid' }); box(x - 6, y - 2, 15, 7, 120, 3, {}); }
    for (let i = 0; i < 14; i++) line([998, 200 - i * 14, -12], [1186, 200 - i * 14 - 4, -12], { tone: 'lo', bias: -9e3 });
    // second, smaller yard stack and lashing bridge on the ship
    for (let r = 0; r < 3; r++) box(820, 120 + r * 22, 60, 18, 0, 18, { tone: r % 2 ? 'hi' : 'mid' });
    for (let i = 0; i < 4; i++) box(1052 + i * 45, 28, 2, 128, 37, 22, { tone: 'lo' });
    // ---------------- paint far to near ----------------
    parts.sort((a, b) => a[0] - b[0]);
    return parts.map((p) => p[1]).join('');
  }
  return {
    width: W, height: H, seconds: T, theme: 'light', poster: 8.9,
    tokens: {
      '--anatomy-card': '#EEEBE3', '--anatomy-page': '#EEEBE3', '--anatomy-paper': '#EEEBE3',
      '--anatomy-face': '#F8F6F1', '--anatomy-top': '#FFFFFF',
      '--anatomy-shade-0': '#AFA898', '--anatomy-shade-1': '#BFB8AA', '--anatomy-shade-2': '#CEC8BC', '--anatomy-shade-3': '#DCD7CD',
      '--anatomy-lit-top': '#D3DFEE', '--anatomy-lit-shade': '#A9BEDB', '--anatomy-lit': '#1F4F8F',
      '--anatomy-hi': '#151C26', '--anatomy-mid': '#5E6873', '--anatomy-lo': '#9A9FA3', '--anatomy-faint': '#C9C3B6',
      '--anatomy-weight': '1.1px', '--anatomy-halo': '#8a8a80', '--anatomy-dot': '#151C26',
    },
    anchors: (t) => ({ fab: at([110, 34, 130]), pkg: at([392, 42, 128]), rack: at([593, 54, 172]), port: at([1060, 24, 190]) }),
    frame,
  };
};
