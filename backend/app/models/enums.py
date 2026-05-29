from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    TEACHER = "teacher"
    STUDENT = "student"


class GradingMode(str, Enum):
    STRICT = "STRICT"
    MEDIUM = "MEDIUM"
    LOOSE = "LOOSE"


class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    GRADING = "GRADING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"