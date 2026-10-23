// Portable film route (web-film): any HTML/SVG/Canvas page -> MP4, rendered frame by frame in headless Chrome.
//   node web_film.mjs PAGE.html --out assets/film/NAME.mp4 [--seconds 12] [--fps 30] [--w 1920] [--h 810]
// PAGE.html defines   window.frame = (t) => { ...draw the picture at t seconds... }   (pure function of t:
// no clocks, no requestAnimationFrame, no unseeded randomness), optionally window.SECONDS. Fonts: @font-face to
// local files. Needs Node 20+, Chrome/Chromium (or CHROME=/path), ffmpeg. Then: python3 film_check.py NAME.mp4
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync, existsSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { pathToFileURL } from "node:url";

if (typeof WebSocket === "undefined" && !process.execArgv.includes("--experimental-websocket")) {
  const c = spawn(process.execPath, ["--experimental-websocket", ...process.argv.slice(1)], { stdio: "inherit" });
  c.on("exit", (code) => process.exit(code ?? 1));
} else await main();

function arg(n, d) { const i = process.argv.indexOf(n); return i > 0 ? process.argv[i + 1] : d; }

async function main() {
  const page = process.argv[2];
  if (!page || page.startsWith("-")) { console.log("usage: node web_film.mjs PAGE.html --out NAME.mp4 [--seconds S] [--fps 30] [--w 1920] [--h 810]"); process.exit(2); }
  const out = resolve(arg("--out", "film.mp4")), fps = +arg("--fps", 30), W = +arg("--w", 1920), H = +arg("--h", 810);
  mkdirSync(dirname(out), { recursive: true });
  const bin = process.env.CHROME || ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"].find(existsSync);
  if (!bin) { console.error("no Chrome/Chromium: set CHROME=/path, else use canvas_film.py (principles/web-film.md)"); process.exit(2); }
  const prof = mkdtempSync(join(tmpdir(), "web-film-"));
  const ch = spawn(bin, ["--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--remote-debugging-port=0",
    "--allow-file-access-from-files", `--user-data-dir=${prof}`, "--no-first-run", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
  const port = await new Promise((ok, no) => { let s = ""; const tm = setTimeout(() => no(new Error("Chrome did not start")), 20000);
    ch.stderr.on("data", (c) => { s += c; const m = s.match(/DevTools listening on ws:\/\/[^:]+:(\d+)\//); if (m) { clearTimeout(tm); ok(+m[1]); } }); });
  const tgt = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === "page");
  const ws = new WebSocket(tgt.webSocketDebuggerUrl); await new Promise((r) => ws.addEventListener("open", r, { once: true }));
  let id = 0; const pend = new Map();
  ws.addEventListener("message", (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
  const send = (method, params = {}) => new Promise((r, j) => { const i = ++id; pend.set(i, (m) => (m.error ? j(new Error(method + ": " + m.error.message)) : r(m.result))); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async (x) => { const r = await send("Runtime.evaluate", { expression: x, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error("page error: " + (r.exceptionDetails.exception?.description || r.exceptionDetails.text)); return r.result.value; };
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  const loaded = new Promise((r) => ws.addEventListener("message", (e) => { if (JSON.parse(e.data).method === "Page.loadEventFired") r(); }));
  await send("Page.navigate", { url: pathToFileURL(resolve(page)).href }); await loaded;
  await ev("document.fonts.ready.then(() => 1)");
  if (await ev("typeof window.frame") !== "function") { console.error("PAGE ERROR: the page has no window.frame(t)"); process.exit(3); }
  const secs = +arg("--seconds", (await ev("window.SECONDS || 0")) || 10), n = Math.round(secs * fps);
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
    "-crf", "20", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    await ev(`Promise.resolve(window.frame(${i / fps})).then(() => new Promise((r) => requestAnimationFrame(() => r(1))))`);
    const { data } = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
    if (!ff.stdin.write(Buffer.from(data, "base64"))) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % 60 === 0) process.stdout.write(`frame ${i}/${n}\r`);
  }
  ff.stdin.end(); const code = await new Promise((r) => ff.on("exit", r));
  ws.close(); ch.kill("SIGKILL"); await new Promise((r) => setTimeout(r, 300)); rmSync(prof, { recursive: true, force: true });
  if (code) { console.error("ffmpeg failed"); process.exit(1); }
  console.log(`wrote ${out}: ${n} frames, ${W}x${H} @ ${fps} in ${((Date.now() - t0) / 1000).toFixed(1)} s. Next: python3 film_check.py ${out}`);
}
