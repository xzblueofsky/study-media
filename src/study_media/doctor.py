from __future__ import annotations

import importlib.util
import shutil

from .settings import Config


def run_doctor(config: Config) -> list[tuple[str, bool, str]]:
    return [
        ("courses_root", config.courses_root.exists(), str(config.courses_root)),
        ("library_root", True, str(config.library_root)),
        ("iphone_export_root", True, str(config.iphone_export_root)),
        ("ffmpeg", shutil.which(config.audio.ffmpeg) is not None, config.audio.ffmpeg),
        ("ffprobe", shutil.which(config.audio.ffprobe) is not None, config.audio.ffprobe),
        (
            "faster-whisper",
            importlib.util.find_spec("faster_whisper") is not None,
            "required for transcription",
        ),
    ]

