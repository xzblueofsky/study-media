# study-media

`study-media` is a small personal tool for turning course videos into iPhone-friendly study packages:

- `.m4a` audio for listening.
- `.md` transcript for reading, searching, and later note-taking.
- `.html` transcript player for reading while listening.

The project is intentionally local-first. Source videos stay in your course folders, generated assets stay on your Mac, and only the small export folder needs to be sent to your iPhone.

## Current Scope

Phase 1 supports processing one video at a time:

```bash
study-media process /Users/zhaoxin/workspace/study/courses/3Blue1Brown/Entropy-Compression.mp4
```

It creates:

```text
library/
  3Blue1Brown/
    Entropy-Compression/
      audio.m4a
      transcript.json
      transcript.md
      study.html
      source.json

iphone_export/
  3Blue1Brown/
    Entropy-Compression/
      Entropy-Compression.m4a
      Entropy-Compression.md
      Entropy-Compression.html
```

If a same-name `.m4a` already exists next to the video, such as `Entropy-Compression.m4a`, the tool reuses it instead of extracting audio again.

## Install

From this repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[transcribe]'
```

Install `ffmpeg` if it is not already available:

```bash
brew install ffmpeg
```

The first transcription run downloads the selected Whisper model. The default model is `small`.

## Configure

Create a local config file:

```bash
cp config.example.toml config.toml
```

Edit `config.toml` when using another Mac. The default paths are:

```toml
courses_root = "/Users/zhaoxin/workspace/study/courses"
library_root = "/Users/zhaoxin/workspace/study/study_project/library"
iphone_export_root = "/Users/zhaoxin/workspace/study/study_project/iphone_export"
```

`config.toml`, `library/`, and `iphone_export/` are ignored by Git.

## Process One Video

```bash
study-media process /Users/zhaoxin/workspace/study/courses/3Blue1Brown/Entropy-Compression.mp4
```

Useful options:

```bash
study-media process video.mp4 --model base
study-media process video.mp4 --language auto
study-media process video.mp4 --skip-transcribe
study-media process video.mp4 --force-transcript
study-media process video.mp4 --embed-audio
```

`--skip-transcribe` is useful for quickly testing audio extraction. `--embed-audio` creates an exported HTML file with the audio embedded, which is larger but easier to open as a single standalone file on iPhone.

## iPhone Transfer

Since iCloud Drive is full, use one of these:

1. AirDrop the lesson folder under `iphone_export/`. This is simplest for a few lessons. Apple also positions AirDrop for nearby device file transfer: <https://support.apple.com/en-us/102538>
2. For bigger batches, connect the iPhone by USB and use Finder file transfer into an app that can store local files, such as VLC, Infuse, or Documents. Apple documents this Finder flow here: <https://support.apple.com/guide/mac-help/sync-files-to-your-device-mchl4bd77d3a/mac>
3. For local-network transfer, enable macOS File Sharing and connect from the iPhone Files app using `smb://<your-mac-name>.local`.

AirDrop is still the best default for your current workflow. USB Finder transfer is the most reliable fallback when sending many lessons or very large standalone HTML files.

## Development

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

Run the CLI without installing:

```bash
PYTHONPATH=src python -m study_media process /path/to/video.mp4
```

Check local dependencies:

```bash
study-media doctor
```

## Next Phases

- `study-media sync` to scan the whole course tree.
- Better status reporting and retry behavior.
- Optional standalone HTML export by default for selected lessons.
- Optional launchd automation for periodic local processing.
