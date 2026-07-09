from __future__ import annotations

import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import StudyMediaError
from .paths import infer_course, lesson_paths, slugify
from .settings import Config


PACKAGE_SCHEMA_VERSION = 1


def create_study_package(
    target: Path | str,
    config: Config,
    *,
    output_path: Path | None = None,
) -> dict[str, Any]:
    lesson = resolve_lesson(target, config)
    _validate_lesson(lesson)

    transcript = json.loads(lesson["transcript_json"].read_text(encoding="utf-8"))
    source = _read_json_if_exists(lesson["source"])
    course = source.get("course") or lesson["course"]
    slug = source.get("slug") or lesson["slug"]
    title = source.get("title") or slug

    manifest = {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "id": f"{course}/{slug}",
        "course": course,
        "slug": slug,
        "title": title,
        "language": transcript.get("language"),
        "duration": transcript.get("duration"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "audio": "audio.m4a",
        "transcript_json": "transcript.json",
        "transcript_markdown": "transcript.md",
        "segments_count": len(transcript.get("segments", [])),
        "source_video": source.get("source_video"),
        "transcribe_backend": source.get("transcribe_backend") or transcript.get("backend"),
        "transcribe_model": source.get("transcribe_model") or transcript.get("model"),
        "container": "tar",
    }

    destination = output_path or _default_package_path(config, course, slug)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as archive:
        _add_bytes(archive, "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"))
        archive.add(lesson["audio"], arcname="audio.m4a", recursive=False)
        archive.add(lesson["transcript_json"], arcname="transcript.json", recursive=False)
        archive.add(lesson["transcript_md"], arcname="transcript.md", recursive=False)

    return {
        "package": destination,
        "manifest": manifest,
        "audio": lesson["audio"],
        "transcript_json": lesson["transcript_json"],
        "transcript_md": lesson["transcript_md"],
    }


def resolve_lesson(target: Path | str, config: Config) -> dict[str, Any]:
    raw = Path(target).expanduser()
    if raw.exists():
        resolved = raw.resolve()
        if resolved.is_dir():
            course, slug = _course_and_slug_from_lesson_dir(resolved, config.library_root)
            paths = lesson_paths(config.library_root, course, slug)
            paths["lesson_dir"] = resolved
            paths["source"] = resolved / "source.json"
            paths["audio"] = resolved / "audio.m4a"
            paths["transcript_json"] = resolved / "transcript.json"
            paths["transcript_md"] = resolved / "transcript.md"
            return {"course": course, "slug": slug, **paths}

        course = infer_course(resolved, config.courses_root)
        slug = slugify(resolved.stem)
        return {"course": course, "slug": slug, **lesson_paths(config.library_root, course, slug)}

    value = str(target).strip("/")
    if not value:
        raise StudyMediaError("Package target cannot be empty")
    parts = [slugify(part) for part in value.split("/") if part]
    if len(parts) < 2:
        raise StudyMediaError(
            "Package target must be a video path, lesson directory, or course/lesson like 3Blue1Brown/Entropy-Compression"
        )
    course = "/".join(parts[:-1])
    slug = parts[-1]
    return {"course": course, "slug": slug, **lesson_paths(config.library_root, course, slug)}


def _validate_lesson(lesson: dict[str, Any]) -> None:
    lesson_dir = lesson["lesson_dir"]
    required = {
        "audio.m4a": lesson["audio"],
        "transcript.json": lesson["transcript_json"],
        "transcript.md": lesson["transcript_md"],
    }
    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        missing_text = ", ".join(missing)
        raise StudyMediaError(
            f"Cannot package {lesson_dir}; missing {missing_text}. "
            "Run study-media process for this video first."
        )


def _default_package_path(config: Config, course: str, slug: str) -> Path:
    return config.iphone_export_root / "packages" / Path(*course.split("/")) / f"{slug}.study"


def _course_and_slug_from_lesson_dir(lesson_dir: Path, library_root: Path) -> tuple[str, str]:
    try:
        relative = lesson_dir.relative_to(library_root.resolve())
    except ValueError as exc:
        raise StudyMediaError(
            f"Lesson directory must be inside library_root: {library_root}"
        ) from exc
    if len(relative.parts) < 2:
        raise StudyMediaError("Lesson directory must look like library_root/course/lesson")
    return "/".join(relative.parts[:-1]), relative.parts[-1]


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mtime = int(datetime.now(timezone.utc).timestamp())
    archive.addfile(info, fileobj=_BytesReader(data))


class _BytesReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._data) - self._offset
        chunk = self._data[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk

