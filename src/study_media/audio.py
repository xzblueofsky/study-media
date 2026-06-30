from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .errors import DependencyError, StudyMediaError
from .settings import AudioConfig


def ensure_media_commands(config: AudioConfig) -> None:
    missing = [cmd for cmd in (config.ffmpeg, config.ffprobe) if shutil.which(cmd) is None]
    if missing:
        names = ", ".join(missing)
        raise DependencyError(
            f"Missing media command: {names}. Install ffmpeg, for example: brew install ffmpeg"
        )


def probe_audio_codec(video_path: Path, config: AudioConfig) -> str | None:
    ensure_media_commands(config)
    cmd = [
        config.ffprobe,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise StudyMediaError(f"ffprobe failed for {video_path}: {result.stderr.strip()}")

    payload = json.loads(result.stdout or "{}")
    streams = payload.get("streams", [])
    if not streams:
        return None
    return streams[0].get("codec_name")


def extract_audio(video_path: Path, output_path: Path, config: AudioConfig, force: bool = False) -> Path:
    ensure_media_commands(config)
    if output_path.exists() and not force:
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    codec = probe_audio_codec(video_path, config)
    if codec is None:
        raise StudyMediaError(f"No audio stream found in {video_path}")

    if codec == "aac":
        cmd = [
            config.ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-map",
            "0:a:0",
            "-c:a",
            "copy",
            str(output_path),
        ]
    else:
        cmd = [
            config.ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-map",
            "0:a:0",
            "-c:a",
            "aac",
            "-b:a",
            config.bitrate,
            str(output_path),
        ]

    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise StudyMediaError(f"ffmpeg failed for {video_path}: {result.stderr.strip()}")
    return output_path


def copy_existing_audio(source_audio: Path, output_path: Path, force: bool = False) -> Path:
    if output_path.exists() and not force:
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_audio, output_path)
    return output_path

