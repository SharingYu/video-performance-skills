# Video Performance Skills

**Keep the look, gesture, and reaction that make a scene work.**

[简体中文](README.zh-CN.md) · [Try an example](examples/README.md) · [Skill](skills/performance-direction/SKILL.md) · [Evaluation cases](evals/README.md)

A focused Agent Skill for AI video creators: analyze the expressive essence of a reference, design original visual highlights, and carry those choices into shots and review. Works with your existing AI assistant; the text examples need no GPU or video service.

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
npx skills add SharingYu/video-performance-skills --skill performance-direction
```

Choose your assistant when prompted. Or specify Codex or Claude Code:

```bash
npx skills add SharingYu/video-performance-skills --skill performance-direction --agent codex
npx skills add SharingYu/video-performance-skills --skill performance-direction --agent claude-code
```

This installs a skill, not a new model or video generator. [Manual installation and optional Claude Code plugin](docs/INSTALL.md).

## Use it

Ask your assistant in your preferred language. Attach material it can actually inspect, or provide a concrete observation log.

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
- **One six-part event card:** expectation/payoff, visible performance chain, protected details, attention handoff, adjustable conditions, and evidence or creative intent.
- **A production handoff:** connect protected beats to shot duties, actual candidate intervals, and repair decisions.
- **Separate review gates:** technical integrity, action, continuity, highlight, and rhythm. Unseen evidence stays pending.
- **Portable examples and counterexamples:** self-contained text materials, including restrained acting, occlusion, changed scenery, and misleading endpoint evidence.

The package is model-agnostic. It can inform a workflow using H3, another video model, live action, or animation; these backends are **not bundled or controlled by v0.1**. [End-to-end workflow](docs/WORKFLOW.md).

## What is verified

v0.1 is an instruction package with fictional text examples and a ten-case text evaluation set. Package checks cover portability, links and release hygiene. The evaluation oracle defines intended judgments; it is not a measured video-quality score.

Media understanding depends on the assistant's access and perception capabilities. No arbitrary-URL video reader, rendering server, expression-transfer engine, or posting service is included. We do not claim measured improvements in generated video, exact imitation, audience laughter, or virality. [Validation scope](docs/VALIDATION.md).

## Contribute

The most useful contributions are reproducible counterexamples, original examples you can share, translations, and small backend adapters with clear behavior. [Contribution guide](CONTRIBUTING.md) · [Roadmap](docs/ROADMAP.md) · [Open an issue](https://github.com/SharingYu/video-performance-skills/issues).

## Sources and license

Maintained by [SharingYu](https://github.com/SharingYu). The synthesis builds on credited acting, animation, and comedy resources. [Attribution and pinned sources](docs/ATTRIBUTION.md).

[MIT](LICENSE) covers the contributions distributed in this repository. Linked third-party resources retain their own terms; their manuals, videos, images, and full skill collections are not bundled.
