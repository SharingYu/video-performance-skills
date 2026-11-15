# Installation

The skills need an AI assistant that supports Agent Skills or can read the instruction files. Video observation also needs a host that can actually display images to its model. Neither skill installs an LLM or video-generation model.

## Skills CLI

The upstream [Skills CLI](https://github.com/vercel-labs/skills) currently requires Node.js 22.20+. Run inside the project where you want the skill:

```bash
npx skills add SharingYu/video-performance-skills --skill performance-direction video-observation
```

Select an assistant when prompted. Explicit project installs:

```bash
npx skills add SharingYu/video-performance-skills --skill performance-direction video-observation --agent codex
npx skills add SharingYu/video-performance-skills --skill performance-direction video-observation --agent claude-code
```

On Windows, use `npx.cmd` if your shell blocks the PowerShell shim. Add `--copy` when symlinks are unsuitable. For a global installation, the upstream CLI offers `--global`; project scope is enough for the examples.

Open a new assistant session if the host requires it. Ask it to use `performance-direction`. The CLI is a third-party installer; its update, telemetry and host support policies are maintained upstream.

## Manual installation

1. Download the [versioned release](https://github.com/SharingYu/video-performance-skills/releases/tag/v0.2.0) ZIP, or clone the repository.
2. Copy either or both complete skill folders from `skills/`, including their references, scripts and licenses, to your host's project skill directory.
3. For Codex, the project location is `.agents/skills/<skill-name>/`. For Claude Code, it is `.claude/skills/<skill-name>/`.
4. Start a session in that project and ask it to use the skill. In Codex, explicit invocation is `$video-observation` or `$performance-direction`; Claude Code standalone mode uses `/video-observation` or `/performance-direction`.

Do not copy just `SKILL.md`; it routes to bundled references. No sibling skill or research directory is needed.

## Python setup for local video observation

Python 3.12+ is required for the observation CLI and its pinned dependencies. Use an isolated environment; no GPU, model weights or API credentials are needed. From a repository clone:

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\python.exe -m pip install -r skills/video-observation/scripts/requirements.txt
.venv\Scripts\python.exe skills/video-observation/scripts/video_observe.py --help
```

On Linux/macOS:

```bash
.venv/bin/python -m pip install -r skills/video-observation/scripts/requirements.txt
.venv/bin/python skills/video-observation/scripts/video_observe.py --help
```

If installed through Skills CLI, use that installed skill's `scripts/requirements.txt` and `scripts/video_observe.py` paths instead. The script uses PyAV's bundled FFmpeg libraries; a separate FFmpeg executable is not needed for these commands. Its dependencies retain their respective licenses. [Observation example](../examples/observation/README.md).

For a host without Skills support, ask it to read `skills/performance-direction/SKILL.md` and the applicable reference files from a clone. This is a manual fallback, not a claim of tested integration with every assistant.

## Optional Claude Code plugin wrapper

The repository also has a thin [Claude Code plugin manifest](https://code.claude.com/docs/en/plugins/create). It packages the same skills with a namespace; it adds no hooks or MCP server. Python setup above is still needed for the CLI.

```bash
git clone https://github.com/SharingYu/video-performance-skills.git
claude --plugin-dir ./video-performance-skills
```

In that session:

```text
/video-performance-skills:performance-direction
/video-performance-skills:video-observation
```

Use either the standalone install or plugin mode for a given session to avoid duplicate discovery. No marketplace acceptance or public directory listing is implied.

## First task

Use the [fictional reference input](../examples/reference/input.md), then ask:

```text
Use performance-direction. Read this observation log and build a performance
event card. Keep observed facts separate from interpretation. A different
setting is allowed. Do not generate media.
```

The [illustrative output](../examples/reference/output.md) helps you compare decisions. It is not a fixed response your assistant must reproduce.
