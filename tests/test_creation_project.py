"""Black-box project/source tests with original temporary text fixtures.

These tests exercise persistence, provenance and source boundaries. They do not
score story quality or claim that tool delivery means an assistant read a novel.
All files are temporary; no private source, media, model or network is needed.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlencode, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/video-creation/scripts/project_tool.py"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class CreationProjectTests(unittest.TestCase):
    def setUp(self):
        if not SCRIPT.is_file():
            self.fail(f"Missing creation project CLI: {SCRIPT}")
        self.temporary = tempfile.TemporaryDirectory(prefix="creation-project-")
        self.work = Path(self.temporary.name) / "中文 空格"
        self.work.mkdir()
        self.project = self.work / "project"
        self.originals: dict[Path, bytes] = {}

    def tearDown(self):
        for path, content in self.originals.items():
            self.assertEqual(path.read_bytes(), content, f"A command changed its external source: {path.name}")
        self.temporary.cleanup()

    def cli(self, command, *arguments, project=None, success=True):
        env = os.environ.copy()
        env.update({"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        result = subprocess.run(
            [sys.executable, str(SCRIPT), command, "--project", str(project or self.project),
             *map(str, arguments)],
            capture_output=True, encoding="utf-8", timeout=20, env=env,
        )
        try:
            data = json.loads(result.stdout)
        except ValueError:
            self.fail(f"CLI did not return JSON: {result.stdout!r}; stderr={result.stderr!r}")
        if success:
            self.assertEqual(result.returncode, 0, f"CLI failed: {data}; stderr={result.stderr}")
            self.assertIs(data.get("ok"), True)
        else:
            self.assertNotEqual(result.returncode, 0, "Invalid operation unexpectedly succeeded")
            self.assertIs(data.get("ok"), False)
        return data

    def init(self, route="novel", project=None):
        return self.cli("init", "--route", route, "--title", "原创教学项目", project=project)

    def state(self, project=None):
        return json.loads(((project or self.project) / "creation-project.json").read_text(encoding="utf-8"))

    def original(self, name="source.txt", text=None, raw=None):
        path = self.work / name
        content = raw if raw is not None else (text or "第一章 开门\n她打开旧店门。\n第二章 回信\n同伴带来一封信。\n").encode("utf-8")
        path.write_bytes(content)
        self.originals[path] = content
        return path

    def add(self, path, source_id="S1", kind="novel", project=None):
        return self.cli("source", "--id", source_id, "--kind", kind, "--file", path, project=project)

    def registered_source(self, source_id="S1", project=None):
        return next(item for item in self.state(project)["sources"] if item["id"] == source_id)

    def index(self, source_id="S1", chunk_chars=256):
        result = self.cli("index", "--source", source_id, "--chunk-chars", chunk_chars)
        source = self.registered_source(source_id)
        path = self.project / source["index"]["path"]
        return path, json.loads(path.read_text(encoding="utf-8")), result

    def status_source(self, source_id="S1"):
        return next(item for item in self.cli("status")["sources"] if item["id"] == source_id)

    def artifact_file(self, text="第一版分析：只解释已读范围。"):
        path = self.project / "development" / "analysis.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def record(self, path, artifact_id="A1", stage="analysis", replace=False, success=True):
        arguments = ["--artifact-id", artifact_id, "--stage", stage, "--file", path,
                     "--source-ids", "S1", "--next-step", "继续写第二集"]
        if replace:
            arguments.append("--replace")
        return self.cli("record", *arguments, success=success)

    def test_routes_initialize_separately_and_keep_their_own_sources(self):
        projects = []
        for route in ("reference", "novel", "original"):
            with self.subTest(route=route):
                project = self.work / route
                self.init(route, project)
                source = self.original(f"{route}.txt", text=f"本文件只属于{route}路线。")
                self.add(source, project=project, kind="text")
                state = self.state(project)
                self.assertEqual(state["route"], route)
                self.assertEqual(len(state["sources"]), 1)
                self.assertEqual(state["sources"][0]["file"]["sha256"], digest(source.read_bytes()))
                projects.append(state)
        self.assertEqual(len({row["sources"][0]["file"]["sha256"] for row in projects}), 3)

    def test_repeat_init_refuses_to_replace_existing_state(self):
        self.init()
        self.add(self.original())
        path = self.project / "creation-project.json"
        initial = path.read_bytes()
        self.cli("init", "--route", "original", success=False)
        self.assertEqual(path.read_bytes(), initial)

    def test_registered_source_is_a_read_only_copy_and_duplicate_is_idempotent(self):
        self.init()
        source = self.original()
        self.add(source)
        registered = self.registered_source()
        copied = self.project / registered["file"]["path"]
        self.assertTrue(copied.is_relative_to(self.project / "inputs"))
        self.assertNotEqual(copied.resolve(), source.resolve())
        self.assertEqual(copied.read_bytes(), source.read_bytes())
        self.assertEqual(registered["file"]["sha256"], digest(source.read_bytes()))
        result = self.add(source)
        self.assertIs(result["idempotent"], True)
        self.assertEqual(len(self.state()["sources"]), 1)

    def test_same_source_id_with_changed_bytes_refuses_overwrite(self):
        self.init()
        self.add(self.original())
        old = self.registered_source()
        path = self.project / old["file"]["path"]
        initial = path.read_bytes()
        replacement = self.original("replacement.txt", text="完全不同的新版本。")
        self.cli("source", "--id", "S1", "--kind", "novel", "--file", replacement, success=False)
        self.assertEqual(path.read_bytes(), initial)
        self.assertEqual(self.registered_source()["file"]["sha256"], digest(initial))

    def test_bad_source_ids_never_become_paths(self):
        self.init()
        source = self.original()
        for bad_id in ("../outside", "a/b", "bad id", "角色", ".", "x" * 65):
            with self.subTest(source_id=bad_id):
                self.cli("source", "--id", bad_id, "--kind", "text", "--file", source, success=False)
        self.assertEqual(self.state()["sources"], [])
        self.assertFalse((self.work / "outside").exists())

    def test_link_only_is_not_read_video_and_tokens_are_not_saved(self):
        self.init("reference")
        secret = "private-value-" * 3
        query = urlencode({"xsec_token": secret, "share_id": "temporary-share", "access_token": secret})
        url = "https://example.invalid/video?" + query
        self.cli("source", "--id", "V1", "--kind", "video", "--url", url)
        registered = self.registered_source("V1")
        stored = (self.project / "creation-project.json").read_text(encoding="utf-8")
        self.assertNotIn(secret, stored)
        self.assertEqual(urlsplit(registered["url"]).query, "")
        self.assertFalse(registered.get("file"))
        state = self.cli("status")
        row = next(item for item in state["sources"] if item["id"] == "V1")
        self.assertNotEqual(row["status"], "ready")
        self.assertEqual(state["reads"]["valid_deliveries"], 0)
        self.cli("index", "--source", "V1", success=False)

    def test_youtube_video_id_survives_query_cleaning(self):
        self.init("reference")
        query = urlencode({"v": "demo_video_id", "token": "private-value-" * 3, "utm_source": "tracking"})
        self.cli("source", "--id", "YT", "--kind", "video", "--url", "https://www.youtube.com/watch?" + query)
        self.assertEqual(parse_qs(urlsplit(self.registered_source("YT")["url"]).query), {"v": ["demo_video_id"]})

    def test_link_registration_can_later_admit_a_file_under_the_same_id(self):
        self.init("reference")
        self.cli("source", "--id", "V1", "--kind", "video", "--url", "https://example.invalid/video")
        source = self.original("local-video.dat", raw=b"original synthetic placeholder; no decoder needed")
        self.add(source, source_id="V1", kind="video")
        self.assertEqual(len(self.state()["sources"]), 1)
        registered = self.registered_source("V1")
        self.assertEqual(registered["url"], "https://example.invalid/video")
        self.assertEqual((self.project / registered["file"]["path"]).read_bytes(), source.read_bytes())
        self.assertEqual(self.cli("status")["reads"]["valid_deliveries"], 0)

    def test_url_only_analysis_and_development_preserve_metadata_without_claiming_video_observation(self):
        self.init("reference")
        url = "https://example.invalid/unavailable-video"
        self.cli("source", "--id", "S1", "--kind", "video", "--url", url)
        path = self.artifact_file("Only the supplied URL is available; story, action and sound remain unobserved.")
        for stage in ("analysis", "development"):
            with self.subTest(stage=stage):
                result = self.record(path, artifact_id=stage, stage=stage)
                artifact = result["artifact"]
                self.assertEqual(artifact["source_refs"], [{
                    "source_id": "S1", "source_url": url, "evidence_kind": "url_metadata_only",
                }])
                self.assertEqual(artifact["media_acceptance"], "not_evaluated_by_record")
        status = self.cli("status")
        self.assertNotEqual(self.status_source()["status"], "ready")
        self.assertFalse(self.registered_source().get("file"))
        self.assertEqual(status["reads"]["valid_deliveries"], 0)
        self.assertEqual(self.state()["reads"], [])
        self.assertEqual(len(status["artifacts"]), 2)
        for artifact in status["artifacts"]:
            self.assertEqual(artifact["status"], "ready")
            self.assertEqual(artifact["source_evidence"], [{
                "source_id": "S1", "evidence_kind": "url_metadata_only", "scope": "metadata_only",
            }])
        self.cli("read", "--source", "S1", "--chunk", "C0001", success=False)

    def test_url_only_source_cannot_support_script_or_downstream_production_records(self):
        self.init("reference")
        self.cli("source", "--id", "S1", "--kind", "video", "--url", "https://example.invalid/video")
        path = self.artifact_file("A real local output file is not evidence that its linked source was acquired.")
        for stage in ("script", "assets", "storyboard", "production", "edit", "review"):
            with self.subTest(stage=stage):
                result = self.record(path, artifact_id=stage, stage=stage, success=False)
                self.assertEqual(result["error"]["code"], "SOURCE_MISSING")
        self.assertEqual(self.state()["artifacts"], [])
        self.assertEqual(self.cli("status")["analysis_artifacts"], [])
        self.assertFalse((self.project / "artifact-history").exists())

    def test_url_metadata_dependency_stays_metadata_after_file_attachment_and_detects_source_changes(self):
        self.init("reference")
        url = "https://example.invalid/original-video"
        self.cli("source", "--id", "S1", "--kind", "video", "--url", url)
        self.record(self.artifact_file("Source access is pending; this intake contains no observed video events."))
        old_refs = self.state()["artifacts"][0]["source_refs"]
        source = self.original("attached-video.dat", raw=b"newly acquired synthetic source; not decoded or watched")
        self.add(source, kind="video")
        status = self.cli("status")
        self.assertEqual(self.status_source()["status"], "ready")
        self.assertEqual(self.state()["artifacts"][0]["source_refs"], old_refs)
        self.assertEqual(status["artifacts"][0]["status"], "ready")
        self.assertEqual(status["artifacts"][0]["source_evidence"], [{
            "source_id": "S1", "evidence_kind": "url_metadata_only", "scope": "metadata_only",
        }])
        self.assertEqual(status["reads"]["valid_deliveries"], 0)

        # Simulate external record changes and require a fresh dependency check
        # in each process, rather than trusting the former metadata receipt.
        state_path = self.project / "creation-project.json"
        current_bytes = state_path.read_bytes()
        for change in ("changed_url", "removed_source"):
            with self.subTest(change=change):
                current = json.loads(current_bytes)
                if change == "changed_url":
                    current["sources"][0]["url"] = "https://example.invalid/different-video"
                else:
                    current["sources"] = []
                state_path.write_text(json.dumps(current, ensure_ascii=False), encoding="utf-8")
                status = self.cli("status")
                self.assertEqual(status["artifacts"][0]["status"], "stale")
                self.assertEqual(status["analysis_artifacts"], [])
        state_path.write_bytes(current_bytes)
        self.assertEqual(self.cli("status")["artifacts"][0]["status"], "ready")

    def test_chunks_reassemble_exact_utf8_bytes_bom_crlf_and_long_lines(self):
        self.init()
        text = "\ufeff第一章 初见\r\n" + "甲乙😀，保持原始换行。" * 70 + "\r\n第二章 同行\r\n" + "没有句号也要完整" * 80 + "\r\n"
        source = self.original(raw=text.encode("utf-8"))
        self.add(source)
        _, index, _ = self.index()
        self.assertTrue(index["has_utf8_bom"])
        self.assertEqual(index["raw_bytes"], len(source.read_bytes()))
        self.assertEqual(index["text_chars"], len(text))
        text_parts, byte_parts = [], []
        next_char = next_byte = 0
        for chunk in index["chunks"]:
            self.assertEqual(chunk["char_start"], next_char)
            self.assertEqual(chunk["byte_start"], next_byte)
            part = text[chunk["char_start"]:chunk["char_end"]]
            raw_part = source.read_bytes()[chunk["byte_start"]:chunk["byte_end"]]
            self.assertEqual(part.encode("utf-8"), raw_part)
            self.assertEqual(chunk["sha256"], digest(raw_part))
            self.assertEqual(chunk["line_start"], text.count("\n", 0, chunk["char_start"]) + 1)
            self.assertEqual(chunk["line_end"], text.count("\n", 0, max(chunk["char_start"], chunk["char_end"] - 1)) + 1)
            delivered = self.cli("read", "--source", "S1", "--chunk", chunk["id"])
            self.assertEqual(delivered["chunk"]["text"], part)
            self.assertEqual(delivered["delivery_status"], "tool_delivery_only")
            text_parts.append(part)
            byte_parts.append(raw_part)
            next_char, next_byte = chunk["char_end"], chunk["byte_end"]
        self.assertEqual("".join(text_parts), text)
        self.assertEqual(b"".join(byte_parts), source.read_bytes())
        self.assertEqual(next_byte, len(source.read_bytes()))
        self.assertEqual(self.cli("status")["analysis_artifacts"], [])

    def test_material_without_chapters_is_still_fully_indexed(self):
        self.init()
        source = self.original(text="只是正文，没有章节标题。🌿" * 150)
        self.add(source)
        _, index, _ = self.index()
        self.assertEqual(index["chapters"], [])
        self.assertGreater(len(index["chunks"]), 1)
        parts = [self.cli("read", "--source", "S1", "--chunk", part["id"])["chunk"]["text"]
                 for part in index["chunks"]]
        self.assertEqual("".join(parts).encode("utf-8"), source.read_bytes())

    def test_candidate_chapters_do_not_become_episodes_or_analysis(self):
        self.init()
        self.add(self.original(text="第一章 开门\n她开门。\n第二章 来客\n同伴进门。\n"))
        _, index, _ = self.index()
        self.assertEqual(len(index["chapters"]), 2)
        status = self.cli("status")
        self.assertEqual(status["artifacts"], [])
        self.assertEqual(status["analysis_artifacts"], [])
        self.assertEqual(status["reads"]["valid_deliveries"], 0)
        self.assertEqual(self.status_source()["index"]["undelivered_chunks"], [part["id"] for part in index["chunks"]])

    def test_same_line_same_size_source_edit_invalidates_old_reads_and_records(self):
        self.init()
        self.add(self.original(text="第一章 初见\n甲" + "共同线索" * 100 + "\n"))
        self.index()
        source = self.registered_source()
        copied = self.project / source["file"]["path"]
        before = copied.stat()
        raw = copied.read_bytes()
        changed = raw.replace("甲".encode(), "乙".encode(), 1)
        self.assertEqual(len(raw), len(changed))
        copied.write_bytes(changed)
        os.utime(copied, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertEqual(self.status_source()["status"], "stale")
        self.cli("read", "--source", "S1", "--chunk", "C0001", success=False)
        self.record(self.artifact_file(), success=False)
        self.assertEqual(self.state()["artifacts"], [])

    def test_changed_index_is_not_trusted_by_read_or_record(self):
        self.init()
        self.add(self.original())
        index_path, index, _ = self.index()
        index["chunks"][0]["char_end"] -= 1
        index_path.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(self.status_source()["index"]["status"], "stale")
        self.cli("read", "--source", "S1", "--chunk", "C0001", success=False)
        self.record(self.artifact_file(), success=False)

    def test_missing_input_is_reported_and_does_not_create_a_delivery(self):
        self.init()
        self.add(self.original())
        self.index()
        source = self.registered_source()
        (self.project / source["file"]["path"]).unlink()
        self.assertEqual(self.status_source()["status"], "missing")
        self.cli("read", "--source", "S1", "--chunk", "C0001", success=False)
        self.assertEqual(self.cli("status")["reads"]["valid_deliveries"], 0)

    def test_unknown_chunk_and_non_utf8_source_do_not_fake_analysis(self):
        self.init()
        self.add(self.original())
        self.index()
        self.cli("read", "--source", "S1", "--chunk", "C9999", success=False)
        binary = self.original("binary.txt", raw=b"\xff\xfe\x80\x81")
        self.add(binary, source_id="BINARY")
        self.cli("index", "--source", "BINARY", success=False)
        status = self.cli("status")
        self.assertEqual(status["reads"]["valid_deliveries"], 0)
        self.assertEqual(status["analysis_artifacts"], [])

    def test_restart_keeps_delivery_progress_without_claiming_analysis(self):
        self.init()
        self.add(self.original(text="某个普通段落，只有一位叙述者。" * 100))
        _, index, _ = self.index()
        first = index["chunks"][0]["id"]
        self.cli("read", "--source", "S1", "--chunk", first)
        # Every CLI invocation is a new process; status reconstructs from disk.
        status = self.cli("status")
        source = next(item for item in status["sources"] if item["id"] == "S1")
        self.assertEqual(source["index"]["tool_delivered_chunks"], [first])
        self.assertEqual(source["index"]["undelivered_chunks"], [part["id"] for part in index["chunks"][1:]])
        self.assertEqual(status["reads"]["delivery_status"], "tool_delivery_only")
        self.assertEqual(status["analysis_artifacts"], [])
        self.assertEqual(status["artifacts"], [])

    def test_artifacts_require_real_project_files_outside_inputs(self):
        self.init()
        self.add(self.original())
        self.index()
        source_copy = self.project / self.registered_source()["file"]["path"]
        external = self.original("not-a-project-artifact.md", text="外部文件不可登记成项目产物。")
        for path in (self.project / "missing.md", source_copy, external):
            with self.subTest(path=path.name):
                self.record(path, success=False)
        self.assertEqual(self.state()["artifacts"], [])

    def test_artifact_hash_change_is_stale_and_next_step_survives_restart(self):
        self.init()
        self.add(self.original())
        self.index()
        path = self.artifact_file()
        self.record(path)
        status = self.cli("status")
        row = next(item for item in status["artifacts"] if item["id"] == "A1")
        self.assertEqual(row["status"], "ready")
        self.assertEqual(status["next_step"], "继续写第二集")
        self.assertEqual(status["analysis_artifacts"], ["A1"])
        path.write_text("原产物已经被外部编辑。", encoding="utf-8")
        row = next(item for item in self.cli("status")["artifacts"] if item["id"] == "A1")
        self.assertEqual(row["status"], "stale")
        self.assertEqual(self.cli("status")["analysis_artifacts"], [])

    def test_replace_preserves_old_bytes_and_replay_does_not_duplicate_completion(self):
        self.init()
        self.add(self.original())
        self.index()
        path = self.artifact_file("第一版结果，保留原样。")
        first_bytes = path.read_bytes()
        self.record(path)
        repeated = self.record(path)
        self.assertIs(repeated["idempotent"], True)
        self.assertEqual(len(self.state()["artifacts"]), 1)
        path.write_text("第二版结果，有明确修订。", encoding="utf-8")
        self.record(path, success=False)
        self.record(path, replace=True)
        state = self.state()
        self.assertEqual(len(state["artifacts"]), 1)
        self.assertEqual(state["artifacts"][0]["version"], 2)
        self.assertEqual(len(state["artifact_history"]), 1)
        snapshots = [item for item in (self.project / "artifact-history").rglob("*") if item.is_file()]
        self.assertTrue(any(item.read_bytes() == first_bytes for item in snapshots))
        self.record(path)
        self.assertEqual(len(self.state()["artifact_history"]), 1)
        self.assertEqual(self.cli("status")["analysis_artifacts"], ["A1"])

    def test_bad_artifact_id_cannot_escape_history_or_register_metadata_as_work(self):
        self.init()
        self.add(self.original())
        self.index()
        artifact = self.artifact_file()
        self.record(artifact, artifact_id="../escape", success=False)
        self.record(self.project / "creation-project.json", success=False)
        self.assertEqual(self.state()["artifacts"], [])


if __name__ == "__main__":
    unittest.main()
