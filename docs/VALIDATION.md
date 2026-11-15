# Validation scope

## Available evidence

The package includes a three-route creation hub, two focused companion skills, local project/text and video-observation tools, fictional demonstrations, and ten text cases with a separate expected-judgment oracle. The text cases exercise changed scenery, absent reactions, deadpan acting, visibility, redundant holds and incomplete evidence. Dialogue observation adds optional local ASR, transcript import and source-linked context; its fictional example illustrates the evidence boundary rather than reporting a model-accuracy result.

The examples are authored illustrations. The oracle is an evaluation design, not an automatic score or a published model run. No generated video is distributed as a measured result in this release.

## Package checks

From a clone, with Python 3.12+ for the full suite:

```bash
python scripts/check_package.py
python -m unittest discover -s tests
```

These check required files, local-link portability, release version agreement, text-case structure and common accidental private-file patterns. The tests include negative fixtures. They do not judge humor, acting, perception or originality and are not a comprehensive secrets scanner.

Install `skills/video-observation/scripts/requirements.txt` to run the media integration tests. Without media dependencies, the media suite explicitly skips; the release CI installs them and sets `VIDEO_OBSERVE_REQUIRE_MEDIA=1` so missing dependencies or required fixture encoders fail instead of silently reducing coverage. Temporary media covers source-frame correspondence, variable timing, nonzero starts, crop provenance, output collisions and observation bookkeeping. No fixture media is committed.

The project-tool tests use temporary original text inputs and real CLI processes. They cover UTF-8/BOM/CRLF preservation, long lines, source/index changes, link-only state, URL-token removal, cross-process continuation, artifact version history and path boundaries. URL-only analysis/development records retain metadata provenance without becoming media evidence; later source-dependent stages require real files. A read receipt means only that the tool returned a chunk. A recorded file and its matching hash do not establish a correct adaptation, a complete book analysis or accepted media.

The maintainer also checks installation into clean project folders with the Skills CLI and validates the optional Claude plugin manifest. An installer success proves file discovery and copying, not the reasoning quality of every supported host or model. See the [release notes](https://github.com/SharingYu/video-performance-skills/releases/tag/v0.4.0) for the actual commands and versions used.

Observation journals record what an observer says they opened, with source and view references. The CLI cannot verify the observer's perception. A successful export, note or agreement between assistants is not automatic approval of the video.

## Dialogue validation boundaries

For v0.4, the maintainer ran the local large-v3 model on Windows CPU/int8 using six original offline controls: Chinese, English, short Chinese replies, mixed Chinese/English, digital silence and a synthetic instrumental chord. The two speech-free controls returned no text. The English control reproduced its known words; Chinese controls retained a homophone error and a short-interjection error, including after one bounded no-VAD comparison. These few synthetic controls are not a representative recognition benchmark or a listening pass.

A private, attributed Sintel-trailer trial also exposed a real failure: a full-run ASR segment combined three distant lines and misplaced words near pauses. The tool now offers explicitly unverified word-gap navigation, retaining raw evidence; bounded source-window comparisons recovered different, more complete candidates. Navigation is not automatic sentence or speaker recognition. The initial result and comparisons were retained rather than replaced with a success-only account. No source footage or private trial files are distributed.

Keep transcript-format/timing tests separate from real ASR trials. Importing an SRT/VTT/WhisperX fixture checks parsing and provenance; it does not prove that its words were spoken or its speaker labels are correct. Exporting a linked audio/window checks source association; it does not prove anyone listened. Record the chosen audio stream, actual audio-to-video offset, source hash, model revision, language and compute options for a real transcription trial.

When evaluating speech on representative material, include clear Chinese dialogue and short negations/replies, digital silence, music/effects without speech, off-screen narration, a line across a cut, subtitle/audio disagreement and overlapping speakers. Check audio/video start offsets and silence gaps so a cue does not drift after extraction. An empty VAD-filtered result around suspected speech needs a bounded no-VAD comparison; extra text on silence is a failure, not recovery. Preserve initial and retry candidates.

Word error, source-time agreement, anonymous speaker grouping, visible role attribution, response order, listening and subjective delivery are different questions. Speaker clusters cannot certify role identity; forced alignment cannot certify supplied text. A correct negative control or a few good lines do not establish accuracy for every reference, voice, language or accent. Actual real-time listening is required to judge speech delivery and cue-to-reaction rhythm. No such pass is implied merely by this documentation or a generated transcript.

## Reproduce a behavioral evaluation

Follow [evals/README.md](../evals/README.md). Give a fresh assistant the skill and test inputs, without the oracle. Record the host, model, date, accessible evidence, judgments and reasoning. Compare meaning and evidence use, rather than exact wording. Save missing or ambiguous cases instead of silently marking them passed.

For a future media study, use original or shareable material, retain candidate identity and source intervals, distinguish scene-level from frame-level evidence, and report perception and generation separately. Actual dynamic playback is needed to evaluate timing. Viewer engagement would require audience evidence of its own.

## Not established

- A causal improvement in generated-video quality.
- Accurate perception of every expression, glance or fine paw action.
- Complete or error-free dialogue recognition, visual speaker attribution, or naturalness assessment from transcripts alone.
- Equivalence across video generators or assistant models.
- Full-book semantic consistency or an end-to-end generated, spoken novel series.
- Current publishing eligibility or technical acceptance for Hongguo or another platform.
- A guaranteed comic response, retention uplift, or viral hit rate.

The useful claim is narrower: a portable way to specify and review what a performance must visibly achieve, with explicit counterexamples and uncertainty.
