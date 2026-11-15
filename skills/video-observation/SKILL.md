---
name: video-observation
description: "Inspect reference-video actions, broad attention, spoken dialogue and partner reactions. Use shot views and context-linked crops, with optional local speech transcription or imported subtitles, to connect what is said to who acts or responds. Keep visible, audio-derived and interpreted evidence distinct."
license: MIT
metadata:
  version: "0.4.0"
---

# Video Observation

Help the existing assistant understand ordinary, audience-visible performance: who attends to whom or what, what they do or say, how the body responds, and how a partner answers. Do not turn a broad acting question into facial-muscle, skeleton, or precise gaze measurement.

Respond in the user's language and preserve the requested scope. Read [the image observation workflow](references/reading-workflow.md) for commands, evidence handling, and handoff. Its [CPU tool](scripts/video_observe.py) uses [these dependencies](scripts/requirements.txt), without model weights or a cloud API. When speech may carry story meaning or a reaction cue, also read [the dialogue workflow](references/dialogue-workflow.md): optional local ASR or imported transcripts support the same source timeline, but do not certify listening or identify a visible character.

## Observe before explaining

1. **Cover the shots.** Inspect the overview images before deciding which moments matter. Automatic cut boundaries are navigation candidates, not detected jokes or guaranteed scene boundaries. Overview poses do not establish every action between them.
2. **Return to a question.** If a turn, interrupted action, or partner response is unclear, request a short window around it. Start with the default four frames per second; increase sampling or open an original frame only when the question needs it. Do not exhaustively magnify every moment.
3. **Keep the relationship visible.** Check the full composition alongside a useful crop. A face alone can hide its attention target; an isolated hand can hide the partner's cue.
4. **Write visible facts first.** Describe approximate direction, approach or withdrawal, action changes, partner response, and result. Separate body/head direction, readable eye direction, and the object being handled. Use qualified language for an apparent attention target; an unreadable eye direction can stay unknown without blocking the rest of the scene.
5. **Check the important uncertainty.** An independent observer can inspect the same material before receiving the first interpretation. Use disagreement to choose a useful return view. Agreement between assistants is not ground truth. Stop repeating views when the source cannot resolve the question; retain the uncertainty and continue useful work.

For a reference recreation, establish whether dialogue is present and what coverage was actually obtained. Connect consequential lines to the speaker, action and listener response using the dialogue workflow. An audio track, silent ASR result or subtitle file alone cannot establish that the scene has no speech.

## Make the observation real

The tool exports images and metadata. A path, success message, frame count, caption, or completed decode is not evidence that the assistant saw the images. Open the relevant `views[].image_path` with the host's image-viewing tool, or inspect actual image content returned to the host. Then record the actual view IDs with `note`.

Check the host's response for omitted or discarded images. If a batch is truncated, reopen the missing views in smaller batches before recording them. Calling an image tool is not enough when its image output never reached the model.

Keep observation, interpretation, and open questions distinct. Bind statements to the supplied source version and viewed frames. Sampling gaps remain gaps; not seeing a response in a few frames does not prove it never happened.

Static sequences support poses and visible order. They do not establish real-time comic rhythm or audible quality. Record those limits rather than claiming playback or listening. Complete the work available to the host without making routine per-shot user confirmation a dependency.

Hand verified broad actions and unresolved details to the user's adaptation, shot-planning, or review workflow. If `performance-direction` is already available, its event card can consume these observations; this skill does not require it or any particular production backend.

The bundled tools make no model API request; image observation and transcript import need no speech model. Optional transcription requires separately prepared local model files and the speech extra. It does not silently substitute a cloud service. Additional cloud review is external: use it only within the task's authorization and, when no extra API cost is required, after confirming the actual project/model is on a free tier. A free website or an unverified key is not proof of a free API. Unavailable service or quota leaves the local image/import workflow usable.

Source acknowledgments and limits: [sources](references/sources.md).
