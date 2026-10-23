# cinematic-manimgx
R14 critics called our films "toy-like cube banks": flat-shaded pastel blocks on an empty ground. A film is a shot.
- **Light it:** a key light at 30-45 degrees, a rim/back light, falloff on the ground and contact shadows.
  ManimGX: `SunLight`/`SpotLight`/`PointLight` + `EnvironmentLight`, `set_material(Material(...))` (roughness,
  metalness) on 3-D surfaces/solids; never flat fill_opacity=1 boxes.
- **Real materials:** brushed metal, wet sand, paper, fabric, glass - a texture map or a procedural grain on every
  surface, in the deck's palette (style.json).
- **Camera depth:** a lens (focal length), near objects soft and far objects soft (depth of field by blur layers),
  2+ moves with one 3-D move; the subject fills >= 50 % of the frame at the hero moment.
- **Shape of the real thing:** model the object's silhouette (a crank, a phin, a hull), not cubes standing in for it.
  If it cannot be modelled well, film a photo (parallax of cut-out layers) instead.
- **Gate:** `scripts/film_art.py FILM.mp4` (build.py runs it on every embedded film): FAIL when > 30 % of the
  subject is flat-shaded (a toy render); WARN when the subject fills < 30 %. Re-light and re-render; never ship a FAIL.
- **Gates define film quality** (film_art flat <= 30 %, film_check depth >= 0.10): calm water or sky stays textured and lit; a critic order to make it flat/clean loses to the gate (DONE: conflict).
