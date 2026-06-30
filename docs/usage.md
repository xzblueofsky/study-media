# Usage Guide

## Daily Flow

For phase 1, process one video:

```bash
study-media process /Users/zhaoxin/workspace/study/courses/3Blue1Brown/Entropy-Compression.mp4
```

Then send this folder to iPhone:

```text
/Users/zhaoxin/workspace/study/study_project/iphone_export/3Blue1Brown/Entropy-Compression
```

Open the `.m4a` for audio-only listening, the `.md` for plain text reading, or the `.html` for reading while listening.

## When HTML Cannot Find Audio On iPhone

The normal HTML file expects the `.m4a` to be in the same folder. If iPhone separates the files during transfer, rerun with:

```bash
study-media process /path/to/video.mp4 --embed-audio --force-transcript
```

This produces a larger but standalone HTML file in `iphone_export`.

## Model Choice

Good starting points:

```bash
study-media process video.mp4 --model base
study-media process video.mp4 --model small
study-media process video.mp4 --model medium
```

`base` is faster and cheaper for rough study notes. `small` is the default balance. `medium` is slower but often more accurate.

## Language Choice

For English videos:

```bash
study-media process video.mp4 --language en
```

For automatic language detection:

```bash
study-media process video.mp4 --language auto
```

