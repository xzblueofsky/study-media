# Design

`study-media` follows a simple local pipeline:

```text
video file
  -> audio.m4a
  -> transcript.json
  -> transcript.md
  -> study.html
  -> iphone_export/
```

## Source Of Truth

Original videos stay in:

```text
/Users/zhaoxin/workspace/study/courses
```

Generated artifacts stay in:

```text
/Users/zhaoxin/workspace/study/study_project/library
```

The iPhone transfer folder is:

```text
/Users/zhaoxin/workspace/study/study_project/iphone_export
```

## Lesson Metadata

Each processed lesson has a `source.json` file. It records source path, size, modified time, transcription model, and generated output paths. Later phases can use this to skip unchanged lessons.

## Dependency Boundary

Most of the project uses only Python standard library. Runtime dependencies are:

- `ffmpeg` and `ffprobe` for media handling.
- `faster-whisper` only when transcription is needed.

This keeps setup simple on a personal Mac while leaving room for future backends such as `whisper.cpp`.

