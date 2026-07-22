"""Fail when generated data or common secret files are tracked by Git."""

from pathlib import PurePosixPath
import subprocess
import sys


ALLOWED_PATHS = {PurePosixPath(".env.example")}
FORBIDDEN_NAMES = {
    ".env",
    "db.sqlite3",
    "id_ed25519",
    "id_rsa",
}
FORBIDDEN_DIRECTORIES = {
    ".venv",
    "__pycache__",
    "htmlcov",
    "media",
    "postgres_data",
    "staticfiles",
    "venv",
}
FORBIDDEN_SUFFIXES = {
    ".key",
    ".log",
    ".pem",
    ".sqlite3",
}


def tracked_paths():
    """Return repository paths from Git without reading environment values."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [
        PurePosixPath(path.decode("utf-8"))
        for path in result.stdout.split(b"\0")
        if path
    ]


def is_forbidden(path):
    """Identify common generated or sensitive paths that must not be tracked."""
    if path in ALLOWED_PATHS:
        return False
    return (
        path.name in FORBIDDEN_NAMES
        or any(part in FORBIDDEN_DIRECTORIES for part in path.parts)
        or path.suffix.lower() in FORBIDDEN_SUFFIXES
    )


def main():
    forbidden_paths = [path for path in tracked_paths() if is_forbidden(path)]
    if forbidden_paths:
        print("Refusing to continue: sensitive or generated files are tracked:")
        for path in forbidden_paths:
            print(f"- {path}")
        return 1

    print("Tracked-file check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
