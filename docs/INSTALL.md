# Installation

The skills need an AI assistant that supports Agent Skills or can read the instruction files. Visual observation needs a host that can actually display images to its model. Listening claims need a host with actual audio access; a transcript or player alone is insufficient. The skills do not install an LLM or video-generation model.

## Skills CLI

The upstream [Skills CLI](https://github.com/vercel-labs/skills) currently requires Node.js 22.20+. Run inside the project where you want the skill:

```bash
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation
```

Select an assistant when prompted. Explicit project installs:

```bash
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation --agent codex
npx skills add SharingYu/video-performance-skills --skill video-creation performance-direction video-observation --agent claude-code
```

On Windows, use `npx.cmd` if your shell blocks the PowerShell shim. Add `--copy` when symlinks are unsuitable. For a global installation, the upstream CLI offers `--global`; project scope is enough for the examples.

Open a new assistant session if the host requires it. Ask it to use `performance-direction`. The CLI is a third-party installer; its update, telemetry and host support policies are maintained upstream.

## Manual installation

1. Download the [versioned release](https://github.com/SharingYu/video-performance-skills/releases/tag/v0.4.0) ZIP, or clone the repository.
2. Copy one or more complete skill folders from `skills/`, including their references, scripts and licenses, to your host's project skill directory.
3. For Codex, the project location is `.agents/skills/<skill-name>/`. For Claude Code, it is `.claude/skills/<skill-name>/`.
4. Start a session in that project and ask it to use the skill. Begin with `$video-creation` in Codex or `/video-creation` in Claude Code standalone mode. Both specialized companions can still be used directly.

Do not copy just `SKILL.md`; it routes to bundled references. No sibling skill or research directory is needed.

The hub's `scripts/project_tool.py` uses only the Python 3.10+ standard library. It records source and artifact state; it does not download links, convert documents, write stories or render films. See [the three-route walkthrough](../examples/three-routes/README.md).

## Python setup for local video observation

Python 3.12+ is required for the observation CLI and its pinned dependencies. Use an isolated environment; the image observation and transcript-import commands need no GPU, speech model weights or API credentials. From a repository clone:

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

## Optional local dialogue transcription

Skip this extra when you only need images or are importing an existing SRT/VTT/WhisperX file. For local ASR, add the separate speech requirements to the observation environment:

```bash
python -m pip install -r skills/video-observation/scripts/requirements-speech.txt
python skills/video-observation/scripts/dialogue_observe.py --help
```

Use that environment's Python executable on Windows or Linux/macOS as shown above. The adapter uses `faster-whisper` 1.2.1 with a **separately prepared local CTranslate2 model directory**. Multilingual `large-v3`, CPU and `int8` are the baseline; English-only `.en` checkpoints and English-oriented distillations are not the Chinese default. The selected [Systran/faster-whisper-large-v3 model](https://huggingface.co/Systran/faster-whisper-large-v3/tree/edaa852ec7e145841d8ffdb056a99866b5f0a478) is MIT-licensed, publicly downloadable without a gated agreement, and approximately 3.1 GB. Pin revision `edaa852ec7e145841d8ffdb056a99866b5f0a478` when preparing it explicitly:

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Systran/faster-whisper-large-v3",
    revision="edaa852ec7e145841d8ffdb056a99866b5f0a478",
    local_dir="models/faster-whisper-large-v3",
)
```

Run this preparation with the observation environment's Python only when the download is intended. The skill does not run it implicitly on first transcription. Keep the model revision and resolved runtime versions with the project evidence. Weights are not included in the package; model loading uses the supplied local directory with no paid/cloud transcription fallback. Other conversions need separate validation; see the [upstream model guidance](https://github.com/SYSTRAN/faster-whisper/tree/v1.2.1#model-conversion).

```bash
python skills/video-observation/scripts/dialogue_observe.py transcribe --video clip.mp4 --model-dir models/faster-whisper-large-v3 --language zh --device cpu --compute-type int8 --output observation/dialogue
python skills/video-observation/scripts/dialogue_observe.py import --video clip.mp4 --file captions.srt --format srt --time-offset 0 --output observation/captions
```

CPU use does not require a new CUDA/PyTorch stack. Optional CUDA inference requires compatible CTranslate2/CUDA libraries and available resources; do not install over an existing video-generation environment. Importing a WhisperX result does not install WhisperX or its gated diarization models. No Hugging Face account or speaker-enrollment setup is required for local model inference or caption import after files have been obtained.

Read [the dialogue workflow](../skills/video-observation/references/dialogue-workflow.md) for source-clock offsets, short-utterance VAD retries, role attribution and listening limits. [The fictional dialogue example](../examples/dialogue/README.md) shows how a line and its reaction become a protected event; it is not a measured transcription run.

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
/video-performance-skills:video-creation
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
