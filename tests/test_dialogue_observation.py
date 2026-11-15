"""Temporary media tests for dialogue provenance and shared audio/video clocks.

ASR subprocess tests inject a deliberately tiny fake backend. They test the
adapter and failure handling, not recognition quality. No weights, network,
GPU, private recordings or source media are needed by this suite.
"""

from __future__ import annotations

from array import array
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import wave


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/video-observation/scripts/dialogue_observe.py"
REQUIRE_MEDIA = os.environ.get("VIDEO_OBSERVE_REQUIRE_MEDIA") == "1"
MEDIA_IMPORT_ERROR = None
try:
    import av
    import scenedetect  # noqa: F401 -- existing window's required runtime
    from PIL import Image
except ImportError as exc:
    MEDIA_IMPORT_ERROR = str(exc)
if REQUIRE_MEDIA and MEDIA_IMPORT_ERROR:
    raise RuntimeError(f"Dialogue media dependencies are required: {MEDIA_IMPORT_ERROR}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_av_clip(path: Path, *, video_start=2, audio_times=(), values=None, frame_count=15):
    """Lossless frames and PCM bursts whose real decoded PTS provide truth."""
    events = []
    with av.open(str(path), "w") as container:
        video = container.add_stream("ffv1", rate=10)
        video.width, video.height, video.pix_fmt = 96, 64, "bgr0"
        video.time_base = video.codec_context.time_base = Fraction(1, 1000)
        for number in range(frame_count):
            frame = av.VideoFrame.from_image(Image.new("RGB", (96, 64), (number * 13 % 255, 30, 90)))
            frame.time_base = Fraction(1, 1000)
            frame.pts = round((video_start + number / 10) * 1000)
            events.append((Fraction(frame.pts, 1000), video, frame))
        audio = None
        if audio_times:
            audio = container.add_stream("pcm_s16le", rate=16000)
            audio.layout = "mono"
            audio.time_base = Fraction(1, 16000)
            for index, timestamp in enumerate(audio_times):
                value = values[index] if values is not None else 9000
                samples = array("h", [value] * 1600)
                if sys.byteorder != "little":
                    samples.byteswap()
                frame = av.AudioFrame(format="s16", layout="mono", samples=1600)
                frame.sample_rate = 16000
                frame.time_base = Fraction(1, 16000)
                frame.pts = round(timestamp * 16000)
                frame.planes[0].update(samples.tobytes())
                events.append((Fraction(frame.pts, 16000), audio, frame))
        for _, stream, frame in sorted(events, key=lambda item: item[0]):
            for packet in stream.encode(frame):
                container.mux(packet)
        for stream in (video, audio):
            if stream is not None:
                for packet in stream.encode():
                    container.mux(packet)


def audio_truth(path):
    with av.open(str(path)) as container:
        return [(float(f.pts * f.time_base), f.samples / f.sample_rate)
                for f in container.decode(audio=0)]


FAKE_BACKEND = r'''
import json, os, wave
from dataclasses import dataclass, field
from types import SimpleNamespace
__version__ = "1.2.1"
@dataclass
class Word:
    start: float
    end: float
    word: str
    probability: float = 0.9
@dataclass
class Segment:
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list = field(default_factory=list)
    avg_logprob: float = -0.1
    compression_ratio: float = 1.0
    no_speech_prob: float = 0.01
    words: list = field(default_factory=list)
    temperature: float = 0.0
class WhisperModel:
    def __init__(self, model, **kwargs):
        if kwargs.get("local_files_only") is not True:
            raise RuntimeError("Test backend requires explicit local_files_only=True")
        if kwargs.get("device") != "cpu":
            raise RuntimeError("Default test backend must stay on CPU")
        self.model = model
        self.kwargs = kwargs
    def transcribe(self, audio, **kwargs):
        assert audio.ndim == 1
        duration = len(audio)/16000
        log = os.environ.get("DIALOGUE_TEST_LOG")
        if log:
            with open(log, "w", encoding="utf-8") as f:
                json.dump({"init": self.kwargs, "transcribe": kwargs, "duration":duration}, f)
        mode = os.environ.get("DIALOGUE_TEST_MODE", "normal")
        def result():
            if mode == "failure":
                raise RuntimeError("Deliberate deferred decoder failure")
            if mode == "empty":
                return
            rows = json.loads(os.environ.get("DIALOGUE_TEST_SEGMENTS", '[{"start":0.2,"end":0.4,"text":"别动。 Wait."}]'))
            for i,row in enumerate(rows):
                yield Segment(id=i, seek=0, **row)
        return result(), SimpleNamespace(language="zh", language_probability=0.98,
            duration=duration, duration_after_vad=duration, all_language_probs=[("zh",0.98)])
'''


@unittest.skipIf(MEDIA_IMPORT_ERROR is not None,
                 f"Dialogue media dependencies unavailable: {MEDIA_IMPORT_ERROR}")
class DialogueObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.is_file():
            raise RuntimeError(f"Missing dialogue CLI: {SCRIPT}")
        for codec in ("ffv1", "pcm_s16le"):
            if codec not in av.codec.codecs_available:
                if REQUIRE_MEDIA:
                    raise RuntimeError(f"Required fixture encoder unavailable: {codec}")
                raise unittest.SkipTest(f"Fixture encoder unavailable: {codec}")
        cls.fixture_temp = tempfile.TemporaryDirectory(prefix="dialogue-synthetic-")
        cls.fixtures = Path(cls.fixture_temp.name) / "中文 空格"
        cls.fixtures.mkdir()
        cls.video_only = cls.fixtures / "无音轨.mkv"
        cls.delayed = cls.fixtures / "延迟与空档.mkv"
        cls.audio_before = cls.fixtures / "音频先开始.mkv"
        cls.long_dialogue = cls.fixtures / "短句与长停顿.mkv"
        make_av_clip(cls.video_only)
        make_av_clip(cls.delayed, audio_times=[2.2, 2.3, 2.8, 2.9])
        make_av_clip(cls.audio_before, audio_times=[1.5, 1.6, 2.0, 2.1], values=[7000, 7000, 12000, 12000])
        make_av_clip(cls.long_dialogue, audio_times=[2.2, 14.1, 20.8, 44.4], frame_count=450)
        cls.protected = {path: digest(path) for path in (cls.video_only, cls.delayed, cls.audio_before, cls.long_dialogue)}
        # Assertions about fixtures use decoder truth, not muxing assumptions.
        assert abs(audio_truth(cls.delayed)[0][0] - 2.2) < 0.001
        assert abs(audio_truth(cls.audio_before)[0][0] - 1.5) < 0.001

    @classmethod
    def tearDownClass(cls):
        cls.fixture_temp.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="dialogue-output-")
        self.work = Path(self.temporary.name)
        self.fake = self.work / "fake"
        (self.fake / "faster_whisper").mkdir(parents=True)
        (self.fake / "faster_whisper/__init__.py").write_text(FAKE_BACKEND, encoding="utf-8")
        (self.fake / "faster_whisper/vad.py").write_text(
            "import numpy as np\n"
            "class VadOptions:\n"
            "    def __init__(self, **kwargs): self.options = kwargs\n"
            "def get_speech_timestamps(audio, **kwargs):\n"
            "    mask = np.abs(audio) > 0.001\n"
            "    edges = np.diff(np.r_[False, mask, False].astype(np.int8))\n"
            "    return [{'start':int(a),'end':int(b)} for a,b in zip(np.where(edges==1)[0],np.where(edges==-1)[0])]\n",
            encoding="utf-8")
        info = self.fake / "faster_whisper-1.2.1.dist-info"
        info.mkdir()
        (info / "METADATA").write_text("Metadata-Version: 2.1\nName: faster-whisper\nVersion: 1.2.1\n", encoding="utf-8")
        self.model = self.work / "explicit local model"
        self.model.mkdir()
        (self.model / "model.bin").write_bytes(b"adapter-test-only-not-real-weights")

    def tearDown(self):
        for path, expected in self.protected.items():
            self.assertEqual(digest(path), expected, f"Tool changed source: {path.name}")
        self.temporary.cleanup()

    def cli(self, *arguments, success=True, mode="normal", segments=None):
        env = os.environ.copy()
        env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "HF_HUB_OFFLINE":"1",
                    "DIALOGUE_TEST_MODE":mode, "DIALOGUE_TEST_LOG":str(self.work / "asr-call.json"),
                    "PYTHONPATH":str(self.fake)})
        if segments is not None:
            env["DIALOGUE_TEST_SEGMENTS"] = json.dumps(segments, ensure_ascii=False)
        completed = subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                                   capture_output=True, encoding="utf-8", env=env, timeout=90)
        try:
            data = json.loads(completed.stdout)
        except ValueError:
            self.fail(f"Invalid CLI JSON: {completed.stdout!r}; stderr={completed.stderr!r}")
        if success:
            self.assertEqual(completed.returncode, 0, f"{data}; stderr={completed.stderr}")
        else:
            self.assertNotEqual(completed.returncode, 0, "Invalid operation succeeded")
            self.assertIs(data.get("ok"), False)
            self.assertTrue(data.get("error", {}).get("code"))
        return data

    def transcribe(self, video=None, *, output="asr", mode="normal", segments=None, success=True, extra=()):
        folder = self.work / output
        self.cli("transcribe", "--video", video or self.delayed, "--model-dir", self.model,
                 "--output", folder, *extra, success=success, mode=mode, segments=segments)
        return folder, json.loads((folder / "manifest.json").read_text(encoding="utf-8"))

    def captions(self, *, text=None, fmt="srt", offset=0, video=None, output="imported"):
        source = self.work / ("captions." + ("json" if fmt=="whisperx" else fmt))
        source.write_text(text or "1\n00:00:00,250 --> 00:00:00,500\n别动。 Wait.\n", encoding="utf-8")
        before = source.read_bytes()
        folder = self.work / output
        self.cli("import", "--video", video or self.delayed, "--file", source,
                 "--format", fmt, "--time-offset", offset, "--output", folder)
        self.assertEqual(source.read_bytes(), before)
        return folder, json.loads((folder / "manifest.json").read_text(encoding="utf-8"))

    def waveform(self, manifest):
        path = Path(manifest["audio"]["path"])
        self.assertEqual(digest(path), manifest["audio"]["sha256"])
        with wave.open(str(path), "rb") as f:
            self.assertEqual((f.getframerate(), f.getnchannels(), f.getsampwidth()), (16000, 1, 2))
            result = array("h", f.readframes(f.getnframes()))
        if sys.byteorder != "little":
            result.byteswap()
        return result

    def test_subtitle_import_is_caption_evidence_not_spoken_or_role_proof(self):
        folder, manifest = self.captions()
        self.assertEqual(manifest["evidence_kind"], "caption")
        self.assertEqual(manifest["source"]["sha256"], digest(self.delayed))
        segment = manifest["segments"][0]
        self.assertEqual(segment["text"], "别动。 Wait.")
        self.assertIsNone(segment["audio_speaker_id"])
        self.assertIsNone(segment["character"])
        self.assertEqual(segment["role_evidence"], [])
        self.assertEqual(segment["review_status"], "unreviewed")
        self.assertTrue((folder / "transcript.md").is_file())
        self.assertTrue((folder / "candidate.srt").is_file())

    def test_subtitle_offset_uses_video_relative_clock_not_container_zero(self):
        _, manifest = self.captions(offset=0.5)
        self.assertAlmostEqual(manifest["clock"]["video_origin_seconds"], 2.0)
        self.assertEqual(manifest["clock"]["time_origin"], "first_presented_frame")
        self.assertAlmostEqual(manifest["segments"][0]["start"], 0.75)
        self.assertAlmostEqual(manifest["segments"][0]["end"], 1.0)

    def test_vtt_preserves_multiline_original_words(self):
        _, manifest = self.captions(fmt="vtt", text="WEBVTT\n\n00:00.200 --> 00:00.600\n不，不是那个！\nNot that one!\n")
        self.assertIn("不，不是那个！", manifest["segments"][0]["text"])
        self.assertIn("Not that one!", manifest["segments"][0]["text"])

    def test_whisperx_import_retains_anonymous_speakers_and_overlap(self):
        raw = {"language":"zh", "segments":[
            {"start":0.2,"end":0.7,"text":"先别动。","speaker":"SPEAKER_00"},
            {"start":0.6,"end":1.0,"text":"Wait!","speaker":"SPEAKER_01"}]}
        _, manifest = self.captions(fmt="whisperx", text=json.dumps(raw, ensure_ascii=False))
        self.assertEqual(manifest["evidence_kind"], "imported_asr_candidate")
        voices = [s["audio_speaker_id"] for s in manifest["segments"]]
        self.assertTrue(all(isinstance(voice, str) and voice for voice in voices))
        self.assertEqual(len(set(voices)), 2)
        self.assertEqual([s["raw_asr"]["speaker"] for s in manifest["segments"]], ["SPEAKER_00", "SPEAKER_01"])
        self.assertTrue(all(s["character"] is None for s in manifest["segments"]))
        self.assertLess(manifest["segments"][1]["start"], manifest["segments"][0]["end"])

    def test_named_imported_speaker_is_not_promoted_to_visible_character(self):
        raw = {"segments":[{"start":0.2,"end":0.5,"text":"先等等。","speaker":"菲菲"}]}
        _, manifest = self.captions(fmt="whisperx", text=json.dumps(raw, ensure_ascii=False))
        item = manifest["segments"][0]
        self.assertNotEqual(item["audio_speaker_id"], "菲菲")
        self.assertIsNone(item["character"])
        self.assertEqual(item["raw_asr"]["speaker"], "菲菲")

    def test_outside_captions_are_clipped_but_frozen_source_is_retained(self):
        text = "1\n00:00:00,100 --> 00:00:00,300\nBefore start.\n\n2\n00:00:01,800 --> 00:00:02,000\nAfter end.\n"
        _, manifest = self.captions(text=text, offset=-0.2)
        self.assertEqual(len(manifest["segments"]), 1)
        self.assertEqual(manifest["segments"][0]["start"], 0)
        self.assertAlmostEqual(manifest["segments"][0]["end"], 0.1)
        self.assertIs(manifest["segments"][0]["clipped_start"], True)
        self.assertEqual(manifest["import_source"]["cues_total"], 2)
        self.assertEqual(manifest["import_source"]["cues_outside_video"], 1)
        frozen = Path(manifest["import_source"]["frozen_path"])
        self.assertEqual(frozen.read_text(encoding="utf-8"), text)
        self.assertEqual(digest(frozen), manifest["import_source"]["sha256"])

    def test_no_audio_stream_does_not_attempt_asr_or_claim_listening(self):
        _, manifest = self.transcribe(self.video_only)
        self.assertEqual(manifest["status"], "no_audio_stream")
        self.assertEqual(manifest["segments"], [])
        self.assertIsNone(manifest["audio"])
        self.assertFalse((self.work / "asr-call.json").exists())

    def test_successful_empty_asr_stays_distinct_from_no_audio(self):
        _, manifest = self.transcribe(mode="empty")
        self.assertEqual(manifest["status"], "completed_empty_transcript")
        self.assertEqual(manifest["segments"], [])
        self.assertIsNotNone(manifest["audio"])
        self.assertEqual(manifest["evidence_kind"], "asr_candidate")

    def test_deferred_asr_failure_is_preserved_with_audio_and_nonzero_exit(self):
        _, manifest = self.transcribe(mode="failure", success=False)
        self.assertEqual(manifest["status"], "asr_failed")
        self.assertIsNotNone(manifest["audio"])

    def test_asr_is_local_cpu_and_keeps_raw_words_without_fabricated_speaker(self):
        _, manifest = self.transcribe()
        call = json.loads((self.work / "asr-call.json").read_text())
        self.assertIs(call["init"]["local_files_only"], True)
        self.assertEqual(call["init"]["device"], "cpu")
        self.assertEqual(call["init"]["compute_type"], "int8")
        self.assertIs(call["transcribe"]["vad_filter"], True)
        segment = manifest["segments"][0]
        self.assertEqual(segment["text"], "别动。 Wait.")
        self.assertIsNone(segment["corrected_text"])
        self.assertIsNone(segment["audio_speaker_id"])
        self.assertIsNone(segment["character"])
        self.assertIsNotNone(segment["raw_asr"])

    def test_audio_delay_and_internal_gaps_remain_in_pcm_clock(self):
        _, manifest = self.transcribe()
        self.assertAlmostEqual(manifest["clock"]["audio_first_source_seconds"], 2.2, places=3)
        self.assertAlmostEqual(manifest["clock"]["audio_offset_seconds"], 0.2, places=3)
        samples = self.waveform(manifest)
        self.assertTrue(all(abs(x) < 2 for x in samples[1600:2400]))
        self.assertGreater(max(samples[4000:4800]), 5000)
        self.assertTrue(all(abs(x) < 2 for x in samples[8000:11200]))
        self.assertGreater(max(samples[13600:14400]), 5000)

    def test_audio_before_first_video_frame_is_clipped_without_shifting_dialogue(self):
        _, manifest = self.transcribe(self.audio_before)
        self.assertAlmostEqual(manifest["clock"]["audio_offset_seconds"], -0.5, places=3)
        samples = self.waveform(manifest)
        self.assertGreater(min(samples[100:1500]), 10000)
        self.assertAlmostEqual(manifest["segments"][0]["start"], 0.2)

    def test_bounded_no_vad_retry_keeps_its_global_offset(self):
        _, manifest = self.transcribe(extra=("--start",0.7,"--end",1.2,"--no-vad"),
            segments=[{"start":0.1,"end":0.3,"text":"嗯。"}])
        self.assertAlmostEqual(manifest["segments"][0]["start"], 0.8)
        self.assertAlmostEqual(manifest["segments"][0]["end"], 1.0)
        call = json.loads((self.work / "asr-call.json").read_text())
        self.assertIs(call["transcribe"]["vad_filter"], False)
        self.assertAlmostEqual(call["duration"], 0.5, places=3)

    def test_language_choice_reaches_backend(self):
        self.transcribe(extra=("--language", "en"))
        call = json.loads((self.work / "asr-call.json").read_text())
        self.assertEqual(call["transcribe"]["language"], "en")

    def test_word_gaps_create_navigable_cues_without_rewriting_original_asr(self):
        words = [
            {"start":12.05,"end":13.0,"word":" A"},
            {"start":13.1,"end":15.15,"word":" first line."},
            {"start":18.76,"end":20.12,"word":" A second line."},
            {"start":42.33,"end":43.53,"word":" Final line."},
        ]
        text = " A first line. A second line. Final line."
        raw = {"start":12.05,"end":43.53,"text":text,"words":words}
        folder, manifest = self.transcribe(self.long_dialogue, segments=[raw],
            extra=("--start",0.5,"--end",44.5))
        self.assertEqual(len(manifest["segments"]), 3)
        for item, expected, span in zip(manifest["segments"],
                [(12.55,15.65),(19.26,20.62),(42.83,44.03)], [[0,2],[2,3],[3,4]]):
            self.assertAlmostEqual(item["start"], expected[0], places=6)
            self.assertAlmostEqual(item["end"], expected[1], places=6)
            self.assertEqual(item["navigation"]["raw_segment_index"], 0)
            self.assertEqual(item["navigation"]["raw_word_span"], span)
            self.assertEqual(item["navigation"]["split_threshold_seconds"], 1.0)
            self.assertIsNone(item["audio_speaker_id"])
            self.assertIsNone(item["character"])
            self.assertEqual(item["raw_asr"]["text"], text)
        self.assertEqual(len({item["id"] for item in manifest["segments"]}),3)
        self.assertEqual("".join(item["text"] for item in manifest["segments"]).strip(),text.strip())
        retained = json.loads((folder / "raw-asr.json").read_text(encoding="utf-8"))
        self.assertEqual(len(retained["segments"]),1)
        self.assertEqual(retained["segments"][0]["start"],12.05)
        self.assertEqual(retained["segments"][0]["end"],43.53)
        self.assertEqual(retained["segments"][0]["words"],words)
        self.assertEqual(retained["segments"][0]["text"],text)

    def test_incomplete_word_timestamps_keep_original_segment_and_warning(self):
        words=[{"start":1.0,"end":2.0,"word":" First."},
               {"start":None,"end":None,"word":" Missing."},
               {"start":8.0,"end":9.0,"word":" Last."}]
        _, manifest=self.transcribe(self.long_dialogue, segments=[{
            "start":1.0,"end":9.0,"text":" First. Missing. Last.","words":words}])
        self.assertEqual(len(manifest["segments"]),1)
        self.assertEqual(manifest["segments"][0]["text"]," First. Missing. Last.")
        self.assertEqual(manifest["segments"][0]["start"],1.0)
        self.assertEqual(manifest["segments"][0]["end"],9.0)
        self.assertIn("navigation_split_not_applied_raw_segment_0_incomplete_word_coverage",manifest["warnings"])

    def test_word_text_mismatch_keeps_all_original_transcript_text(self):
        _, manifest=self.transcribe(self.long_dialogue, segments=[{
            "start":1.0,"end":9.0,"text":" First. A missing phrase. Last.","words":[
                {"start":1.0,"end":2.0,"word":" First."},
                {"start":8.0,"end":9.0,"word":" Last."}]}])
        self.assertEqual(len(manifest["segments"]),1)
        self.assertEqual(manifest["segments"][0]["text"]," First. A missing phrase. Last.")
        self.assertIn("navigation_split_not_applied_raw_segment_0_incomplete_word_coverage",manifest["warnings"])

    def test_exactly_one_second_word_gap_is_not_split(self):
        _, manifest=self.transcribe(self.long_dialogue, segments=[{
            "start":1.0,"end":4.0,"text":" First. Last.","words":[
                {"start":1.0,"end":2.0,"word":" First."},
                {"start":3.0,"end":4.0,"word":" Last."}]}])
        self.assertEqual(len(manifest["segments"]),1)
        self.assertEqual(manifest["segments"][0]["text"]," First. Last.")

    def test_reports_must_finish_before_completed_manifest_is_written(self):
        module=self.load_tool()
        original_open=Path.open
        for target in ("transcript.md","candidate.srt"):
            with self.subTest(report=target):
                output=self.work / ("write-failure-"+target)
                output.mkdir()
                result={"status":"completed","evidence_kind":"asr_candidate","segments":[],"warnings":[]}
                def failing(path,*args,**kwargs):
                    if path.parent==output and path.name==target:
                        raise OSError("Injected report write failure")
                    return original_open(path,*args,**kwargs)
                with mock.patch.object(Path,"open",new=failing):
                    with self.assertRaises(OSError):
                        module.save(output,result)
                self.assertFalse((output / "manifest.json").exists(),
                    "A failed report must not leave a completed result manifest")

    def test_model_fingerprint_ignores_download_metadata_but_tracks_weights(self):
        module=self.load_tool()
        first=module.model_record(self.model)
        (self.model / ".cache/download").mkdir(parents=True)
        (self.model / ".cache/download/transfer.json").write_text("temporary download metadata")
        (self.model / ".control.json").write_text("local control file")
        second=module.model_record(self.model)
        self.assertEqual(first["fingerprint_sha256"],second["fingerprint_sha256"])
        self.assertEqual([entry["path"] for entry in second["files"]],["model.bin"])
        self.assertTrue(second.get("fingerprint_scope"))
        self.assertTrue(second.get("excluded_path_parts"))
        (self.model / ".cache/download/transfer.json").write_text("changed transfer receipt")
        third=module.model_record(self.model)
        self.assertEqual(second["fingerprint_sha256"],third["fingerprint_sha256"])
        (self.model / "model.bin").write_bytes(b"changed actual model bytes")
        fourth=module.model_record(self.model)
        self.assertNotEqual(third["fingerprint_sha256"],fourth["fingerprint_sha256"])

    def test_import_rejects_malformed_cues(self):
        source = self.work / "bad.srt"
        source.write_text("1\nnot a timestamp --> neither\n角色开口。\n", encoding="utf-8")
        self.cli("import", "--video", self.delayed, "--file", source, "--format", "srt",
                 "--time-offset",0,"--output",self.work / "bad-import", success=False)

    def test_import_requires_explicit_caption_time_offset(self):
        source = self.work / "valid.srt"
        source.write_text("1\n00:00:00,100 --> 00:00:00,300\nHello.\n", encoding="utf-8")
        self.cli("import", "--video",self.delayed,"--file",source,"--format","srt",
                 "--output",self.work / "no-clock",success=False)

    def test_nonfinite_import_timing_is_rejected(self):
        source = self.work / "not-finite.json"
        source.write_text('{"segments":[{"start":NaN,"end":0.5,"text":"Hello."}]}', encoding="utf-8")
        self.cli("import","--video",self.delayed,"--file",source,"--format","whisperx",
                 "--time-offset",0,"--output",self.work / "nonfinite",success=False)

    def test_output_collision_preserves_first_result(self):
        folder, _ = self.captions()
        before = (folder / "manifest.json").read_bytes()
        self.cli("import", "--video",self.delayed,"--file",self.work / "captions.srt",
                 "--format","srt","--time-offset",0,"--output",folder,success=False)
        self.assertEqual((folder / "manifest.json").read_bytes(), before)

    def test_window_rejects_source_mutation(self):
        source = self.work / "mutable.mkv"
        source.write_bytes(self.delayed.read_bytes())
        folder, manifest = self.captions(video=source)
        source.write_bytes(source.read_bytes() + b"changed after observation")
        self.cli("window","--dialogue",folder / "manifest.json","--segment-id",manifest["segments"][0]["id"],
                 "--output",self.work / "stale-window", success=False)

    def test_window_exports_existing_frames_and_matching_audio_context(self):
        folder, manifest = self.captions(text="1\n00:00:00,850 --> 00:00:00,950\n等一下！\n")
        output = self.work / "context"
        self.cli("window","--dialogue",folder / "manifest.json","--segment-id",manifest["segments"][0]["id"],
                 "--context",0.1,"--output",output)
        produced = list(output.rglob("*.png")) + list(output.rglob("*.jpg"))
        self.assertTrue(produced, "Review window must produce actual source views")
        wavs = list(output.rglob("*.wav"))
        self.assertTrue(wavs, "Review window must produce actual audio context")
        with wave.open(str(wavs[0]), "rb") as f:
            self.assertAlmostEqual(f.getnframes()/f.getframerate(),0.3,places=3)
        all_manifests = [json.loads(path.read_text(encoding="utf-8")) for path in output.rglob("manifest.json")]
        visual = [item for item in all_manifests if item.get("frames")]
        self.assertTrue(visual, "Review window must link actual frame evidence")
        for frame in visual[0]["frames"]:
            self.assertGreaterEqual(frame["seconds"],0.75 - 1e-9)
            self.assertLess(frame["seconds"],1.05)

    def test_window_rejects_unknown_segment(self):
        folder, _ = self.captions()
        self.cli("window","--dialogue",folder / "manifest.json","--segment-id","missing",
                 "--output",self.work / "bad-segment",success=False)

    def test_audio_stream_selection_rejects_video_stream_index(self):
        self.cli("transcribe","--video",self.delayed,"--model-dir",self.model,"--audio-stream",0,
                 "--output",self.work / "bad-stream",success=False)

    def test_remote_input_is_rejected_without_network_access(self):
        self.cli("transcribe","--video","https://example.invalid/video.mp4","--model-dir",self.model,
                 "--output",self.work / "remote",success=False)

    def load_tool(self):
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            spec = importlib.util.spec_from_file_location("dialogue_clock_guard_test", SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        return module

    def decoder_guard(self, timestamps, expected_code):
        """Inject malformed decoded clocks a well-formed muxer cannot encode."""
        module=self.load_tool()
        source, _, _ = module.source_scan(self.delayed)
        stream = SimpleNamespace(index=1, codec_context=SimpleNamespace(thread_count=0))
        frames = []
        for timestamp in timestamps:
            frame = av.AudioFrame(format="s16",layout="mono",samples=1600)
            frame.sample_rate=16000
            frame.time_base=Fraction(1,16000)
            frame.pts=timestamp
            frame.planes[0].update(b"\0\0" * 1600)
            frames.append(frame)
        class Decoder:
            streams=SimpleNamespace(audio=[stream])
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def decode(self,*args): return iter(frames)
        fake_av = SimpleNamespace(open=lambda *args, **kwargs: Decoder(), AudioResampler=av.AudioResampler)
        output = self.work / "clock-guard"
        output.mkdir()
        with mock.patch.object(module.visual,"dependencies",return_value=(fake_av,None,None,None)):
            with self.assertRaises(module.ObserveError) as caught:
                module.extract_audio(self.delayed,source,output,0,1.5)
        self.assertEqual(caught.exception.code, expected_code)

    def test_missing_decoded_audio_pts_does_not_receive_guessed_timing(self):
        self.decoder_guard([None], "MISSING_AUDIO_PTS")

    def test_nonmonotonic_decoded_audio_clock_is_rejected(self):
        self.decoder_guard([32000,31800], "NONMONOTONIC_AUDIO_PTS")


if __name__ == "__main__":
    unittest.main()
