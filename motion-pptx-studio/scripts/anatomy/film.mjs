// Render an Anatomy figure module as a film: PNG frames (headless Chrome, the kit's own CSS),
// the poster frame, and the poster as vector shapes for an editable PowerPoint version.
//
//   node film.mjs FIGURE.mjs --out DIR [--fps 25] [--scale 1.5] [--anatomy $ANATOMY_HOME] [--only-poster]
//
// FIGURE.mjs exports default  (k) => ({ width, height, seconds, theme: "light"|"dark", tokens: {"--anatomy-lit": "#1464F4"},
//                                     label, poster: <seconds>, frame: (t) => "<svg body markup>" })
// `k` is the Anatomy kit (kit/iso-kit.mjs). frame(t) must be a pure function of t (no clocks, no randomness
// without a seed) so a frame can be rendered again. Words stay OUT of the drawing (Anatomy's rule): the slide sets them.
// Writes DIR/frames/f00000.png..., DIR/poster.png, DIR/poster.svg, DIR/poster-shapes.json, DIR/film.json
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

if (typeof WebSocket === "undefined" && !process.execArgv.includes("--experimental-websocket")) {
  const child = spawn(process.execPath, ["--experimental-websocket", ...process.argv.slice(1)], { stdio: "inherit" });
  child.on("exit", (code) => process.exit(code ?? 1));
} else {
  await main();
}

function arg(name, dflt) {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : dflt;
}

async function main() {
  const figPath = process.argv[2];
  if (!figPath || figPath.startsWith("-")) {
    console.log("usage: node film.mjs FIGURE.mjs --out DIR [--fps 25] [--scale 1.5] [--anatomy DIR] [--only-poster]");
    process.exit(2);
  }
  const out = resolve(arg("--out", "film"));
  const fps = Number(arg("--fps", "25"));
  const scale = Number(arg("--scale", "1.5"));
  const home = resolve(arg("--anatomy", process.env.ANATOMY_HOME || join(homedir(), ".local/share/anatomy")));
  const kitFile = join(home, "kit/iso-kit.mjs");
  if (!existsSync(kitFile)) {
    console.error(`Anatomy kit not found at ${kitFile}: run scripts/setup_anatomy.sh (or pass --anatomy)`);
    process.exit(2);
  }
  const k = await import(pathToFileURL(kitFile));
  const mod = (await import(pathToFileURL(resolve(figPath)))).default;
  const spec = typeof mod === "function" ? await mod(k) : mod;
  const { width: W, height: H, seconds, theme = "light", tokens = {}, label = "figure" } = spec;
  const posterT = spec.poster ?? seconds;
  const n = process.argv.includes("--only-poster") ? 0 : Math.round(seconds * fps);
  mkdirSync(join(out, "frames"), { recursive: true });

  const chromeBin = process.env.CHROME || ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"].find(existsSync);
  if (!chromeBin) { console.error("no Chrome/Chromium (set CHROME)"); process.exit(2); }
  const profile = mkdtempSync(join(tmpdir(), "anatomy-film-"));
  const chrome = spawn(chromeBin, ["--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--remote-debugging-port=0",
    `--user-data-dir=${profile}`, "--no-first-run", "--no-default-browser-check", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
  const port = await new Promise((done, fail) => {
    let text = "";
    const timer = setTimeout(() => fail(new Error("Chrome did not start")), 20000);
    chrome.stderr.on("data", (c) => { text += c; const m = text.match(/DevTools listening on ws:\/\/[^:]+:(\d+)\//); if (m) { clearTimeout(timer); done(Number(m[1])); } });
    chrome.on("exit", (c) => fail(new Error("Chrome exited " + c)));
  });
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = targets.find((t) => t.type === "page");
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener("open", r, { once: true }));
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
  const send = (method, params = {}) => new Promise((r, j) => { const i = ++id; pending.set(i, (m) => (m.error ? j(new Error(method + ": " + m.error.message)) : r(m.result))); ws.send(JSON.stringify({ id: i, method, params })); });

  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: scale, mobile: false });
  const tok = Object.entries(tokens).map(([a, b]) => `${a}:${b}`).join(";");
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${k.ISO_CSS}
    html,body{margin:0;padding:0;width:${W}px;height:${H}px;overflow:hidden}
    body{background:var(--anatomy-card)} #f{width:${W}px;height:${H}px}
    #f .iso-svg{width:${W}px;height:${H}px;overflow:hidden}
    *{animation:none!important;transition:none!important}${spec.css || ""}</style></head>
    <body class="iso" data-theme="${theme}" style="${tok}"><div id="f"></div></body></html>`;
  const { frameTree } = await send("Page.getFrameTree");
  await send("Page.setDocumentContent", { frameId: frameTree.frame.id, html });
  const svgAt = (t) => k.figureSvg({ width: W, height: H, label, body: frameBody(spec, t) });
  const show = (svg) => send("Runtime.evaluate", { expression: `document.getElementById('f').innerHTML=${JSON.stringify(svg)};1`, returnByValue: true });
  const shoot = async (file) => {
    const { data } = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: W, height: H, scale: 1 }, captureBeyondViewport: false });
    writeFileSync(file, Buffer.from(data, "base64"));
  };
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await show(svgAt(i / fps));
    await shoot(join(out, "frames", `f${String(i).padStart(5, "0")}.png`));
    if (i % 50 === 0) process.stdout.write(`frame ${i}/${n}\r`);
  }
  // poster: raster + vector, colours resolved by the browser (so themes and tokens are honoured)
  const posterSvg = svgAt(posterT);
  await show(posterSvg);
  await shoot(join(out, "poster.png"));
  writeFileSync(join(out, "poster.svg"), posterSvg.replace("<svg ", `<svg data-theme="${theme}" `));
  const ev = await send("Runtime.evaluate", { returnByValue: true, expression: `(${extract.toString()})()` });
  if (ev.exceptionDetails) throw new Error("extract failed: " + JSON.stringify(ev.exceptionDetails).slice(0, 400));
  const result = ev.result.value;
  writeFileSync(join(out, "poster-shapes.json"), JSON.stringify({ width: W, height: H, background: result.background, shapes: result.shapes }));
  writeFileSync(join(out, "film.json"), JSON.stringify({ anchors: anchorsAt(spec, posterT), figure: resolve(figPath), width: W, height: H, fps, scale, seconds, frames: n, poster: posterT, theme, tokens, anatomy: home, shapes: result.shapes.length, ms: Date.now() - t0 }, null, 1));
  console.log(`\nwrote ${n} frames + poster (${result.shapes.length} vector shapes) to ${out} in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  ws.close();
  // wait for Chrome to exit before removing its profile (it keeps writing for a moment: ENOTEMPTY race)
  const exited = new Promise((ok) => (chrome.exitCode !== null ? ok() : chrome.once("exit", ok)));
  chrome.kill("SIGKILL");
  await Promise.race([exited, new Promise((ok) => setTimeout(ok, 3000))]);
  for (let i = 0; i < 5; i++) {
    try { rmSync(profile, { recursive: true, force: true }); break; }
    catch (e) { if (i === 4) console.error(`note: could not remove ${profile} (${e.code}); harmless`); else await new Promise((ok) => setTimeout(ok, 300)); }
  }
}

// v5.4: a figure mistake exits 3 with the reason (not "re-run setup", which is exit 2)
function figureError(msg) {
  console.error("FIGURE ERROR: " + msg);
  process.exit(3);
}

// frame(t) must return SVG markup. A kit helper that returns an object (topTicks gives {minor, major}) and is
// interpolated into the string shows up as "[object Object]": say so instead of crashing in the extractor.
function frameBody(spec, t) {
  if (typeof spec.frame !== "function") figureError("the figure has no frame(t) function");
  let body = spec.frame(t);
  if (Array.isArray(body)) body = body.join("");
  if (typeof body !== "string") figureError(`frame(${t}) returned ${typeof body}, not an SVG string`);
  const bad = body.indexOf("[object Object]");
  if (bad >= 0) figureError(`frame(${t}) markup contains "[object Object]" near ${JSON.stringify(body.slice(Math.max(0, bad - 60), bad + 20))}: ` +
    "a kit helper returned an object (e.g. topTicks returns {minor, major}: interpolate .minor and .major, or lineSvg each part)");
  return body;
}

// anchors: an object of [x, y] screen points, or a function (t) => object (evaluated at the poster time).
// Anything else used to be dropped silently by JSON.stringify; now it is an error that names the anchor.
function anchorsAt(spec, t) {
  let a = spec.anchors;
  if (a === undefined || a === null) return {};
  if (typeof a === "function") a = a(t);
  if (typeof a !== "object" || Array.isArray(a)) figureError("anchors must be an object {name: [x, y]} or a function (t) => that object");
  const outA = {};
  for (const [name, v] of Object.entries(a)) {
    const p = Array.isArray(v) ? v : v && typeof v === "object" && "x" in v ? [v.x, v.y] : null;
    if (!p || p.length < 2 || !Number.isFinite(+p[0]) || !Number.isFinite(+p[1])) figureError(`anchor ${JSON.stringify(name)} is ${JSON.stringify(v)}: give a screen point [x, y] (k.iso([x, y, z], P))`);
    outA[name] = [+p[0], +p[1]];
  }
  return outA;
}

// Runs in the page: every visible path/circle as polygons in viewBox units with resolved paint.
function extract() {
  const svg = document.querySelector("#f svg");
  const bg = getComputedStyle(document.body).backgroundColor;
  const out = [];
  const tmp = document.createElementNS("http://www.w3.org/2000/svg", "path");
  svg.appendChild(tmp);
  const opac = (el) => { let o = 1; for (let e = el; e && e !== svg; e = e.parentElement) o *= Number(getComputedStyle(e).opacity || 1); return o; };
  const paint = (v) => (!v || v === "none" || v.startsWith("url(") ? null : v);
  for (const el of svg.querySelectorAll("path, circle")) {
    if (el === tmp) continue;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const fill = paint(cs.fill), stroke = paint(cs.stroke);
    const fo = Number(cs.fillOpacity), so = Number(cs.strokeOpacity), o = opac(el);
    if ((!fill || fo === 0) && (!stroke || so === 0)) continue;
    if (o < 0.02) continue;
    const m = el.getCTM();
    const T = (x, y) => [+(m.a * x + m.c * y + m.e).toFixed(2), +(m.b * x + m.d * y + m.f).toFixed(2)];
    const base = { fill, fillOpacity: fo * o, stroke, strokeOpacity: so * o, strokeWidth: parseFloat(cs.strokeWidth) || 0 };
    if (el.tagName === "circle") {
      const c = T(+el.getAttribute("cx"), +el.getAttribute("cy"));
      out.push({ kind: "circle", cx: c[0], cy: c[1], r: +el.getAttribute("r") * Math.hypot(m.a, m.b), ...base });
      continue;
    }
    const d = el.getAttribute("d") || "";
    for (const sub of d.split(/(?=M)/).map((s) => s.trim()).filter(Boolean)) {
      const closed = /Z\s*$/i.test(sub);
      let pts;
      if (/^[MLZ0-9.\s,-]+$/i.test(sub)) {
        const nums = sub.replace(/[MLZ]/gi, " ").trim().split(/[\s,]+/).map(Number);
        pts = []; for (let i = 0; i + 1 < nums.length; i += 2) pts.push(T(nums[i], nums[i + 1]));
      } else {
        tmp.setAttribute("d", sub);
        const len = tmp.getTotalLength();
        const steps = Math.max(4, Math.min(200, Math.ceil(len / 1.5)));
        pts = []; for (let i = 0; i <= steps; i++) { const p = tmp.getPointAtLength((len * i) / steps); pts.push(T(p.x, p.y)); }
      }
      if (pts.length >= 2) out.push({ kind: "poly", pts, closed, ...base });
    }
  }
  tmp.remove();
  return { background: bg, shapes: out };
}
