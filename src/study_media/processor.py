from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audio import copy_existing_audio, extract_audio
from .export import export_lesson
from .paths import infer_course, lesson_paths, slugify
from .render import render_html, render_markdown
from .settings import Config, TranscribeConfig
from .transcribe import transcribe_audio


@dataclass(frozen=True)
class ProcessOptions:
    course: str | None = None
    title: str | None = None
    slug: str | None = None
    force_audio: bool = False
    force_transcript: bool = False
    skip_transcribe: bool = False
    export_enabled: bool | None = None
    embed_audio_in_html: bool | None = None
    transcribe_model: str | None = None
    transcribe_language: str | None = None


def process_video(video_path: Path, config: Config, options: ProcessOptions) -> dict[str, Any]:
    source_video = video_path.expanduser().resolve()
    title = options.title or source_video.stem
    slug = slugify(options.slug or source_video.stem)
    course = options.course or infer_course(source_video, config.courses_root)
    paths = lesson_paths(config.library_root, course, slug)
    paths["lesson_dir"].mkdir(parents=True, exist_ok=True)

    audio_source = source_video.with_suffix(".m4a")
    if audio_source.exists():
        audio_path = copy_existing_audio(audio_source, paths["audio"], force=options.force_audio)
        audio_action = "copied-existing"
    else:
        audio_path = extract_audio(source_video, paths["audio"], config.audio, force=options.force_audio)
        audio_action = "extracted"

    transcript = None
    transcript_action = "skipped"
    transcribe_config = _override_transcribe_config(config.transcribe, options)
    if not options.skip_transcribe:
        transcript = transcribe_audio(
            audio_path,
            paths["transcript_json"],
            transcribe_config,
            force=options.force_transcript,
        )
        transcript_action = "generated" if options.force_transcript else "available"

    rendered: dict[str, Path] = {}
    if transcript is not None:
        rendered["markdown"] = render_markdown(
            transcript,
            paths["transcript_md"],
            title=title,
            course=course,
            source_video=source_video,
            audio_filename=paths["audio"].name,
        )
        rendered["html"] = render_html(
            transcript,
            paths["html"],
            title=title,
            course=course,
            audio_filename=paths["audio"].name,
        )

    export_enabled = config.export.enabled if options.export_enabled is None else options.export_enabled
    embed_audio = (
        config.export.embed_audio_in_html
        if options.embed_audio_in_html is None
        else options.embed_audio_in_html
    )
    exported: dict[str, Path] = {}
    if export_enabled and transcript is not None:
        exported = export_lesson(
            export_root=config.iphone_export_root,
            course=course,
            slug=slug,
            title=title,
            source_video=source_video,
            audio_path=audio_path,
            transcript=transcript,
            embed_audio_in_html=embed_audio,
        )

    metadata = _build_metadata(
        source_video=source_video,
        source_audio=audio_source if audio_source.exists() else None,
        course=course,
        title=title,
        slug=slug,
        audio_action=audio_action,
        transcript_action=transcript_action,
        transcribe_config=transcribe_config,
        paths=paths,
        rendered=rendered,
        exported=exported,
    )
    paths["source"].write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "course": course,
        "title": title,
        "slug": slug,
        "lesson_dir": paths["lesson_dir"],
        "audio": audio_path,
        "transcript_json": paths["transcript_json"] if paths["transcript_json"].exists() else None,
        "rendered": rendered,
        "exported": exported,
        "metadata": paths["source"],
    }


def _override_transcribe_config(config: TranscribeConfig, options: ProcessOptions) -> TranscribeConfig:
    updates: dict[str, Any] = {}
    if options.transcribe_model:
        updates["model"] = options.transcribe_model
    if options.transcribe_language:
        updates["language"] = options.transcribe_language
    if not updates:
        return config
    return TranscribeConfig(**{**config.__dict__, **updates})


def _build_metadata(
    *,
    source_video: Path,
    source_audio: Path | None,
    course: str,
    title: str,
    slug: str,
    audio_action: str,
    transcript_action: str,
    transcribe_config: TranscribeConfig,
    paths: dict[str, Path],
    rendered: dict[str, Path],
    exported: dict[str, Path],
) -> dict[str, Any]:
    stat = source_video.stat()
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "course": course,
        "title": title,
        "slug": slug,
        "source_video": str(source_video),
        "source_audio": str(source_audio) if source_audio else None,
        "source_size": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
        "audio_status": "done",
        "audio_action": audio_action,
        "transcript_status": transcript_action,
        "transcribe_backend": transcribe_config.backend,
        "transcribe_model": transcribe_config.model,
        "transcribe_language": transcribe_config.language,
        "library": {name: str(path) for name, path in paths.items()},
        "rendered": {name: str(path) for name, path in rendered.items()},
        "exported": {name: str(path) for name, path in exported.items()},
    }
    if paths["audio"].exists():
        metadata["audio_size"] = paths["audio"].stat().st_size
    return metadata


def copy_example_config(project_root: Path) -> Path:
    source = project_root / "config.example.toml"
    target = project_root / "config.toml"
    if not target.exists():
        shutil.copy2(source, target)
    return target

