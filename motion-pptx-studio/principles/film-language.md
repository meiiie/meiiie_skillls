# film-language
A signature film is cinema: a camera with intent over a world that is busy doing its job.
A pan across a still diagram is a slideshow with a moving frame (Codex v6.4: motion 9.9, 7.0).
- **At least one 3-D camera move per ManimGX film:** tilt or orbit (`ThreeDScene.move_camera(phi=, theta=)`,
  `frame.set_euler_angles` / `reorient`), tilt or orbit >= 25 deg. `film_check.py` FAILS any non-Anatomy film
  with depth < 0.10 (a full frame no longer excuses it), motion < 5, alive < 35 % or fill < 30 %.
- **Two or more kinds of camera move per film**, each motivated: establish (wide/plan view),
  tilt from plan to oblique to reveal depth, orbit to show the other side, push in on the
  detail that carries the number, pull out for scale. ManimGX: `class F(m.ThreeDScene)` and
  `self.move_camera(phi=, theta=, zoom=, added_anims=[...])` (proof: research-v65/proof/cam.py).
  Keep kit.View for type-safe 2-D tracking inside one of those moves.
- **The process keeps running while the camera moves** (`added_anims`): drops fall, levels rise,
  parts travel, counters tick. Assembly is a prologue, at most a third of the runtime.
- **Something changes inside the frame every second.** Passing is the floor, not the goal: look at the strip.
- **Depth layers:** foreground parts that cross the lens, a mid-ground subject, a material
  backdrop (the chapter's surface, not a flat colour). Light from the same side as the slide.
- **End on the composition the next slide continues** (the native end-state slide), not on a hold.
- Storyboard each film as 4-6 beats: beat, camera move, what runs, what the viewer learns.
