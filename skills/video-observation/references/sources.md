# Sources and Adoption Scope

The workflow and bundled tool are original contributions. The sources below informed the interaction design and technical checks; their code, complete skills, models, or media are not bundled. External links are background, not runtime dependencies.

| Source | Pinned reference | Adopted idea and boundary |
|---|---|---|
| [video-understanding-skill](https://github.com/subh05sus/video-understanding-skill/tree/344c608d78f13d95ee644fbf3093c954cdad5281), subh05sus | `344c608d78f13d95ee644fbf3093c954cdad5281`; MIT | Ask a question, request a useful view, inspect it, and keep an observation record. We do not adopt its Apple-specific analysis, treat low motion as no event, or infer listening from sound statistics. |
| [video-agent](https://github.com/agamm/video-agent/tree/cc00d2815869cbf2d708426a5082612f0c3b4dbf), agamm | `cc00d2815869cbf2d708426a5082612f0c3b4dbf`; MIT | Use a sheet to locate an event, then return to the source frame. Its platform dependencies and average-frame-rate time conversion are not adopted as the timing authority. |
| [Qwen-MM-Plugins core](https://github.com/QwenLM/Qwen-MM-Plugins/tree/33a54695774020e5da2d6b1ed13119d4014f848f), Qwen Team | Core v1.3.0, `33a54695774020e5da2d6b1ed13119d4014f848f`; Apache-2.0 | Return actual image content for the host to inspect, offer metadata and context-linked crops. This skill does not require the plugin or its cloud API module; requested FPS is not proof of delivered coverage. |

Technical references:

- [FFmpeg / ffprobe](https://ffmpeg.org/ffprobe.html): inspect source streams and metadata; [showinfo](https://ffmpeg.org/ffmpeg-filters.html#showinfo) documents frame timestamps.
- [PyAV frames](https://pyav.org/docs/stable/api/frame.html): presentation timestamp and time base distinguish actual presentation time from an assumed frame-rate grid.
- [PySceneDetect detectors](https://www.scenedetect.com/docs/latest/api/detectors.html): candidate cut detection; it does not detect acting intentions, partner reactions, or jokes.

## Dialogue observation sources

The dialogue adapter is original integration around separately installed libraries and local model files. Candidate skill packages were inspected for reusable workflow ideas; none is installed by this skill or copied in full.

| Source | Pinned reference / terms | Adopted scope and limit |
|---|---|---|
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper/tree/65882eee9f5cdbeeb2d877f1131d48cf241b327d), SYSTRAN | v1.2.1, `65882eee9f5cdbeeb2d877f1131d48cf241b327d`; MIT code | Primary optional local ASR, VAD and available word/segment timing. No native role identification; VAD and ASR can miss short replies or hallucinate on non-speech. Models and runtime dependencies retain their own terms. |
| [WhisperX](https://github.com/m-bain/whisperX/tree/3ccc17b8de34f305300f8a3fd3c9f76ba820c0d0) | v3.8.6, `3ccc17b8de34f305300f8a3fd3c9f76ba820c0d0`; BSD-2-Clause code | Import its existing structured output. No WhisperX installer or diarization runtime is included. Its current pyannote Community-1 model is CC-BY-4.0 and gated by separate user conditions; neither model nor token is bundled. Alignment positions supplied words; it does not verify them. |
| [video-analyzer](https://github.com/33Yjh/video-analyzer/tree/22e9f706edbf7caa7baef5386ae2b02d38f40322), 33Yjh | `22e9f706edbf7caa7baef5386ae2b02d38f40322`; MIT | Workflow comparison for speech plus image evidence and reusable results. Its PowerShell extraction, default mirror, installer and coarse-time assumptions are not imported. |
| [faster-whisper-transcriber](https://github.com/macrobert-com/faster-whisper-transcriber/tree/4cf122046f9b92ee77de42b5f16223485d108625), macrobert-com | `4cf122046f9b92ee77de42b5f16223485d108625`; MIT | Comparison of local reusable transcription and stored output. Its English-only default and outputs beside source files are not adopted. |
| [FunASR](https://github.com/modelscope/FunASR/tree/cdd82b5cbfd05015f8fb2b167d61f25142c3a9e8) | v1.4.26, `cdd82b5cbfd05015f8fb2b167d61f25142c3a9e8`; MIT code, checkpoint-specific model terms | Evaluated alternative, not installed or an implemented backend here. Timestamp and speaker support depend on the actual checkpoint and composed pipeline; do not transfer one model's features to every FunASR path. |

The distributed skill has no model weights, gaze estimator, automatic visible-speaker identity system or cloud integration. The optional speech adapter invokes a separately installed ASR library and local model; image observation and transcript import remain model-free. Runtime libraries retain their own licenses. Usable evidence can improve the assistant's decisions; it does not guarantee correct interpretation or measured creative improvement.
