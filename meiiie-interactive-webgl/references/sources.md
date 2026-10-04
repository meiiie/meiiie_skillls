# Sources and provenance

## Reference-derived principles

An inspected user-supplied 26.3-second, 1920×1080, silent engine-like assembly clip inspired the workflow. Visible evidence: a stationary stage; axial/lateral part separation; selective bright contours; reassembly; staged luminous exhaust; environment glow; residual smoke. These support compositional and interaction hypotheses, not claims about original source code, true live picking, physical accuracy, or a one-shot creation process. Do not distribute the supplied media or copy its exact branded geometry without appropriate rights. No reference asset is bundled in this skill.

Keep a project asset ledger: source/creator, URL or supplied-file identifier, license/permission, modifications, attribution requirements, and intended distribution. Original procedural geometry is a useful substitute when licensed meshes are unavailable. An externally visible model requires its own rights check; a clip's existence grants no reuse license. Avoid claiming engineering fidelity for invented details.

## Primary documentation checked 2026-10-04

- [Three.js Raycaster](https://threejs.org/docs/pages/Raycaster.html): NDC camera picking, target layers, line thresholds and mesh face direction affect selection.
- [Three.js EdgesGeometry](https://threejs.org/docs/pages/EdgesGeometry.html): angle-based edge extraction, not a complete authored technical drawing.
- [Three.js ShaderMaterial](https://threejs.org/docs/pages/ShaderMaterial.html): custom GLSL and uniforms; native line-width controls have platform limitations.
- [MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices): resource discipline, draw-call batching, back-buffer sizing, and avoiding blocking calls.
- [MDN context loss](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/webglcontextlost_event): browser context-loss event and testing hook. Recreate/reinitialize necessary GPU resources during restoration; test actual renderer behavior.
- [MDN reduced motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion): user motion preference; JavaScript-driven scene animation needs matching handling.
- [MDN Page Visibility](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API): document visibility and lifecycle signals.

These are verified pages, not guarantees about a project's installed version. Check pinned APIs and supported WebGL capabilities before coding. A historical Three.js cleanup manual URL returned 404 during this review and is not treated as verified guidance. Performance numbers in this skill are proposed starting budgets, not documentation claims or benchmark results.
