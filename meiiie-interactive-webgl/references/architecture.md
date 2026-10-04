# Object and interaction contract

## Semantic part graph

Each part owns: stable `id`, `parentId`, label/description, immutable local rest pose, authored local exploded pose, visual meshes/detail edges, pick proxy, local focus anchor, and optional connector/effect anchors. Map child mesh hits to the semantic part. Transform anchors through current world matrices; never copy a world position once and expect it to follow animation.

Connectors spanning two moving groups need a declared behavior: flex/rebuild from endpoints, rigid ownership, telescoping, or deliberate suppression with explanation. Do not leave a tube attached to yesterday's endpoint. An exploded view communicates assembly relationships, not debris. Separate along meaningful axes and inspect overlaps from supported cameras.

Derive every pose from one normalized assembly value where possible. Interpolate translations/scales and quaternion rotations using stable endpoints. Retarget transitions from current values with elapsed-time easing. For complex articulated objects use per-part phase offsets without sacrificing a reversible global contract.

## Orthogonal state

Keep at least these concepts separate:
- Intent: target assembly pose, requested effect, persistent selected ID, transient hovered ID, camera target.
- Progress: assembly parameter, effect envelope/phase, connector state.
- Clock: active elapsed time, paused/hidden status, reduced-motion policy.
- Capability: GPU/context availability, quality tier, fallback mode.

Selection must not secretly restart assembly or effects. Gate subject-specific effects with explicit prerequisites. For example, an assembled-only effect first converges to assembly and then starts only if intent still requests it. Stop during convergence cancels that request. Reset cancels pending transitions and restores camera, selection, poses, time, effect uniforms and residual layers. Test rapid alternating commands.

## Picking and DOM parity

Calculate normalized pointer coordinates from the canvas bounding rectangle, not full-window dimensions. Raycast only intended targets; use generous proxy meshes or appropriate line thresholds, resolve nearest meaningful semantic hit, and avoid invisible effects intercepting clicks. Touch taps and list buttons select persistently; hover is optional. Use native buttons, state labels and focus indicators. Announce meaningful changes, not every animation frame.

## Rendering layers

1. Geometry and composition: silhouette, proportion, seams, spatial separation, framing.
2. Material and lighting: opaque surfaces, selective edges, directional form cues and readable contrast.
3. Interaction emphasis: selected contour/material plus a textual counterpart; preserve enough unselected context.
4. Effect: bounded source/core and surrounding medium with spatial attenuation.
5. Environment response: restrained illumination/contact and residual decay.

Examples: fan airflow uses directional stream cues rather than flame; a lamp uses light and illuminated surfaces without smoke; liquid uses a bounded stream and contact/ripple only if meaningful. Subject geometry and physics claims stay independent of effect beauty.

Transparent effects need deliberate depth testing/writing, sorting and blend choices. Inspect bounds, intersections, camera-dependent artifacts and clipping. Avoid expensive fullscreen volume effects as a default. Do not depend on wide native WebGL lines; use supported mesh-based lines if thick contours are necessary. Reuse geometry/materials where ownership permits; do not rebuild topology every frame.
