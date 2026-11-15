# Observe a local video

This walkthrough uses your own local file. It does not download or upload media and makes no model API calls. The script extracts images; your assistant must actually open them with its image-viewing tools.

Set up Python as described in [installation](../../docs/INSTALL.md). In the commands below, `python` means that isolated environment's Python, and `my clip.mp4` means an existing local video you choose.

## 1. Inspect and cover the shots

```bash
python skills/video-observation/scripts/video_observe.py inspect --video "my clip.mp4"
python skills/video-observation/scripts/video_observe.py overview --video "my clip.mp4" --output scratch/overview
```

The overview exports start/middle/end frames for detected shots and readable sheets. Shot detection proposes boundaries; it is not action recognition. Ask the assistant to open the sheet images listed in the returned manifest and make a simple map of who does what. A returned path alone is not an observation.

If the host reports discarded images, reopen those views in smaller batches. One or two sheets per response is a useful starting point for hosts with strict image-output limits.

## 2. Revisit an unclear interaction

```bash
python skills/video-observation/scripts/video_observe.py window --video "my clip.mp4" --start 4 --end 7 --fps 4 --output scratch/interaction
```

This requests the half-open interval `[4, 7)` seconds relative to the first displayed source frame. The manifest records the actual selected source frames and their timestamps. It does not synthesize missing frames. Open the relevant sheet images, then individual frame PNGs if the broad look or body action remains unclear.

Prefer concrete questions: Who turns toward whom? Does the reaching hand stop before changing target? Does the partner respond before or after the move? Keep a quiet character in the inspection; little global motion does not imply nothing happens.

Use `--fps 0` for all native frames in a short interval only when necessary. Increase coverage because of a question, not to measure every blink.

## 3. Enlarge a region with its context

```bash
python skills/video-observation/scripts/video_observe.py crop --manifest scratch/interaction/manifest.json --frame-id f000000120 --box 100,100,700,700 --output scratch/detail
```

Replace the frame ID with one returned by your manifest. The box is normalized left/top/right/bottom on a 0–1000 grid. The crop retains its full-frame relationship and source identity. Open both views if the other performer or handled object is needed to understand the action. Cropping cannot recover detail that the original lacks.

## 4. Record only what was actually inspected

After opening images, use their actual view IDs:

```bash
python skills/video-observation/scripts/video_observe.py note --manifest scratch/interaction/manifest.json --view-ids sheet0001 --observer assistant --method static_sequence --kind observation --text "The left performer turns toward the partner; the raised hand stops before changing target."
```

Replace `sheet0001` with the actual returned view ID. The note is an observer's attestation, not an automatic proof of perception. Put an explanation such as “trying to save face” in a separate `--kind interpretation` note. Use `--kind question` for something to revisit. An optional `--event-id` connects the note to a protected performance event.

Existing output manifests are not overwritten; use a new output directory for another extraction. Scratch images, notes and private media belong outside the release package.

## Handoff

Give `performance-direction` the observed sequence and evidence references. Identify the audience-facing turn, essential body action and partner response. Static sequences support poses and order; real-time rhythm and sound remain pending until a suitable backend actually observes them.

The local tools do not require a cloud account. If a later workflow uses a free cloud tier, verify the account's real tier first and stop at its quota; this package includes no cloud client or paid fallback.
