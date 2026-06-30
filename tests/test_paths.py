from pathlib import Path
import unittest

from study_media.paths import infer_course, slugify


class PathTests(unittest.TestCase):
    def test_slugify_keeps_readable_names(self):
        self.assertEqual(slugify("Entropy Compression.mp4"), "Entropy-Compression.mp4")
        self.assertEqual(slugify("a/b:c?d"), "a-b-c-d")

    def test_infer_nested_course(self):
        root = Path("/study/courses")
        video = Path("/study/courses/youtube/llm_stanford/lecture.mp4")
        self.assertEqual(infer_course(video, root), "youtube/llm_stanford")


if __name__ == "__main__":
    unittest.main()

