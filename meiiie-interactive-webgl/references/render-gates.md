# Acceptance gates

Choose project-specific budgets before implementation. Numbers below are starting targets, never measured results or universal guarantees.

## Proof before scale

At a named desktop size and narrow/mobile size, inspect rendered idle, exploded, selected, active-effect, release/residual, and reset states. Inspect reduced motion and forced GPU failure separately. Capture a short actual transition recording; stills cannot verify smoothness or cancellation. Compare reference and implementation using matched states/camera intent, not unrelated screenshots.

Check silhouette and part hierarchy, clean contours instead of stray triangulation, no z-fighting, no detached anchors/connectors, no occluding labels, effect contact/occlusion, no quad rectangles, legible controls, and comfortable mobile margins. Confirm light and material response before increasing noise/detail.

## Interaction matrix

Exercise pointer picking, touch tap/list selection, keyboard-only operation, Escape clearing, Pause/Resume, Reset from every major phase, and rapid repeated/alternating commands. Reverse explosion halfway. Stop before effect onset and during release. Change selection while moving. Resize and rotate viewport. All essential states must remain reachable without hover.

Change reduced-motion preference before load and at runtime. Hide/restore the tab and move the component offscreen/back; ensure no elapsed-time jump or duplicate render loop. Test unmount/remount cleanup. Force context loss and restoration when supported, plus initial creation failure. Retain semantic UI and show a labeled simplified fallback if recovery fails. A mocked state test is distinct from actual browser context recovery.

## Performance and quality tiers

An initial small-object target might be fewer than 100 draw calls and 100k triangles desktop, half that triangle budget on mobile, without dynamic shadows or large textures. Start with capped DPR around 1.5–2 desktop and 1–1.5 mobile; adjust from actual evidence, not user-agent assumptions. Permit project needs to override these numbers explicitly.

Measure sustained active-effect frame times after warmup; record device/GPU when available, browser, viewport, DPR, sample duration, median/p95, draw calls/triangles and memory/resource counts. Aim for the selected 60 or 30 fps tier. Do not claim mobile performance based solely on a narrow desktop viewport. FPS alone does not identify GPU/CPU bottlenecks. Low draw-call and triangle counts establish only geometry/submission cost bounds; they do not establish fill-rate, shader cost, thermal stability, or frame-time performance.

Reduce the measured bottleneck: transparent overdraw/smoke coverage, bloom render size, shader octave/sample count, DPR, then unneeded geometry/detail as appropriate. Avoid per-frame allocations and synchronous GPU reads in normal rendering. Ensure lower tiers retain semantic information and interaction. Recheck after quality changes.

## Evidence and handoff

Report each gate as passed, failed, or not checked, with actual artifact/test evidence. Separate logic checks, browser-render checks, input checks, and standalone-deliverable checks; a large combined test count conceals missing categories. If delivering a standalone HTML or archive, open that exact delivered artifact and verify its assets and controls independently of the development server. Keep requirements, automated assertions, actual rendered inspection, and real-device measurements distinct. A test command exiting successfully cannot substitute for a missing rendered state. Disclose blockers and preserve the runnable prototype without calling it finished visual work.
