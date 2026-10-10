const TAU = Math.PI * 2;

export const K = 6;
export const WHEEL_R = 4.8;
export const PIN_R = 6;
export const SHAFT_R = 1.05;
export const HOLE_R = 1.5;
export const WHEEL_HALF = 1.55;
export const GEAR_R = 8;
export const DISC_R = 10.5;
export const HANDLE_R = 18;
export const KNOB_R = 2.35;
export const PIN_C = 0.78;

export const DISK = { x: 8, y: 0, r: 26, z0: 9, z1: 15 };
export const WHEEL_Z = DISK.z1 + WHEEL_R;
export const WHEEL_X0 = DISK.x + K * 2;

const dirLen = Math.hypot(1, 0.72);
const DIR = [-1 / dirLen, -0.72 / dirLen];
const STEP = GEAR_R * 2;

export const GEARS = [0, 1, 2, 3, 4].map((index) => ({
  x: DISK.x + DIR[0] * STEP * index,
  y: DISK.y + DIR[1] * STEP * index,
  r: GEAR_R,
}));

export const CRANK = GEARS[4];
export const GEAR_Z = 1.2;
export const GEAR_H = 3.65;
export const DISC_Z = GEAR_Z + GEAR_H;
export const DISC_H = 3.55;
export const YOKE_Z = 10.2;
export const YOKE_H = 3.8;

export const PLATE = { x: -82, y: -72, w: 180, d: 128, r: 9 };
export const PLATE_H = 11;
export const FOOT_H = 5;

export function f(x) {
  return 2 + Math.sin(x);
}

export function integral(x) {
  return 2 * x + (1 - Math.cos(x));
}

export function rho(x) {
  return K * f(x);
}

export function wheelX(x) {
  return DISK.x + rho(x);
}

export function shiftOf(x) {
  return wheelX(x) - WHEEL_X0;
}

export function wheelAngle(x) {
  return (K / WHEEL_R) * integral(x);
}

export function pinAt(x) {
  return [CRANK.x + PIN_R * Math.sin(x), CRANK.y + PIN_R * Math.cos(x)];
}

export function handleAt(x) {
  return [CRANK.x - HANDLE_R * Math.sin(x), CRANK.y - HANDLE_R * Math.cos(x)];
}

export function readoutOf(x) {
  return `x ${x.toFixed(2)} · f ${f(x).toFixed(2)} · ∫ ${integral(x).toFixed(2)}`;
}

function box(name, x, y, z, w, d, h) {
  return { name, x, y, z, w, d, h };
}

function cyl(name, x, y, z, r, h) {
  return { name, x, y, z, r, h };
}

function rod(name, x0, x1, y, z, r) {
  return { name, x0, x1, y, z, r };
}

export function layout(x = 0) {
  const s = shiftOf(x);
  const wx = WHEEL_X0 + s;
  const boxes = [];
  const cyls = [];
  const rods = [];
  const addB = (name, px, py, z, w, d, h) => boxes.push(box(name, px, py, z, w, d, h));
  const addC = (name, cx, cy, z, r, h) => cyls.push(cyl(name, cx, cy, z, r, h));

  for (const [fx, fy] of [
    [PLATE.x + 20, PLATE.y + 20],
    [PLATE.x + PLATE.w - 20, PLATE.y + 20],
    [PLATE.x + 20, PLATE.y + PLATE.d - 20],
    [PLATE.x + PLATE.w - 20, PLATE.y + PLATE.d - 20],
  ]) {
    addC("stand.flange", fx, fy, -PLATE_H - FOOT_H, 6.4, 1.5);
    addC("stand.foot", fx, fy, -PLATE_H - FOOT_H + 1.5, 5, FOOT_H - 1.5);
  }
  addB("stand.plate", PLATE.x, PLATE.y, -PLATE_H, PLATE.w, PLATE.d, PLATE_H);

  addB("label", -68, 16, 0, 26, 14, 0.8);
  addB("ruler", -46, PLATE.y + PLATE.d - 14, 0, 30, 5, 0.7);

  GEARS.forEach((gear, index) => {
    addC(`gear.axle.${index}`, gear.x, gear.y, 0, 2.1, GEAR_Z);
    addC(`gear.${index}`, gear.x, gear.y, GEAR_Z, gear.r, GEAR_H);
  });
  addC("hub", DISK.x, DISK.y, DISC_Z, 4.6, DISK.z0 - DISC_Z);
  addC("disk", DISK.x, DISK.y, DISK.z0, DISK.r, DISK.z1 - DISK.z0);
  addC("crank.disc", CRANK.x, CRANK.y, DISC_Z, DISC_R, DISC_H);

  const [px, py] = pinAt(x);
  addC("pin.shaft", px, py, DISC_Z + DISC_H, PIN_C, YOKE_Z + YOKE_H - (DISC_Z + DISC_H));
  addC("pin.head", px, py, YOKE_Z + YOKE_H, 1.85, 1.7);

  const [hx, hy] = handleAt(x);
  addC("handle", hx, hy, DISC_Z, KNOB_R, 5.2);

  const yokeY = CRANK.y - 9;
  const yokeD = 18;
  addB("yoke.left", CRANK.x + s - 4.95, yokeY, YOKE_Z, 3.15, yokeD, YOKE_H);
  addB("yoke.right", CRANK.x + s + 1.8, yokeY, YOKE_Z, 3.15, yokeD, YOKE_H);
  addB("yoke.far", CRANK.x + s - 4.95, CRANK.y - 12.3, YOKE_Z, 9.9, 3.3, YOKE_H);
  addB("yoke.near", CRANK.x + s - 4.95, CRANK.y + 9, YOKE_Z, 9.9, 3.3, YOKE_H);

  const rearRodZ = 11.05;
  const rearRodR = 1.3;
  const beamZ = rearRodZ + rearRodR;
  const beamH = 3.15;
  const beamY = -59.2;
  const beamD = 5.4;
  addB("beam", -56 + s, beamY, beamZ, 82, beamD, beamH);
  addB("drop", CRANK.x + s - 4.2, beamY + beamD, YOKE_Z, 8.4, CRANK.y - 12.3 - (beamY + beamD), YOKE_H);

  rods.push(rod("rear.rod", -73, 40, -56.5, rearRodZ, rearRodR));
  for (const postX of [-64, 32]) addC("rear.post", postX, -56.5, 0, 2.2, rearRodZ - rearRodR);
  addB("rear.stop.l", -76.2, -59.6, 8.4, 3.2, 6.2, 7);
  addB("rear.stop.r", 40, -59.6, 8.4, 3.2, 6.2, 7);

  const riserTop = 26.6;
  addB("riser", wx - 2.6, -59.2, beamZ + beamH, 5.2, 53, riserTop - (beamZ + beamH));
  addB("bridge", wx - 5.4, -12, riserTop, 10.8, 18.4, 2.7);
  addB("finger.left", wx - WHEEL_HALF - 2.7, -5.4, 17.2, 2.7, 4.2, riserTop - 17.2);
  addB("finger.right", wx + WHEEL_HALF, -5.4, 17.2, 2.7, 4.2, riserTop - 17.2);

  const frontY = 49;
  const frontRodZ = 19.4;
  const frontRodR = 1.25;
  rods.push(rod("front.rod", 4, 46, frontY, frontRodZ, frontRodR));
  for (const postX of [10, 40]) addC("front.post", postX, frontY, 0, 2.1, frontRodZ - frontRodR);
  addB("arm", wx - 1.7, 6.4, 22.4, 3.4, frontY - 3.3 - 6.4, 6.9);
  addB("front.shoe", wx - 3.2, frontY - 3.3, frontRodZ + frontRodR, 6.4, 6.6, 5.6);

  addB("bearing.base", -36, -7.2, 0, 14, 14.4, WHEEL_Z - SHAFT_R);
  addB("bearing.cap", -36, -7.2, WHEEL_Z + SHAFT_R, 14, 14.4, 4);
  rods.push(rod("shaft", -30, 54, 0, WHEEL_Z, SHAFT_R));
  rods.push(rod("wheel", wx - WHEEL_HALF, wx + WHEEL_HALF, 0, WHEEL_Z, WHEEL_R));

  addB("case", 54, -16, 0, 32, 34, 23);
  addC("dial", 70, 1, 23, 12.5, 6.4);
  addB("scale", 12, 30.2, 15.6, 18, 3.2, 1.15);
  addC("scale.post.0", 15, 31.8, 0, 1.35, 15.66);
  addC("scale.post.1", 25, 31.8, 0, 1.35, 15.66);
  addB("pointer", wx - 0.7, 30.2, 16.69, 1.4, 3.2, 3.46);
  addC("index.post", DISK.x, 33.5, 0, 2.2, 15);
  addB("index.arm", DISK.x - 3.8, 26.35, 15, 7.2, 10.6, 1.45);

  return { boxes, cyls, rods, wx, s };
}

function finiteBox(item) {
  if (![item.x, item.y, item.z, item.w, item.d, item.h].every(Number.isFinite)) throw new Error(`bad box ${item.name}`);
}
function boxesOverlap(a, b) {
  const dx = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  const dy = Math.min(a.y + a.d, b.y + b.d) - Math.max(a.y, b.y);
  const dz = Math.min(a.z + a.h, b.z + b.h) - Math.max(a.z, b.z);
  if (dx > 0.08 && dy > 0.08 && dz > 0.08) return Math.min(dx, dy, dz);
  return 0;
}

function pointInBox(px, py, pz, box, pad = 0) {
  return px >= box.x - pad && px <= box.x + box.w + pad && py >= box.y - pad && py <= box.y + box.d + pad && pz >= box.z - pad && pz <= box.z + box.h + pad;
}

function cylHitsBox(cyls, box) {
  const z0 = Math.max(cyls.z, box.z);
  const z1 = Math.min(cyls.z + cyls.h, box.z + box.h);
  if (z1 - z0 <= 0.08) return 0;
  const cx = Math.max(box.x, Math.min(cyls.x, box.x + box.w));
  const cy = Math.max(box.y, Math.min(cyls.y, box.y + box.d));
  const dist = Math.hypot(cx - cyls.x, cy - cyls.y);
  return cyls.r - dist > 0.12 ? cyls.r - dist : 0;
}

function rodHitsBox(rod, box) {
  const x0 = Math.max(rod.x0, box.x);
  const x1 = Math.min(rod.x1, box.x + box.w);
  if (x1 - x0 <= 0.08) return 0;
  const cy = Math.max(box.y, Math.min(rod.y, box.y + box.d));
  const cz = Math.max(box.z, Math.min(rod.z, box.z + box.h));
  const dist = Math.hypot(cy - rod.y, cz - rod.z);
  return rod.r - dist > 0.12 ? rod.r - dist : 0;
}

const ALLOW = new Set(["shaft|wheel", "wheel|disk"]);

function allowed(a, b) {
  return ALLOW.has(`${a}|${b}`) || ALLOW.has(`${b}|${a}`);
}

export function clashes(x = 0) {
  const { boxes, cyls, rods } = layout(x);
  const found = [];
  for (const block of boxes) finiteBox(block);
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const hit = boxesOverlap(boxes[i], boxes[j]);
      if (hit && !allowed(boxes[i].name, boxes[j].name)) found.push(`${boxes[i].name} ∩ ${boxes[j].name} ${hit.toFixed(2)}`);
    }
  }
  for (const cylinder of cyls) {
    for (const block of boxes) {
      if (allowed(cylinder.name, block.name)) continue;
      const hit = cylHitsBox(cylinder, block);
      if (hit) found.push(`${cylinder.name} ∩ ${block.name} ${hit.toFixed(2)}`);
    }
    for (const other of cyls) {
      if (other === cylinder || other.name < cylinder.name) continue;
      if (allowed(cylinder.name, other.name)) continue;
      const z0 = Math.max(cylinder.z, other.z);
      const z1 = Math.min(cylinder.z + cylinder.h, other.z + other.h);
      if (z1 - z0 <= 0.08) continue;
      const dist = Math.hypot(cylinder.x - other.x, cylinder.y - other.y);
      const hit = cylinder.r + other.r - dist;
      if (hit > 0.12) found.push(`${cylinder.name} ∩ ${other.name} ${hit.toFixed(2)}`);
    }
  }
  for (let i = 0; i < rods.length; i++) {
    for (let j = i + 1; j < rods.length; j++) {
      const a = rods[i];
      const b = rods[j];
      if (allowed(a.name, b.name)) continue;
      const x0 = Math.max(a.x0, b.x0);
      const x1 = Math.min(a.x1, b.x1);
      if (x1 - x0 <= 0.08) continue;
      const dist = Math.hypot(a.y - b.y, a.z - b.z);
      const hit = a.r + b.r - dist;
      if (hit > 0.12) found.push(`${a.name} ∩ ${b.name} ${hit.toFixed(2)}`);
    }
  }
  for (const bar of rods) {
    for (const block of boxes) {
      if (allowed(bar.name, block.name)) continue;
      const hit = rodHitsBox(bar, block);
      if (hit) found.push(`${bar.name} ∩ ${block.name} ${hit.toFixed(2)}`);
    }
    for (const cylinder of cyls) {
      if (allowed(bar.name, cylinder.name)) continue;
      const x0 = Math.max(bar.x0, cylinder.x - cylinder.r);
      const x1 = Math.min(bar.x1, cylinder.x + cylinder.r);
      if (x1 - x0 <= 0.08) continue;
      const dist = Math.hypot(cylinder.y - bar.y, cylinder.z + cylinder.h / 2 - bar.z);
      const limit = bar.r + cylinder.r;
      if (cylinder.z + cylinder.h < bar.z - bar.r - 0.08 || cylinder.z > bar.z + bar.r + 0.08) continue;
      if (dist < limit - 0.2 && pointInBox(cylinder.x, cylinder.y, bar.z, { x: bar.x0, y: bar.y - bar.r, z: bar.z - bar.r, w: bar.x1 - bar.x0, d: bar.r * 2, h: bar.r * 2 }, cylinder.r)) {
        found.push(`${bar.name} ∩ ${cylinder.name}`);
      }
    }
  }
  const [px, py] = pinAt(x);
  const slot = boxes.filter((item) => item.name.startsWith("yoke"));
  const left = slot.find((item) => item.name === "yoke.left");
  const right = slot.find((item) => item.name === "yoke.right");
  if (px - PIN_C < left.x + left.w - 0.05 || px + PIN_C > right.x + 0.05) found.push("pin leaves the slot in x");
  const far = slot.find((item) => item.name === "yoke.far");
  const near = slot.find((item) => item.name === "yoke.near");
  if (py - PIN_C < far.y + far.d - 0.05 || py + PIN_C > near.y + 0.05) found.push("pin leaves the slot in y");
  const rhoNow = rho(x);
  if (rhoNow - WHEEL_R < 1 || rhoNow + WHEEL_R > DISK.r - 1) found.push(`wheel leaves the disk at ρ ${rhoNow.toFixed(2)}`);
  return found;
}

export function assertModel() {
  const period = integral(TAU);
  if (Math.abs(period - 4 * Math.PI) > 1e-9) throw new Error(`period integral ${period}`);
  let numeric = 0;
  const steps = 720;
  const h = TAU / steps;
  for (let index = 0; index < steps; index++) {
    const a = index * h;
    const b = a + h;
    numeric += ((f(a) + 4 * f((a + b) / 2) + f(b)) * h) / 6;
  }
  if (Math.abs(numeric - period) > 1e-4) throw new Error(`simpson ${numeric}`);
  if (Math.abs(wheelX(0) - WHEEL_X0) > 1e-9) throw new Error("rest wheel");
  if (Math.abs(shiftOf(Math.PI / 2) - PIN_R) > 1e-9) throw new Error("shift");
  const samples = 48;
  const found = [];
  for (let index = 0; index <= samples; index++) found.push(...clashes((index / samples) * TAU).map((line) => `x ${(index / samples).toFixed(2)}τ ${line}`));
  if (found.length) throw new Error(found.slice(0, 24).join("\n"));
}
