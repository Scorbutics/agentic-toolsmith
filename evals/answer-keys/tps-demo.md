# Answer key — tps-demo

**Repository:** https://github.com/godotengine/tps-demo @ `a82f154` · **Shape:** Godot 4 game

**Filled by:** bug-grounded draft — an agent blind to the skill, from the fixed bugs below · 2026-11-25 — verify the citations
**M1 accepted:** piece × witness

I examined 47 candidates. These are all the non-merge commits reachable from `a82f154` (138 in total) whose subject or body matches fix/bug/regression/revert/crash/broken/wrong/error/issue/#n. That is fewer than 60, so I took all of them. I kept 27 real behaviour or visual bugs. I excluded 20: 4 CI action bumps, 5 docs or README changes, 6 engine-port or engine-version or feature commits with no identifiable fixed bug, 3 tuning or refactor commits, and 2 file-mode or stale-import housekeeping commits. The evidence is moderate. The project has no tests or CI gameplay checks at all, and several kept fixes are bundled into larger update commits (`a82f154`, `374bd8d`, `241b450`, `2beb6c4`, `b1048c5`, `34b6977`), so the exact defect sometimes comes from the commit message more than from a small diff. The bugs fall into three groups. Most are scene or entity behaviour: enemy state, aim, gravity, sound tracks. The next group is rendering artefacts that can only be seen. The rest are errors that appear only when a command or input runs: firing, Play, settings apply, export. Seven bugs came from engine-version, platform or renderer differences.

| Cell | Expect (`propose` · `leave` · `either`) | Why — what in the repository says so |
|---|---|---|
| `unit × bring out` | either | 1 bug: `bd457e3` (operator-precedence error in the robot's `to_cannon_local` aim maths). It did not crash, so one bug is not enough to propose. |
| `unit × witness` | either | 0 bugs cheapest here. GDScript functions can log state, so the cell can exist. |
| `unit × reach in` | either | 0 bugs cheapest here. A single function can be evaluated inside the running game, so the cell is not structurally impossible. |
| `piece × bring out` | propose | 5 bugs: `65de4fd` (crash in `blast.gd` `_process` on a freed camera), `1fd0e76`, `4e8ea82`, `b1048c5`, `d56b156`. These are scenes, resources or shaders that fail to load or compile when opened alone. |
| `piece × witness` | propose | 10 bugs: `2039076`, `e3bfd23`, `fab68bc`, `d564c62`, `34b6977`, `79e878d`, `2beb6c4`, `733e195`, `93556f7`, `702114f`. Each is a red robot or player scene whose recorded state, animation parameter, audio track or error log is wrong. |
| `piece × reach in` | propose | 6 bugs: `a82f154`, `518df67`, `374bd8d`, `241b450`, `0840219`, `79b67eb`. Each is a rendering artefact (shadow acne, opaque or thin materials, overly strong lights, shaded particles, vertex-compression artefacts, over-occlusion) that can only be seen in captured frames. |
| `operation × bring out` | either | 0 bugs cheapest here. A single settings apply or RPC handler could be run in a fixture, so the cell can exist. |
| `operation × witness` | propose | 5 bugs: `b314223` (typed-array error spam on every shot), `3a92da2` (pipeline compilations on the first shot), `690ee91` (wrong cached-load branch on Play), `4d510e9` (resolution setting read `ssao_quality`), `117eca0` (export errors from legacy transform tracks). |
| `operation × reach in` | either | 0 bugs cheapest here. Input can be injected into the running game, so the cell can exist. |
| `journey × bring out` | either | 0 bugs cheapest here. A scripted headless playthrough is possible. |
| `journey × witness` | either | 0 bugs cheapest here. Host and client multiplayer sessions (`bb833aa`) exist and could be recorded, but none of the fixed bugs needed them. |
| `journey × reach in` | either | 0 bugs cheapest here. A full playthrough with injected input and captured frames is possible. |
| `loop` | propose | 7 bugs came from environment, platform, renderer or export differences: `518df67` (visual errors only on Linux), `d56b156` (Windows name conflict), `117eca0` (export errors), `0840219` (vertex-compression artefacts), and `b314223`, `1fd0e76`, `702114f` (engine-version changes). |

## Evidence — fixed bugs

| Commit | What broke | Cheapest cell that would have caught it | Why that cell |
|---|---|---|---|
| a82f154 | The flying forklift's spotlight showed shadow acne (a bundled fix in the 4.7.2 update). | `piece × reach in` | The forklift scene has to be rendered and the frame looked at. Nothing logs it. |
| 2039076 | Red robots spawned in their walk animation and never went idle. The IDLE state was missing. | `piece × witness` | A robot spawned alone with no player could be checked by recording its `state` or animation. |
| e3bfd23 | The robot laser's hit point was cast downward into the floor, because it used `-basis.z` on a RayCast3D that is rotated 90 degrees. | `piece × witness` | A robot plus target in a harness, with the recorded `intersect_ray` hit position, shows the shot lands at its feet. |
| b314223 | Firing bullets spammed typed-array errors in 4.5, because `intersect_ray` was given an exclude array of `[self]`. | `operation × witness` | One shoot action and a look at the error log is enough. |
| 117eca0 | The export failed with errors from orphan animation resources that still had legacy `transform` tracks. | `operation × witness` | A headless export run, with its output read for errors. |
| 3a92da2 | The first shot stuttered with 2 to 4 extra pipeline compilations, because the BackgroundCache bullet was not cached. | `operation × witness` | Fire once and record the pipeline-compilation monitor. |
| 34b6977 | The robot walk sound did not play. The Walk animation had no working audio track (fixed with the 4.3 update). | `piece × witness` | Play the robot's Walk animation in isolation and record audio playback. |
| 690ee91 | Pressing Play took a "superfluous and wrong" `has_cached` branch that called `load_threaded_get` on a load that had not been requested. | `operation × witness` | One Play press, with the emitted signal and errors recorded. |
| 518df67 | On Linux the font was very thin, Material_001 failed to compile, and god rays, sparks, the laser and the blast showed wrong or opaque cards. | `piece × reach in` | Render each effect or menu scene on Linux and capture frames. This is a platform (loop) difference. |
| 241b450 | Some particles were shaded when they should have been unshaded. | `piece × reach in` | A purely visual difference, seen in a captured frame of the effect scene. |
| 93556f7 | The aiming camera transition was broken. The player scene was missing the AIM animations or tracks. | `piece × witness` | Trigger aim on the player scene and record the camera transform over time. |
| 374bd8d | Lights were overly strong because their range was excessive (clustering artefacts), and the menu did not use `experiment.hdr` for reflections. | `piece × reach in` | Only visible in rendered frames of the level and menu. |
| bd457e3 | The robot aim blend was wrong because of operator precedence: `target_position + Vector3.UP * xform` instead of `(target_position + Vector3.UP) * xform`. | `unit × bring out` | Pure vector maths that a function-level test would catch. |
| 2beb6c4 | After the 4.0 port the step audio was missing (old-format AudioStreamRandomizer), and the GI quality setting was written to ProjectSettings at runtime, where it had no effect. | `piece × witness` | Play the player step and record whether audio is emitted. |
| 0840219 | Level geometry showed visual artefacts from vertex compression (issue #143). | `piece × reach in` | A render artefact, only seen in a frame of the level. This is a renderer/import (loop) difference. |
| 79b67eb | Misplaced occluder shapes caused too much occlusion, so objects disappeared (issue #148). | `piece × reach in` | Render the level from affected viewpoints and compare frames. |
| fab68bc | An idle Red Robot did not apply gravity and floated. | `piece × witness` | A robot spawned alone with no player, with its Y position recorded over frames. |
| 65de4fd | The game crashed in `blast.gd` `_process` when the camera reference had been freed (`if camera` instead of `is_instance_valid`). | `piece × bring out` | Run the impact-effect scene alone and free its camera to reproduce the crash. |
| 1fd0e76 | The red robot laser shader broke after the engine's shader-language change to varyings. The varying it wrote was rejected. | `piece × bring out` | Load and compile the shader or scene alone and the compile error appears. This is an engine-version (loop) difference. |
| 79e878d | The player step sound was wrong. Animation lengths and timings were fixed. | `piece × witness` | Play the player run animation and record the step-sound calls and their timings. |
| 733e195 | The shader-cache bullet's ExplosionAudio was `queue_free`d, which left a dangling node for the bullet script. | `piece × witness` | Run the shader-cache scene and watch the error log when the cache bullet explodes. |
| b1048c5 | After the 3.2 update, models referenced textures that did not exist and the fog was broken. | `piece × bring out` | Load each model or scene alone and missing-dependency errors appear. |
| 4d510e9 | The resolution setting was chosen from `ssao_quality` instead of `resolution`, so the 1080/720/576 options misapplied. | `operation × witness` | Apply one resolution setting and record the resulting viewport stretch size. |
| 4e8ea82 | The level failed to load after `d56b156` deleted `Tile_Steel.material`, which `demolevel.dae` still referenced. | `piece × bring out` | Opening the level scene alone fails on the missing dependency. |
| d564c62 | Robot aim wrote the blend position to `parameters/aiming/blend_amount` instead of `parameters/aim/blend_position`. | `piece × witness` | A robot in a harness, with the AnimationTree aim parameter recorded, shows it never changes. |
| d56b156 | `Tile_Steel.material` caused a name conflict on Windows (#9). | `piece × bring out` | Import or load the level on a case-insensitive filesystem. This is a platform (loop) difference. |
| 702114f | The physics engine setting `"GodotPhysics - deprecated"` became invalid after the 3.1-beta rename. | `piece × witness` | Any scene run logs a fallback or invalid-engine message. This is an engine-version (loop) difference. |

## Excluded candidates

- da8f61e — feature (HDR output, D3D12 default); no bug fixed.
- 9f4ba0c — CI-only (actions/checkout bump).
- c42dd30 — CI-only (actions/checkout bump).
- 5109b6a — tuning of volumetric fog values to stop relying on an engine transmittance bug; no game defect fixed.
- 90f2e38 — refactor (static typing); no behaviour fix.
- 5f4c259 — feature (MetalFX scaling modes).
- a3e0b06 — engine-version update (4.5) and re-imports; no identified behaviour fix.
- 8091677 — CI-only (actions/checkout bump).
- bd9b9ef — engine-version update (4.4); uid files and re-imports.
- 34c0506 — removes dangling `.import` files; asset housekeeping.
- 32f43f4 — file permission fix after #184; no behaviour change.
- ceb92d0 — CI-only (actions/checkout bump).
- bb833aa — feature (networked multiplayer).
- 2f67daf — docs (README controls).
- f41444c — engine port to 4.0 (the work that introduced bugs, not a fix).
- df9e497 — feature/quality (anisotropic filtering).
- 3512cff — fog configuration tuning; no defect named.
- be5e19b — feature (in-game debug text).
- 539e585 — docs (README import/LFS note).
- a65ff53 — docs (README and markdownlint).
