from pathlib import Path
import json
import tarfile
import tempfile
import unittest

from study_media.package import create_study_package
from study_media.settings import Config


class PackageTests(unittest.TestCase):
    def test_create_study_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lesson = root / "library" / "Course" / "Lesson"
            lesson.mkdir(parents=True)
            (lesson / "audio.m4a").write_bytes(b"fake audio")
            (lesson / "transcript.json").write_text(
                json.dumps(
                    {
                        "language": "en",
                        "duration": 1.0,
                        "segments": [{"start": 0.0, "end": 1.0, "text": "Hello"}],
                    }
                ),
                encoding="utf-8",
            )
            (lesson / "transcript.md").write_text("[00:00:00] Hello\n", encoding="utf-8")
            (lesson / "source.json").write_text(
                json.dumps({"course": "Course", "slug": "Lesson", "title": "Lesson"}),
                encoding="utf-8",
            )
            config = Config(
                courses_root=root / "courses",
                library_root=root / "library",
                iphone_export_root=root / "export",
            )

            result = create_study_package("Course/Lesson", config)

            self.assertEqual(result["package"].suffix, ".study")
            with tarfile.open(result["package"], "r") as archive:
                names = set(archive.getnames())
                self.assertEqual(
                    names,
                    {"manifest.json", "audio.m4a", "transcript.json", "transcript.md"},
                )
                manifest_file = archive.extractfile("manifest.json")
                self.assertIsNotNone(manifest_file)
                manifest = json.loads(manifest_file.read().decode("utf-8"))
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["container"], "tar")
            self.assertEqual(manifest["segments_count"], 1)


if __name__ == "__main__":
    unittest.main()
