"""Create a portable submission ZIP without caches, Git metadata or build outputs."""

import os
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent.parent
DIRECTORIES = ("exam1", "exam2", "scripts", "tests", "docs", ".github")
EXCLUDED = {"__pycache__", "build", "install", "log", ".venv", ".pytest_cache"}


def main():
    destination = ROOT / "dist" / "python-ros2-assessment.zip"
    destination.parent.mkdir(exist_ok=True)
    files = [ROOT / name for name in ("README.md", "LICENSE", ".gitignore", ".gitattributes")]
    for directory in DIRECTORIES:
        # Prune generated directories before visiting their WSL symlinks.
        for parent, subdirectories, names in os.walk(ROOT / directory, followlinks=False):
            subdirectories[:] = [name for name in subdirectories
                                 if name not in EXCLUDED and not name.endswith(".egg-info")]
            files.extend(Path(parent) / name for name in names
                         if Path(name).suffix not in (".pyc", ".pyo"))
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            if path.is_file():
                archive.write(path, path.relative_to(ROOT).as_posix())
    print(f"Created {destination} ({len(files)} files)")


if __name__ == "__main__":
    main()
