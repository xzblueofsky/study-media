from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import DependencyError, StudyMediaError
from .settings import TranscribeConfig


def transcribe_audio(audio_path: Path, output_path: Path, config: TranscribeConfig, force: bool = False) -> dict[str, Any]:
    if output_path.exists() and not force:
        return read_transcript(output_path)

    if config.backend != "faster-whisper":
        raise StudyMediaError(f"Unsupported transcription backend: {config.backend}")

    try:
        from faster_whisper import WhisperModel
    except ModuleNotFoundError as exc:
        raise DependencyError(
            "Missing Python package faster-whisper. Install it with: "
            "python -m pip install -e '.[transcribe]'"
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    language = None if config.language.lower() in {"", "auto"} else config.language
    model = WhisperModel(config.model, device=config.device, compute_type=config.compute_type)
    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        vad_filter=config.vad_filter,
        word_timestamps=config.word_timestamps,
    )

    segments: list[dict[str, Any]] = []
    for index, segment in enumerate(segments_iter):
        item: dict[str, Any] = {
            "id": index,
            "start": float(segment.start),
            "end": float(segment.end),
            "text": segment.text.strip(),
        }
        words = getattr(segment, "words", None)
        if words:
            item["words"] = [
                {
                    "start": float(word.start),
                    "end": float(word.end),
                    "word": word.word,
                    "probability": float(word.probability),
                }
                for word in words
            ]
        segments.append(item)

    payload = {
        "backend": config.backend,
        "model": config.model,
        "language": getattr(info, "language", language),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
        "segments": segments,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def read_transcript(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

