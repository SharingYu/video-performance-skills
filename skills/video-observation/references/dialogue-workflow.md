# Read Dialogue With the Action and Reaction

Use this branch when speech is present, may explain an action, or carries a reference's joke or reveal. The goal is a source-linked account of what is said, by whom when supported, and what changes around it. Do not replace the visual workflow or require phoneme-level analysis for ordinary story reading.

## Obtain the actual evidence

Inspect the supplied video's streams with `scripts/video_observe.py inspect`. Select the actual audio stream index from that result; a dubbed track and original track may tell different stories. Keep the source hash, chosen stream, source-video time origin and any audio offset. Do not reset each audio excerpt to zero and then treat its timestamps as full-video times.

There are two local entry paths. Run from this skill's directory; use a new output directory for each job.

```bash
# Optional speech extra and a separately prepared multilingual model directory.
python scripts/dialogue_observe.py transcribe --video clip.mp4 --output observation/dialogue --model-dir /path/to/local/large-v3 --language zh --device cpu --compute-type int8

# Existing captions or a WhisperX result; this command does not run those engines.
python scripts/dialogue_observe.py import --video clip.mp4 --file captions.srt --format srt --time-offset 0 --output observation/captions
python scripts/dialogue_observe.py import --video clip.mp4 --file whisperx.json --format whisperx --time-offset 0 --output observation/whisperx
```

Transcription accepts `--language auto|zh|en`, `--audio-stream INDEX`, and source-video `--start` / `--end` for a bounded question. Use `--no-vad` only for a justified retry, not as the default. The primary model choice is multilingual `large-v3`; an English-only `.en` model or an English distillation is unsuitable as the Chinese default. CPU/int8 avoids requiring a second GPU workload. CUDA/float16 is optional and needs a compatible runtime and available resources.

Imports accept `srt`, `vtt`, or `whisperx`. Explicitly set `--time-offset` so **source-video time = imported cue time + offset**. A subtitle timed to a cropped excerpt needs that excerpt's source start, while a full-video subtitle normally uses zero. If the relationship is unknown, retain it as unresolved instead of picking a convenient offset. A plausible import is not verification that the subtitle belongs to this video or matches its audio.

The tool returns the actual output paths, including `manifest.json`, `transcript.md` and `candidate.srt`. Read the returned manifest and preserve its source and timing evidence. A candidate subtitle is for review; it is not automatically a corrected transcript or approved delivery subtitle. Imported speaker information, when present, is normalized to recording-local anonymous labels; the frozen import and raw segment preserve the upstream record. Neither form names a visible character.

## Review the consequential lines

Read the transcript in source order, retaining short replies, repetitions, incomplete phrases, names and negations. Do not silently polish words into what the story ought to say. Keep a source line and any proposed correction separate, with the reason and evidence. A caption, OCR reading, platform transcript and ASR result are different sources; preserve disagreements rather than overwriting one with another.

The tool may divide a long ASR segment into navigation candidates at word-timestamp gaps strictly greater than one second, only when those words reconstruct the complete raw text. These are convenient return points, not verified sentence or speaker boundaries. Word timing itself can put a following word on the wrong side of a pause. If a consequential phrase is incomplete or crosses a doubtful boundary, request one bounded source interval with context and preserve the comparison; do not move words between roles by grammar alone. The original ASR remains unchanged.

For an important cue, request linked context:

```bash
python scripts/dialogue_observe.py window --dialogue observation/dialogue/manifest.json --segment-id SEGMENT_ID --context 1 --output observation/dialogue-window
```

Use an actual segment ID from the manifest. The default adds one second of context on both sides; increase it only if the trigger or response falls outside. A transcription window reuses its selected audio track; an imported-caption window uses the video's first audio track, since a subtitle file does not establish its track. Inspect the returned stream selection and warnings before associating captions with what is heard. Open the returned visual manifest's actual images and use the returned audio snippet with an available listening-capable host. File extraction or attaching a player is not proof that the assistant heard it. If the host cannot listen, label words as ASR-derived or imported, and keep voice quality, delivery and exact auditory confirmation pending. Do not use the image-only `note` command to certify audio listening.

VAD can miss a very short “嗯”, “别”, an interrupted word or speech under music. An empty transcript is not proof of silence. If the question or captions suggest missed speech, inspect the contextual snippet and retry that bounded interval once with `--no-vad`. Preserve both candidates. Silence, music and effects can also induce ASR hallucinations; a no-VAD retry is a comparison, not automatic evidence of speech. When evidence remains unclear, keep the uncertainty rather than retrying until plausible text appears.

## Connect a line to a performer and response

Anonymous voice clusters answer “which similar-sounding voice segment?”; they do not name people or characters. One performer may voice several animated characters, and several voices may represent one role. Cross-recording speaker IDs are not stable identities. An imported WhisperX speaker label does not add visual character recognition.

Associate a role only when the actual viewed interval supports it: an unambiguous visible speaker, established context, or another explicit source. Mark narration, off-screen speech, overlap and uncertain attribution separately. Do not assign the nearest face, assume the current shot's subject is speaking, or infer a line from a mouth movement. Automatic speaker detection is optional, not a prerequisite for preserving a line whose role remains unknown.

A compact working record is enough:

| Source interval / line ID | Words and source type | Voice label / supported role | Broad visible action and partner response | Meaning or open issue |
|---|---|---|---|---|
| Actual manifest segment and viewed frames | ASR candidate, imported caption, or actually checked words | Keep anonymous voice and character attribution distinct | What starts, stops, turns or changes, and in what order | Separate interpretation from source evidence |

Return to broad attention, body language and reciprocal consequences. Do not add precise gaze, word timings or emotion labels the source does not support. A question mark in ASR text does not establish questioning intonation. Listener responses can begin during a line; preserve meaningful interruption and overlap rather than forcing every response after the last word.

## Protect and hand off

When a phrase changes the action or delivers the payoff, carry its line ID, source interval, speaker-attribution evidence and reaction window into the existing event card and `protected_beats`. State which words or meanings must survive a role/style change, which delivery choices are observed, and which remain a directing proposal. Preserve negation and information order; do not freeze the answer into an earlier frame or remove the listener's recognition in editing.

Keep evidence levels distinct: source streams; machine transcript; caption comparison; viewed speaker/reaction; actually listened-to delivery. None automatically upgrades the others. ASR confidence, VAD, forced alignment and agreement between assistants cannot certify correct words, a known character, natural audio or real-time comic rhythm. Finish the supported analysis without making routine user confirmation of each line a dependency.
