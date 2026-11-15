# Attribution and source scope

The distributed skill is an original, concise synthesis by SharingYu. Its methods draw on the resources below. These ideas are not presented as newly invented acting or comedy theory. We do not bundle the upstream skill collections, instructional media, manuals, or book excerpts.

Sources were reviewed at the pinned revisions listed here. Upstream licenses govern upstream content; the repository's MIT license covers the contributions actually distributed here. Linking a source is not an endorsement by its author.

| Source | Revision / terms observed | Adopted scope |
| --- | --- | --- |
| [facial-expression-prompting](https://github.com/zhouwei713/facial-expression-prompting/tree/a3236cc9b8972ce3dab998c438bfbb51542a411b) by zhouwei713 | `a3236cc9b8972ce3dab998c438bfbb51542a411b`; root MIT, copyright 2026 zhouwei713 | Trigger, recognition, concealment, visible leakage and residue; translating an emotional intention into observable behavior. No fixed timing or human facial-action codes for animals. |
| [Higgsfield Acting](https://github.com/OSideMedia/higgsfield-ai-prompt-skill/blob/6a6a5dd105d285782dd6992692be4d8b3825ca13/skills/higgsfield-acting/SKILL.md) by O-Side Media | `6a6a5dd105d285782dd6992692be4d8b3825ca13`; root MIT, copyright 2026 O-Side Media | Character objectives, attention targets, triggered habits and persistence after a reaction. No vendor syntax or claimed empirical performance imported. |
| [joke-engineering](https://github.com/jwynia/agent-skills/blob/e02ec7e226a6e4f8419fd3b88a1d8e472d421b32/skills/creative/humor/joke-engineering/SKILL.md) by jwynia | `e02ec7e226a6e4f8419fd3b88a1d8e472d421b32`; the selected file declares MIT; no blanket license claim for the entire collection | Diagnose over-obvious, obscure, over-explained, out-of-character and overlong setups. Used as questions, not a laughter predictor. |
| [Use Character Staging to Guide Viewer Focus](https://www.animationmentor.com/blog/tutorial-use-character-staging-to-guide-viewer-focus/) by Nathaniel Seymour / Animation Mentor | Public tutorial, October 6, 2026; linked, not redistributed | Attention handoff, allowing one character to settle while another acts, and judging readability from the actual camera. |
| [Animating Caution in Character Acting](https://www.animationmentor.com/blog/tutorial-animating-caution-in-character-acting/) by Nathaniel Seymour / Animation Mentor | Public tutorial, October 27, 2026; linked, not redistributed | Discovery before head/body response; anticipation, peak and recovery. Example frame counts are not universal prescriptions. |
| [CatFACS](https://github.com/AnimalFACS/CatFACS/tree/afec3ce30c1af06f7122c4bcf3de269dc1388bd1) by AnimalFACS | `afec3ce30c1af06f7122c4bcf3de269dc1388bd1`; linked only | Separate observable feline movement from an emotion label. This is not an emotion detector or video-generation control. Manuals and training media are not included. |

## Video observation sources — v0.2

The local observation script is original implementation. The following projects informed the workflow and interfaces; their code and installers are not vendored:

| Source | Fixed version / terms | Adopted scope and limits |
| --- | --- | --- |
| [video-understanding-skill](https://github.com/subh05sus/video-understanding-skill/tree/344c608d78f13d95ee644fbf3093c954cdad5281) | `344c608d78f13d95ee644fbf3093c954cdad5281`; MIT | Question-led overview, revisit, enlargement and observation notes. No Apple-only perception dependencies or assumption that still scenes need only one frame. |
| [agamm/video-agent](https://github.com/agamm/video-agent/tree/cc00d2815869cbf2d708426a5082612f0c3b4dbf) | `cc00d2815869cbf2d708426a5082612f0c3b4dbf`; MIT | Grid-to-frame navigation and source mapping. No Mac-only dependencies, average-fps timestamp conversion or editing subsystem imported. |
| [Qwen-MM-Plugins core](https://github.com/QwenLM/Qwen-MM-Plugins/tree/33a54695774020e5da2d6b1ed13119d4014f848f) | core v1.3.0, `33a54695774020e5da2d6b1ed13119d4014f848f`; Apache-2.0 | Native image-returning observation interfaces and context-linked crops. No cloud caption service or MCP code bundled; do not assume requested sampling equals actual images received. |

Runtime dependencies are installed separately: [PyAV](https://github.com/PyAV-Org/PyAV) (BSD-3-Clause; links FFmpeg libraries), [Pillow](https://github.com/python-pillow/Pillow) (the tested 13.0.0 distribution declares MIT-CMU), and [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) (BSD-3-Clause; includes its own dependency tree). FFmpeg's build-dependent LGPL/GPL terms remain applicable to FFmpeg libraries; this repository does not redistribute its binaries. Refer to the installed distributions for their complete notices. [PyAV timestamps](https://pyav.org/docs/stable/api/frame.html) and [FFmpeg showinfo](https://ffmpeg.org/ffmpeg-filters.html#showinfo) inform source-time bookkeeping.

## Packaging references

- [Agent Skills specification](https://agentskills.io/specification): portable folder and metadata structure.
- [Skills CLI](https://github.com/vercel-labs/skills): optional installation; not bundled.
- [Claude Code plugins](https://code.claude.com/docs/en/plugins/create): optional thin plugin manifest.
- [Model Context Protocol](https://modelcontextprotocol.io/docs/learn/server-concepts): informs possible future executable adapters. No MCP server ships in v0.2.

## Related production work

[ZenStory Drama Skills](https://github.com/zenstory-ai/drama-skills), [Open Film Skills](https://github.com/62656456/ai-film-skills), [ComfyTV](https://github.com/jtydhr88/ComfyTV), and [H3 Continuity Studio](https://github.com/KadoBOT/ComfyUI-H3-Continuity-Studio) are useful adjacent projects, not dependencies or included code. Their full content and licenses remain upstream.

## Examples and evaluation materials

The examples and text cases distributed here are original fictional teaching materials. They are not transcripts of another creator's film, records of real pets or people, or video generation results. Illustrative outputs were authored for the package; they are not represented as independently measured model outputs.

Media integration tests generate simple temporary fixtures in code. Private reference-video reading trials are not distributed as footage or as a public model-accuracy benchmark.
