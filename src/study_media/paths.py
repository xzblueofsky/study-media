from __future__ import annotations

import re
import unicodedata
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = re.sub(r"[\\/:*?\"<>|\s]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-._ ")
    return normalized or "untitled"


def is_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def infer_course(video_path: Path, courses_root: Path) -> str:
    try:
        relative_parent = video_path.resolve().parent.relative_to(courses_root.resolve())
    except ValueError:
        return slugify(video_path.parent.name)

    if str(relative_parent) == ".":
        return "uncategorized"
    return "/".join(slugify(part) for part in relative_parent.parts)


def lesson_paths(library_root: Path, course: str, slug: str) -> dict[str, Path]:
    lesson_dir = library_root.joinpath(*course.split("/"), slug)
    return {
        "lesson_dir": lesson_dir,
        "source": lesson_dir / "source.json",
        "audio": lesson_dir / "audio.m4a",
        "transcript_json": lesson_dir / "transcript.json",
        "transcript_md": lesson_dir / "transcript.md",
        "html": lesson_dir / "study.html",
    }

