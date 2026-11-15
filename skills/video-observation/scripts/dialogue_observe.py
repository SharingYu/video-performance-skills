#!/usr/bin/env python3
"""Local candidate dialogue evidence on the video-observation source clock.

ASR candidates, captions, anonymous audio speakers and visible character roles
are different evidence. This tool never claims listening, role recognition,
understanding or media approval. Models must already exist locally.
"""
from __future__ import annotations

import argparse
from array import array
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import wave

import video_observe as visual

VERSION = "0.4.0"
RATE = 16000
ObserveError = visual.ObserveError


def number(value, label="time"):
    if isinstance(value, bool):
        raise ObserveError("INVALID_TIMING", f"{label} must be a finite number.")
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ObserveError("INVALID_TIMING", f"{label} must be a finite number.") from exc
    if not math.isfinite(value):
        raise ObserveError("INVALID_TIMING", f"{label} must be a finite number.")
    return value


def unchanged(path, digest):
    if not path.is_file() or visual.sha256(path) != digest:
        raise ObserveError("SOURCE_CHANGED", "The source changed; old timing/evidence cannot be reused.")


def new_output(value, command):
    output = visual.output_directory(value)
    try:
        visual.write_json_new(output / "run-receipt.json", {
            "tool_version": VERSION, "command": command,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "started_not_media_approved",
        })
    except FileExistsError as exc:
        raise ObserveError("OUTPUT_EXISTS", "This output directory is already claimed; choose a new directory.") from exc
    return output


def source_scan(video):
    source, frames, _, warnings = visual.scan(video)
    end = source.get("duration_seconds")
    if end is None:
        # A nominal frame rate is not a trustworthy duration for VFR inputs.
        end = source["last_frame_seconds"]
        warnings.append("video_end_conservative_last_pts_last_frame_extent_unknown")
    if not end or end <= 0:
        raise ObserveError("UNKNOWN_VIDEO_DURATION", "A positive source presentation interval could not be established.")
    return source, float(end), warnings


def selection(start, end, duration):
    start = number(start, "start") if start is not None else 0.0
    end = number(end, "end") if end is not None else duration
    if start < 0 or end <= start or start >= duration:
        raise ObserveError("INVALID_ARGUMENT", "Use a video-relative interval 0 <= start < end within the source.")
    return start, min(end, duration)


def base(source, start, end, evidence_kind):
    return {
        "ok": True, "schema_version": 1, "tool_version": VERSION, "kind": "dialogue",
        "created_at": datetime.now(timezone.utc).isoformat(), "status": "not_run",
        "source": source, "evidence_kind": evidence_kind,
        "clock": {"time_origin": "first_presented_frame",
                  "video_origin_seconds": source["first_source_seconds"],
                  "audio_first_source_seconds": None, "audio_offset_seconds": None,
                  "range_start_seconds": start, "range_end_seconds": end},
        "audio": None, "asr": None, "segments": [], "warnings": [],
        "coverage": {"observation_status": "not_observed", "listening_status": "not_listened",
                     "dialogue_verification": "unverified", "speaker_verification": "unverified"},
        "boundary": "Candidates/captions only. Exporting does not prove what was heard, who spoke, or whether a recreation is correct.",
    }


def timestamp(seconds):
    value = max(0, round(seconds * 1000))
    hours, value = divmod(value, 3600000)
    minutes, value = divmod(value, 60000)
    sec, milliseconds = divmod(value, 1000)
    return f"{hours:02}:{minutes:02}:{sec:02},{milliseconds:03}"


def save(output, result):
    result["manifest_path"] = str(output / "manifest.json")
    result["transcript_path"] = str(output / "transcript.md")
    result["srt_path"] = str(output / "candidate.srt")
    with (output / "transcript.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(f"# Candidate dialogue\n\nStatus: {result['status']}\n\n")
        stream.write(f"Evidence: {result['evidence_kind']}. All times use the first presented video frame as zero.\n\n")
        stream.write("ASR and subtitle text are unverified; role attribution and actual listening are pending.\n\n")
        for item in result["segments"]:
            stream.write(f"- {item['id']} [{item['start']:.3f}, {item['end']:.3f}) "
                         f"speaker={item['audio_speaker_id'] or 'unknown'}; character=unknown\n")
            # Indent source content so Markdown in source material stays quoted material.
            stream.write("\n" + "\n".join("    " + line for line in item["text"].splitlines()) + "\n\n")
        if result["warnings"]:
            stream.write("Warnings:\n\n" + "\n".join(f"- {x}" for x in result["warnings"]) + "\n")
    with (output / "candidate.srt").open("x", encoding="utf-8", newline="\n") as stream:
        for index, item in enumerate(result["segments"], 1):
            stream.write(f"{index}\n{timestamp(item['start'])} --> {timestamp(item['end'])}\n{item['text']}\n\n")
    # A valid manifest is the completion marker. Interrupted/failed report
    # writes leave only partial evidence and a started run receipt.
    visual.write_json_new(output / "manifest.json", result)
    return result


def extract_audio(video, source, output, start, end, stream_index=None):
    """Decode to a PCM clock starting at video-relative start, padding gaps.

    A new resampler is used for each timestamp-contiguous run. Its emitted
    sample count is anchored to that run's actual first PTS. Decoder timestamps
    are checked before clearing them for resampling; silence is inserted, never
    removed, between discontinuous runs. Subsample PTS rounding is tolerated.
    """
    av, _, _, _ = visual.dependencies()
    path = output / "audio.wav"
    count = math.ceil((Fraction(str(end)) - Fraction(str(start))) * RATE)
    if count <= 0:
        raise ObserveError("INVALID_ARGUMENT", "The selected audio interval has no samples.")
    video_origin = source["start_pts"] * Fraction(source["first_frame_time_base"])
    range_start = Fraction(str(start))
    info = {"path": str(path), "sample_rate": RATE, "channels": 1,
            "format": "pcm_s16le", "range_start_seconds": start,
            "range_end_seconds": end, "gaps": [], "warnings": [],
            "decoded_frames": 0, "samples": count}
    with av.open(str(video), mode="r", options={"protocol_whitelist": "file"}) as container:
        streams = list(container.streams.audio)
        if stream_index is not None:
            streams = [item for item in streams if item.index == stream_index]
            if not streams:
                raise ObserveError("UNKNOWN_AUDIO_STREAM", "audio-stream must be an actual absolute audio stream index.")
        if not streams:
            return None
        stream = streams[0]
        stream.codec_context.thread_count = 2
        info["stream_index"] = stream.index
        info["stream_selection"] = "explicit" if stream_index is not None else "first_audio_stream"
        if stream_index is None and len(streams) > 1:
            info["warnings"].append("multiple_audio_streams_first_selected_not_mixed")
        first_pts = previous_start = previous_end = run_start = None
        emitted = 0
        position = 0
        resampler = None
        with path.open("xb") as raw_output, wave.open(raw_output, "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(RATE)

            def zeroes(samples):
                nonlocal position
                while samples > 0:
                    block = min(samples, RATE)
                    writer.writeframesraw(b"\0\0" * block)
                    samples -= block
                    position += block

            def append(frame):
                nonlocal emitted, position
                absolute = run_start + Fraction(emitted, RATE)
                emitted += frame.samples
                target = round((absolute - video_origin - range_start) * RATE)
                data = bytes(frame.planes[0])[:frame.samples * 2]
                if sys.byteorder != "little":
                    values = array("h")
                    values.frombytes(data)
                    values.byteswap()
                    data = values.tobytes()
                if target < 0:
                    trim = min(-target, len(data) // 2)
                    data = data[trim * 2:]
                    target += trim
                if not data or target >= count:
                    return
                if target < position:
                    overlap = position - target
                    if overlap > 1:
                        raise ObserveError("UNRESOLVABLE_AUDIO_CLOCK", "Decoded/resampled audio overlaps on the source clock.")
                    data = data[overlap * 2:]
                    target += overlap
                if target > position:
                    zeroes(min(target, count) - position)
                data = data[:max(0, count - position) * 2]
                writer.writeframesraw(data)
                position += len(data) // 2

            for frame in container.decode(stream):
                if not frame.samples:
                    continue
                if frame.pts is None or frame.time_base is None or not frame.sample_rate:
                    raise ObserveError("MISSING_AUDIO_PTS", "Audio frames need PTS, time base and sample rate for exact source timing.")
                pts = frame.pts * Fraction(frame.time_base)
                tolerance = max(Fraction(1, frame.sample_rate), Fraction(frame.time_base))
                if previous_start is not None and pts <= previous_start:
                    raise ObserveError("NONMONOTONIC_AUDIO_PTS", "Audio presentation timestamps did not advance.")
                gap = pts - previous_end if previous_end is not None else None
                if gap is not None and gap < -tolerance:
                    raise ObserveError("UNRESOLVABLE_AUDIO_CLOCK", "Audio frames overlap; a single reliable speech clock cannot be assigned.")
                if first_pts is None:
                    first_pts = pts
                if resampler is None or (gap is not None and gap > tolerance):
                    if resampler is not None:
                        for item in resampler.resample(None):
                            append(item)
                        gap_start = max(start, float(previous_end - video_origin))
                        gap_end = min(end, float(pts - video_origin))
                        if gap_end > gap_start:
                            info["gaps"].append({"start": gap_start, "end": gap_end, "kind": "timestamp_gap_padded_with_silence"})
                    run_start, emitted = pts, 0
                    resampler = av.AudioResampler(format="s16", layout="mono", rate=RATE)
                elif gap:
                    info["warnings"].append("subsample_audio_timestamp_rounding_tolerated")
                previous_start = pts
                previous_end = pts + Fraction(frame.samples, frame.sample_rate)
                info["decoded_frames"] += 1
                # The checked original PTS above is authoritative. The resampler
                # gets one contiguous run, not a silently re-clocked whole file.
                frame.pts = None
                for item in resampler.resample(frame):
                    append(item)
            if resampler is not None:
                for item in resampler.resample(None):
                    append(item)
            if first_pts is None:
                raise ObserveError("EMPTY_AUDIO_STREAM", "An audio stream exists but no timestamped samples decoded.")
            if position < count:
                zeroes(count - position)
    info["first_source_seconds"] = float(first_pts)
    info["offset_seconds"] = float(first_pts - video_origin)
    leading_end = min(end, float(first_pts - video_origin))
    if leading_end > start:
        info["gaps"].insert(0, {"start": start, "end": leading_end,
                                "kind": "leading_audio_absence_padded_with_silence"})
    trailing_start = max(start, float(previous_end - video_origin))
    if trailing_start < end:
        info["gaps"].append({"start": trailing_start, "end": end,
                             "kind": "trailing_audio_absence_padded_with_silence"})
    info["sha256"] = visual.sha256(path)
    info["warnings"] = sorted(set(info["warnings"]))
    unchanged(video, source["sha256"])
    return info


def primitive(value):
    if is_dataclass(value):
        return primitive(asdict(value))
    if hasattr(value, "_asdict"):
        return primitive(value._asdict())
    if isinstance(value, dict):
        return {str(k): primitive(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [primitive(item) for item in value]
    if isinstance(value, (str, bool, int)) or value is None:
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "__dict__"):
        return primitive({key: item for key, item in vars(value).items() if not key.startswith("_")})
    return str(value)


def model_record(directory):
    directory = Path(directory).expanduser().resolve()
    if not directory.is_dir() or not (directory / "model.bin").is_file():
        raise ObserveError("MODEL_NOT_LOCAL", "model-dir must contain an existing local CTranslate2 model.bin; no model download is attempted.")
    files, excluded = [], []
    for folder, directories, names in os.walk(directory):
        hidden = [name for name in directories if name.startswith(".")]
        excluded.extend((Path(folder) / name).relative_to(directory).as_posix() + "/" for name in hidden)
        directories[:] = sorted(name for name in directories if not name.startswith("."))
        for name in sorted(names):
            path = Path(folder) / name
            if name.startswith("."):
                excluded.append(path.relative_to(directory).as_posix())
                continue
            if path.is_file():
                files.append({"path": path.relative_to(directory).as_posix(),
                              "size": path.stat().st_size, "sha256": visual.sha256(path)})
    files.sort(key=lambda item: item["path"])
    fingerprint = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"path": str(directory), "fingerprint_sha256": fingerprint, "files": files,
            "fingerprint_scope": "non_hidden_deployed_model_files",
            "excluded_path_parts": [".cache", "any path component starting with '.'"],
            "excluded_paths": sorted(excluded),
            "revision": None, "revision_note": "No revision inferred from a directory name; content fingerprint is authoritative."}


def segment_record(raw, index, offset, lower, upper, speaker=None):
    if not isinstance(raw, dict) or not isinstance(raw.get("text"), str):
        raise ObserveError("INVALID_TRANSCRIPT", "Every cue needs a text string and finite start/end timestamps.")
    raw_start, raw_end = number(raw.get("start")), number(raw.get("end"))
    if raw_end <= raw_start or raw_start < 0:
        raise ObserveError("INVALID_TIMING", "Cue timestamps must satisfy 0 <= start < end.")
    begin, finish = raw_start + offset, raw_end + offset
    if finish <= lower or begin >= upper:
        return None
    result = {"id": f"s{index:04d}", "start": max(lower, begin), "end": min(upper, finish),
              "text": raw["text"], "corrected_text": None, "audio_speaker_id": speaker,
              "character": None, "role_evidence": [], "review_status": "unreviewed",
              "words": [], "raw_asr": raw,
              "clipped_start": begin < lower, "clipped_end": finish > upper}
    for word in raw.get("words") or []:
        if not isinstance(word, dict) or word.get("start") is None or word.get("end") is None:
            # WhisperX can leave unalignable words without timestamps. Preserve
            # their original record but never manufacture a precise time.
            continue
        word_start, word_end = number(word["start"]) + offset, number(word["end"]) + offset
        if word_end < word_start:
            raise ObserveError("INVALID_TIMING", "Word timestamps moved backwards.")
        if word_end <= lower or word_start >= upper:
            continue
        result["words"].append({"start": max(lower, word_start), "end": min(upper, word_end),
                                "text": word.get("word", word.get("text", "")),
                                "probability": word.get("probability", word.get("score")),
                                "audio_speaker_id": word.get("audio_speaker_id")})
    return result


def navigation_segments(raw_segments, offset, lower, upper, threshold=1.0):
    """Split only safe timestamp gaps, never infer grammar or speaker turns.

    Raw decoder segments remain intact in raw-asr.json and in each projected
    entry. Word groups are merely shorter navigation targets; a model's word
    alignment can be wrong even when its text reconstructs the segment.
    """
    projected, warnings = [], []
    for raw_index, raw in enumerate(raw_segments):
        if not isinstance(raw, dict) or not isinstance(raw.get("text"), str):
            raise ObserveError("INVALID_TRANSCRIPT", "ASR segments must have a text string.")
        words = raw.get("words")
        valid, usable = True, []
        if not isinstance(words, list) or not words:
            valid = False
            words = []
        for word in words:
            try:
                if not isinstance(word, dict) or not isinstance(word.get("word"), str):
                    raise ObserveError("INVALID_TIMING", "A navigation word needs its original text and timing.")
                begin, finish = number(word.get("start")), number(word.get("end"))
                if begin < 0 or finish < begin:
                    raise ObserveError("INVALID_TIMING", "A navigation word has invalid timing.")
            except ObserveError:
                valid = False
                continue
            usable.append(word)
        if "".join(word.get("word", "") for word in usable).strip() != raw["text"].strip():
            valid = False
        if len(usable) != len(words):
            valid = False
        for previous, current in zip(usable, usable[1:]):
            if number(current["start"]) < number(previous["end"]):
                valid = False
        boundaries = [0]
        if valid:
            boundaries += [index for index in range(1, len(words))
                           if (Fraction(str(words[index]["start"])) - Fraction(str(words[index - 1]["end"])))
                           > Fraction(str(threshold))]
        boundaries.append(len(words))
        split = valid and len(boundaries) > 2
        if split and any(number(words[finish - 1]["end"]) <= number(words[begin]["start"])
                         for begin, finish in zip(boundaries, boundaries[1:])):
            valid, split = False, False
        if not valid:
            warnings.append(f"navigation_split_not_applied_raw_segment_{raw_index}_incomplete_word_coverage")
        groups = list(zip(boundaries, boundaries[1:])) if split else [(0, len(words))]
        for begin, finish in groups:
            if split:
                group = words[begin:finish]
                candidate = {**raw, "start": group[0]["start"], "end": group[-1]["end"],
                             "text": "".join(word["word"] for word in group), "words": group}
            else:
                # Preserve all coarse text even when some word alignment is
                # missing. Only valid timed words enter precise projections.
                candidate = {**raw, "words": usable}
            entry = segment_record(candidate, len(projected) + 1, offset, lower, upper)
            if entry is not None:
                entry["raw_asr"] = raw
                entry["navigation"] = {"method": "word_timestamp_gap_navigation_only" if split else "original_asr_segment",
                                       "evidence_label": "navigation_candidate",
                                       "split_applied": split, "split_threshold_seconds": threshold,
                                       "raw_segment_index": raw_index,
                                       "raw_word_span": [begin, finish] if valid else None,
                                       "word_span_interval": "[start,end)",
                                       "boundary": "Navigation grouping only; not verified sentence, reaction or speaker boundaries."}
                projected.append(entry)
    return projected, warnings


def transcribe_command(args):
    video = visual.source_path(args.video)
    source, duration, warnings = source_scan(video)
    start, end = selection(args.start, args.end, duration)
    output = new_output(args.output, "transcribe")
    result = base(source, start, end, "asr_candidate")
    result["warnings"] = warnings + ["asr_candidates_not_verified_dialogue", "speaker_and_character_unknown",
                                     "vad_omission_or_empty_asr_does_not_prove_no_dialogue"]
    try:
        audio = extract_audio(video, source, output, start, end, args.audio_stream)
        result["audio"] = audio
        if audio is None:
            result["status"] = "no_audio_stream"
            return save(output, result)
        result["clock"].update(audio_first_source_seconds=audio["first_source_seconds"],
                                audio_offset_seconds=audio["offset_seconds"])
        record = model_record(args.model_dir)
        if args.device == "cpu" and args.compute_type != "int8":
            raise ObserveError("INVALID_ARGUMENT", "The CPU baseline requires int8; float16 is available only with explicit CUDA.")
        try:
            import numpy as np
            from faster_whisper import WhisperModel
            from faster_whisper.vad import VadOptions, get_speech_timestamps
        except ImportError as exc:
            raise ObserveError("SPEECH_DEPENDENCY_MISSING", "Install requirements-speech.txt in the isolated speech environment.") from exc
        installed = importlib.metadata.version("faster-whisper")
        if installed != "1.2.1":
            raise ObserveError("SPEECH_VERSION_MISMATCH", "This adapter is validated against faster-whisper==1.2.1.")
        with wave.open(audio["path"], "rb") as reader:
            samples = np.frombuffer(reader.readframes(reader.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
        vad_parameters = {"min_silence_duration_ms": 500}
        kept = None
        if not args.no_vad:
            speech = get_speech_timestamps(samples, vad_options=VadOptions(**vad_parameters), sampling_rate=RATE)
            kept = [{"start": start + item["start"] / RATE,
                     "end": min(end, start + item["end"] / RATE)} for item in speech]
        omitted, cursor = [], start
        for item in kept or []:
            if item["start"] > cursor:
                omitted.append({"start": cursor, "end": item["start"]})
            cursor = max(cursor, item["end"])
        if kept is not None and cursor < end:
            omitted.append({"start": cursor, "end": end})
        result["asr"] = {"provider": "faster-whisper", "version": installed, "model": record,
                         "device": args.device, "compute_type": args.compute_type,
                         "language_requested": args.language, "task": "transcribe",
                         "vad_filter": not args.no_vad, "vad_parameters": vad_parameters if not args.no_vad else None,
                         "vad_retained_ranges": kept, "vad_omitted_ranges": omitted if kept is not None else None,
                         "vad_ranges_are": "candidate_speech_not_complete_dialogue_coverage",
                         "word_timestamps": True, "beam_size": 5, "condition_on_previous_text": False,
                         "local_files_only": True}
        started = time.monotonic()
        model = WhisperModel(str(Path(args.model_dir).expanduser().resolve()), device=args.device,
                             compute_type=args.compute_type, cpu_threads=2, num_workers=1, local_files_only=True)
        segments, info = model.transcribe(samples, language=None if args.language == "auto" else args.language,
                                          task="transcribe", beam_size=5, temperature=0,
                                          condition_on_previous_text=False, word_timestamps=True,
                                          vad_filter=not args.no_vad,
                                          vad_parameters=vad_parameters if not args.no_vad else None)
        raw_segments = [primitive(item) for item in segments]
        raw = {"segments": raw_segments, "info": primitive(info)}
        visual.write_json_new(output / "raw-asr.json", raw)
        result["raw_asr_path"] = str(output / "raw-asr.json")
        result["raw_asr_sha256"] = visual.sha256(output / "raw-asr.json")
        result["segments"], navigation_warnings = navigation_segments(raw_segments, start, start, end)
        result["warnings"].extend(navigation_warnings)
        result["asr"]["navigation_grouping"] = {"method": "word_timestamp_gap_navigation_only",
                                                "split_threshold_seconds": 1.0,
                                                "full_word_text_coverage_required": True,
                                                "does_not_infer": ["grammar", "speaker_changes", "verified_utterances"]}
        result["asr"].update(elapsed_seconds=time.monotonic() - started,
                              language_detected=getattr(info, "language", None),
                              language_probability=primitive(getattr(info, "language_probability", None)))
        result["status"] = "completed" if any(x["text"].strip() for x in result["segments"]) else "completed_empty_transcript"
        unchanged(video, source["sha256"])
        return save(output, result)
    except Exception as exc:
        result.update(ok=False, status="asr_failed")
        result["error"] = {"code": getattr(exc, "code", "ASR_FAILED"), "message": str(exc)}
        return save(output, result)


def cue_time(text):
    pieces = text.replace(",", ".").split(":")
    if len(pieces) not in (2, 3):
        raise ObserveError("INVALID_TIMING", "Subtitle time must be MM:SS.mmm or HH:MM:SS.mmm.")
    try:
        parts = [float(x) for x in pieces]
    except ValueError as exc:
        raise ObserveError("INVALID_TIMING", "Subtitle timestamp is not numeric.") from exc
    if any(not math.isfinite(x) or x < 0 for x in parts) or parts[-1] >= 60 or parts[-2] >= 60:
        raise ObserveError("INVALID_TIMING", "Subtitle timestamp components are outside their ranges.")
    return sum(value * multiplier for value, multiplier in zip(reversed(parts), (1, 60, 3600)))


def subtitle_cues(text, kind):
    if kind == "vtt" and not text.lstrip("\ufeff").startswith("WEBVTT"):
        raise ObserveError("INVALID_SUBTITLE", "VTT input must start with WEBVTT.")
    blocks = re.split(r"\n\s*\n", text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").strip())
    cues = []
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        if kind == "vtt" and (lines[0].startswith("WEBVTT") or re.match(r"^(NOTE|STYLE|REGION)(?:\s|$)", lines[0])):
            continue
        positions = [i for i, line in enumerate(lines) if "-->" in line]
        if len(positions) != 1 or positions[0] not in (0, 1):
            raise ObserveError("INVALID_SUBTITLE", "Every subtitle cue needs one valid timing line.")
        pos = positions[0]
        match = re.fullmatch(r"\s*(\S+)\s+-->\s+(\S+)(?:\s+.*)?", lines[pos])
        if not match:
            raise ObserveError("INVALID_SUBTITLE", "Malformed subtitle cue timing.")
        body = "\n".join(lines[pos + 1:])
        if not body:
            raise ObserveError("INVALID_SUBTITLE", "A subtitle cue is missing its text.")
        cues.append({"start": cue_time(match[1]), "end": cue_time(match[2]), "text": body,
                     "source_cue_id": lines[0] if pos == 1 else None})
    if not cues:
        raise ObserveError("INVALID_SUBTITLE", "No timed subtitle cues were found.")
    return cues


def import_command(args):
    video, supplied = visual.source_path(args.video), visual.source_path(args.file)
    source, duration, warnings = source_scan(video)
    offset = number(args.time_offset, "time-offset")
    digest = visual.sha256(supplied)
    text = supplied.read_text(encoding="utf-8-sig")
    speakers = {}

    def anonymous(value):
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ObserveError("INVALID_TRANSCRIPT", "Supplied speaker labels must be nonempty strings.")
        if value not in speakers:
            speakers[value] = f"speaker{len(speakers) + 1:04d}"
        return speakers[value]

    if args.format in ("srt", "vtt"):
        cues = subtitle_cues(text, args.format)
        evidence = "caption"
    else:
        data = json.loads(text)
        if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
            raise ObserveError("INVALID_TRANSCRIPT", "WhisperX JSON requires a segments array.")
        cues = data["segments"]
        evidence = "imported_asr_candidate"
    result = base(source, 0.0, duration, evidence)
    result.update(status="imported", import_source={"path": str(supplied), "sha256": digest,
                                                    "format": args.format, "time_offset_seconds": offset,
                                                    "mapping": "video_relative_time = supplied_time + time_offset"})
    result["warnings"] = warnings + ["import_not_verified_against_audio", "unobserved_role_and_reaction"]
    if evidence == "caption":
        result["warnings"].append("captions_are_not_proof_of_spoken_words")
    omitted = 0
    for index, original in enumerate(cues, 1):
        if not isinstance(original, dict):
            raise ObserveError("INVALID_TRANSCRIPT", "Imported segments must be objects.")
        raw = dict(original)
        speaker = anonymous(raw.get("speaker")) if evidence != "caption" else None
        if evidence != "caption" and raw.get("words") is not None:
            if not isinstance(raw["words"], list):
                raise ObserveError("INVALID_TRANSCRIPT", "Imported words must be an array.")
            raw["words"] = [dict(word, audio_speaker_id=anonymous(word.get("speaker")))
                            if isinstance(word, dict) else word for word in raw["words"]]
        entry = segment_record(raw, index, offset, 0.0, duration, speaker)
        if entry is None:
            omitted += 1
        else:
            # Normalized word speaker IDs above belong only to the projected
            # evidence. Keep the imported segment's original parsed content.
            entry["raw_asr"] = original
            result["segments"].append(entry)
    result["import_source"].update(cues_total=len(cues), cues_outside_video=omitted,
                                    supplied_speaker_count=len(speakers),
                                    speaker_boundary="Anonymous imported labels only; no voice or character identity inferred.")
    if omitted:
        result["warnings"].append("outside_video_cues_not_projected_original_import_retained")
    output = new_output(args.output, "import")
    # Freeze exact original bytes as well as the normalized representation.
    frozen = output / f"import-source.{args.format if args.format != 'whisperx' else 'json'}"
    with frozen.open("xb") as stream:
        stream.write(supplied.read_bytes())
    unchanged(supplied, digest)
    unchanged(video, source["sha256"])
    result["import_source"]["frozen_path"] = str(frozen)
    return save(output, result)


def window_command(args):
    supplied = visual.source_path(args.dialogue)
    parent_hash = visual.sha256(supplied)
    parent = json.loads(supplied.read_text(encoding="utf-8"))
    if not isinstance(parent, dict) or parent.get("kind") != "dialogue" or parent.get("schema_version") != 1:
        raise ObserveError("INVALID_MANIFEST", "Expected a dialogue schema_version=1 manifest.")
    source = parent.get("source", {})
    video = visual.source_path(source["path"])
    unchanged(video, source["sha256"])
    matches = [x for x in parent.get("segments", []) if x.get("id") == args.segment_id]
    if len(matches) != 1:
        raise ObserveError("UNKNOWN_SEGMENT", "segment-id must identify one source utterance/caption.")
    context = number(args.context, "context")
    if context < 0:
        raise ObserveError("INVALID_ARGUMENT", "context must be nonnegative.")
    current, duration, warnings = source_scan(video)
    item = matches[0]
    start, end = selection(max(0, number(item["start"]) - context), number(item["end"]) + context, duration)
    output = new_output(args.output, "window")
    images = visual.window_command(argparse.Namespace(video=str(video), output=str(output / "visual"),
                                                     start=start, end=end, fps=4.0))
    stream_index = parent.get("audio", {}).get("stream_index") if isinstance(parent.get("audio"), dict) else None
    audio = extract_audio(video, current, output, start, end, stream_index)
    result = {"ok": True, "schema_version": 1, "tool_version": VERSION, "kind": "dialogue_window",
              "source": current, "parent_manifest": str(supplied), "parent_manifest_sha256": parent_hash,
              "segment_id": args.segment_id, "evidence_kind": parent.get("evidence_kind"),
              "window": {"start": start, "end": end, "time_origin": "first_presented_frame"},
              "audio": audio, "visual_manifest": images["manifest_path"],
              "visual_manifest_sha256": visual.sha256(Path(images["manifest_path"])),
              "warnings": warnings + ["snippet_export_not_listening_or_character_attribution", "static_images_do_not_establish_real_time_delivery"],
              "coverage": {"observation_status": "not_observed", "listening_status": "not_listened"}}
    unchanged(supplied, parent_hash)
    unchanged(video, source["sha256"])
    return visual.save_manifest(output, result)


def parser():
    root = visual.Parser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True, parser_class=visual.Parser)
    transcribe = commands.add_parser("transcribe", help="Candidate local ASR; a supplied local model is required.")
    transcribe.add_argument("--video", required=True)
    transcribe.add_argument("--output", required=True)
    transcribe.add_argument("--model-dir", required=True)
    transcribe.add_argument("--language", choices=("auto", "zh", "en"), default="auto")
    transcribe.add_argument("--audio-stream", type=int)
    transcribe.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    transcribe.add_argument("--compute-type", choices=("int8", "float16"), default="int8")
    transcribe.add_argument("--no-vad", action="store_true")
    transcribe.add_argument("--start", type=float)
    transcribe.add_argument("--end", type=float)
    transcribe.set_defaults(handler=transcribe_command)
    imported = commands.add_parser("import", help="Import captions or supplied WhisperX output with an explicit source-clock offset.")
    imported.add_argument("--video", required=True)
    imported.add_argument("--file", required=True)
    imported.add_argument("--format", choices=("srt", "vtt", "whisperx"), required=True)
    imported.add_argument("--time-offset", type=float, required=True)
    imported.add_argument("--output", required=True)
    imported.set_defaults(handler=import_command)
    window = commands.add_parser("window", help="Export context frames and an aligned PCM snippet; no listening claim.")
    window.add_argument("--dialogue", required=True)
    window.add_argument("--segment-id", required=True)
    window.add_argument("--context", type=float, default=1.0)
    window.add_argument("--output", required=True)
    window.set_defaults(handler=window_command)
    return root


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        result = args.handler(args)
    except ObserveError as exc:
        result = {"ok": False, "error": {"code": exc.code, "message": exc.message}}
    except Exception as exc:
        result = {"ok": False, "error": {"code": "PROCESSING_ERROR", "message": str(exc)}}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
