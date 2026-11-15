"""Check a source package's portability and common accidental release leaks.

Standard library only. These checks cannot judge creative quality or replace a
dedicated secrets scanner. They never execute links, skill text, or examples.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", "__pycache__", ".venv", "node_modules", "scratch"}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}
SPECIAL_FILES = {"LICENSE", ".gitignore", ".gitattributes"}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SENSITIVE = (
    ("Windows personal/runtime path", re.compile(r"[A-Za-z]:[\\/](?:Users|AI|Temp)[\\/]", re.I)),
    ("Unix personal path", re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/")),
    ("GitHub credential", re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("API credential", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}")),
    ("private share token", re.compile(r"(?:xsec_token|access_token|refresh_token)\s*=[^\s&\"']{10,}", re.I)),
)


def sensitive_findings(text: str) -> list[str]:
    return [label for label, pattern in SENSITIVE if pattern.search(text)]


def link_errors(path: Path, root: Path, text: str) -> list[str]:
    """Validate local Markdown targets without fetching remote URLs."""
    errors: list[str] = []
    for match in LINK.finditer(text):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        parts = urlsplit(target)
        if parts.scheme in {"http", "https", "mailto"}:
            continue
        if parts.scheme or parts.netloc or target.startswith("/"):
            errors.append(f"nonportable or unsupported link: {target}")
            continue
        if not parts.path:
            continue
        resolved = (path.parent / unquote(parts.path)).resolve()
        if not resolved.is_relative_to(root.resolve()):
            errors.append(f"link escapes package: {target}")
        elif not resolved.exists():
            errors.append(f"missing local target: {target}")
    return errors


def evaluation_errors(cases: dict, oracle: dict) -> list[str]:
    errors: list[str] = []
    if cases.get("schema_version") != 1 or oracle.get("schema_version") != 1:
        errors.append("evaluation schema_version must be 1")
    items = cases.get("cases", [])
    expected = oracle.get("expected", [])
    if not isinstance(items, list) or not isinstance(expected, list):
        return errors + ["evaluation cases and expected must be arrays"]
    ids: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            errors.append("each evaluation case must be an object")
            continue
        case_id = item.get("id", "")
        if not isinstance(case_id, str) or not case_id:
            errors.append("each evaluation case needs a nonempty id")
            continue
        ids.append(case_id)
        for key in ("request", "evidence", "candidate"):
            if not item.get(key):
                errors.append(f"{case_id}: missing {key}")
        if item.get("synthetic_text") is not True:
            errors.append(f"{case_id}: must be labeled synthetic_text")
    if len(set(ids)) != len(ids):
        errors.append("duplicate evaluation case ids")
    oracle_ids: list[str] = []
    for item in expected:
        if not isinstance(item, dict):
            errors.append("each oracle entry must be an object")
            continue
        oracle_ids.append(item.get("id", ""))
        if item.get("decision") not in {"supported", "revise", "pending"}:
            errors.append(f"{item.get('id')}: unsupported oracle decision")
    if len(set(oracle_ids)) != len(oracle_ids):
        errors.append("duplicate oracle ids")
    if set(ids) != set(oracle_ids):
        errors.append("case and oracle ids do not match")
    if not ids:
        errors.append("evaluation set is empty")
    return errors


def check(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    required = (
        "README.md", "README.zh-CN.md", "LICENSE", "docs/ATTRIBUTION.md",
        "docs/INSTALL.md", "docs/VALIDATION.md", ".claude-plugin/plugin.json",
        "skills/performance-direction/SKILL.md", "skills/performance-direction/LICENSE",
        "skills/video-observation/SKILL.md", "skills/video-observation/LICENSE",
        "skills/video-observation/scripts/video_observe.py",
        "skills/video-observation/scripts/requirements.txt",
        "evals/cases.json", "evals/oracle.json",
    )
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if set(relative.parts) & IGNORED or relative.parts[:2] == ("evals", "runs"):
            continue
        if path.is_symlink():
            errors.append(f"release contains a symlink: {relative.as_posix()}")
            continue
        if not path.is_file():
            continue
        if path.name not in SPECIAL_FILES and path.suffix.lower() not in TEXT_SUFFIXES:
            errors.append(f"unreviewed release file type: {relative.as_posix()}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError) as exc:
            errors.append(f"unreadable UTF-8 file: {relative.as_posix()}: {exc}")
            continue
        for finding in sensitive_findings(text):
            errors.append(f"{relative.as_posix()}: {finding}")
        if path.suffix.lower() == ".md":
            for finding in link_errors(path, root, text):
                errors.append(f"{relative.as_posix()}: {finding}")

    try:
        manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        release_version = manifest.get("version")
        if manifest.get("name") != "video-performance-skills":
            errors.append("unexpected plugin name")
    except (ValueError, OSError) as exc:
        errors.append(f"cannot read plugin manifest: {exc}")
        release_version = None
    for skill in sorted((root / "skills").glob("*/SKILL.md")):
        skill_dir = skill.parent
        content = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.S)
        if not match:
            errors.append(f"{skill_dir.name}: missing YAML frontmatter")
        else:
            frontmatter = match.group(1)
            if not re.search(r"^name: " + re.escape(skill_dir.name) + r"\s*$", frontmatter, re.M):
                errors.append(f"{skill_dir.name}: skill name must match its folder")
            if not re.search(r"^description: .+", frontmatter, re.M):
                errors.append("skill description is missing")
            if not re.search(r"^license: MIT\s*$", frontmatter, re.M):
                errors.append("skill must declare its distributed license")
            version = re.search(r'^  version: "([^"]+)"\s*$', frontmatter, re.M)
            if not version or release_version != version.group(1):
                errors.append(f"{skill_dir.name}: skill and plugin versions differ")
        for path in skill_dir.rglob("*.md"):
            for finding in link_errors(path, skill_dir, path.read_text(encoding="utf-8")):
                errors.append(f"installed skill is not self-contained ({path.name}): {finding}")
        license_file = skill_dir / "LICENSE"
        if not license_file.is_file():
            errors.append(f"{skill_dir.name}: missing standalone license")
        elif (root / "LICENSE").is_file() and license_file.read_bytes() != (root / "LICENSE").read_bytes():
            errors.append(f"{skill_dir.name}: standalone license differs from repository license")
    try:
        cases = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
        oracle = json.loads((root / "evals/oracle.json").read_text(encoding="utf-8"))
        errors.extend(evaluation_errors(cases, oracle))
    except (ValueError, OSError) as exc:
        errors.append(f"cannot read evaluation files: {exc}")
    return errors


if __name__ == "__main__":
    failures = check(ROOT)
    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        sys.exit(1)
    print("PASS: package files, local links, standalone skill, versions, text-case structure and common private-file patterns")
    print("Scope: packaging only; no creative-quality or media-performance score.")
