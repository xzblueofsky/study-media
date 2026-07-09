from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from . import __version__
from .doctor import run_doctor
from .errors import StudyMediaError
from .package import create_study_package
from .processor import ProcessOptions, process_video
from .settings import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="study-media",
        description="Generate personal iPhone-friendly study packages from videos.",
    )
    parser.add_argument("--version", action="version", version=f"study-media {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process = subparsers.add_parser("process", help="process one video file")
    process.add_argument("video", type=Path, help="source video path")
    process.add_argument("--config", type=Path, default=None, help="config TOML path")
    process.add_argument("--course", help="override course path, for example 3Blue1Brown")
    process.add_argument("--title", help="override lesson title")
    process.add_argument("--slug", help="override filesystem-safe lesson slug")
    process.add_argument("--model", help="override faster-whisper model, for example base or small")
    process.add_argument("--language", help="override transcription language, for example en or auto")
    process.add_argument("--force-audio", action="store_true", help="recreate audio.m4a")
    process.add_argument("--force-transcript", action="store_true", help="recreate transcript files")
    process.add_argument("--skip-transcribe", action="store_true", help="only create/reuse audio")
    process.add_argument("--no-export", action="store_true", help="do not copy files to iphone_export")
    process.add_argument(
        "--embed-audio",
        action="store_true",
        help="embed m4a inside exported HTML so it is a standalone file",
    )
    process.set_defaults(func=run_process)

    status = subparsers.add_parser("status", help="list processed lessons")
    status.add_argument("--config", type=Path, default=None, help="config TOML path")
    status.set_defaults(func=run_status)

    doctor = subparsers.add_parser("doctor", help="check local setup")
    doctor.add_argument("--config", type=Path, default=None, help="config TOML path")
    doctor.set_defaults(func=run_doctor_command)

    package = subparsers.add_parser("package", help="create a .study package for the iPhone app")
    package.add_argument(
        "target",
        help="video path, lesson directory, or course/lesson such as 3Blue1Brown/Entropy-Compression",
    )
    package.add_argument("--config", type=Path, default=None, help="config TOML path")
    package.add_argument("--output", type=Path, default=None, help="output .study path")
    package.set_defaults(func=run_package)

    return parser


def run_process(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    result = process_video(
        args.video,
        config,
        ProcessOptions(
            course=args.course,
            title=args.title,
            slug=args.slug,
            force_audio=args.force_audio,
            force_transcript=args.force_transcript,
            skip_transcribe=args.skip_transcribe,
            export_enabled=not args.no_export,
            embed_audio_in_html=args.embed_audio,
            transcribe_model=args.model,
            transcribe_language=args.language,
        ),
    )
    print("Processed lesson:")
    print(f"  course: {result['course']}")
    print(f"  title:  {result['title']}")
    print(f"  folder: {result['lesson_dir']}")
    print(f"  audio:  {result['audio']}")
    if result["transcript_json"]:
        print(f"  transcript: {result['transcript_json']}")
    for label, path in result["rendered"].items():
        print(f"  {label}: {path}")
    if result["exported"]:
        print("  exported:")
        for label, path in result["exported"].items():
            print(f"    {label}: {path}")
    print(f"  metadata: {result['metadata']}")
    return 0


def run_status(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    if not config.library_root.exists():
        print(f"No library found: {config.library_root}")
        return 0

    sources = sorted(config.library_root.rglob("source.json"))
    if not sources:
        print(f"No processed lessons found under: {config.library_root}")
        return 0

    for source in sources:
        data = json.loads(source.read_text(encoding="utf-8"))
        print(f"{data.get('course')} / {data.get('slug')}: {data.get('transcript_status')}")
    return 0


def run_doctor_command(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    has_error = False
    for name, ok, detail in run_doctor(config):
        marker = "ok" if ok else "missing"
        print(f"{marker:7} {name}: {detail}")
        if not ok and name in {"courses_root", "ffmpeg", "ffprobe"}:
            has_error = True
    return 1 if has_error else 0


def run_package(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    result = create_study_package(args.target, config, output_path=args.output)
    manifest = result["manifest"]
    print("Created study package:")
    print(f"  course:   {manifest['course']}")
    print(f"  title:    {manifest['title']}")
    print(f"  segments: {manifest['segments_count']}")
    print(f"  package:  {result['package']}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except StudyMediaError as exc:
        parser.exit(2, f"study-media: error: {exc}\n")
    except KeyboardInterrupt:
        parser.exit(130, "study-media: interrupted\n")
