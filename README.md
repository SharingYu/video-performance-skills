# Video Performance Skills

**Create from a video reference, a novel, or an original idea. Keep the performance that makes it work.**

[简体中文](README.zh-CN.md) · [Three routes](docs/THREE-ROUTES.md) · [Creation hub](skills/video-creation/SKILL.md) · [Examples](examples/three-routes/README.md)

One creation hub, two focused companion skills, and small local tools for AI video creators. Use your existing assistant to develop the story, inspect accessible material, preserve expressive actions and reactions, and carry source-aware decisions into scripts, shots and review. Local tools make no model API calls.

## Choose your route

Reference reading can now include local Chinese/English speech candidates, timed captions and linked action/reaction windows. The optional speech extra uses a separately prepared multilingual model; voice labels, visible characters and actually verified words remain distinct. [Dialogue workflow and example](examples/dialogue/README.md).

| You bring | The hub helps you do |
| --- | --- |
| A video link or file | Obtain real media, connect visible action with candidate dialogue and responses, protect its highlights and rebuild the requested story |
| A novel | Read traceable chunks, develop characters and dramatic units, design episodes, then write scripts and production handoffs |
| An idea or an inspiring video | Compare story mechanisms and develop an original or meaningfully adapted story |

The same brief, source records, series memory and review methods connect all three. A selected script can enter directly at shot design; there is no mandatory full-pipeline ritual. [Route details](docs/THREE-ROUTES.md) · [What is actually provided](docs/CAPABILITIES.md).

## See the difference

A cat reaches for a treat, notices its companion watching, freezes, and redirects the same paw into an overly careful adjustment of a placemat.

| A technically complete scene | The performance worth protecting |
| --- | --- |
| Paw reaches; placemat ends up straight. | **Notice → freeze → conspicuously casual cover-up.** |
| The companion moves the treat dish. | Its quiet response lands; the first cat follows the dish with its eyes, starts to follow with its head, then stops. |

Correct endpoints can still lose the joke. This skill turns the meaningful middle into observable, reviewable requirements. This is a **fictional text illustration**, not a generated-video result. [Read the complete example](examples/reference/output.md).

## Install

With [Node.js 22.20+ and the Skills CLI](https://github.com/vercel-labs/skills), run in your project directory:

```bash
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation
```

Choose your assistant when prompted. Or specify Codex or Claude Code:

```bash
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation --agent codex
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation --agent claude-code
```

This installs instructions and the local observation script. To use the script, install its Python dependencies in an isolated environment. No model is installed. [Setup, manual installation and optional Claude Code plugin](docs/INSTALL.md).

## Use it

Ask your assistant in your preferred language. Attach material it can actually inspect, or provide a concrete observation log.

Start with **video-creation**: “recreate this video's story with my characters,” “adapt this novel into an episodic comic drama,” or “develop an original story from this idea.” It routes the task and uses specialist skills when present. [Three-route text walkthroughs](examples/three-routes/README.md).

**Read a local video before recreating it**

```text
Use video-observation on this local video. Cover each shot, then revisit any
unclear interaction. Record roughly who looks at whom, body actions, partner
responses and their order. Actually open the returned images before recording
an observation. Then use performance-direction for the protected beats.
```

The observation skill provides a shot overview, denser time windows, context-linked crops and an observer journal. It does not require fine facial coding or pose measurement. [Local video walkthrough](examples/observation/README.md).

**Recreate a reference's performance**

```text
Use performance-direction on this reference. Identify the looks, body actions,
reactions and attention changes that make it work. Separate observations from
interpretations. Make a performance event card; preserve its essential beats
while allowing a different setting. Do not generate video yet.
```

**Design an original visual highlight**

```text
Use performance-direction. Two adult library workers prepare a book display:
Alex wants to look competent and tends to overdo things; Robin quietly helps
Alex save face. Propose three different visual-comedy mechanisms, compare them,
then develop the strongest into a visible performance event card. No dialogue.
```

**Review a candidate**

```text
Use performance-direction to compare this candidate with its event card.
Check action, continuity, highlight and rhythm separately. Identify what is
visible, missing, or still unverified. Do not infer acting from endpoints alone.
```

The skill follows your requested scope. An event card does not force every request through a full production pipeline.

## What you get

- **Two creative entry points:** reference essence and original highlights.
- **One integrated hub:** reference reconstruction, novel adaptation and original/reference-derived story development.
- **Recoverable source work:** frozen inputs, hashes, UTF-8 chunks, delivered-read records and versioned artifacts. File integrity is distinct from understanding and creative approval.
- **Local observation tools:** shot coverage, timestamped image sequences, crops linked to the full view, and observer-attested notes. Exporting frames does not mark them watched.
- **One six-part event card:** expectation/payoff, visible performance chain, protected details, attention handoff, adjustable conditions, and evidence or creative intent.
- **A production handoff:** connect protected beats to shot duties, actual candidate intervals, and repair decisions.
- **Separate review gates:** technical integrity, action, continuity, highlight, and rhythm. Unseen evidence stays pending.
- **Portable examples and counterexamples:** self-contained text materials, including restrained acting, occlusion, changed scenery, and misleading endpoint evidence.

The package is model-agnostic. It can inform a workflow using H3, another video model, live action, or animation; generation backends are not bundled or controlled. [End-to-end workflow](docs/WORKFLOW.md).

## What is verified

v0.3 adds the three-route hub and a standard-library source/project tool. Text-intake tests check byte preservation, Unicode chunks, source changes, continuation and artifact history. Media tests use temporary synthetic clips to check frame/time correspondence, crops and observation bookkeeping. Text examples and the ten-case oracle remain design materials, not a measured video-quality score.

Media understanding still depends on the assistant actually receiving the images and reasoning about them. Static sequences support visible action and order; they do not establish real-time rhythm or audible quality. No arbitrary-URL downloader, video-generation server or posting service is included. We do not claim measured improvements in generated video, exact imitation, audience laughter, or virality. [Validation scope](docs/VALIDATION.md).

Novel analysis and script development are usable workflows; a complete spoken series still needs real image/video, voice, timing, editing and publishing tools. Local H3 experience is not evidence of a verified novel-to-platform automation pipeline. [Readiness boundaries](docs/CAPABILITIES.md).

## Contribute

The most useful contributions are reproducible counterexamples, original examples you can share, translations, and small backend adapters with clear behavior. [Contribution guide](CONTRIBUTING.md) · [Roadmap](docs/ROADMAP.md) · [Open an issue](https://github.com/SharingYu/video-performance-skills/issues).

## Sources and license

Maintained by [SharingYu](https://github.com/SharingYu). The synthesis builds on credited acting, animation, and comedy resources. [Attribution and pinned sources](docs/ATTRIBUTION.md).

[MIT](LICENSE) covers the contributions distributed in this repository. Linked third-party resources retain their own terms; their manuals, videos, images, and full skill collections are not bundled.
