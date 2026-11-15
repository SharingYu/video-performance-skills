"""Media integration tests using original, temporary synthetic clips.

No private footage, GPU, network or model inference is needed. Set
VIDEO_OBSERVE_REQUIRE_MEDIA=1 in the media CI job to make missing media
dependencies an error rather than a clearly reported skip.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/video-observation/scripts/video_observe.py"
REQUIRE_MEDIA = os.environ.get("VIDEO_OBSERVE_REQUIRE_MEDIA") == "1"
MEDIA_IMPORT_ERROR = None
try:
    import av
    import scenedetect  # noqa: F401 -- overview's required runtime dependency
    from PIL import Image, ImageChops, ImageDraw
except ImportError as exc:
    MEDIA_IMPORT_ERROR = str(exc)

if REQUIRE_MEDIA and MEDIA_IMPORT_ERROR:
    raise RuntimeError(f"Media integration dependencies are required: {MEDIA_IMPORT_ERROR}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_clip(path: Path, pts: list[int], *, codec: str = "ffv1", shots: bool = False) -> None:
    """Encode numbered RGB patterns; the decoder itself supplies test truth."""
    time_base = Fraction(1, 1000)
    with av.open(str(path), "w") as container:
        stream = container.add_stream(codec, rate=10)
        stream.width, stream.height = 128, 96
        stream.pix_fmt = "bgr0" if codec == "ffv1" else "yuv420p"
        stream.time_base = time_base
        stream.codec_context.time_base = time_base
        if codec == "libx264":
            stream.codec_context.max_b_frames = 2
            stream.options = {"crf": "16", "preset": "medium", "bf": "2", "g": "24"}
        for number, timestamp in enumerate(pts):
            if shots:
                color = ((220, 30, 30), (235, 235, 235), (20, 20, 20))[number // 20]
            else:
                color = (20 + number * 13 % 200, 30 + number * 29 % 200, 50 + number * 7 % 170)
            picture = Image.new("RGB", (128, 96), color)
            draw = ImageDraw.Draw(picture)
            if not shots:
                draw.rectangle((0, 48, 63, 95), fill=(250, number * 11 % 255, 20))
                draw.rectangle((64, 48, 127, 95), fill=(10, 40, 240))
            draw.text((8, 8), f"F{number}", fill="white")
            frame = av.VideoFrame.from_image(picture)
            frame.pts, frame.time_base = timestamp, time_base
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)


def decoded_truth(path: Path) -> list[dict]:
    result = []
    with av.open(str(path)) as container:
        for index, frame in enumerate(container.decode(video=0)):
            result.append({
                "frame_index": index,
                "pts": frame.pts,
                "time_base": Fraction(frame.time_base),
                "source_seconds": float(frame.pts * frame.time_base),
                "image": frame.to_image().convert("RGB"),
                "picture_type": str(frame.pict_type),
            })
    if result:
        first_time = result[0]["source_seconds"]
        for entry in result:
            entry["seconds"] = entry["source_seconds"] - first_time
    return result


@unittest.skipIf(MEDIA_IMPORT_ERROR is not None, f"Media integration dependencies unavailable: {MEDIA_IMPORT_ERROR}")
class VideoObservationMediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.is_file():
            raise RuntimeError(f"Missing video observation CLI: {SCRIPT}")
        if "ffv1" not in av.codec.codecs_available:
            if REQUIRE_MEDIA:
                raise RuntimeError("The media CI requires the FFV1 fixture encoder")
            raise unittest.SkipTest("FFV1 fixture encoder is unavailable")
        cls.fixture_temp = tempfile.TemporaryDirectory(prefix="video-observe-media-")
        cls.fixture_dir = Path(cls.fixture_temp.name) / "含 空格"
        cls.fixture_dir.mkdir()
        cls.cfr = cls.fixture_dir / "numbered cfr.mkv"
        cls.vfr = cls.fixture_dir / "numbered vfr.mkv"
        cls.offset = cls.fixture_dir / "nonzero pts.mkv"
        cls.shots = cls.fixture_dir / "three shots.mkv"
        make_clip(cls.cfr, [index * 100 for index in range(10)])
        make_clip(cls.vfr, [0, 100, 350, 600, 700, 950])
        make_clip(cls.offset, [2000, 2100, 2350, 2600, 2700])
        make_clip(cls.shots, [index * 100 for index in range(60)], shots=True)
        cls.sources = [cls.cfr, cls.vfr, cls.offset, cls.shots]
        cls.source_digests = {path: digest(path) for path in cls.sources}

    @classmethod
    def tearDownClass(cls):
        cls.fixture_temp.cleanup()

    def setUp(self):
        self.work_temp = tempfile.TemporaryDirectory(prefix="video-observe-output-")
        self.work = Path(self.work_temp.name)

    def tearDown(self):
        for path, initial in self.source_digests.items():
            self.assertEqual(digest(path), initial, f"Command changed its source: {path.name}")
        self.work_temp.cleanup()

    def run_cli(self, *arguments, success=True):
        env = os.environ.copy()
        env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            capture_output=True, encoding="utf-8", env=env, timeout=90,
        )
        try:
            value = json.loads(completed.stdout)
        except ValueError as exc:
            self.fail(f"CLI returned invalid JSON ({exc}): {completed.stdout!r}; stderr={completed.stderr!r}")
        if success:
            self.assertEqual(completed.returncode, 0, f"CLI failed: {value}; stderr={completed.stderr}")
        else:
            self.assertNotEqual(completed.returncode, 0, "Invalid request unexpectedly succeeded")
            self.assertIs(value.get("ok"), False)
            self.assertTrue(value.get("error", {}).get("code"))
        return value

    def window(self, video, *, start=0, end=1, fps=0, folder="window"):
        output = self.work / folder
        self.run_cli("window", "--video", video, "--start", start, "--end", end,
                     "--fps", fps, "--output", output)
        manifest_path = output / "manifest.json"
        self.assertTrue(manifest_path.is_file())
        return manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))

    def assert_export_matches(self, manifest, video):
        truth = decoded_truth(video)
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["source"]["sha256"], digest(video))
        self.assertEqual(manifest["coverage"]["observation_status"], "not_observed")
        for entry in manifest["frames"]:
            actual = truth[entry["frame_index"]]
            self.assertEqual(entry["pts"], actual["pts"])
            self.assertEqual(Fraction(entry["time_base"]), actual["time_base"])
            self.assertAlmostEqual(entry["source_seconds"], actual["source_seconds"], places=9)
            self.assertAlmostEqual(entry["seconds"], actual["seconds"], places=9)
            path = Path(entry["image_path"])
            self.assertEqual(entry["image_sha256"], digest(path))
            with Image.open(path) as exported:
                self.assertIsNone(ImageChops.difference(exported.convert("RGB"), actual["image"]).getbbox())
        selected_ids = {entry["id"] for entry in manifest["frames"]}
        for view in manifest["views"]:
            self.assertTrue(Path(view["image_path"]).is_file())
            self.assertTrue(set(view["frame_ids"]).issubset(selected_ids))
        return truth

    def test_inspect_reports_actual_timeline_without_observation_claim(self):
        output = self.work / "metadata.json"
        inspected = self.run_cli("inspect", "--video", self.offset, "--output", output)
        self.assertEqual(inspected["kind"], "inspect")
        self.assertEqual(inspected["source"]["sha256"], digest(self.offset))
        self.assertEqual(inspected["source"]["dimensions"], [128, 96])
        self.assertEqual(inspected["source"]["start_pts"], 2000)
        self.assertEqual(inspected["coverage"]["frames_decoded"], 5)
        self.assertEqual(inspected["coverage"]["observation_status"], "not_observed")
        self.assertEqual(inspected["frames"], [])
        self.assertEqual(inspected["views"], [])
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), inspected)

    def test_cfr_window_is_half_open_and_pixels_match_source(self):
        _, manifest = self.window(self.cfr, start=0.2, end=0.6)
        self.assertEqual([entry["frame_index"] for entry in manifest["frames"]], [2, 3, 4, 5])
        self.assert_export_matches(manifest, self.cfr)

    def test_vfr_uses_actual_timestamps_instead_of_average_rate(self):
        _, manifest = self.window(self.vfr, start=0.1, end=0.7)
        self.assertEqual([entry["frame_index"] for entry in manifest["frames"]], [1, 2, 3])
        self.assert_export_matches(manifest, self.vfr)
        self.assertAlmostEqual(manifest["frames"][1]["seconds"], 0.35, places=9)

    def test_nonzero_pts_keeps_source_time_and_relative_time(self):
        _, manifest = self.window(self.offset, start=0.1, end=0.7)
        self.assertEqual(manifest["source"]["start_pts"], 2000)
        self.assertEqual([entry["frame_index"] for entry in manifest["frames"]], [1, 2, 3])
        self.assert_export_matches(manifest, self.offset)
        self.assertAlmostEqual(manifest["frames"][0]["source_seconds"], 2.1, places=9)
        self.assertAlmostEqual(manifest["frames"][0]["seconds"], 0.1, places=9)

    def test_sampling_above_native_rate_never_duplicates_a_frame(self):
        _, manifest = self.window(self.cfr, fps=100)
        indices = [entry["frame_index"] for entry in manifest["frames"]]
        self.assertEqual(indices, list(range(10)))
        self.assertEqual(len(indices), len(set(indices)))
        self.assert_export_matches(manifest, self.cfr)

    def test_four_fps_request_records_actual_selected_source_frames(self):
        _, manifest = self.window(self.cfr, fps=4)
        selected_times = [entry["seconds"] for entry in manifest["frames"]]
        self.assertTrue(3 <= len(selected_times) <= 5)
        self.assertEqual(selected_times, sorted(selected_times))
        self.assert_export_matches(manifest, self.cfr)

    def test_overview_covers_each_detected_shot_with_source_images(self):
        output = self.work / "overview"
        self.run_cli("overview", "--video", self.shots, "--output", output)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assert_export_matches(manifest, self.shots)
        indices = {entry["frame_index"] for entry in manifest["frames"]}
        # Three abrupt, two-second shots. Verify endpoints and a middle image,
        # not a particular rounding choice for an even-length midpoint.
        for first, end in ((0, 20), (20, 40), (40, 60)):
            self.assertIn(first, indices)
            self.assertIn(end - 1, indices)
            self.assertTrue({first + 9, first + 10} & indices)
        self.assertEqual(len(indices), 9)

    def test_crop_matches_pixels_and_keeps_full_frame_context(self):
        parent_path, parent = self.window(self.cfr, start=0.2, end=0.3)
        selected = parent["frames"][0]
        output = self.work / "crop"
        self.run_cli("crop", "--manifest", parent_path, "--frame-id", selected["id"],
                     "--box", "0,0,500,1000", "--output", output)
        cropped = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(cropped["source"]["sha256"], parent["source"]["sha256"])
        views = [view for view in cropped["views"] if view["kind"] == "crop"]
        self.assertEqual(len(views), 1)
        view = views[0]
        self.assertEqual(view["frame_ids"], [selected["id"]])
        self.assertEqual(Path(view["context_image_path"]), Path(selected["image_path"]))
        self.assertEqual(view["box_pixels"], [0, 0, 64, 96])
        with Image.open(selected["image_path"]) as original, Image.open(view["image_path"]) as actual:
            expected = original.convert("RGB").crop((0, 0, 64, 96))
            self.assertIsNone(ImageChops.difference(actual.convert("RGB"), expected).getbbox())
        self.assertEqual(cropped["coverage"]["observation_status"], "not_observed")

    def test_existing_output_is_refused_without_changing_manifest(self):
        manifest_path, _ = self.window(self.cfr)
        before = manifest_path.read_bytes()
        self.run_cli("window", "--video", self.cfr, "--start", 0, "--end", 1,
                     "--fps", 4, "--output", manifest_path.parent, success=False)
        self.assertEqual(manifest_path.read_bytes(), before)

    def test_crop_rejects_changed_exported_pixels(self):
        manifest_path, manifest = self.window(self.cfr, start=0.2, end=0.3)
        entry = manifest["frames"][0]
        image_path = Path(entry["image_path"])
        with Image.open(image_path) as original:
            modified = original.convert("RGB")
        modified.putpixel((0, 0), (1, 2, 3))
        modified.save(image_path)
        self.run_cli("crop", "--manifest", manifest_path, "--frame-id", entry["id"],
                     "--box", "0,0,500,1000", "--output", self.work / "tampered", success=False)

    def test_crop_rejects_invalid_region(self):
        manifest_path, manifest = self.window(self.cfr, start=0.2, end=0.3)
        self.run_cli("crop", "--manifest", manifest_path, "--frame-id", manifest["frames"][0]["id"],
                     "--box", "800,0,100,1000", "--output", self.work / "invalid region", success=False)

    def test_empty_window_and_unknown_frame_fail_without_claiming_observation(self):
        self.run_cli("window", "--video", self.cfr, "--start", 5, "--end", 6,
                     "--output", self.work / "empty", success=False)
        manifest_path, _ = self.window(self.cfr)
        self.run_cli("crop", "--manifest", manifest_path, "--frame-id", "unknown",
                     "--box", "0,0,500,1000", "--output", self.work / "bad crop", success=False)
        self.assertFalse((manifest_path.parent / "observations.jsonl").exists())

    def test_note_rejects_unseen_view_and_only_appends_claimed_method(self):
        manifest_path, manifest = self.window(self.cfr)
        journal = manifest_path.parent / "observations.jsonl"
        self.assertFalse(journal.exists())
        self.run_cli("note", "--manifest", manifest_path, "--view-ids", "not-a-view",
                     "--observer", "synthetic-test", "--method", "static_sequence",
                     "--text", "Synthetic observation.", success=False)
        self.assertFalse(journal.exists())
        view_id = manifest["views"][0]["id"]
        note = self.run_cli("note", "--manifest", manifest_path, "--view-ids", view_id,
                            "--observer", "synthetic-test", "--method", "static_sequence",
                            "--kind", "observation", "--event-id", "E1",
                            "--text", "Numbered pattern changes; no real acting was inspected.")
        stored = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["view_ids"], [view_id])
        self.assertEqual(stored[0]["source_sha256"], manifest["source"]["sha256"])
        self.assertEqual(stored[0]["method"], "static_sequence")
        self.assertEqual(stored[0]["claim_kind"], "observation")
        self.assertEqual(stored[0]["event_id"], "E1")
        self.assertIs(stored[0]["observer_attested"], True)
        self.assertEqual(stored[0]["observation_status"], "self_reported")
        self.assertEqual(note["method"], "static_sequence")
        # Saving a self-reported observation is not automatic perceptual proof.
        saved_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_manifest["coverage"]["observation_status"], "not_observed")

    def test_b_frames_export_in_display_order_with_matching_pixels(self):
        if "libx264" not in av.codec.codecs_available:
            if REQUIRE_MEDIA:
                self.fail("The media CI requires the libx264 fixture encoder")
            self.skipTest("libx264 is unavailable; B-frame integration case was not run")
        path = self.work / "b frames.mp4"
        make_clip(path, [index * 100 for index in range(24)], codec="libx264")
        with av.open(str(path)) as container:
            packets = [packet for packet in container.demux(video=0) if packet.pts is not None]
        if not any(packet.dts is not None and packet.pts != packet.dts for packet in packets):
            if REQUIRE_MEDIA:
                self.fail("The media CI requires a fixture with reordered B-frame packets")
            self.skipTest("Encoder produced no reordered packets; B-frame case was not exercised")
        initial = digest(path)
        _, manifest = self.window(path, start=0.2, end=1.7)
        self.assertEqual([frame["frame_index"] for frame in manifest["frames"]], list(range(2, 17)))
        self.assert_export_matches(manifest, path)
        self.assertEqual(digest(path), initial)


if __name__ == "__main__":
    unittest.main()
