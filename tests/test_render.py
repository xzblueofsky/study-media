from pathlib import Path
import tempfile
import unittest

from study_media.render import format_timestamp, render_markdown


class RenderTests(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(format_timestamp(65.2), "00:01:05")
        self.assertEqual(format_timestamp(3661.234, include_ms=True), "01:01:01.234")

    def test_render_markdown(self):
        transcript = {
            "backend": "test",
            "model": "tiny",
            "language": "en",
            "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world."}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "transcript.md"
            render_markdown(
                transcript,
                output,
                title="Lesson",
                course="Course",
                source_video=Path("/tmp/source.mp4"),
                audio_filename="audio.m4a",
            )
            text = output.read_text(encoding="utf-8")
        self.assertIn("# Lesson", text)
        self.assertIn("[00:00:00] Hello world.", text)


if __name__ == "__main__":
    unittest.main()

