from __future__ import annotations

import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AudioConfig:
    ffmpeg: str = "ffmpeg"
    ffprobe: str = "ffprobe"
    bitrate: str = "128k"


@dataclass(frozen=True)
class TranscribeConfig:
    backend: str = "faster-whisper"
    model: str = "small"
    language: str = "en"
    device: str = "auto"
    compute_type: str = "default"
    vad_filter: bool = True
    word_timestamps: bool = False


@dataclass(frozen=True)
class ExportConfig:
    enabled: bool = True
    embed_audio_in_html: bool = False


@dataclass(frozen=True)
class Config:
    courses_root: Path = Path("/Users/zhaoxin/workspace/study/courses")
    library_root: Path = DEFAULT_PROJECT_ROOT / "library"
    iphone_export_root: Path = DEFAULT_PROJECT_ROOT / "iphone_export"
    audio: AudioConfig = AudioConfig()
    transcribe: TranscribeConfig = TranscribeConfig()
    export: ExportConfig = ExportConfig()


def load_config(config_path: Path | None = None) -> Config:
    path = config_path or DEFAULT_PROJECT_ROOT / "config.toml"
    if not path.exists():
        return Config()

    with path.open("rb") as fh:
        data = tomllib.load(fh)

    return Config(
        courses_root=Path(data.get("courses_root", Config.courses_root)),
        library_root=Path(data.get("library_root", Config.library_root)),
        iphone_export_root=Path(data.get("iphone_export_root", Config.iphone_export_root)),
        audio=_load_section(AudioConfig(), data.get("audio", {})),
        transcribe=_load_section(TranscribeConfig(), data.get("transcribe", {})),
        export=_load_section(ExportConfig(), data.get("export", {})),
    )


def _load_section(default: Any, raw: dict[str, Any]) -> Any:
    values = {key: raw[key] for key in raw if hasattr(default, key)}
    return replace(default, **values)

