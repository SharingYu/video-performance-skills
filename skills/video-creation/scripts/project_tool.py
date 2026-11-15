#!/usr/bin/env python3
"""Local creation-project records and exact UTF-8 source locators.

No network, model, rendering, platform API, or semantic chapter analysis is
performed. Returning a text chunk is tool delivery, not proof of understanding.
The JSON files are this package's side records, not production-backend fields.
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from uuid import uuid4


PROJECT_FILE = "creation-project.json"
ROUTES = ("reference", "novel", "original")
STAGES = ("analysis", "development", "script", "assets", "storyboard", "production", "edit", "review")
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
HEADING = re.compile(
    r"^(?:#{1,6}\s+\S|第[零〇一二三四五六七八九十百千万两0-9]+[章节卷部回集]|"
    r"(?:chapter|part|book|volume)\s+(?:\d+|[ivxlcdm]+)\b|(?:序章|楔子|尾声|终章)(?:\s|$))", re.I
)


class ProjectError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Argument errors must not echo a mistakenly supplied signed URL.
        raise ProjectError("INVALID_ARGUMENT", "Invalid command arguments; use --help for syntax.")


def now():
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(value: bytes):
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def valid_id(value: str):
    if not SAFE_ID.fullmatch(value):
        raise ProjectError("INVALID_ID", "IDs must use 1-64 ASCII letters, digits, underscores or hyphens.")
    return value


def contained(root: Path, value, *, must_exist=False):
    if not isinstance(value, (str, Path)):
        raise ProjectError("INVALID_PATH", "A project path must be a string.")
    candidate = Path(value).expanduser()
    candidate = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if not candidate.is_relative_to(root):
        raise ProjectError("PATH_ESCAPE", "The managed path must remain inside its project.")
    if must_exist and not candidate.is_file():
        raise ProjectError("FILE_MISSING", "A required project file is missing.")
    return candidate


def relative(root, path):
    return contained(root, path).relative_to(root).as_posix()


def atomic_json(path: Path, value, *, new=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if new and path.exists():
        raise ProjectError("OUTPUT_EXISTS", "An existing record will not be overwritten.")
    temporary = path.with_name(path.name + "." + uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write((json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def json_file(path):
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def project_lock(root: Path):
    lock = contained(root, ".creation-project.lock")
    with lock.open("a+b") as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ProjectError("PROJECT_BUSY", "Another command owns this project's write lock.") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def load_project(root: Path):
    path = contained(root, PROJECT_FILE, must_exist=True)
    value = json_file(path)
    if (not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("route") not in ROUTES
            or any(not isinstance(value.get(key), list) for key in ("sources", "reads", "artifacts"))):
        raise ProjectError("INVALID_PROJECT", "Expected a schema_version=1 creation-project record.")
    for group in ("sources", "artifacts"):
        ids = []
        for item in value[group]:
            if not isinstance(item, dict):
                raise ProjectError("INVALID_PROJECT", "Source and artifact records must be objects.")
            ids.append(valid_id(item.get("id", "")))
        if len(ids) != len(set(ids)):
            raise ProjectError("INVALID_PROJECT", "Duplicate source or artifact IDs are not allowed.")
    return value


def save_project(root, project):
    project["updated_at"] = now()
    atomic_json(contained(root, PROJECT_FILE), project)


def find_source(project, source_id):
    valid_id(source_id)
    matches = [row for row in project["sources"] if row["id"] == source_id]
    if not matches:
        raise ProjectError("UNKNOWN_SOURCE", "Register this source before using it.")
    return matches[0]


def file_state(root, record):
    if not record:
        return {"status": "missing", "reason": "no_local_file"}
    try:
        path = contained(root, record["path"])
        if not path.is_file():
            return {"status": "missing", "reason": "file_missing"}
        if sha_file(path) != record.get("sha256"):
            return {"status": "stale", "reason": "hash_changed"}
        return {"status": "ready"}
    except (ProjectError, KeyError, TypeError, OSError):
        return {"status": "stale", "reason": "invalid_or_escaped_file_reference"}


def verified_source(root, source, *, text=False):
    record = source.get("file")
    state = file_state(root, record)
    if state["status"] != "ready":
        raise ProjectError("SOURCE_" + state["status"].upper(), "The registered input is missing or changed; old source locators cannot be used.")
    path = contained(root, record["path"], must_exist=True)
    if not path.is_relative_to(root / "inputs"):
        raise ProjectError("INVALID_SOURCE", "Registered input copies must remain inside inputs.")
    if not text:
        return path
    if source.get("kind") not in ("novel", "text") or path.suffix.lower() not in (".txt", ".md", ".markdown"):
        raise ProjectError("UNSUPPORTED_TEXT", "Indexing accepts UTF-8 TXT/MD novel or text inputs only.")
    raw = path.read_bytes()
    if sha_bytes(raw) != record["sha256"]:
        raise ProjectError("SOURCE_STALE", "The input changed during reading.")
    try:
        # Preserve a BOM as U+FEFF and CRLF verbatim so every original byte has
        # a locator; no silent decoding, newline conversion or normalization.
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectError("NOT_UTF8", "The input must be UTF-8; convert a separate copy before registration.") from exc
    return raw, decoded


def clean_url(value: str):
    try:
        if any(ord(ch) < 33 for ch in value):
            raise ValueError()
        parts = urlsplit(value)
        if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
            raise ValueError()
        host = parts.hostname.encode("idna").decode("ascii").lower()
        netloc = "[" + host + "]" if ":" in host else host
        if parts.port:
            netloc += ":" + str(parts.port)
        query = ""
        if host in ("youtube.com", "www.youtube.com", "m.youtube.com") and parts.path == "/watch":
            video_id = parse_qs(parts.query).get("v", [""])[0]
            if re.fullmatch(r"[A-Za-z0-9_-]{1,128}", video_id):
                query = urlencode({"v": video_id})
        return urlunsplit((parts.scheme.lower(), netloc, parts.path or "", query, ""))
    except (ValueError, UnicodeError) as exc:
        raise ProjectError("INVALID_URL", "Use a valid http(s) source URL; credentials, query tokens and fragments are not stored.") from exc


def copy_frozen(source: Path, target: Path):
    """Copy bytes without writing the source; accept an identical prior copy."""
    before = source.stat()
    expected = sha_file(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.is_file() and sha_file(target) == expected:
            return {"sha256": expected, "bytes": before.st_size}
        raise ProjectError("OUTPUT_EXISTS", "A frozen destination already contains different bytes.")
    temporary = target.with_name(target.name + "." + uuid4().hex + ".tmp")
    try:
        digest, count = hashlib.sha256(), 0
        with source.open("rb") as incoming, temporary.open("xb") as outgoing:
            for block in iter(lambda: incoming.read(1024 * 1024), b""):
                outgoing.write(block)
                digest.update(block)
                count += len(block)
            outgoing.flush()
            os.fsync(outgoing.fileno())
        after = source.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or digest.hexdigest() != expected:
            raise ProjectError("SOURCE_CHANGED", "The file changed while being frozen; use a stable file version.")
        os.replace(temporary, target)
        return {"sha256": expected, "bytes": count}
    finally:
        temporary.unlink(missing_ok=True)


def line_starts(text):
    return [0] + [match.end() for match in re.finditer(r"\r\n|\r|\n", text)]


def make_index(source, raw: bytes, text: str, chunk_chars: int):
    starts = line_starts(text)
    chunks, byte_cursor = [], 0
    for start in range(0, len(text), chunk_chars):
        end = min(start + chunk_chars, len(text))
        block = text[start:end].encode("utf-8")
        chunks.append({
            "id": f"C{len(chunks) + 1:04d}", "char_start": start, "char_end": end,
            "byte_start": byte_cursor, "byte_end": byte_cursor + len(block),
            "line_start": bisect_right(starts, start),
            "line_end": bisect_right(starts, end - 1), "sha256": sha_bytes(block),
        })
        byte_cursor += len(block)
    chapters, byte_cursor = [], 0
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        line = text[start:end]
        title = line.rstrip("\r\n").lstrip("\ufeff")
        if HEADING.match(title):
            chapters.append({"title": title[:200], "title_truncated": len(title) > 200,
                             "line": i + 1, "char_start": start, "byte_start": byte_cursor})
        byte_cursor += len(line.encode("utf-8"))
    return {
        "schema_version": 1, "source_id": source["id"], "source_sha256": source["file"]["sha256"],
        "chunk_chars": chunk_chars, "text_chars": len(text), "raw_bytes": len(raw),
        "has_utf8_bom": raw.startswith(b"\xef\xbb\xbf"),
        "line_numbering": "1-based inclusive; char/byte half-open",
        "coordinate_origin": "Original UTF-8 bytes and decoded characters, including BOM and original newline characters.",
        "chapters": chapters, "chunks": chunks,
        "boundary": "Mechanical chunks and candidate headings only; not semantic reading, episodes, or adaptation approval.",
    }


def verified_index(root, source, *, payload=None):
    raw, text = payload if payload is not None else verified_source(root, source, text=True)
    record = source.get("index")
    state = file_state(root, record)
    if state["status"] != "ready":
        raise ProjectError("INDEX_" + state["status"].upper(), "The source index is missing or changed; rebuild under a new source identity if necessary.")
    path = contained(root, record["path"], must_exist=True)
    if not path.is_relative_to(root / "source-analysis" / source["id"]):
        raise ProjectError("INVALID_INDEX", "The index must remain inside its source-analysis directory.")
    index = json_file(path)
    size = index.get("chunk_chars") if isinstance(index, dict) else None
    if type(size) is not int or not 256 <= size <= 20000:
        raise ProjectError("INVALID_INDEX", "Invalid chunk size in the stored index.")
    expected = make_index(source, raw, text, size)
    # Reconstruct all locators to reject gaps, repeated spans, byte splits,
    # duplicate IDs and altered headings even after a manually edited ledger.
    if index != expected or record.get("source_sha256") != source["file"]["sha256"] or record.get("chunk_chars") != size:
        raise ProjectError("INVALID_INDEX", "Stored source locators do not exactly cover the frozen UTF-8 input.")
    return index, raw, text


def source_refs(root, project, ids, *, allow_url_only=False):
    refs = []
    for source_id in ids:
        source = find_source(project, source_id)
        if allow_url_only and not source.get("file") and source.get("url"):
            if clean_url(source["url"]) != source["url"]:
                raise ProjectError("INVALID_SOURCE_URL", "The registered source URL is no longer canonical.")
            refs.append({"source_id": source_id, "source_url": source["url"],
                         "evidence_kind": "url_metadata_only"})
            continue
        verified_source(root, source)
        row = {"source_id": source_id, "source_sha256": source["file"]["sha256"]}
        if source.get("index"):
            verified_index(root, source)
            row["index_sha256"] = source["index"]["sha256"]
        refs.append(row)
    return refs


def init_command(args, root):
    if (root / PROJECT_FILE).exists():
        raise ProjectError("PROJECT_EXISTS", "The project already exists; its state will not be replaced.")
    project = {"schema_version": 1, "route": args.route, "title": args.title or root.name,
               "created_at": now(), "sources": [], "reads": [], "artifacts": [],
               "artifact_history": [], "next_step": "Register and inspect source material before developing the chosen route.",
               "boundary": "Package side records only; no model understanding, rendering, media approval or backend API mutation is performed."}
    atomic_json(contained(root, PROJECT_FILE), project, new=True)
    return {"project": project}


def source_command(args, root, project):
    source_id = valid_id(args.id)
    if not args.file and not args.url:
        raise ProjectError("INVALID_ARGUMENT", "Provide a local file, a source URL, or both.")
    canonical_url = clean_url(args.url) if args.url else None
    existing = next((item for item in project["sources"] if item["id"] == source_id), None)
    if existing and (existing["kind"] != args.kind or (args.url and existing.get("url") != canonical_url)):
        raise ProjectError("SOURCE_CONFLICT", "Source kind and registered URL are immutable; use a new source ID.")
    record = existing or {"id": source_id, "kind": args.kind, "registered_at": now()}
    if not existing and canonical_url:
        record["url"] = canonical_url
    if args.file:
        original = Path(args.file).expanduser().resolve()
        if not original.is_file():
            raise ProjectError("FILE_MISSING", "The supplied local source file does not exist.")
        digest = sha_file(original)
        if record.get("file"):
            if record["file"]["sha256"] != digest:
                raise ProjectError("SOURCE_CONFLICT", "A source ID cannot acquire different bytes; use a new ID for a new version.")
            verified_source(root, record)
            return {"source": record, "idempotent": True}
        suffix = original.suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
            suffix = ".txt" if args.kind in ("novel", "text") and not suffix else ".bin"
        target = contained(root, Path("inputs") / source_id / ("source" + suffix))
        frozen = copy_frozen(original, target)
        record["file"] = {"path": relative(root, target), **frozen}
        record["original_filename"] = original.name
    elif existing:
        return {"source": record, "idempotent": True}
    if not existing:
        project["sources"].append(record)
    save_project(root, project)
    return {"source": record, "idempotent": False, "acquisition": "local_copy" if args.file else "url_metadata_only_not_downloaded"}


def index_command(args, root, project):
    if not 256 <= args.chunk_chars <= 20000:
        raise ProjectError("INVALID_ARGUMENT", "chunk-chars must be between 256 and 20000.")
    source = find_source(project, args.source)
    payload = verified_source(root, source, text=True)
    if source.get("index"):
        index, _, _ = verified_index(root, source, payload=payload)
        if index["chunk_chars"] != args.chunk_chars:
            raise ProjectError("INDEX_CONFLICT", "An existing index uses another chunk size; use a new source ID instead of overwriting it.")
        return {"index": index, "index_path": str(contained(root, source["index"]["path"])), "idempotent": True}
    index = make_index(source, *payload, args.chunk_chars)
    path = contained(root, Path("source-analysis") / source["id"] / "index.json")
    if path.exists():
        if json_file(path) != index:
            raise ProjectError("INDEX_CONFLICT", "Unregistered index bytes differ; use a new source ID.")
    else:
        atomic_json(path, index, new=True)
    source["index"] = {"path": relative(root, path), "sha256": sha_file(path),
                       "source_sha256": source["file"]["sha256"], "chunk_chars": args.chunk_chars,
                       "chunk_count": len(index["chunks"])}
    save_project(root, project)
    return {"index": index, "index_path": str(path), "idempotent": False}


def read_command(args, root, project):
    source = find_source(project, args.source)
    index, raw, _ = verified_index(root, source)
    chunks = [item for item in index["chunks"] if item["id"] == args.chunk]
    if len(chunks) != 1:
        raise ProjectError("UNKNOWN_CHUNK", "Select exactly one actual chunk ID from the current index.")
    chunk = chunks[0]
    block = raw[chunk["byte_start"]:chunk["byte_end"]]
    if sha_bytes(block) != chunk["sha256"]:
        raise ProjectError("CHUNK_STALE", "The selected chunk no longer matches its frozen locator.")
    text = block.decode("utf-8")
    project["reads"].append({"source_id": source["id"], "source_sha256": source["file"]["sha256"],
                              "index_sha256": source["index"]["sha256"], "chunk_id": chunk["id"],
                              "delivery_status": "tool_delivery_only", "delivered_at": now()})
    save_project(root, project)
    return {"source_id": source["id"], "chunk": {**chunk, "text": text},
            "locator": {"source_id": source["id"], "source_sha256": source["file"]["sha256"], **chunk},
            "delivery_status": "tool_delivery_only", "semantic_reading": "not_verified"}


def record_command(args, root, project):
    artifact_id = valid_id(args.artifact_id)
    path = contained(root, args.file, must_exist=True)
    rel = path.relative_to(root)
    if rel.parts[0] in ("inputs", "source-analysis", "artifact-history") or rel.as_posix() in (PROJECT_FILE, ".creation-project.lock"):
        raise ProjectError("RESERVED_ARTIFACT", "Register actual work outside managed input, index, history and project-record paths.")
    ids = list(dict.fromkeys(item.strip() for item in (args.source_ids or "").split(",") if item.strip()))
    refs = source_refs(root, project, ids, allow_url_only=args.stage in ("analysis", "development"))
    digest = sha_file(path)
    existing = next((item for item in project["artifacts"] if item["id"] == artifact_id), None)
    if (existing and existing["file"]["sha256"] == digest and existing["file"]["path"] == rel.as_posix()
            and existing["stage"] == args.stage and existing.get("source_refs", []) == refs):
        if file_state(root, existing.get("snapshot"))["status"] != "ready":
            raise ProjectError("HISTORY_STALE", "The frozen artifact snapshot is missing or changed.")
        if args.next_step is not None:
            project["next_step"] = args.next_step
            save_project(root, project)
        return {"artifact": existing, "idempotent": True}
    if existing and not args.replace:
        raise ProjectError("ARTIFACT_CONFLICT", "The artifact changed; use a new ID or explicit --replace to preserve its old version.")
    if existing and file_state(root, existing.get("snapshot"))["status"] != "ready":
        raise ProjectError("HISTORY_STALE", "A replacement cannot discard missing or changed historical snapshot bytes.")
    version = existing["version"] + 1 if existing else 1
    snapshot = contained(root, Path("artifact-history") / artifact_id / f"v{version:04d}" / path.name)
    frozen = copy_frozen(path, snapshot)
    if frozen["sha256"] != digest:
        raise ProjectError("ARTIFACT_CHANGED", "The artifact changed during registration.")
    record = {"id": artifact_id, "version": version, "stage": args.stage,
              "file": {"path": rel.as_posix(), **frozen},
              "snapshot": {"path": relative(root, snapshot), **frozen},
              "source_refs": refs, "recorded_at": now(), "media_acceptance": "not_evaluated_by_record"}
    if args.next_step is not None:
        project["next_step"] = args.next_step
        record["next_step"] = args.next_step
    if existing:
        project.setdefault("artifact_history", []).append(existing)
        project["artifacts"] = [row if row["id"] != artifact_id else record for row in project["artifacts"]]
    else:
        project["artifacts"].append(record)
    save_project(root, project)
    return {"artifact": record, "idempotent": False}


def status_command(args, root, project):
    rows, indices = [], {}
    for source in project["sources"]:
        state = file_state(root, source.get("file"))
        if state["status"] == "ready":
            try:
                verified_source(root, source)
            except (ProjectError, KeyError, TypeError, OSError):
                state = {"status": "stale", "reason": "invalid_input_copy_reference"}
        row = {"id": source["id"], "kind": source["kind"], **state}
        index_state = {"status": "missing", "reason": "not_indexed", "chunk_count": 0,
                       "tool_delivered_chunks": [], "undelivered_chunks": []}
        if source.get("index"):
            try:
                index, _, _ = verified_index(root, source)
                ids = [item["id"] for item in index["chunks"]]
                delivered = {item.get("chunk_id") for item in project["reads"]
                             if item.get("delivery_status") == "tool_delivery_only" and item.get("source_id") == source["id"]
                             and item.get("source_sha256") == source["file"]["sha256"]
                             and item.get("index_sha256") == source["index"]["sha256"]}
                index_state = {"status": "ready", "chunk_count": len(ids),
                               "tool_delivered_chunks": [item for item in ids if item in delivered],
                               "undelivered_chunks": [item for item in ids if item not in delivered]}
                indices[source["id"]] = {"ids": set(ids), "sha256": source["index"]["sha256"], "source_sha256": source["file"]["sha256"]}
            except (ProjectError, ValueError, KeyError, TypeError, OSError) as exc:
                index_file_state = file_state(root, source.get("index"))
                index_state.update({"status": "missing" if index_file_state["status"] == "missing" else "stale",
                                    "reason": getattr(exc, "code", "invalid_index")})
        row["index"] = index_state
        rows.append(row)
    artifacts = []
    for artifact in project["artifacts"]:
        evidence = [{"source_id": ref.get("source_id"),
                     "evidence_kind": "url_metadata_only" if ref.get("evidence_kind") == "url_metadata_only" else "local_file",
                     "scope": "metadata_only" if ref.get("evidence_kind") == "url_metadata_only" else "frozen_input"}
                    for ref in artifact.get("source_refs", [])]
        state = file_state(root, artifact.get("file"))
        if state["status"] == "ready":
            rel = Path(artifact["file"]["path"])
            actual = contained(root, rel).relative_to(root)
            if actual.parts[0] in ("inputs", "source-analysis", "artifact-history") or actual.as_posix() in (PROJECT_FILE, ".creation-project.lock"):
                state = {"status": "stale", "reason": "reserved_artifact_reference"}
        if state["status"] == "ready" and file_state(root, artifact.get("snapshot"))["status"] != "ready":
            state = {"status": "stale", "reason": "snapshot_missing_or_changed"}
        if state["status"] == "ready":
            try:
                for ref in artifact.get("source_refs", []):
                    source = find_source(project, ref["source_id"])
                    if ref.get("evidence_kind") == "url_metadata_only":
                        if (artifact["stage"] not in ("analysis", "development")
                                or source.get("url") != ref.get("source_url")
                                or not ref.get("source_url")
                                or clean_url(ref["source_url"]) != ref["source_url"]):
                            raise ProjectError("SOURCE_STALE", "The URL metadata dependency changed or is invalid for this stage.")
                        # A subsequently attached file does not upgrade this
                        # document's original metadata-only evidence scope.
                        continue
                    verified_source(root, source)
                    if ref["source_sha256"] != source["file"]["sha256"]:
                        raise ProjectError("SOURCE_STALE", "Source hash changed.")
                    if ref.get("index_sha256"):
                        verified_index(root, source)
                        if ref["index_sha256"] != source["index"]["sha256"]:
                            raise ProjectError("INDEX_STALE", "Index identity changed.")
            except (ProjectError, KeyError, TypeError, ValueError, OSError):
                state = {"status": "stale", "reason": "source_reference_stale_or_missing"}
        artifacts.append({"id": artifact["id"], "version": artifact["version"], "stage": artifact["stage"], **state,
                          "source_evidence": evidence,
                          "media_acceptance": "not_evaluated_by_record"})
    valid_deliveries = sum(1 for item in project["reads"] if item.get("source_id") in indices
                           and item.get("delivery_status") == "tool_delivery_only"
                           and item.get("source_sha256") == indices[item["source_id"]]["source_sha256"]
                           and item.get("index_sha256") == indices[item["source_id"]]["sha256"]
                           and item.get("chunk_id") in indices[item["source_id"]]["ids"])
    history = [{"id": item["id"], "version": item["version"], **file_state(root, item.get("snapshot"))}
               for item in project.get("artifact_history", [])]
    return {"route": project["route"], "title": project["title"], "sources": rows, "artifacts": artifacts,
            "artifact_history": history, "reads": {"delivery_status": "tool_delivery_only", "valid_deliveries": valid_deliveries},
            "analysis_artifacts": [row["id"] for row in artifacts if row["stage"] == "analysis" and row["status"] == "ready"],
            "next_step": project.get("next_step"),
            "boundary": "ready means matching local records, not semantic understanding, complete analysis or accepted media."}


def parser():
    root = Parser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True, parser_class=Parser)
    for name, handler in (("init", init_command), ("source", source_command), ("index", index_command),
                          ("read", read_command), ("record", record_command), ("status", status_command)):
        sub = commands.add_parser(name)
        sub.add_argument("--project", required=True)
        sub.set_defaults(handler=handler)
        if name == "init":
            sub.add_argument("--route", choices=ROUTES, required=True)
            sub.add_argument("--title")
        elif name == "source":
            sub.add_argument("--id", required=True)
            sub.add_argument("--kind", choices=("video", "novel", "text"), required=True)
            sub.add_argument("--file")
            sub.add_argument("--url")
        elif name == "index":
            sub.add_argument("--source", required=True)
            sub.add_argument("--chunk-chars", type=int, default=6000)
        elif name == "read":
            sub.add_argument("--source", required=True)
            sub.add_argument("--chunk", required=True)
        elif name == "record":
            sub.add_argument("--artifact-id", required=True)
            sub.add_argument("--stage", choices=STAGES, required=True)
            sub.add_argument("--file", required=True)
            sub.add_argument("--source-ids")
            sub.add_argument("--next-step")
            sub.add_argument("--replace", action="store_true")
    return root


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        root = Path(args.project).expanduser().resolve()
        if args.command == "init":
            root.mkdir(parents=True, exist_ok=True)
        elif not root.is_dir():
            raise ProjectError("PROJECT_MISSING", "Initialize the project directory before using it.")
        with project_lock(root):
            if args.command == "init":
                result = args.handler(args, root)
            else:
                project = load_project(root)
                result = args.handler(args, root, project)
        result = {"ok": True, "command": args.command, "project_file": str(root / PROJECT_FILE), **result}
    except ProjectError as exc:
        print(json.dumps({"ok": False, "error": {"code": exc.code, "message": str(exc)}}, ensure_ascii=False))
        return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": {"code": "RECORD_ERROR", "message": str(exc)}}, ensure_ascii=False))
        return 2
    except Exception:
        print(json.dumps({"ok": False, "error": {"code": "INVALID_RECORD_STATE", "message": "Stored records could not be processed; inspect their structure before continuing."}}))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
