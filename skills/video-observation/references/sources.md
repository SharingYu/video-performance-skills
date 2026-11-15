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

The distributed skill has no model weights, gaze estimator, audio-understanding engine, or cloud integration. Runtime libraries retain their own licenses. A usable view can improve the evidence available to an assistant; it does not guarantee a correct interpretation or measured creative improvement.
