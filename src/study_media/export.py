from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .render import render_html, render_markdown


def export_lesson(
    *,
    export_root: Path,
    course: str,
    slug: str,
    title: str,
    source_video: Path,
    audio_path: Path,
    transcript: dict[str, Any],
    embed_audio_in_html: bool = False,
) -> dict[str, Path]:
    export_dir = export_root.joinpath(*course.split("/"), slug)
    export_dir.mkdir(parents=True, exist_ok=True)

    audio_filename = f"{slug}.m4a"
    md_filename = f"{slug}.md"
    html_filename = f"{slug}.html"

    exported_audio = export_dir / audio_filename
    shutil.copy2(audio_path, exported_audio)
    exported_md = render_markdown(
        transcript,
        export_dir / md_filename,
        title=title,
        course=course,
        source_video=source_video,
        audio_filename=audio_filename,
    )
    exported_html = render_html(
        transcript,
        export_dir / html_filename,
        title=title,
        course=course,
        audio_filename=audio_filename,
        embed_audio_path=exported_audio if embed_audio_in_html else None,
    )

    return {"audio": exported_audio, "markdown": exported_md, "html": exported_html}

