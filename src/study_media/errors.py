class StudyMediaError(Exception):
    """Base exception for user-facing study-media failures."""


class DependencyError(StudyMediaError):
    """Raised when an external command or Python package is missing."""

