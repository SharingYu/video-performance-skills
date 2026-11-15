#!/usr/bin/env python3
"""Local, CPU-only evidence views for an assistant inspecting a video.

Exports are not observations or approvals. No network, model, API or player is
used. Source frames are decoded in presentation order; source PTS, rather than
average FPS, supplies their time coordinates. JSON is the command interface.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys


class ObserveError(Exception):
    def __init__(self, code: str, message: str):
        self.code, self.message = code, message
        super().__init__(message)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ObserveError("INVALID_ARGUMENT", message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fraction_text(value) -> str | None:
    if value is None:
        return None
    number = Fraction(value)
    return f"{number.numerator}/{number.denominator}"


def dependencies(scene_detection=False):
    try:
        import av
        from PIL import Image, ImageDraw, ImageOps
        if scene_detection:
            from scenedetect import AdaptiveDetector, FrameTimecode
    except ImportError as exc:
        raise ObserveError(
            "DEPENDENCY_MISSING",
            "Install scripts/requirements.txt in a separate Python environment. "
            f"Missing module: {getattr(exc, 'name', 'unknown')}",
        ) from exc
    return av, Image, ImageDraw, ImageOps


def source_path(value: str) -> Path:
    # All inputs are local files. In particular av.open must never see a URL.
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise ObserveError("SOURCE_NOT_FOUND", "The local source file does not exist.")
    return path


def output_directory(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ObserveError("OUTPUT_EXISTS", "Use an empty or new output directory; existing evidence is not overwritten.")
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json_new(path: Path, data: dict):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def save_manifest(output: Path, manifest: dict) -> dict:
    manifest["manifest_path"] = str(output / "manifest.json")
    write_json_new(output / "manifest.json", manifest)
    return manifest


def base_manifest(kind: str, source: dict) -> dict:
    return {
        "ok": True,
        "schema_version": 1,
        "kind": kind,
        "source": source,
        "coverage": {
            "observation_status": "not_observed",
            "selected_count": 0,
            "frames_decoded": 0,
            "warnings": [],
        },
        "frames": [],
        "views": [],
    }


def finite(value: float, label: str) -> float:
    if not math.isfinite(value):
        raise ObserveError("INVALID_ARGUMENT", f"{label} must be finite.")
    return value


def scan(video: Path, *, detect_scenes=False, on_frame=None):
    """One sequential decode; metadata only stays in memory after callbacks."""
    av, _, _, _ = dependencies(detect_scenes)
    before = video.stat()
    source = {"path": str(video), "sha256": sha256(video)}
    timeline, cuts, warnings = [], [], []
    # A local playlist can itself contain remote segment URLs. Restrict the
    # demuxer as well as the CLI input so inspection stays local.
    with av.open(str(video), mode="r", options={"protocol_whitelist": "file"}) as container:
        streams = container.streams.video
        if not streams:
            raise ObserveError("NO_VIDEO_STREAM", "The file has no video stream.")
        stream = streams[0]
        stream.codec_context.thread_count = 2
        rate = stream.average_rate
        source.update({
            "video_stream_index": stream.index,
            "time_base": fraction_text(stream.time_base),
            "dimensions": [stream.codec_context.width, stream.codec_context.height],
            "average_rate": fraction_text(rate),
            "declared_frame_count": stream.frames,
            "declared_start_pts": stream.start_time,
            "audio_streams": [
                {"index": audio.index, "sample_rate": audio.codec_context.sample_rate,
                 "channels": audio.codec_context.channels}
                for audio in container.streams.audio
            ],
        })
        detector = None
        if detect_scenes:
            from scenedetect import AdaptiveDetector, FrameTimecode
            detector = AdaptiveDetector(adaptive_threshold=3.0, min_scene_len=3, min_content_val=15.0)
            # Only a frame-counter carrier for the detector. No time coordinates
            # or exported intervals are derived from this nominal rate.
            detector_rate = float(rate) if rate and rate > 0 else 24.0
        first_time = previous_time = None
        last_duration = None
        for index, frame in enumerate(container.decode(stream)):
            if frame.pts is None or frame.time_base is None:
                raise ObserveError("MISSING_PTS", "A decoded frame has no presentation timestamp; exact source timing is unavailable.")
            time_base = Fraction(frame.time_base)
            source_time = frame.pts * time_base
            if first_time is None:
                first_time = source_time
                source["start_pts"] = frame.pts
                source["first_source_seconds"] = float(source_time)
                source["first_frame_time_base"] = fraction_text(time_base)
                source["rotation"] = int(getattr(frame, "rotation", 0))
            if previous_time is not None and source_time < previous_time:
                raise ObserveError("NONMONOTONIC_PTS", "Presentation timestamps moved backwards; the source needs separate inspection.")
            if previous_time is not None and source_time == previous_time:
                warnings.append(f"duplicate_pts_at_frame_{index}")
            relative = source_time - first_time
            rotation = int(getattr(frame, "rotation", 0))
            record = {
                "id": f"f{index:09d}", "frame_index": index,
                "pts": frame.pts, "time_base": fraction_text(time_base),
                "seconds": float(relative), "source_seconds": float(source_time),
                "rotation_applied": rotation,
            }
            timeline.append(record)
            if on_frame:
                on_frame(frame, record, relative)
            if detector:
                ratio = min(1.0, 480 / max(frame.width, frame.height))
                small = frame.reformat(width=max(1, round(frame.width * ratio)),
                                      height=max(1, round(frame.height * ratio)), format="bgr24")
                timecode = FrameTimecode(index, fps=detector_rate)
                cuts.extend(cut.frame_num for cut in detector.process_frame(timecode, small.to_ndarray()))
            previous_time = source_time
            duration = getattr(frame, "duration", None)
            last_duration = duration * time_base if duration is not None and duration > 0 else None
        if detector and timeline:
            cuts.extend(cut.frame_num for cut in detector.post_process(timecode))
    after = video.stat()
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
        raise ObserveError("SOURCE_CHANGED", "The source file changed during extraction; use a stable source version.")
    if not timeline:
        raise ObserveError("NO_FRAMES", "The video contains no decodable frames.")
    source["decoded_frame_count"] = len(timeline)
    source["last_frame_seconds"] = timeline[-1]["seconds"]
    source["last_source_seconds"] = timeline[-1]["source_seconds"]
    source["duration_seconds"] = float(previous_time + last_duration - first_time) if last_duration else None
    if last_duration is None:
        warnings.append("last_frame_duration_unknown")
    return source, timeline, sorted(set(cuts)), warnings


def export_frame(frame, record: dict, output: Path) -> dict:
    _, Image, _, _ = dependencies()
    directory = output / "frames"
    directory.mkdir(exist_ok=True)
    path = directory / f"{record['id']}.png"
    if path.exists():
        raise ObserveError("OUTPUT_EXISTS", "A frame image already exists; use a new output directory.")
    image = frame.to_image().convert("RGB")
    if record["rotation_applied"]:
        image = image.rotate(record["rotation_applied"], expand=True)
    with path.open("xb") as stream:
        image.save(stream, format="PNG")
    return {**record, "image_path": str(path), "image_sha256": sha256(path),
            "image_dimensions": list(image.size)}


def make_sheets(frames: list[dict], output: Path) -> list[dict]:
    _, Image, ImageDraw, ImageOps = dependencies()
    views = []
    for offset in range(0, len(frames), 6):
        block = frames[offset:offset + 6]
        thumbs = []
        for item in block:
            with Image.open(item["image_path"]) as image:
                # Never enlarge the source and never stretch its aspect ratio.
                thumbs.append(ImageOps.contain(image.convert("RGB"),
                              (min(640, image.width), min(640, image.height))))
        tile_width = max(image.width for image in thumbs) + 16
        tile_height = max(image.height for image in thumbs) + 44
        columns = min(2, len(block))
        rows = (len(block) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * tile_width, rows * tile_height), "#171717")
        draw = ImageDraw.Draw(sheet)
        for index, (item, image) in enumerate(zip(block, thumbs)):
            x, y = index % columns * tile_width, index // columns * tile_height
            draw.text((x + 8, y + 4), f"{item['id']}  t={item['seconds']:.6f}s", fill="white")
            draw.text((x + 8, y + 18), f"PTS={item['pts']}  tb={item['time_base']}", fill="#bbbbbb")
            sheet.paste(image, (x + (tile_width - image.width) // 2, y + 38))
        view_id = f"sheet{len(views) + 1:04d}"
        path = output / f"{view_id}.png"
        with path.open("xb") as stream:
            sheet.save(stream, format="PNG")
        views.append({"id": view_id, "kind": "sheet", "image_path": str(path),
                      "image_sha256": sha256(path), "frame_ids": [item["id"] for item in block],
                      "image_dimensions": list(sheet.size)})
    return views


def inspect_command(args):
    source, timeline, _, warnings = scan(source_path(args.video))
    result = base_manifest("inspect", source)
    result["coverage"].update({"frames_decoded": len(timeline), "warnings": warnings})
    if args.output:
        path = Path(args.output).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise ObserveError("OUTPUT_EXISTS", "Metadata output already exists.")
        write_json_new(path, result)
    return result


def overview_command(args):
    video = source_path(args.video)
    output = output_directory(args.output)
    source, timeline, cuts, warnings = scan(video, detect_scenes=True)
    boundaries = [0] + [cut for cut in cuts if 0 < cut < len(timeline)] + [len(timeline)]
    shots, selected = [], set()
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:])):
        chosen = sorted({start, (start + end - 1) // 2, end - 1})
        selected.update(chosen)
        shots.append({
            "id": f"shot{index + 1:04d}", "start_frame": start, "end_frame": end,
            "start_seconds": timeline[start]["seconds"],
            "end_seconds": timeline[end]["seconds"] if end < len(timeline) else source["duration_seconds"],
            "selected_frame_ids": [timeline[number]["id"] for number in chosen],
        })
    exported = []

    def collect(frame, record, _):
        if record["frame_index"] in selected:
            exported.append(export_frame(frame, record, output))

    second_source, second_timeline, _, second_warnings = scan(video, on_frame=collect)
    if source["sha256"] != second_source["sha256"] or timeline != second_timeline:
        raise ObserveError("SOURCE_CHANGED", "The source changed between detection and frame export.")
    result = base_manifest("overview", source)
    result["shots"] = shots
    result["detector"] = {"name": "PySceneDetect AdaptiveDetector", "adaptive_threshold": 3.0,
                          "min_scene_len_frames": 3, "min_content_val": 15.0,
                          "role": "candidate_cuts_not_action_detection"}
    result["coverage"].update({
        "requested": {"per_shot": "first_middle_last"}, "selected_count": len(exported),
        "frames_decoded": len(timeline), "decode_passes": 2,
        "warnings": sorted(set(warnings + second_warnings + ["candidate_cuts_require_review", "unsampled_intervals_not_observed"])),
    })
    result["frames"] = exported
    result["views"] = make_sheets(exported, output)
    return save_manifest(output, result)


def window_command(args):
    start, end, fps = finite(args.start, "start"), finite(args.end, "end"), finite(args.fps, "fps")
    if start < 0 or end <= start or fps < 0:
        raise ObserveError("INVALID_ARGUMENT", "Use 0 <= start < end and fps >= 0; fps=0 selects every source frame.")
    start_time, end_time = Fraction(str(start)), Fraction(str(end))
    interval = Fraction(1) / Fraction(str(fps)) if fps else None
    next_time = start_time
    video = source_path(args.video)
    output = output_directory(args.output)
    exported = []

    def collect(frame, record, relative):
        nonlocal next_time
        if start_time <= relative < end_time and (interval is None or relative >= next_time):
            exported.append(export_frame(frame, record, output))
            if interval is not None:
                # Advance beyond this timestamp, including gaps in VFR sources.
                next_time += ((relative - next_time) // interval + 1) * interval

    source, timeline, _, warnings = scan(video, on_frame=collect)
    if not exported:
        raise ObserveError("EMPTY_SELECTION", "No actual source frames fall in the requested half-open interval.")
    if source["duration_seconds"] is not None and end > source["duration_seconds"]:
        warnings.append("requested_end_extends_beyond_source")
    result = base_manifest("window", source)
    result["coverage"].update({
        "requested": {"start_seconds": start, "end_seconds": end, "fps": fps,
                      "interval": "[start,end)", "time_origin": "first_presented_frame"},
        "selected_count": len(exported), "frames_decoded": len(timeline),
        "selected_first_seconds": exported[0]["seconds"],
        "selected_last_seconds": exported[-1]["seconds"],
        "warnings": warnings + (["unsampled_intervals_not_observed"] if fps else []),
    })
    result["frames"] = exported
    result["views"] = make_sheets(exported, output)
    return save_manifest(output, result)


def read_manifest(value: str):
    path = source_path(value)
    with path.open("r", encoding="utf-8") as stream:
        result = json.load(stream)
    if (not isinstance(result, dict) or result.get("schema_version") != 1
            or not isinstance(result.get("source"), dict)
            or not isinstance(result.get("frames"), list) or not isinstance(result.get("views"), list)):
        raise ObserveError("INVALID_MANIFEST", "Expected a schema_version=1 video-observation manifest.")
    return path, result


def verified_image(item: dict, manifest_path: Path) -> Path:
    try:
        path = Path(item["image_path"]).expanduser()
        if not path.is_absolute():
            path = manifest_path.parent / path
        path = path.resolve()
        expected = item["image_sha256"]
    except (KeyError, TypeError) as exc:
        raise ObserveError("INVALID_MANIFEST", "Image references need a path and SHA-256.") from exc
    if not path.is_file() or not isinstance(expected, str) or sha256(path) != expected:
        raise ObserveError("IMAGE_HASH_MISMATCH", "An evidence image is missing or differs from its recorded SHA-256.")
    return path


def crop_command(args):
    manifest_path, original = read_manifest(args.manifest)
    matches = [frame for frame in original["frames"] if frame.get("id") == args.frame_id]
    if len(matches) != 1:
        raise ObserveError("UNKNOWN_FRAME", "The frame ID must identify one original frame in the manifest.")
    frame = matches[0]
    context_path = verified_image(frame, manifest_path)
    try:
        box = [float(value.strip()) for value in args.box.split(",")]
    except ValueError as exc:
        raise ObserveError("INVALID_ARGUMENT", "box must contain x0,y0,x1,y1 in normalized 0-1000 coordinates.") from exc
    if (len(box) != 4 or not all(math.isfinite(value) for value in box)
            or not 0 <= box[0] < box[2] <= 1000 or not 0 <= box[1] < box[3] <= 1000):
        raise ObserveError("INVALID_ARGUMENT", "Use 0 <= x0 < x1 <= 1000 and 0 <= y0 < y1 <= 1000.")
    _, Image, _, _ = dependencies()
    with Image.open(context_path) as image:
        width, height = image.size
        pixels = [math.floor(box[0] * width / 1000), math.floor(box[1] * height / 1000),
                  math.ceil(box[2] * width / 1000), math.ceil(box[3] * height / 1000)]
        crop = image.crop(pixels)
    output = output_directory(args.output)
    path = output / "crop0001.png"
    with path.open("xb") as stream:
        crop.save(stream, format="PNG")
    result = base_manifest("crop", original["source"])
    result["frames"] = [frame]
    result["parent_manifest"] = str(manifest_path)
    result["parent_manifest_sha256"] = sha256(manifest_path)
    result["coverage"].update({"requested": {"frame_id": args.frame_id, "box_normalized": box},
                                  "selected_count": 1,
                                  "warnings": ["crop_omits_surrounding_context", "no_generated_detail_or_inferred_gaze"]})
    result["views"] = [{"id": "crop0001", "kind": "crop", "image_path": str(path),
                        "image_sha256": sha256(path), "image_dimensions": list(crop.size),
                        "frame_ids": [frame["id"]], "box_normalized": box, "box_pixels": pixels,
                        "context_image_path": str(context_path), "context_image_sha256": frame["image_sha256"]}]
    return save_manifest(output, result)


def note_command(args):
    manifest_path, manifest = read_manifest(args.manifest)
    ids = list(dict.fromkeys(value.strip() for group in args.view_ids for value in group.split(",") if value.strip()))
    if not ids or not args.observer.strip() or not args.method.strip() or not args.text.strip():
        raise ObserveError("INVALID_ARGUMENT", "A note needs view IDs, observer, method and nonempty text.")
    available = {item["id"]: item for item in manifest["frames"] + manifest["views"]}
    if any(view_id not in available for view_id in ids):
        raise ObserveError("UNKNOWN_VIEW", "Every asserted view ID must exist in this manifest.")
    seen = []
    for view_id in ids:
        item = available[view_id]
        path = verified_image(item, manifest_path)
        seen.append({"id": view_id, "image_path": str(path), "image_sha256": item["image_sha256"],
                     "frame_ids": item.get("frame_ids", [view_id])})
    result = {
        "ok": True, "schema_version": 1, "kind": "note",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": manifest["source"].get("sha256"),
        "manifest_path": str(manifest_path), "manifest_sha256": sha256(manifest_path),
        "observer": args.observer, "method": args.method,
        "view_ids": ids, "asserted_view_ids": ids, "view_evidence": seen,
        "observation_status": "self_reported", "observer_attested": True,
        "claim_kind": args.kind, "event_id": args.event_id,
        "text": args.text,
        "boundary": "Observer attestation only; exporting, logging or agreeing does not prove perception or content approval.",
        "not_asserted_in_this_note_view_ids": [item["id"] for item in manifest["views"] if item["id"] not in ids],
    }
    journal = manifest_path.parent / "observations.jsonl"
    result["journal_path"] = str(journal)
    with journal.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n")
    return result


def parser():
    root = Parser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True, parser_class=Parser)
    inspect = commands.add_parser("inspect", help="Inspect a local video and its actual PTS timeline.")
    inspect.add_argument("--video", required=True)
    inspect.add_argument("--output", help="Optional new JSON metadata file.")
    inspect.set_defaults(handler=inspect_command)
    overview = commands.add_parser("overview", help="Candidate cuts and per-shot first/middle/last frames.")
    overview.add_argument("--video", required=True)
    overview.add_argument("--output", required=True)
    overview.set_defaults(handler=overview_command)
    window = commands.add_parser("window", help="Sample an actual source interval [start,end).")
    window.add_argument("--video", required=True)
    window.add_argument("--start", required=True, type=float)
    window.add_argument("--end", required=True, type=float)
    window.add_argument("--fps", type=float, default=4, help="Sampling frequency; 0 means every source frame.")
    window.add_argument("--output", required=True)
    window.set_defaults(handler=window_command)
    crop = commands.add_parser("crop", help="Crop a verified original frame; keep its full context reference.")
    crop.add_argument("--manifest", required=True)
    crop.add_argument("--frame-id", required=True)
    crop.add_argument("--box", required=True, help="x0,y0,x1,y1 in 0-1000 coordinates.")
    crop.add_argument("--output", required=True)
    crop.set_defaults(handler=crop_command)
    note = commands.add_parser("note", help="Append an observer-attested observation, interpretation or question.")
    note.add_argument("--manifest", required=True)
    note.add_argument("--view-ids", required=True, nargs="+", help="Space- or comma-separated frame/view IDs actually inspected.")
    note.add_argument("--observer", required=True)
    note.add_argument("--method", required=True)
    note.add_argument("--text", required=True)
    note.add_argument("--event-id")
    note.add_argument("--kind", choices=("observation", "interpretation", "question"), default="observation")
    note.set_defaults(handler=note_command)
    return root


def main(argv=None) -> int:
    try:
        args = parser().parse_args(argv)
        result = args.handler(args)
    except ObserveError as exc:
        print(json.dumps({"ok": False, "error": {"code": exc.code, "message": exc.message}}, ensure_ascii=False))
        return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": {"code": "READ_ERROR", "message": str(exc)}}, ensure_ascii=False))
        return 2
    except Exception as exc:
        # Decoder errors must still respect the JSON protocol. Do not dump a
        # traceback or any surrounding configuration/credentials to stdout.
        print(json.dumps({"ok": False, "error": {"code": "PROCESSING_ERROR", "message": str(exc)}}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
