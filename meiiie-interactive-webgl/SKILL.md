---
name: meiiie-interactive-webgl
description: Design, build, and verify cinematic interactive 3D/WebGL objects with semantic part selection, reversible exploded views, and subject-appropriate shader effects. Use for inspectable product assemblies, technical illustrations, interactive 3D explainers, and real-time object showcases, including translating a supplied reference clip into a new implementation. Not for video-only editing, generic landing-page styling, engineering simulation, or unrelated repository work.
---

# Interactive WebGL objects

Build a legible object first, a reliable interaction second, and a cinematic effect third. Treat a reference as evidence of visible behavior, never proof of its implementation.

## Scope and routing

Use the existing project's renderer, dependencies, design system, and authorized environment. Apply the software-engineering skill for environment selection and repository work; apply Sites only for an authorized hosted Site. This skill grants no installs, paid generation, external publishing, or access permissions. Do not execute code on a different computer to bypass an environment constraint.

Complement `meiiie-reference-to-product` for surrounding layout and brand fidelity, `meiiie-product-motion` for a rendered film, and `meiiie-explain-clearly` for explanatory accuracy. Keep this skill focused on the live 3D object and interaction contract.

## 1. Establish evidence and a bounded proof

- Inspect actual reference frames and transitions. Record observed appearance, inferred interaction, unknown implementation, and desired differences separately. A cursor near a brightened part suggests selection; it does not prove live picking. Captions such as “one-shot” are unverified without process evidence.
- Establish subject, audience, explanatory goal, assets and licenses, target browsers/devices, integration point, and essential states. Make a small reversible assumption when harmless; ask only for consequential gaps.
- Label invented geometry and visualized processes as a conceptual technical illustration. Do not imply validated CAD, measured airflow, combustion, or engineering accuracy.
- Choose one representative assembly, one selection, and one effect transition as a quality proof before expanding detail. Read [architecture.md](references/architecture.md) for the model contract and [render-gates.md](references/render-gates.md) before building.

## 2. Author semantic geometry and composition

Define stable part IDs and a parent graph, local rest/exploded transforms, local focus/effect/connector anchors, generous pick bounds, human-readable labels, and accessible descriptions. Keep a stationary stage separate from moving parts. Store subject-specific dimensions, palette, labels, effect settings, and choreography in configuration, not the reusable interaction core.

Solve silhouette, camera, negative space, lighting, contrast, and material hierarchy before shader complexity. Use meaningful contour/detail edges; blanket triangle wireframes are not a substitute for technical drawing. Simplify nonessential hardware. Check mobile framing independently rather than shrinking the desktop canvas.

## 3. Make interaction deterministic and reversible

Separate user intent/selection, assembly progress, effect phase, and animation time. Derive transforms from immutable poses; do not accumulate frame-to-frame offsets. Reverse or retarget from the current pose without jumps. Clamp elapsed time after suspension. Define Stop, Reset, repeated commands, mid-transition selection, and incompatible states explicitly.

Use canvas-relative pointer coordinates, semantic hit resolution, and pick layers/proxies. Keep hover transient and persistent selection distinct. Essential operations must work through native DOM controls and a semantic part list on keyboard and touch. Avoid competing timelines and stale callbacks.

## 4. Give effects an explanatory role

Choose heat, airflow, liquid, energy, light, deformation, or another role appropriate to the subject; do not impose rocket exhaust or a dark palette on every model. Attach effects to local anchors. Keep source/core, surrounding medium, surface response, and residual decay separable. A plume may use bounded geometry and a low-cost shader; it is not automatically a fluid simulation.

Stage onset, sustained effect, and release deliberately. Light spill, occlusion, contact, and floor/material response matter as much as shader noise. Start with the least costly representation that communicates the phenomenon. Add bloom or volume sampling only after visual and performance evidence justifies it.

## 5. Ship accessible, resilient behavior

Provide visible focus, usable touch targets, concise state text, Pause, and Reset. Do not make hover or canvas vision the only path. Preserve touch scrolling outside intended gestures. Respect reduced motion with instant/short pose changes and a readable static effect; disable flashing, camera shake, continuous noise and drift.

Suspend rendering when hidden/offscreen, reconcile clocks on resume, and render on demand when settled. Dispose owned GPU resources, listeners, observers, controls, and animation callbacks on teardown. Handle context creation failure and loss/restoration; a usable static/SVG alternative must explain the current state and retain essential semantic controls rather than show a black canvas.

## 6. Verify before claiming success

Run the actual application and inspect actual renders. Unit tests, source inspection, and a compiling shader cannot establish visible fidelity or smooth interaction. Use the gates in [render-gates.md](references/render-gates.md); explicitly report unavailable checks and distinguish real-device measurements from emulation.

Deliver the runnable artifact in its authorized destination, concise controls, verified states, visual evidence, measured performance with device/browser context, limitations, and asset provenance. Never call a render-unverified implementation production-ready. Consult [sources.md](references/sources.md) for primary documentation and reference limits; recheck APIs against the pinned release.
