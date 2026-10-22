#!/usr/bin/env python3
"""Read-only, standard-library portability checks. No network or child processes.

Exit 0: requested static checks have no errors. Exit 2: static blocking errors.
A successful report NEVER certifies ChatCut connectivity or visual quality.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import platform
import re
import shutil
import sys


CORE_FILES = (
    "SKILL.md",
    "references/environment-and-portability.md",
    "scripts/check_environment.py",
)
NATIVE_TOOL_HINTS = (
    "get_active_project", "read_project", "preview_timeline", "inspect_item",
    "inspect_asset", "read_captions", "edit_captions", "push_asset", "edit_item",
    "export", "track_progress",
)
FONT_SUFFIXES = {".otf", ".ttf", ".ttc", ".woff", ".woff2"}


def is_within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def safe_relative_file(root, value):
    if not isinstance(value, str) or not value or "\\" in value or PureWindowsPath(value).drive:
        raise ValueError("resource path must be a non-empty portable relative path using forward slashes")
    requested = Path(value)
    if requested.is_absolute():
        raise ValueError("required file must be relative to skill root")
    candidate = (root / requested).resolve()
    if not is_within(candidate, root):
        raise ValueError("required file escapes skill root")
    return candidate


def check_resource_manifest(root, check):
    """Validate only paths rooted inside this Skill before opening any resource."""
    manifest_path = root / "assets" / "manifest.json"
    evidence = {"path": "assets/manifest.json", "files_verified": 0, "external_requirements": "not_checked"}
    if not manifest_path.is_file():
        check("resource_manifest", "warning", "No manifest found; only core files checked. Run verify_package.py for the full delivery package.")
        return evidence
    if not is_within(manifest_path.resolve(), root):
        check("resource_manifest", "error", "Manifest is linked outside the Skill root; refused to open it.")
        return evidence
    try:
        with manifest_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        files = data.get("files") if isinstance(data, dict) else None
        if not isinstance(files, list):
            raise ValueError("manifest must contain a files array")
        evidence["declared_files"] = len(files)
        seen = set()
        for index, row in enumerate(files):
            key = "resource_manifest_file:" + str(index)
            try:
                if not isinstance(row, dict):
                    raise ValueError("file entry must be an object")
                value = row.get("path")
                file_path = safe_relative_file(root, value)
                if value in seen:
                    raise ValueError("duplicate resource path")
                seen.add(value)
                digest = row.get("sha256")
                if not isinstance(digest, str) or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None:
                    raise ValueError("missing or malformed sha256")
                if not file_path.is_file():
                    raise ValueError("resource file is missing")
                expected_bytes = row.get("bytes")
                if expected_bytes is not None and (not isinstance(expected_bytes, int) or file_path.stat().st_size != expected_bytes):
                    raise ValueError("resource byte size does not match")
                calculated = hashlib.sha256()
                with file_path.open("rb") as handle:
                    for block in iter(lambda: handle.read(1024 * 1024), b""):
                        calculated.update(block)
                if calculated.hexdigest() != digest.lower():
                    raise ValueError("resource sha256 does not match")
                evidence["files_verified"] += 1
            except (OSError, ValueError, TypeError) as exc:
                check(key, "error", str(exc) + (" (" + str(row.get("path")) + ")" if isinstance(row, dict) else ""))
        check("resource_manifest", "info", "Verified resource existence, byte size when declared, and SHA-256. Rights/status and real rendering still require human review.")
        requirements = data.get("externalRequirements", [])
        evidence["external_requirement_count"] = len(requirements) if isinstance(requirements, list) else None
        evidence["external_requirements"] = "unverified; no download, network, login or font registration attempted"
    except (OSError, ValueError, TypeError) as exc:
        check("resource_manifest", "error", "Cannot read valid resource manifest: " + str(exc))
    return evidence


def bounded_font_files(roots, limit=6000):
    """Inspect filenames only. Do not parse arbitrary binaries or font internals."""
    visited = 0
    candidates = []
    historical_aliases = []
    existing = []
    truncated = False
    for root in roots:
        if not root.is_dir():
            continue
        existing.append(str(root))
        for base, dirs, names in os.walk(str(root), followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for name in sorted(names):
                visited += 1
                if visited > limit:
                    truncated = True
                    break
                if Path(name).suffix.lower() in FONT_SUFFIXES:
                    lowered = name.lower().replace("-", "").replace("_", "")
                    if "misansrico" in lowered:
                        historical_aliases.append(str(Path(base) / name))
                        continue
                    if any(term in lowered for term in ("misans", "notosanssc", "sourcehansans", "pingfang")):
                        candidates.append(str(Path(base) / name))
            if truncated:
                break
        if truncated:
            break
    return {
        "existing_search_roots": existing,
        "files_examined": min(visited, limit),
        "search_truncated": truncated,
        "filename_hints": candidates[:50],
        "historical_name_aliases_excluded": historical_aliases[:20],
        "font_family_and_glyph_coverage": "unverified",
        "native_font_rendering": "unverified",
        "note": "Filename hints are not proof of actual font family, license, glyphs or rendering.",
    }


def platform_candidates(skill_root, extra_fonts):
    home = Path.home()
    system = platform.system()
    launchers = []
    app_candidates = []
    fonts = [skill_root / "assets" / "fonts", skill_root / "resources" / "fonts"]
    if system == "Darwin":
        launchers.append(home / "Library" / "Application Support" / "ChatCut" / "chatcut-mcp")
        app_candidates.extend([Path("/Applications/ChatCut.app"), home / "Applications" / "ChatCut.app"])
        fonts.extend([home / "Library" / "Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts")])
    elif system == "Windows":
        # Only non-secret location variables; no config, credentials or registry reads.
        local = os.environ.get("LOCALAPPDATA")
        windows = os.environ.get("WINDIR", "C:\\Windows")
        if local:
            app_candidates.extend([Path(local) / "Programs" / "ChatCut", Path(local) / "ChatCut"])
            fonts.append(Path(local) / "Microsoft" / "Windows" / "Fonts")
        fonts.append(Path(windows) / "Fonts")
    elif system == "Linux":
        fonts.extend([home / ".local/share/fonts", home / ".fonts", Path("/usr/share/fonts"), Path("/usr/local/share/fonts")])
    path_launcher = shutil.which("chatcut-mcp")
    if path_launcher:
        launchers.append(Path(path_launcher))
    path_app = shutil.which("chatcut")
    if path_app:
        app_candidates.append(Path(path_app))
    fonts.extend(Path(v).expanduser().resolve() for v in extra_fonts)
    unique = lambda values: list(dict.fromkeys(values))
    return unique(launchers), unique(app_candidates), unique(fonts)


def read_tool_names(path):
    """Only a user-supplied MCP tools/list result; do not read runtime config."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict) and isinstance(data.get("result"), dict):
        data = data["result"]
    rows = data.get("tools") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError("manifest must be a tools array or an object with tools (or result.tools)")
    names = []
    for item in rows:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            # Names only: never emit full descriptions, arbitrary responses or schemas.
            names.append(item["name"])
    return sorted(set(names))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", help="Skill directory; defaults to this script's parent skill")
    parser.add_argument("--package-only", action="store_true", help="Only inspect this Skill's core files and resource manifest; skip every host lookup")
    parser.add_argument("--launcher", help="Explicit official Desktop launcher path; existence only")
    parser.add_argument("--font-dir", action="append", default=[], help="Additional bounded font search root")
    parser.add_argument("--tool-manifest", help="Read-only tools/list JSON snapshot, not a config file")
    parser.add_argument("--require-native-tools", action="store_true", help="Fail if historical native tool hints absent")
    parser.add_argument("--required", action="append", default=[], help="Additional required file relative to skill root")
    args = parser.parse_args(argv)
    if args.package_only and (args.launcher or args.font_dir or args.tool_manifest or args.require_native_tools):
        parser.error("--package-only cannot be combined with --launcher, --font-dir, --tool-manifest or --require-native-tools; no host lookup was performed")
    root = Path(args.skill_root).expanduser().resolve() if args.skill_root else Path(__file__).resolve().parent.parent
    checks = []

    def check(key, status, detail):
        checks.append({"check": key, "status": status, "detail": detail})

    if root.is_dir():
        check("skill_root", "pass", str(root))
    else:
        check("skill_root", "error", "Skill root is absent or not a directory: " + str(root))
    for value in dict.fromkeys(CORE_FILES + tuple(args.required)):
        try:
            file_path = safe_relative_file(root, value)
            check("required_file:" + value, "pass" if file_path.is_file() else "error", "present" if file_path.is_file() else "missing")
        except ValueError as exc:
            check("required_file:" + value, "error", str(exc))

    resource_evidence = check_resource_manifest(root, check)

    if args.package_only:
        # Do not call host-discovery helpers, PATH lookups, fonts, app checks,
        # or a tools-list reader in an isolated package review.
        launcher_findings = []
        app_candidates = []
        optional_executables = {}
        font_evidence = {"search": "skipped-package-only", "native_font_rendering": "unverified"}
        tool_evidence = {"source": None, "search": "skipped-package-only", "live_connection": "unverified"}
        check("package_only", "info", "Only Skill-root files and its resource manifest were inspected; every host lookup was skipped.")
    else:
        launchers, app_candidates, font_roots = platform_candidates(root, args.font_dir)
        if args.launcher:
            launchers.insert(0, Path(args.launcher).expanduser().resolve())
        launcher_findings = [{"path": str(p), "is_file": p.is_file(), "executable": p.is_file() and os.access(str(p), os.X_OK)} for p in dict.fromkeys(launchers)]
        explicit = launcher_findings[0] if args.launcher else None
        if explicit and not explicit["is_file"]:
            check("explicit_launcher", "error", "Provided launcher file is absent; no launcher was run.")
        elif explicit and not explicit["executable"] and platform.system() != "Windows":
            check("explicit_launcher", "warning", "File exists but is not executable for this user; no permissions changed.")
        elif any(p["is_file"] for p in launcher_findings):
            check("desktop_launcher_hint", "info", "Local candidate exists. Do not reconnect if Desktop tools are already active.")
        else:
            check("desktop_launcher_hint", "warning", "No candidate found. Installation locations vary; current connected native tools may still work.")

        optional_executables = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe", "node", "npm")}
        check("optional_external_tools", "info", "Presence only; none are mandatory for native Desktop editing and none were executed.")
        tool_evidence = {"source": None, "live_connection": "unverified", "schema_and_equivalent_capabilities": "unverified"}
        if args.tool_manifest:
            manifest = Path(args.tool_manifest).expanduser().resolve()
            try:
                names = read_tool_names(manifest)
                missing = [name for name in NATIVE_TOOL_HINTS if name not in names]
                tool_evidence.update({"source": str(manifest), "tool_count": len(names), "historical_native_names_missing": missing})
                status = "error" if missing and args.require_native_tools else ("warning" if missing else "pass")
                check("provided_tool_manifest", status, "Historical names checked. Renamed capabilities need manual live-schema review; a snapshot is not a live connection.")
            except (OSError, ValueError, TypeError) as exc:
                check("provided_tool_manifest", "error", "Cannot read valid tools/list snapshot: " + str(exc))
        elif args.require_native_tools:
            check("provided_tool_manifest", "error", "--require-native-tools needs --tool-manifest; no live connection was attempted.")
        else:
            check("native_capabilities", "unverified", "Use the current Agent session's actual native tools and schemas; this script does not start MCP.")

        font_evidence = bounded_font_files(font_roots)
        if not font_evidence["filename_hints"]:
            check("font_filename_hints", "warning", "No matching local filename found. Native catalog/cache may still provide it; inspect actual glyphs.")
        else:
            check("font_filename_hints", "info", "Candidate filenames found; native font rendering and licensing remain unverified.")

    errors = sum(item["status"] == "error" for item in checks)
    report = {
        "report_type": "course-long-video-editing-static-environment-check",
        "report_version": 2,
        "package_only": args.package_only,
        "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "read_only": True,
        "external_processes_started": False,
        "network_used": False,
        "credentials_or_configuration_read": False,
        "skill_root": str(root),
        "host": {"search": "skipped-package-only"} if args.package_only else {"platform": platform.system(), "machine": platform.machine(), "python": platform.python_version()},
        "static_check_passed": errors == 0,
        "blocking_errors": errors,
        "checks": checks,
        "resource_manifest": resource_evidence,
        "launcher_candidates": launcher_findings,
        "application_path_hints": [{"path": str(p), "exists": p.exists()} for p in app_candidates],
        "optional_executables": optional_executables,
        "fonts": font_evidence,
        "native_capabilities": tool_evidence,
        "requires_real_test": ["native Desktop connection and current schema", "selected project and new media mapping", "font glyphs and actual rendering", "editable-property binding", "seek/playback/export consistency", "audio and visual quality", "external service login/authorization only if used", "receiving computer end-to-end trial"],
        "result_meaning": "Only requested static checks passed; this is not proof of ChatCut connectivity, rendering, export or aesthetic success.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
