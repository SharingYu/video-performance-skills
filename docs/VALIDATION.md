# Validation scope

## Available evidence

v0.2 includes two self-contained skills, a CPU video-observation CLI, fictional text demonstrations, and ten text cases with a separate expected-judgment oracle. The text cases exercise changed scenery, absent reactions, deadpan acting, visibility, redundant holds and incomplete evidence.

The examples are authored illustrations. The oracle is an evaluation design, not an automatic score or a published model run. No generated video is distributed as a measured result in this release.

## Package checks

From a clone, with Python 3.12+ for the full suite:

```bash
python scripts/check_package.py
python -m unittest discover -s tests
```

These check required files, local-link portability, release version agreement, text-case structure and common accidental private-file patterns. The tests include negative fixtures. They do not judge humor, acting, perception or originality and are not a comprehensive secrets scanner.

Install `skills/video-observation/scripts/requirements.txt` to run the media integration tests. Without media dependencies, the media suite explicitly skips; the release CI installs them and sets `VIDEO_OBSERVE_REQUIRE_MEDIA=1` so missing dependencies or required fixture encoders fail instead of silently reducing coverage. Temporary media covers source-frame correspondence, variable timing, nonzero starts, crop provenance, output collisions and observation bookkeeping. No fixture media is committed.

The maintainer also checks installation into clean project folders with the Skills CLI and validates the optional Claude plugin manifest. An installer success proves file discovery and copying, not the reasoning quality of every supported host or model. See the [release notes](https://github.com/SharingYu/video-performance-skills/releases/tag/v0.2.0) for the actual commands and versions used.

Observation journals record what an observer says they opened, with source and view references. The CLI cannot verify the observer's perception. A successful export, note or agreement between assistants is not automatic approval of the video.

## Reproduce a behavioral evaluation

Follow [evals/README.md](../evals/README.md). Give a fresh assistant the skill and test inputs, without the oracle. Record the host, model, date, accessible evidence, judgments and reasoning. Compare meaning and evidence use, rather than exact wording. Save missing or ambiguous cases instead of silently marking them passed.

For a future media study, use original or shareable material, retain candidate identity and source intervals, distinguish scene-level from frame-level evidence, and report perception and generation separately. Actual dynamic playback is needed to evaluate timing. Viewer engagement would require audience evidence of its own.

## Not established

- A causal improvement in generated-video quality.
- Accurate perception of every expression, glance or fine paw action.
- Equivalence across video generators or assistant models.
- A guaranteed comic response, retention uplift, or viral hit rate.

The useful claim is narrower: a portable way to specify and review what a performance must visibly achieve, with explicit counterexamples and uncertainty.
