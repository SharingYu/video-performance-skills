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

## Three-route integration — v0.3

The `video-creation` entry and standard-library project tool are original contributions. Method selection draws on [ZenStory Drama Skills at 3d813c30871b4db5f2387d83bdc3a49db8ce7b2b](https://github.com/zenstory-ai/drama-skills/tree/3d813c30871b4db5f2387d83bdc3a49db8ce7b2b) and [8cf7404981b7095b498e061832bb3c9ffd6a42be](https://github.com/zenstory-ai/drama-skills/tree/8cf7404981b7095b498e061832bb3c9ffd6a42be), including the dedicated novel-analysis method. Selected opening, payoff and continuity questions also draw on [Short-Drama Factory at 33d9988f5b9d83963cf1010b49f321fc09ea5a22](https://github.com/lixiaoxiao9888-create/short-drama-factory/tree/33d9988f5b9d83963cf1010b49f321fc09ea5a22) and [short-drama at 8979a428c31a865421d661bdb606e24314b683a0](https://github.com/0xsline/short-drama/tree/8979a428c31a865421d661bdb606e24314b683a0). These selected sources declare MIT; their complete skill collections and scripts are not redistributed here.

Premise, character strategy and scene questions also reference [screenwriting-skills at 51115f18d160aa8b2ac5813e4432b6f0b425358f](https://github.com/jtydhr88/screenwriting-skills/tree/51115f18d160aa8b2ac5813e4432b6f0b425358f). Its MIT scope covers original organization and analysis; third-party books, scripts and translations are excluded by its NOTICE and are not included here. More detail is bundled with [the hub's sources](../skills/video-creation/references/sources.md).

The three-chapter prose exercise is newly authored fictional teaching text. It is not a published novel, an actual production case or a licensed third-party IP. No platform rule or commercial-success claim from a method repository is adopted as verified fact.

## Dialogue observation

The source-clock dialogue wrapper, transcript/context records and dialogue/reaction instructions are original package work. Primary runtime reference: [SYSTRAN faster-whisper v1.2.1](https://github.com/SYSTRAN/faster-whisper/tree/65882eee9f5cdbeeb2d877f1131d48cf241b327d), commit `65882eee9f5cdbeeb2d877f1131d48cf241b327d` (MIT). It is an optional dependency installed separately, not vendored; models are obtained separately and retain their applicable terms.

The import interface reads existing [WhisperX v3.8.6](https://github.com/m-bain/whisperX/tree/3ccc17b8de34f305300f8a3fd3c9f76ba820c0d0) output, commit `3ccc17b8de34f305300f8a3fd3c9f76ba820c0d0` (BSD-2-Clause code). It does not bundle WhisperX or pyannote. [pyannote Community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) is CC-BY-4.0 with separate gated access conditions; those conditions are not inherited as a dependency of this package's transcript importer.

Workflow comparisons include [33Yjh/video-analyzer at 22e9f706edbf7caa7baef5386ae2b02d38f40322](https://github.com/33Yjh/video-analyzer/tree/22e9f706edbf7caa7baef5386ae2b02d38f40322) and [macrobert-com/faster-whisper-transcriber at 4cf122046f9b92ee77de42b5f16223485d108625](https://github.com/macrobert-com/faster-whisper-transcriber/tree/4cf122046f9b92ee77de42b5f16223485d108625), both MIT. Their scripts, installers, default models and private assumptions are not redistributed. [FunASR v1.4.26](https://github.com/modelscope/FunASR/tree/cdd82b5cbfd05015f8fb2b167d61f25142c3a9e8) was evaluated as an alternative; its MIT software license does not give one license to all its model weights, and it is not an implemented backend here. See [the observation sources](../skills/video-observation/references/sources.md) for selection and adoption limits.

The dialogue example is newly authored fictional text with proposed staging. It is not another creator's transcript or evidence of an ASR/listening run.

## Packaging specifications

- [Agent Skills specification](https://agentskills.io/specification): portable folder and metadata structure.
- [Skills CLI](https://github.com/vercel-labs/skills): optional installation; not bundled.
- [Claude Code plugins](https://code.claude.com/docs/en/plugins/create): optional thin plugin manifest.
- [Model Context Protocol](https://modelcontextprotocol.io/docs/learn/server-concepts): informs possible future executable adapters. No MCP server ships in v0.4.

## Related production work

[ZenStory Drama Skills](https://github.com/zenstory-ai/drama-skills), [Open Film Skills](https://github.com/62656456/ai-film-skills), [ComfyTV](https://github.com/jtydhr88/ComfyTV), and [H3 Continuity Studio](https://github.com/KadoBOT/ComfyUI-H3-Continuity-Studio) are useful adjacent projects, not dependencies or included code. Their full content and licenses remain upstream.

## Examples and evaluation materials

The examples and text cases distributed here are original fictional teaching materials. They are not transcripts of another creator's film, records of real pets or people, or video generation results. Illustrative outputs were authored for the package; they are not represented as independently measured model outputs.

Media integration tests generate simple temporary fixtures in code. Private reference-video reading trials are not distributed as footage or as a public model-accuracy benchmark.

The private v0.4 dialogue trial used the Sintel trailer: © Blender Foundation | durian.blender.org, [CC-BY-3.0 sharing terms](https://durian.blender.org/sharing/), obtained from a W3C public media mirror. The film, extracted frames, audio and private observation files are not part of this package.
