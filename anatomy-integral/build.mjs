import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "./vendor/iso-kit.mjs";
import * as G from "./vendor/lathe.mjs";
import * as A from "./vendor/audit.mjs";
import {
  assertModel,
  CRANK,
  DISC_H,
  DISC_R,
  DISC_Z,
  DISK,
  GEARS,
  HANDLE_R,
  HOLE_R,
  K,
  KNOB_R,
  PIN_C,
  PIN_R,
  PLATE,
  PLATE_H,
  FOOT_H,
  SHAFT_R,
  WHEEL_HALF,
  WHEEL_R,
  WHEEL_X0,
  WHEEL_Z,
  handleAt,
  layout,
  pinAt,
  readoutOf,
} from "./model.mjs";

assertModel();

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";
const WIDTH = 680;
const HEIGHT = 440;
const DIAL = { x: 70, y: 1, z: 23, h: 6.4, r: 12.5 };
const DIAL_TOP = DIAL.z + DIAL.h;
const PER_TURN = 2;

const P = k.fitProjection(
  [
    ...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0),
    [DIAL.x, DIAL.y, DIAL_TOP + 1],
    [CRANK.x, CRANK.y - HANDLE_R, DISC_Z + 8],
    [WHEEL_X0 + PIN_R, 0, 32],
    [-36, -7, WHEEL_Z + 8],
    [DISK.x, 40, 18],
  ],
  WIDTH,
  HEIGHT,
  { pad: 28, azimuth: 50, elevation: 36 },
);

const scene = layout(0);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const lineOnTop = k.lineOnTop;
const segment = k.segment;
const solidSvg = k.solidSvg;
const extrude = k.extrude;
const at = (point) => k.iso(point, P);
const planOf = (part, r = 0.7) => ({ x: part.x, y: part.y, w: part.w, d: part.d, r });
const find = (name) => scene.boxes.find((part) => part.name === name) ?? scene.cyls.find((part) => part.name === name);
const many = (prefix, list = scene.boxes) => list.filter((part) => part.name.startsWith(prefix));

function slab(part, tone, { bevel = 0.45, steps = 4, r = 0.7, crease = "faint", seam = 0, lit = false } = {}) {
  const plan = planOf(part, r);
  const inner = seam ? L(k.sideSeam(plan, part.z + seam, P, steps), { tone: "faint" }) : "";
  return S(k.slabOf(plan, part.z, part.h, P, steps, bevel), { tone, crease, inner, lit });
}

function rodSvg(part, tone = "mid") {
  const frame = G.frameAlong([0, part.y, part.z], [1, 0, 0]);
  return S(G.disc(part.x0, part.x1, part.r, frame, P), { tone, crease: "none" });
}

function diskMark(x) {
  const s = Math.sin(x);
  const c = Math.cos(x);
  return lineOnTop([DISK.x + s * 5.4, DISK.y + c * 5.4], [DISK.x + s * (DISK.r - 0.15), DISK.y + c * (DISK.r - 0.15)], DISK.z1, P);
}

function crankMark(x) {
  const s = Math.sin(x);
  const c = Math.cos(x);
  const z = DISC_Z + DISC_H;
  return lineOnTop([CRANK.x + s * 2.5, CRANK.y + c * 2.5], [CRANK.x + s * (PIN_R - PIN_C), CRANK.y + c * (PIN_R - PIN_C)], z, P);
}

function spokeAt(phi) {
  const c = Math.cos(phi);
  const n = Math.sin(phi);
  const x = WHEEL_X0 + WHEEL_HALF;
  return segment([x, HOLE_R * c, WHEEL_Z + HOLE_R * n], [x, WHEEL_R * c, WHEEL_Z + WHEEL_R * n], P);
}

function needleAt(turns) {
  const angle = turns * Math.PI * 2;
  const sx = Math.sin(angle);
  const sy = -Math.cos(angle);
  return lineOnTop([DIAL.x + sx * 2.3, DIAL.y + sy * 2.3], [DIAL.x + sx * 9.1, DIAL.y + sy * 9.1], DIAL_TOP + 0.22, P);
}

function armSvg(angle) {
  const dx = -Math.sin(angle);
  const dy = -Math.cos(angle);
  const px = -dy;
  const py = dx;
  const w = 1.25;
  const r0 = DISC_R - 0.15;
  const r1 = HANDLE_R - KNOB_R + 0.15;
  const a = [CRANK.x + dx * r0, CRANK.y + dy * r0];
  const b = [CRANK.x + dx * r1, CRANK.y + dy * r1];
  const ring = [
    [a[0] + px * w, a[1] + py * w],
    [b[0] + px * w, b[1] + py * w],
    [b[0] - px * w, b[1] - py * w],
    [a[0] - px * w, a[1] - py * w],
  ];
  return solidSvg(extrude(ring, DISC_Z + 0.85, 2.15, P, { bevel: 0.25 }), { tone: "mid" });
}

function plate() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  const flanges = many("stand.flange", scene.cyls);
  const foots = many("stand.foot", scene.cyls);
  const pairs = flanges.map((flange, index) => ({ flange, foot: foots[index] }));
  pairs.sort((a, b) => k.depthOf([a.flange.x, a.flange.y, 0], P) - k.depthOf([b.flange.x, b.flange.y, 0], P));
  for (const { flange, foot } of pairs) {
    out.push(S(k.cylinder(flange.x, flange.y, flange.r, flange.z, flange.h, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(foot.x, foot.y, foot.r, foot.z, foot.h, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.5), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }));
  const screws = k.corners(PLATE, 12);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.15, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.48 }));
  return out.join("");
}

function labelAndRuler() {
  const label = find("label");
  const ruler = find("ruler");
  const out = [];
  out.push(slab(label, "lo", { bevel: 0, steps: 3, r: 0.8, crease: "none" }));
  out.push(L(k.planOutline(k.insetPlan(planOf(label, 0.8), 1.5), label.z + label.h, P, 3), { tone: "faint" }));
  const rules = [16, 12, 9];
  rules.forEach((length, index) => {
    out.push(L(k.lineOnTop([label.x + 2.2, label.y + 3.2 + index * 3.2], [label.x + 2.2 + length, label.y + 3.2 + index * 3.2], label.z + label.h, P), { tone: "lo", free: true }));
  });
  out.push(D([at([label.x + 2.2, label.y + 2.2, label.h]), at([label.x + label.w - 2.2, label.y + 2.2, label.h])], { size: 0.42 }));
  out.push(slab(ruler, "lo", { bevel: 0, steps: 3, r: 0.6, crease: "none" }));
  const ruleY = ruler.y + 0.85;
  const ruleZ = ruler.z + ruler.h;
  const ruleX0 = ruler.x + 1.5;
  const ruleX1 = ruler.x + ruler.w - 1.5;
  out.push(L(k.lineOnTop([ruleX0, ruleY], [ruleX1, ruleY], ruleZ, P), { tone: "lo" }));
  out.push(D([at([ruleX0, ruleY, ruleZ]), at([ruleX1, ruleY, ruleZ])], { size: 0.42 }));
  const ticks = k.topTicks(ruleX0, ruleX1, 4, 5, ruleY, ruleZ, [1.7, 2.35], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  return out.join("");
}

function gearTrain() {
  const order = GEARS.map((_, index) => index).sort((a, b) => k.depthOf([GEARS[a].x, GEARS[a].y, 1], P) - k.depthOf([GEARS[b].x, GEARS[b].y, 1], P));
  const out = [];
  for (const index of order) {
    const axle = find(`gear.axle.${index}`);
    const gear = find(`gear.${index}`);
    out.push(S(k.cylinder(axle.x, axle.y, axle.r, axle.z, axle.h, P, 20), { tone: "mid", crease: "none" }));
    out.push(S(k.cylinder(gear.x, gear.y, gear.r, gear.z, gear.h, P, 40, 0.28), { tone: "mid" }));
    const top = gear.z + gear.h;
    const root = gear.r * 0.64;
    out.push(L(k.ring(gear.x, gear.y, root, top, P, 36), { tone: "lo" }));
    out.push(L(k.ring(gear.x, gear.y, gear.r, top, P, 48), { tone: "faint" }));
    const teeth = k.radialTicks(gear.x, gear.y, gear.r, 24, 6, top, [gear.r - root, gear.r - root], P);
    out.push(L(teeth.minor, { tone: "lo" }));
    out.push(L(teeth.major, { tone: "mid" }));
  }
  return out.join("");
}

function crankDisc() {
  const top = DISC_Z + DISC_H;
  const out = [];
  out.push(S(k.cylinder(CRANK.x, CRANK.y, DISC_R, DISC_Z, DISC_H, P, 48, 0.35), { tone: "mid" }));
  out.push(L(k.ring(CRANK.x, CRANK.y, 2.5, top, P, 20), { tone: "lo" }));
  out.push(L(k.ring(CRANK.x, CRANK.y, PIN_R, top, P, 40), { tone: "faint" }));
  const bolts = [0, 1, 2, 3, 4, 5].map((index) => {
    const angle = (index / 6) * Math.PI * 2 + 0.4;
    return at([CRANK.x + Math.sin(angle) * 8.2, CRANK.y + Math.cos(angle) * 8.2, top]);
  });
  out.push(D(bolts, { size: 0.42 }));
  return out.join("");
}

function carriageSvg(names) {
  return names
    .map((name) => {
      const part = find(name);
      if (name === "beam" || name === "riser" || name === "bridge") return slab(part, "mid", { bevel: 0.4, steps: 4, r: 0.8, seam: name === "riser" ? part.h * 0.45 : 0 });
      if (name.startsWith("finger")) return slab(part, "mid", { bevel: 0.3, steps: 3, r: 0.4 });
      return slab(part, "mid", { bevel: 0.35, steps: 3, r: 0.55 });
    })
    .join("");
}

function pinShaft() {
  const pin = pinAt(0);
  const top = DISC_Z + DISC_H;
  return [
    S(k.cylinder(pin[0], pin[1], PIN_C, top, find("pin.shaft").h, P, 16), { tone: "hi", crease: "none" }),
    L(k.ring(pin[0], pin[1], PIN_C, top, P, 16), { tone: "lo" }),
  ].join("");
}

function pinHead() {
  const pin = pinAt(0);
  const head = find("pin.head");
  return S(k.cylinder(pin[0], pin[1], head.r, head.z, head.h, P, 20, 0.2), { tone: "hi" });
}

function diskSvg() {
  const hub = find("hub");
  const out = [];
  out.push(S(k.cylinder(hub.x, hub.y, hub.r, hub.z, hub.h, P, 28), { tone: "mid", crease: "none" }));
  out.push(L(k.sideArc(hub.x, hub.y, hub.r, hub.z + hub.h * 0.5, P, 16), { tone: "faint" }));
  out.push(S(k.cylinder(DISK.x, DISK.y, DISK.r, DISK.z0, DISK.z1 - DISK.z0, P, 72, 0.75), { tone: "mid", crease: "lo" }));
  out.push(L(k.ring(DISK.x, DISK.y, 5.4, DISK.z1, P, 28), { tone: "lo" }));
  out.push(L(k.ring(DISK.x, DISK.y, DISK.r - 0.15, DISK.z1, P, 72), { tone: "faint" }));
  return out.join("");
}

function bearingBase() {
  return slab(find("bearing.base"), "mid", { bevel: 0.5, steps: 4, r: 1, seam: 8 });
}

function shaftPiece(x0, x1) {
  const frame = G.frameAlong([0, 0, WHEEL_Z], [1, 0, 0]);
  return S(G.disc(x0, x1, SHAFT_R, frame, P), { tone: "hi", crease: "none" });
}

function bearingCap() {
  const cap = find("bearing.cap");
  return [
    slab(cap, "mid", { bevel: 0.4, steps: 4, r: 1 }),
    D([at([cap.x + 2.2, cap.y + 2.2, cap.z + cap.h]), at([cap.x + cap.w - 2.2, cap.y + 2.2, cap.z + cap.h])], { size: 0.42 }),
  ].join("");
}

function wheelSvg() {
  const frame = G.frameAlong([WHEEL_X0, 0, WHEEL_Z], [1, 0, 0]);
  const face = WHEEL_HALF;
  return [
    S(G.ringBand(-WHEEL_HALF, WHEEL_HALF, HOLE_R, WHEEL_R, frame, P, { bevel: 0.18 }), { tone: "hi", lit: true, crease: "lo" }),
    L(G.circleOf(frame, face, WHEEL_R, P, 96), { tone: "lo" }),
    L(G.circleOf(frame, face, HOLE_R, P, 32), { tone: "lo" }),
    `<path data-part="spoke" class="iso-line" data-tone="hi" d="${spokeAt(0)}"/>`,
  ].join("");
}

function dialSvg() {
  const casePart = find("case");
  const out = [];
  out.push(slab(casePart, "mid", { bevel: 0.8, steps: 5, r: 1.6, seam: 11 }));
  out.push(D([
    at([casePart.x + 3, casePart.y + 3, casePart.h]),
    at([casePart.x + casePart.w - 3, casePart.y + 3, casePart.h]),
  ], { size: 0.45 }));
  out.push(S(k.cylinder(DIAL.x, DIAL.y, DIAL.r, DIAL.z, DIAL.h, P, 64, 0.7), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(DIAL.x, DIAL.y, DIAL.r, DIAL_TOP - 2.2, DIAL_TOP, 72, P, 0), { tone: "lo" }));
  out.push(L(k.sideArc(DIAL.x, DIAL.y, DIAL.r, DIAL_TOP - 2.2, P, 36), { tone: "faint" }));
  out.push(L(k.ring(DIAL.x, DIAL.y, DIAL.r - 1.8, DIAL_TOP, P, 64), { tone: "lo" }));
  out.push(L(k.ring(DIAL.x, DIAL.y, 2.3, DIAL_TOP, P, 20), { tone: "mid" }));
  const ticks = k.radialTicks(DIAL.x, DIAL.y, DIAL.r - 1.8, 20, 5, DIAL_TOP, [1.2, 2.05], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(k.faceTextSvg(k.topMatrix([DIAL.x, DIAL.y + 6.4], DIAL_TOP, P, "x"), "∫", { size: 3.1, tone: "mid", anchor: "middle" }));
  out.push(`<path data-part="needle" class="iso-line" data-tone="hi" data-free="end" d="${needleAt(0)}" style="stroke-width:1.2"/>`);
  return out.join("");
}

function scaleSvg() {
  const scale = find("scale");
  const out = [];
  for (const post of many("scale.post", scene.cyls)) out.push(S(k.cylinder(post.x, post.y, post.r, post.z, post.h, P, 16), { tone: "mid" }));
  out.push(slab(scale, "lo", { bevel: 0, steps: 2, r: 0.4, crease: "none" }));
  for (const mark of [14, 17, 20, 23, 26]) {
    out.push(L(k.lineOnTop([mark, scale.y], [mark, scale.y + scale.d], scale.z + scale.h, P), { tone: mark % 6 === 2 ? "mid" : "lo" }));
  }
  return out.join("");
}

function indexSvg() {
  const post = find("index.post");
  return [
    S(k.cylinder(post.x, post.y, post.r, post.z, post.h, P, 20), { tone: "mid" }),
    slab(find("index.arm"), "mid", { bevel: 0.25, steps: 3, r: 0.4 }),
  ].join("");
}

function handleSvg() {
  const [x, y] = handleAt(0);
  const handle = find("handle");
  return [
    S(k.cylinder(x, y, handle.r, handle.z, handle.h, P, 24, 0.25), { tone: "mid" }),
    L(k.knurl(x, y, handle.r, handle.z, handle.z + handle.h, 16, P, 0), { tone: "lo" }),
    L(k.ring(x, y, handle.r, handle.z + handle.h, P, 24), { tone: "lo" }),
    L(k.lineOnTop([x - handle.r, y], [x + handle.r, y], handle.z + handle.h, P), { tone: "hi" }),
  ].join("");
}

function stopsAndRods() {
  const out = [];
  for (const name of ["rear.rod", "front.rod"]) out.push(rodSvg(scene.rods.find((part) => part.name === name)));
  for (const post of [...many("rear.post", scene.cyls), ...many("front.post", scene.cyls)]) {
    out.push(S(k.cylinder(post.x, post.y, post.r, post.z, post.h, P, 20), { tone: "mid" }));
  }
  for (const stop of many("rear.stop")) out.push(slab(stop, "mid", { bevel: 0.3, steps: 3, r: 0.4 }));
  return out.join("");
}

const carriageBack = carriageSvg(["beam", "drop", "yoke.far", "yoke.left"]);
const carriageYoke = carriageSvg(["yoke.right", "yoke.near"]);
const carriageMid = carriageSvg(["riser", "finger.left"]);
const carriageFront = carriageSvg(["finger.right", "bridge", "arm", "front.shoe", "pointer"]);

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "A wheel-and-disk integrator. Turning the crank advances x. A Scotch yoke sets the wheel's contact radius to 6 times 2 plus sine x, and the dial needle shows the integral 2x plus 1 minus cosine x.",
  body: [
    plate(),
    labelAndRuler(),
    stopsAndRods(),
    bearingBase(),
    gearTrain(),
    crankDisc(),
    scaleSvg(),
    indexSvg(),
    `<g data-move="carriage">${carriageBack}</g>`,
    `<g data-move="pin">${pinShaft()}</g>`,
    `<g data-move="carriage">${carriageYoke}</g>`,
    `<g data-move="pin">${pinHead()}</g>`,
    diskSvg(),
    `<g data-part="shaft-back">${shaftPiece(-30, WHEEL_X0 - WHEEL_HALF)}</g>`,
    bearingCap(),
    `<g data-move="carriage">${carriageMid}</g>`,
    `<g data-move="carriage">${wheelSvg()}</g>`,
    `<g data-part="shaft-front">${shaftPiece(WHEEL_X0 + WHEEL_HALF, 54)}</g>`,
    `<g data-move="carriage">${carriageFront}</g>`,
    dialSvg(),
    `<g data-move="handle">${handleSvg()}</g>`,
    `<g data-part="arm">${armSvg(0)}</g>`,
    `<path data-part="disk-mark" class="iso-line" data-tone="hi" d="${diskMark(0)}"/>`,
    `<path data-part="crank-mark" class="iso-line" data-tone="hi" d="${crankMark(0)}"/>`,
  ],
});

const solids = (svg.match(/class="iso-solid/g) ?? []).length;

const live = `
const P = ${JSON.stringify(P)};
const TURN = Math.PI * 2;
const DISK = ${JSON.stringify(DISK)};
const CRANK = ${JSON.stringify({ x: CRANK.x, y: CRANK.y })};
const DISC_Z = ${DISC_Z}, DISC_H = ${DISC_H}, DISC_R = ${DISC_R};
const PIN_R = ${PIN_R}, PIN_C = ${PIN_C}, HANDLE_R = ${HANDLE_R}, KNOB_R = ${KNOB_R};
const WHEEL_X0 = ${WHEEL_X0}, WHEEL_Z = ${WHEEL_Z}, WHEEL_HALF = ${WHEEL_HALF}, WHEEL_R = ${WHEEL_R}, HOLE_R = ${HOLE_R};
const K = ${K}, PER_TURN = ${PER_TURN}, SHAFT_R = ${SHAFT_R};
const DIAL = ${JSON.stringify(DIAL)};
const DIAL_TOP = ${DIAL_TOP};
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const carriages = [...svg.querySelectorAll('[data-move="carriage"]')];
const pins = [...svg.querySelectorAll('[data-move="pin"]')];
const handles = [...svg.querySelectorAll('[data-move="handle"]')];
const arm = svg.querySelector('[data-part="arm"]');
const diskMarkEl = svg.querySelector('[data-part="disk-mark"]');
const crankMarkEl = svg.querySelector('[data-part="crank-mark"]');
const spoke = svg.querySelector('[data-part="spoke"]');
const needle = svg.querySelector('[data-part="needle"]');
const shaftBack = svg.querySelector('[data-part="shaft-back"]');
const shaftFront = svg.querySelector('[data-part="shaft-front"]');
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
const pinRest = [${pinAt(0)[0]}, ${pinAt(0)[1]}];
const handleRest = [${handleAt(0)[0]}, ${handleAt(0)[1]}];
${diskMark.toString()}
${crankMark.toString()}
${spokeAt.toString()}
${needleAt.toString()}
${armSvg.toString()}
function shaftPiece(x0, x1) {
  return solidSvg(disc(x0, x1, SHAFT_R, frameAlong([0, 0, WHEEL_Z], [1, 0, 0]), P), { tone: "hi", crease: "none" });
}
let x = 0, target = 0;
let frame = 0, last = 0, clock = 0, touring = !still.matches, visible = false, idleTimer = 0, said = "";
const tourAt = (t) => TURN * (0.5 - 0.5 * Math.cos((TURN * t) / 18));
function draw() {
  const shift = K * Math.sin(x);
  const moved = translateAlong(P, [shift, 0, 0]);
  for (const group of carriages) group.setAttribute("transform", moved);
  const pinNow = [CRANK.x + PIN_R * Math.sin(x), CRANK.y + PIN_R * Math.cos(x)];
  const pinMove = translateAlong(P, [pinNow[0] - pinRest[0], pinNow[1] - pinRest[1], 0]);
  for (const group of pins) group.setAttribute("transform", pinMove);
  const handleNow = [CRANK.x - HANDLE_R * Math.sin(x), CRANK.y - HANDLE_R * Math.cos(x)];
  const handleMove = translateAlong(P, [handleNow[0] - handleRest[0], handleNow[1] - handleRest[1], 0]);
  for (const group of handles) group.setAttribute("transform", handleMove);
  arm.innerHTML = armSvg(x);
  diskMarkEl.setAttribute("d", diskMark(x));
  crankMarkEl.setAttribute("d", crankMark(x));
  spoke.setAttribute("d", spokeAt((K / WHEEL_R) * (2 * x + (1 - Math.cos(x)))));
  needle.setAttribute("d", needleAt((2 * x + (1 - Math.cos(x))) / PER_TURN));
  const faceL = WHEEL_X0 + shift - WHEEL_HALF;
  const faceR = WHEEL_X0 + shift + WHEEL_HALF;
  shaftBack.innerHTML = shaftPiece(-30, faceL);
  shaftFront.innerHTML = shaftPiece(faceR, 54);
  const text = "x " + x.toFixed(2) + " · f " + (2 + Math.sin(x)).toFixed(2) + " · ∫ " + (2 * x + (1 - Math.cos(x))).toFixed(2);
  if (readout.textContent !== text) readout.textContent = text;
  const tenth = (Math.round(x * 10) / 10).toFixed(1);
  if (said !== tenth) {
    said = tenth;
    stage.setAttribute("aria-valuenow", tenth);
    stage.setAttribute("aria-valuetext", text);
  }
}
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  const calm = still.matches;
  if (touring && !calm) { clock += dt; target = tourAt(clock); }
  x = calm ? target : x + (target - x) * (1 - Math.exp(-dt / 0.42));
  if (Math.abs(target - x) < 0.0008) x = target;
  draw();
  const settled = !touring && x === target;
  frame = visible && !settled ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const steer = (next) => {
  touring = false;
  target = clamp(next, 0, TURN);
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => { touring = !still.matches; clock = Math.acos(1 - 2 * (x / TURN)) * 18 / TURN; run(); }, 3600);
  run();
};
new IntersectionObserver((entries) => { visible = entries[entries.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
stage.addEventListener("pointermove", (event) => {
  const box = svg.getBoundingClientRect();
  const share = clamp((event.clientX - box.left) / box.width, 0.06, 0.94);
  steer(((share - 0.06) / 0.88) * TURN);
});
stage.addEventListener("keydown", (event) => {
  const step = event.shiftKey ? TURN / 8 : TURN / 24;
  let next = null;
  if (event.key === "ArrowRight" || event.key === "ArrowUp") next = target + step;
  if (event.key === "ArrowLeft" || event.key === "ArrowDown") next = target - step;
  if (event.key === "Home") next = 0;
  if (event.key === "End") next = TURN;
  if (next === null) return;
  event.preventDefault();
  steer(next);
});
draw();
`;

const kitSource = readFileSync(new URL("./vendor/iso-kit.mjs", import.meta.url), "utf8").replace(/^export /gm, "");
const latheSource = readFileSync(new URL("./vendor/lathe.mjs", import.meta.url), "utf8")
  .replace(/^import .*$/gm, "")
  .replace(/^export /gm, "")
  .replace(/\brunsOf\b/g, "latheRunsOf")
  .replace(/\bsignedArea\b/g, "latheSignedArea")
  .replace(/\boriented\b/g, "latheOriented");
const style = `<style>.iso-stage{cursor:ew-resize;touch-action:pan-y}.iso-stage:focus-visible{outline:1px solid var(--anatomy-muted);outline-offset:6px}</style>`;
const body = k.plateHtml({
  fig: "Fig 1",
  title: "Tích phân",
  hint: "Kéo ngang · ← →",
  readout: readoutOf(0),
  keys: [
    { mark: "lit", label: "Bánh xe tại ρ = 6(2 + sin x)" },
    { mark: "edge", label: "Kim: ∫(2 + sin x) dx, một vòng = 2" },
  ],
  caption:
    "Máy tích phân đĩa–bánh xe. Góc đĩa là x. Chốt Scotch, lệch tâm 6, đẩy xe nên bánh chạm đĩa tại bán kính ρ = 6(2 + sin x). Bánh không trượt, bán kính 4,8, nên góc bánh bằng (6/4,8) lần tích phân. Hộp số đưa kim về đúng ∫₀ˣ (2 + sin t) dt = 2x + 1 − cos x. Hết một vòng, x = 2π và tích phân bằng 4π.",
  body: `${style}<div class="iso-stage" tabindex="0" role="slider" aria-label="Máy tích phân. Kéo ngang hoặc dùng phím mũi tên để quay x từ 0 đến 2 pi." aria-valuemin="0" aria-valuemax="6.3" aria-valuenow="0" aria-valuetext="${readoutOf(0)}">${svg}</div>`,
});

const file = theme === "light" ? "integral-light.html" : "integral.html";
writeFileSync(join(HERE, file), k.pageHtml({ title: "Tích phân — máy đĩa và bánh xe", theme, body, script: kitSource + "\n" + latheSource + "\n" + live, width: 760 }));
console.log("wrote", file, "solids", solids, "scale", P.scale.toFixed(3));

if (process.argv.includes("--audit")) {
  const R = A.recorder(P);
  const put = (name, shape, at) => R.put({ name, at, shapes: [R.solid(shape)], svg: "" });
  for (const part of scene.boxes) put(part.name, A.slab(planOf(part, 0.7), part.z, part.h, { name: part.name }, 4), [part.x + part.w / 2, part.y + part.d / 2, part.z + part.h / 2]);
  for (const part of scene.cyls) put(part.name, A.cylinder(part.x, part.y, part.r, part.z, part.h, { name: part.name }), [part.x, part.y, part.z + part.h / 2]);
  for (const part of scene.rods) {
    const frame = G.frameAlong([0, part.y, part.z], [1, 0, 0]);
    if (part.name === "shaft") {
      const left = WHEEL_X0 - WHEEL_HALF;
      const right = WHEEL_X0 + WHEEL_HALF;
      put("shaft.back", A.disc(frame, part.x0, left, part.r, { name: "shaft.back" }), [(part.x0 + left) / 2, part.y, part.z]);
      put("shaft.front", A.disc(frame, right, part.x1, part.r, { name: "shaft.front" }), [(right + part.x1) / 2, part.y, part.z]);
      continue;
    }
    const shape = part.name === "wheel"
      ? A.ring(frame, part.x0, part.x1, HOLE_R, part.r, { name: part.name })
      : A.disc(frame, part.x0, part.x1, part.r, { name: part.name });
    put(part.name, shape, [(part.x0 + part.x1) / 2, part.y, part.z]);
  }
  A.settle(R, P);
  A.auditOrExit(R, P);
}
