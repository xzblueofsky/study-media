from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import Any


def format_timestamp(seconds: float, include_ms: bool = False) -> str:
    millis = int(round(seconds * 1000))
    total_seconds, ms = divmod(millis, 1000)
    minutes, sec = divmod(total_seconds, 60)
    hours, minute = divmod(minutes, 60)
    if include_ms:
        return f"{hours:02d}:{minute:02d}:{sec:02d}.{ms:03d}"
    return f"{hours:02d}:{minute:02d}:{sec:02d}"


def render_markdown(
    transcript: dict[str, Any],
    output_path: Path,
    *,
    title: str,
    course: str,
    source_video: Path,
    audio_filename: str,
) -> Path:
    lines = [
        f"# {title}",
        "",
        f"- Course: {course}",
        f"- Source video: `{source_video}`",
        f"- Audio: `{audio_filename}`",
        f"- Transcription model: {transcript.get('backend', 'unknown')} / {transcript.get('model', 'unknown')}",
        f"- Language: {transcript.get('language', 'unknown')}",
        "",
        "## Transcript",
        "",
    ]
    for segment in transcript.get("segments", []):
        start = format_timestamp(float(segment["start"]))
        text = segment.get("text", "").strip()
        if text:
            lines.append(f"[{start}] {text}")
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output_path


def render_html(
    transcript: dict[str, Any],
    output_path: Path,
    *,
    title: str,
    course: str,
    audio_filename: str,
    embed_audio_path: Path | None = None,
) -> Path:
    audio_src = html.escape(audio_filename)
    if embed_audio_path is not None:
        encoded = base64.b64encode(embed_audio_path.read_bytes()).decode("ascii")
        audio_src = f"data:audio/mp4;base64,{encoded}"

    segments_html = []
    for segment in transcript.get("segments", []):
        start = float(segment["start"])
        end = float(segment["end"])
        text = html.escape(segment.get("text", "").strip())
        if not text:
            continue
        stamp = format_timestamp(start)
        segments_html.append(
            '<button class="segment" type="button" '
            f'data-start="{start:.3f}" data-end="{end:.3f}">'
            f'<span class="stamp">{stamp}</span><span class="text">{text}</span>'
            "</button>"
        )

    page = HTML_TEMPLATE.format(
        title=html.escape(title),
        course=html.escape(course),
        audio_src=audio_src,
        segments="\n".join(segments_html),
        transcript_json=json.dumps(transcript, ensure_ascii=False),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8")
    return output_path


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #fbfaf8;
      --fg: #1f2328;
      --muted: #687076;
      --line: #d8dee4;
      --accent: #0a7c72;
      --active-bg: #e5f4f1;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #101214;
        --fg: #eef0f2;
        --muted: #9da7b0;
        --line: #30363d;
        --accent: #4cc9b0;
        --active-bg: #17342f;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.58;
      -webkit-text-size-adjust: 100%;
    }}
    header {{
      position: sticky;
      top: 0;
      z-index: 2;
      background: color-mix(in srgb, var(--bg) 92%, transparent);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(16px);
      padding: 14px 16px 12px;
    }}
    main {{
      width: min(860px, 100%);
      margin: 0 auto;
      padding: 18px 16px 44px;
    }}
    h1 {{
      margin: 0 0 4px;
      font-size: 22px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .course {{
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 10px;
    }}
    audio {{
      display: block;
      width: 100%;
      height: 42px;
    }}
    .segment {{
      display: grid;
      grid-template-columns: 86px minmax(0, 1fr);
      gap: 10px;
      width: 100%;
      border: 0;
      border-bottom: 1px solid var(--line);
      border-radius: 0;
      background: transparent;
      color: inherit;
      padding: 12px 0;
      text-align: left;
      font: inherit;
      cursor: pointer;
      touch-action: manipulation;
      -webkit-tap-highlight-color: color-mix(in srgb, var(--accent) 22%, transparent);
    }}
    .segment:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 3px;
    }}
    .segment.active {{
      background: var(--active-bg);
      margin-inline: -10px;
      padding-inline: 10px;
      border-radius: 6px;
    }}
    .stamp {{
      color: var(--accent);
      font-variant-numeric: tabular-nums;
      font-size: 14px;
      padding-top: 2px;
    }}
    .text {{
      min-width: 0;
      overflow-wrap: anywhere;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <div class="course">{course}</div>
    <audio id="audio" controls preload="metadata" src="{audio_src}"></audio>
  </header>
  <main id="transcript">
    {segments}
  </main>
  <script type="application/json" id="transcript-data">{transcript_json}</script>
  <script>
    const audio = document.getElementById("audio");
    const segments = Array.from(document.querySelectorAll(".segment"));
    let active = null;
    let lastTouchAt = 0;
    let touchStart = null;

    function setActive(button) {{
      if (active === button) return;
      if (active) active.classList.remove("active");
      active = button;
      if (active) {{
        active.classList.add("active");
        active.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
      }}
    }}

    function seekTo(button) {{
      audio.currentTime = Number(button.dataset.start);
      setActive(button);
      const playRequest = audio.play();
      if (playRequest && typeof playRequest.catch === "function") {{
        playRequest.catch(() => {{}});
      }}
    }}

    segments.forEach((button) => {{
      button.addEventListener("touchstart", (event) => {{
        const touch = event.changedTouches[0];
        touchStart = {{ x: touch.clientX, y: touch.clientY, at: Date.now() }};
      }}, {{ passive: true }});

      button.addEventListener("touchend", (event) => {{
        const touch = event.changedTouches[0];
        const moved = touchStart
          ? Math.hypot(touch.clientX - touchStart.x, touch.clientY - touchStart.y)
          : 0;
        const elapsed = touchStart ? Date.now() - touchStart.at : 0;
        touchStart = null;
        if (moved > 12 || elapsed > 900) return;
        event.preventDefault();
        lastTouchAt = Date.now();
        seekTo(button);
      }}, {{ passive: false }});

      button.addEventListener("click", (event) => {{
        if (Date.now() - lastTouchAt < 700) {{
          event.preventDefault();
          return;
        }}
        seekTo(button);
      }});
    }});

    audio.addEventListener("timeupdate", () => {{
      const current = audio.currentTime;
      const match = segments.find((button) => {{
        const start = Number(button.dataset.start);
        const end = Number(button.dataset.end);
        return current >= start && current < end;
      }});
      if (match) setActive(match);
    }});
  </script>
</body>
</html>
"""
