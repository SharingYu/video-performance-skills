# Installation

The skill needs an AI assistant that supports Agent Skills or can read the instruction files. It does not install an LLM, video model, or media service. Output quality and accessible media types depend on that assistant.

## Skills CLI

The upstream [Skills CLI](https://github.com/vercel-labs/skills) currently requires Node.js 22.20+. Run inside the project where you want the skill:

```bash
npx skills add SharingYu/video-performance-skills --skill performance-direction
```

Select an assistant when prompted. Explicit project installs:

```bash
npx skills add SharingYu/video-performance-skills --skill performance-direction --agent codex
npx skills add SharingYu/video-performance-skills --skill performance-direction --agent claude-code
```

On Windows, use `npx.cmd` if your shell blocks the PowerShell shim. Add `--copy` when symlinks are unsuitable. For a global installation, the upstream CLI offers `--global`; project scope is enough for the examples.

Open a new assistant session if the host requires it. Ask it to use `performance-direction`. The CLI is a third-party installer; its update, telemetry and host support policies are maintained upstream.

## Manual installation

1. Download the [versioned release](https://github.com/SharingYu/video-performance-skills/releases/tag/v0.1.0) ZIP, or clone the repository.
2. Copy the complete `skills/performance-direction/` folder, including `references/` and `agents/`, to your host's project skill directory.
3. For Codex, the project location is `.agents/skills/performance-direction/`. For Claude Code, it is `.claude/skills/performance-direction/`.
4. Start a session in that project and ask it to use the skill. In Codex, explicit invocation is `$performance-direction`; in Claude Code standalone mode, `/performance-direction`.

Do not copy just `SKILL.md`; it routes to bundled references. No sibling skill or research directory is needed.

For a host without Skills support, ask it to read `skills/performance-direction/SKILL.md` and the applicable reference files from a clone. This is a manual fallback, not a claim of tested integration with every assistant.

## Optional Claude Code plugin wrapper

The repository also has a thin [Claude Code plugin manifest](https://code.claude.com/docs/en/plugins/create). It packages the same skill with a namespace; it adds no hooks, MCP server, or extra powers.

```bash
git clone https://github.com/SharingYu/video-performance-skills.git
claude --plugin-dir ./video-performance-skills
```

In that session:

```text
/video-performance-skills:performance-direction
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
