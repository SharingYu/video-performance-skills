---
name: video-observation
description: "Inspect local videos through shot overviews, ordered short windows, and context-linked crops. Use when reading a reference, checking who looks or moves toward what, following body language and partner reactions, or resolving an uncertain action before adaptation or review. Record visible evidence separately from interpretation."
license: MIT
metadata:
  version: "0.2.0"
---

# Video Observation

Help the existing assistant see enough of a video to understand ordinary, audience-visible performance: who attends to whom or what, what they do, how the body responds, and how a partner answers. Do not turn a broad acting question into facial-muscle, skeleton, or precise gaze measurement.

Respond in the user's language and preserve the requested scope. Read [the observation workflow](references/reading-workflow.md) for commands, evidence handling, and handoff. The bundled [CPU tool](scripts/video_observe.py) uses [these dependencies](scripts/requirements.txt); it includes no model or cloud API.

## Observe before explaining

1. **Cover the shots.** Inspect the overview images before deciding which moments matter. Automatic cut boundaries are navigation candidates, not detected jokes or guaranteed scene boundaries. Overview poses do not establish every action between them.
2. **Return to a question.** If a turn, interrupted action, or partner response is unclear, request a short window around it. Start with the default four frames per second; increase sampling or open an original frame only when the question needs it. Do not exhaustively magnify every moment.
3. **Keep the relationship visible.** Check the full composition alongside a useful crop. A face alone can hide its attention target; an isolated hand can hide the partner's cue.
4. **Write visible facts first.** Describe approximate direction, approach or withdrawal, action changes, partner response, and result. Separate body/head direction, readable eye direction, and the object being handled. Use qualified language for an apparent attention target; an unreadable eye direction can stay unknown without blocking the rest of the scene.
5. **Check the important uncertainty.** An independent observer can inspect the same material before receiving the first interpretation. Use disagreement to choose a useful return view. Agreement between assistants is not ground truth. Stop repeating views when the source cannot resolve the question; retain the uncertainty and continue useful work.

## Make the observation real

The tool exports images and metadata. A path, success message, frame count, caption, or completed decode is not evidence that the assistant saw the images. Open the relevant `views[].image_path` with the host's image-viewing tool, or inspect actual image content returned to the host. Then record the actual view IDs with `note`.

Check the host's response for omitted or discarded images. If a batch is truncated, reopen the missing views in smaller batches before recording them. Calling an image tool is not enough when its image output never reached the model.

Keep observation, interpretation, and open questions distinct. Bind statements to the supplied source version and viewed frames. Sampling gaps remain gaps; not seeing a response in a few frames does not prove it never happened.

Static sequences support poses and visible order. They do not establish real-time comic rhythm or audible quality. Record those limits rather than claiming playback or listening. Complete the work available to the host without making routine per-shot user confirmation a dependency.

Hand verified broad actions and unresolved details to the user's adaptation, shot-planning, or review workflow. If `performance-direction` is already available, its event card can consume these observations; this skill does not require it or any particular production backend.

The bundled tool makes no network call or model API request. Additional cloud review is optional and external: use it only within the task's authorization and, when no extra API cost is required, after confirming the actual project/model is on a free tier. A free website or an unverified key is not proof of a free API. Unavailable service or quota leaves the local workflow usable.

Source acknowledgments and limits: [sources](references/sources.md).
